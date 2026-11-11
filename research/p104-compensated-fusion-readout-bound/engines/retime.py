"""Construct one virtual-zero fusion with exact paid itineraries."""

from argparse import ArgumentParser
from collections import Counter, deque
from fractions import Fraction as Q
from gzip import compress, decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

SOURCE = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
CONTROL_WORD = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
CONTROL_RESULT = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
CONTROL = {
    'role':319, 'entrance_peer':1081, 'readout_peer':1467, 'auxiliary':1567,
    'charts':[1089,207,127], 'cut':44616, 'fusion_clocks':[43029,46308],
    'entrance_coefficient':'-1', 'readout_coefficient':'1',
    'block':[40222,40840,42609,43022,43023,43024,43025,43026,43028,43030,
             43403,43491,43535,43696,43698,43887,45365,45396],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(items):
    value = dict(items)
    require(len(value) == len(items), 'Duplicate JSON key')
    return value


def load(raw):
    return loads(raw, object_pairs_hook=unique)


def checked(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, f'Changed input {path.name}')
    return raw


def canonical(value):
    return dumps(value, sort_keys=True, separators=(',',':')).encode()


def roles(event):
    return event[1:3] if event[0] in ('ADD','COPY') else event[1:2]


def span(frame):
    result = {0}
    for row in frame:
        require(row not in result, 'Dependent chart frame')
        result |= {row ^ old for old in result}
    return result


def add(row, role, value):
    new = row.get(role,Q(0)) + value
    if new:
        row[role] = new
    else:
        row.pop(role,None)


def legal(q):
    d = q.denominator
    for p in (2,3,5):
        while d % p == 0:
            d //= p
    return d == 1 and bool(q) and abs(q)+1 < 2**16 and abs(q.numerator).bit_length() <= 24


def legal_scale(q):
    n = abs(q.numerator)
    if not legal(q):
        return False
    for p in (2,3,5):
        while n % p == 0:
            n //= p
    return n == 1


def identity(block, h, p, q, lam, alpha, beta):
    column = {h:Q(1), p:lam}
    for event in block:
        op, dst = event[:2]
        coefficient = Q(event[-2])
        if op == 'ADD':
            add(column,dst,coefficient*column.get(event[2],Q(0)))
        else:
            add(column,dst,(coefficient-1)*column.get(dst,Q(0)))
    row = {h:Q(1)}
    if q is not None:
        row[q] = -beta
    for event in reversed(block):
        op, dst = event[:2]
        coefficient = Q(event[-2])
        if op == 'ADD':
            add(row,event[2],coefficient*row.get(dst,Q(0)))
        else:
            add(row,dst,(coefficient-1)*row.get(dst,Q(0)))
    require(row == {h:alpha}, 'Wrong exact dirty-output readout')
    discarded = column.pop(h,Q(0))
    require(all(legal(v) for v in column.values()), 'Unsupported or illegal forward correction')
    return column, discarded


def maximal_component(events, public, chart, bypass):
    contacts = {}
    for clock,event in enumerate(events):
        if event[0] in ('ADD','SCALE') and event[-1] == chart and max(roles(event)) < public:
            for role in roles(event):
                contacts.setdefault(role, []).append(clock)
    seen_roles, clocks, pending = {bypass}, set(), [bypass]
    while pending:
        for clock in contacts.get(pending.pop(), []):
            if clock in clocks:
                continue
            clocks.add(clock)
            for role in roles(events[clock]):
                if role not in seen_roles:
                    seen_roles.add(role)
                    pending.append(role)
    return sorted(clocks)


def retime(word, plan):
    original = word['program']
    public, owned = word['public'], word['owned_fields']
    h,p,q,aux = (plan[k] for k in ('role','entrance_peer','readout_peer','auxiliary'))
    low, middle, high = plan['charts']
    cut = plan['cut']
    first, second = plan['fusion_clocks']
    block_ids = plan['block']
    lam = Q(plan['entrance_coefficient'])
    generalized = 'readout_alpha' in plan or 'readout_beta' in plan
    if generalized:
        require('readout_coefficient' not in plan, 'Ambiguous readout coefficient convention')
        alpha,beta = (Q(plan[k]) for k in ('readout_alpha','readout_beta'))
    else:
        alpha,beta = Q(1),-Q(plan['readout_coefficient'])
    require(0 <= h < public and 0 <= p < public and h != p, 'Public distinct bypass role')
    require(q is None or 0 <= q < public and q != h, 'Public distinct readout peer')
    require((q is None) == (beta == 0), 'Readout peer must agree with beta')
    require(public <= aux < public+owned, 'Reuse an existing owned label')
    require(0 <= first < second < len(original) and 0 <= cut < len(original), 'Literal clock bounds')
    require(block_ids == sorted(set(block_ids)) and block_ids and 0 <= block_ids[0] <= block_ids[-1] < len(original), 'Ordered unique block')
    require(legal(lam) and legal_scale(alpha) and (not beta or legal(beta)), 'Illegal entrance/readout coefficient')
    spaces = [span(frame) for frame in word['frames']]
    require(spaces[low] < spaces[middle] < spaces[high], 'Strict nested fusion charts')
    require(original[first] == ['MOVE',h,low,middle,False]
            and original[second] == ['MOVE',h,middle,high,False], 'Exact paid pair')
    block = [original[t] for t in block_ids]
    require(all(e[0] in ('ADD','SCALE') and e[-1] == middle for e in block), 'One scalar coframe')
    require(block_ids == maximal_component(original,public,middle,h), 'Incomplete public coframe component')
    touched = set(r for event in block for r in roles(event))
    required_roles = {h,p} if q is None else {h,p,q}
    require(required_roles <= touched and all(0 <= r < public for r in touched), 'Public block roles')
    forward,discarded = identity(block,h,p,q,lam,alpha,beta)
    require(set(forward) <= touched, 'Correction support stays in the moved block')
    block_set = set(block_ids)
    contacts = {r: [] for r in touched}
    routes = {r: [] for r in touched}
    for clock,event in enumerate(original):
        if event[0] == 'MOVE':
            if event[1] in routes:
                require(not event[-1], 'Public MOVE ownership')
                routes[event[1]].append((clock,event[2],event[3]))
        else:
            for role in roles(event):
                if role in contacts:
                    contacts[role].append(clock)
    lower, upper = 0, len(original)
    for role, clocks in contacts.items():
        chosen = [t for t in clocks if t in block_set]
        require(chosen and [t for t in clocks if chosen[0] <= t <= chosen[-1]] == chosen,
                f'Intervening contact on role {role}')
        if role == h:
            require([t for t in clocks if first < t < second] == chosen, 'All bypassed role contacts retained')
        lower = max(lower,max((t+1 for t in clocks if t < chosen[0]),default=0))
        upper = min(upper,min((t for t in clocks if t > chosen[-1]),default=len(original)))
    require(lower <= cut <= upper, 'No shared legal contact clock')
    route = routes[h]
    fuse_at = next(i for i,leg in enumerate(route) if leg[0] == first)
    require(route[fuse_at:fuse_at+2] == [(first,low,middle),(second,middle,high)], 'Consecutive role-specific paid legs')
    itinerary = {r: list(legs) for r,legs in routes.items()}
    itinerary[h][fuse_at:fuse_at+2] = [(first,low,high)]
    pending = {r: deque(legs) for r,legs in itinerary.items()}
    active = word['initial'] + [None]*owned
    emitted, clocks = [], []

    def append(event):
        op, r = event[:2]
        if op == 'MOVE':
            a,b,is_owned = event[2:]
            require(active[r] == a and is_owned == (r >= public), 'Wrong MOVE source or ownership')
            require(spaces[a] < spaces[b] or is_owned and spaces[b] < spaces[a], 'Illegal paid nesting')
            active[r] = b
        elif op == 'INIT':
            require(r >= public and active[r] is None, 'Owned label already active')
            active[r] = event[2]
        elif op == 'CLEAR':
            require(r >= public and active[r] == event[2], 'Wrong CLEAR chart')
            active[r] = None
        else:
            require(op in ('ADD','COPY','SCALE') and all(active[i] == event[-1] for i in roles(event)), 'Wrong literal coframe')
            require(op == 'SCALE' or event[1] != event[2], 'Aliased scalar contact')
        emitted.append(event)

    def advance(role, frame, source_clock):
        while active[role] != frame:
            require(pending[role], f'No retained route to chart {frame} for role {role}')
            old_clock, a, b = pending[role].popleft()
            require(active[role] == a and spaces[b] <= spaces[frame],
                    f'Retained route misses required coframe for role {role}')
            append(['MOVE',role,a,b,False])
            clocks.append([role,old_clock,source_clock,a,b])

    def scalar(event, source_clock):
        for role in roles(event):
            if role in touched:
                advance(role,event[-1],source_clock)
        append(event)

    def replace_block():
        scalar(['ADD',p,h,str(-lam),low],cut)
        append(['INIT',aux,middle])
        for old in block:
            event = old.copy()
            for i in (1,2) if old[0] == 'ADD' else (1,):
                if event[i] == h:
                    event[i] = aux
            scalar(event,cut)
        append(['CLEAR',aux,middle])
        for role,coefficient in sorted(forward.items()):
            scalar(['ADD',role,h,str(coefficient),high],cut)
        if alpha != 1:
            scalar(['SCALE',h,str(alpha),high],cut)
        if q is not None:
            scalar(['ADD',h,q,str(beta),high],cut)
        if not forward and alpha == 1 and q is None:
            advance(h,high,cut)

    for clock,event in enumerate(original):
        if clock == cut:
            replace_block()
        if clock in block_set or event[0] == 'MOVE' and event[1] in touched:
            continue
        if event[0] in ('ADD','COPY','SCALE'):
            scalar(event,clock)
        else:
            append(event)
    for role in sorted(touched):
        advance(role,word['final'][role],len(original))
    require(all(not remaining for remaining in pending.values()), 'Unemitted paid legs')
    require(active == word['final']+[None]*owned, 'Changed logical endpoints or uncleared owner')
    emitted_routes = {r: [] for r in range(public)}
    original_routes = {r: [] for r in range(public)}
    for program, destination in ((original,original_routes),(emitted,emitted_routes)):
        for event in program:
            if event[0] == 'MOVE' and event[1] < public:
                destination[event[1]].append(tuple(event[2:4]))
    original_routes[h] = [(a,b) for _,a,b in itinerary[h]]
    require(original_routes == emitted_routes, 'Changed undeclared paid itinerary')
    old_owned = [e for e in original if e[0] == 'MOVE' and e[1] >= public]
    new_owned = [e for e in emitted if e[0] == 'MOVE' and e[1] >= public]
    require(old_owned == new_owned, 'Changed owned paid itinerary')
    paid = lambda program: Counter(abs(len(word['frames'][e[3]])-len(word['frames'][e[2]]))
                                   for e in program if e[0] == 'MOVE')
    delta = paid(emitted); delta.subtract(paid(original))
    expected = Counter({len(word['frames'][high])-len(word['frames'][low]):1})
    expected[len(word['frames'][middle])-len(word['frames'][low])] -= 1
    expected[len(word['frames'][high])-len(word['frames'][middle])] -= 1
    sparse = lambda h: {r:n for r,n in sorted(h.items()) if n}
    require(sparse(delta) == sparse(expected), 'Wrong complete paid histogram')
    result = dict(word,program=emitted)
    receipt = {'participants':sorted(touched),'shared_cut_interval':[lower,upper],
                    'paid_delta_per_native':sparse(delta),
                    'replayed_participant_legs':len(clocks),
                    'retimed_legs':sum(new != old for _,old,new,_,_ in clocks),
                    'advanced_legs':[leg for leg in clocks if leg[2] < leg[1]],
                    'preserved_public_itineraries':public-1,
                    'preserved_paid_owned_moves':len(old_owned),'logical_endpoints_unchanged':True,
                    'auxiliary':aux,'ordinary_adds':1+len(forward)+int(q is not None),
                    'forward_correction':{str(r):str(v) for r,v in sorted(forward.items())},
                    'dirty_readout':{str(h):str(alpha)}}
    if generalized:
        receipt.update({'ordinary_scales':int(alpha != 1),
                        'discarded_auxiliary_discrepancy':str(discarded),
                        'readout_alpha':str(alpha),'readout_beta':str(beta),
                        'readout_peer':q})
    return result,receipt


def synthetic_rows(word):
    public = word['public']
    rows = [{r:Q(1)} for r in range(public)]+[{} for _ in range(word['owned_fields'])]
    dirty_clear = False
    for event in word['program']:
        op,dst = event[:2]
        if op == 'SCALE':
            rows[dst] = {k:v*Q(event[2]) for k,v in rows[dst].items()}
        elif op == 'ADD':
            for k,v in rows[event[2]].items():
                add(rows[dst],k,v*Q(event[3]))
        elif op in {'INIT','CLEAR'}:
            if op == 'CLEAR':
                dirty_clear |= bool(rows[dst])
            rows[dst] = {}
    return rows[:public],dirty_clear


def synthetic_control():
    cases = []
    for peer,beta,contact in ((None,'0',['ADD',1,0,'1',1]),(1,'1',['ADD',0,1,'1',1])):
        word = {'public':2,'owned_fields':1,'frames':[[],[1],[1,2]],'initial':[0,0],'final':[2,2],
                'program':[['MOVE',0,0,1,False],['MOVE',1,0,1,False],['SCALE',0,'2',1],
                           contact,['MOVE',0,1,2,False],['MOVE',1,1,2,False]]}
        plan = {'role':0,'entrance_peer':1,'readout_peer':peer,'auxiliary':2,'charts':[0,1,2],
                'cut':2,'fusion_clocks':[0,4],'block':[2,3],'entrance_coefficient':'-1',
                'readout_alpha':'2','readout_beta':beta}
        changed,receipt = retime(word,plan)
        old,_ = synthetic_rows(word)
        new,dirty = synthetic_rows(changed)
        require(new == old and dirty == (peer is not None), 'Synthetic arbitrary-input endpoints or dirty CLEAR differ')
        require(receipt['discarded_auxiliary_discrepancy'] == ('2' if peer is None else '1'),
                'Synthetic discarded coordinate is wrong')
        require(['SCALE',0,'2',2] in changed['program'], 'Missing generalized SCALE')
        if peer is not None:
            require(['ADD',0,peer,beta,2] in changed['program'], 'Missing generalized readout ADD')
        cases.append({'readout_peer':peer,'discarded_coefficient':receipt['discarded_auxiliary_discrepancy'],
                      'cleared_dirty_owned_row':dirty,'exact_public_endpoints_match':True,
                      'paid_delta_per_native':receipt['paid_delta_per_native']})
    require(not legal_scale(Q(7)) and legal_scale(Q(-6,5)), 'Retained SCALE numerator control')
    return {'cases':cases,'forbidden_scale_numerator_rejected':True}


def main():
    parser = ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--known-control',action='store_true')
    group.add_argument('--synthetic-control',action='store_true')
    group.add_argument('--plan',type=Path)
    parser.add_argument('--plan-sha')
    parser.add_argument('--word',type=Path)
    parser.add_argument('--out-word',type=Path)
    args = parser.parse_args()
    if args.synthetic_control:
        require(args.word is None and args.plan_sha is None and args.out_word is None, 'Synthetic control needs no word')
        print(dumps(synthetic_control(),sort_keys=True,indent=2))
        return
    require(args.word is not None, 'Pinned word required')
    if args.known_control:
        require(args.plan_sha is None and args.out_word is None, 'Control does not emit a candidate')
        digest,plan = CONTROL_WORD,CONTROL
    else:
        require(args.plan_sha is not None and args.out_word is not None, 'Require pinned support plan and destination')
        digest,plan = SOURCE,load(checked(args.plan,args.plan_sha))
    word = load(decompress(checked(args.word,digest)))
    if not args.known_control:
        main = set(word['live']) | {r+112 for r in word['live']}
        main |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
        require(plan['role'] not in main | {319,863,1355}, 'Protected or non-helper bypass role')
    result,receipt = retime(word,plan)
    raw = canonical(result)
    receipt.update({'source_sha256':digest,'word_canonical_sha256':sha256(raw).hexdigest()})
    if args.known_control:
        require(receipt['paid_delta_per_native'] == {1:-1,5:-1,6:1}, 'Known-control complete signed price delta')
        require(receipt['word_canonical_sha256'] == CONTROL_RESULT, 'Known author canonical word differs')
        receipt['matches_author_canonical_word'] = True
        intervening = word['program'].copy()
        intervening[43031] = ['SCALE',319,'2',207]
        controls = (
            (word,dict(plan,readout_coefficient='-1'),'Wrong exact dirty-output readout'),
            (dict(word,program=intervening),plan,'Incomplete public coframe component'),
            (word,dict(plan,auxiliary=1568),'Owned label already active'),
        )
        for source, altered, reason in controls:
            try:
                retime(source,altered)
            except ValueError as error:
                require(str(error) == reason, f'Unexpected control rejection {error}')
            else:
                raise ValueError(f'Control accepted instead of {reason}')
        receipt['rejected_controls'] = [row[2] for row in controls]
    else:
        with args.out_word.open('xb') as output:
            output.write(compress(raw,compresslevel=6,mtime=0))
        receipt['word_compressed_sha256'] = sha256(args.out_word.read_bytes()).hexdigest()
    print(dumps(receipt,sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
