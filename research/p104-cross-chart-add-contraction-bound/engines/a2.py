"""Price and verify one cross-chart owned-middle A2 contraction."""

from argparse import ArgumentParser
from collections import Counter, deque
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from itertools import permutations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
WORD = 'inputs/7314/WORD.json.gz'
R58 = 'inputs/r58/PRICE.json'
CROSSING = Fraction('0.0036462214364462343366888845568981')
PINS = {
    'admission/ADMITTED.json':'41b8a189dffeb768e5843446cdc469f9cc2f0aa038d0a593cf2be43aa009a9a3',
    'inputs/7113/CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/7298/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7314/EARLY-RESULT.json':'b5043855411432b24336ecc443cba9ebfae6392e2045ddd01c87cfe2c51f5f08',
    'inputs/7314/NATIVE-RESULT.json':'336f463da5afe5b60bfd3b9f0ce8aeea5a5feb1f854613bf4218ba0b28b3371b',
    WORD:'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    R58:'8d70669e720faabc932366dafbc1bd1fdaef6f088c4eb02b0ea3707ba309ab53',
}
EXCLUDE = {863,1355,1568}


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError('Duplicate JSON key')
    return out


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def auth(root):
    files = {}
    for k,v in PINS.items():
        raw = (root/k).read_bytes()
        if sha256(raw).hexdigest() != v:
            raise ValueError(f'Changed input {k}')
        files[k] = raw
    adm = decode(files['admission/ADMITTED.json'])
    assert adm['head'] == HEAD and adm['caller_sha256'] == PINS['inputs/7113/CALLER.json']
    assert adm['status'] == 'independently_reproduced_comparable'
    assert set(adm['stages']) == {'early','native','caller','frontier'}
    for row in [*adm['stages'].values(),adm['source_history']['evidence']]:
        assert sha256((root/'admission'/row['path']).read_bytes()).hexdigest() == row['sha256']
    return files


def scan_stock(word, deadline):
    tape = word['program']
    n = word['public']
    labels = dict(enumerate(word['initial']))
    frames = word['frames']

    @cache
    def span(f):
        s = {0}
        for x in frames[f]:
            assert x not in s
            s.update(x^v for v in tuple(s))
        return s

    def move_rank(a,b,owned):
        if span(a) < span(b) or (owned and span(b) < span(a)):
            return abs(len(frames[b])-len(frames[a]))
        return None

    history = deque(maxlen=3)
    motifs = []
    counts, paid = Counter(), Counter()
    for clock,event in enumerate(tape):
        if monotonic() >= deadline:
            return {'visited':clock,'counts':counts,'keys':motifs,'native_paid':paid,'complete':False}, move_rank
        op,d,*args = event
        if op == 'MOVE':
            a,b,own = args
            assert labels[d] == a and own == (d >= n)
            rank = move_rank(a,b,own)
            assert rank
            paid[rank] += 1
            labels[d] = b
            continue
        if op in ('ADD','COPY'):
            src,coef,chart = args
            assert labels[d] == labels[src] == chart and src != d
        elif op == 'INIT':
            assert d >= n and d not in labels
            labels[d] = args[0]
        elif op == 'CLEAR':
            assert d >= n and labels.pop(d) == args[0]
        else:
            assert op == 'SCALE' and labels[d] == args[-1]
        if op != 'ADD':
            history.clear()
            continue
        history.append(clock)
        if len(history) != 3:
            continue
        counts['consecutive_add_triples'] += 1
        triple = tuple(history)
        events = [tape[k] for k in triple]
        if len({e[-1] for e in events}) == 1:
            continue
        counts['cross_chart_triples'] += 1
        roles = {role for e in events for role in e[1:3]}
        if len(roles) != 3:
            continue
        counts['three_role_cross_chart_triples'] += 1
        if roles & EXCLUDE:
            continue
        for a,b,z in permutations(triple):
            first,second,outer = (tape[i] for i in (a,b,z))
            if first[2] != second[1] or outer[1:3] != [first[1],second[2]]:
                continue
            counts['directed_triangle_any_middle'] += 1
            if first[2] >= n:
                motifs.append({'clocks':triple,'xy':[a,b],'correction':z,'roles':sorted(roles)})
    assert labels == dict(enumerate(word['final']))
    assert len({tuple(m['clocks']) for m in motifs}) == len(motifs)
    return {'visited':len(tape),'counts':counts,'keys':motifs,'native_paid':paid,'complete':True}, move_rank


def price_window(word, item, move_rank):
    tape,public = word['program'],word['public']
    lo,_,hi = item['clocks']
    roles = set(item['roles'])
    entry,exit,old = {},{},Counter()
    for clock in range(lo,hi+1):
        e = tape[clock]
        if e[0] == 'MOVE' and e[1] in roles:
            _,r,a,b,own = e
            entry.setdefault(r,a)
            exit[r] = b
            old[move_rank(a,b,own)] += 1
        elif e[0] == 'ADD':
            for r in e[1:3]:
                entry.setdefault(r,e[-1])
                exit[r] = e[-1]
        else:
            assert e[0] == 'MOVE'
    assert set(entry) == set(exit) == roles
    order = sorted(item['xy'],reverse=True)
    current = entry.copy()
    new = Counter()
    edges = []
    points = [([(r,tape[i][-1]) for r in tape[i][1:3]],i) for i in order]
    points.append((sorted(exit.items()),hi+1))
    for constraints, before in points:
        for r,end in constraints:
            start = current[r]
            if start == end:
                continue
            rank = move_rank(start,end,r>=public)
            if rank is None:
                return {'legal':False,'blocked_edge':[r,start,end], 'entry':entry,'exit':exit}
            new[rank] += 1
            edges.append({'role':r,'from':start,'to':end,'rank':rank,'before_original_clock':before})
            current[r] = end
    assert current == exit
    return {'legal':True,'entry':entry,'exit':exit,'old_local_paid':dict(old),'new_local_paid':dict(new),
            'new_edges':edges,'new_add_order':order}


def action(events, roles):
    rows = {r:[Fraction(r==c) for c in roles] for r in roles}
    for op,d,s,a,_ in events:
        assert op == 'ADD'
        rows[d] = [x+Fraction(a)*y for x,y in zip(rows[d],rows[s],strict=True)]
    return rows


def controls(directed, net):
    x = ['ADD',0,2,'2',0]
    y = ['ADD',2,1,'3',0]
    z = ['ADD',0,1,'6',0]
    # Chronological y,x adds +ab at (0,1). Chronological x,y,z does as well.
    assert action([x,y,z],[0,1,2]) == action([y,x],[0,1,2])
    bad = z[:]
    bad[3] = '-6'
    assert action([x,y,bad],[0,1,2]) != action([y,x],[0,1,2])
    delta = {1:34,2:-17}
    quoted = net.copy()
    quoted.update(delta)
    assert directed(quoted,CROSSING)[0] > 0
    quoted[1] -= 1
    assert directed(quoted,CROSSING)[1] < 0
    return ['exact_signed_a2','wrong_correction_sign','funded_hypothetical_price','extra_paid_rank_one_kills']


def build_price(root, files, deadline):
    early = decode(files['inputs/7314/EARLY-RESULT.json'])
    inv = early['invoice']
    r58 = decode(files[R58])
    assert r58['head'] == HEAD and r58['caller'] == CALLER
    assert r58['paid'] == inv['P'] and r58['targets'] == inv['T']
    assert (sum(inv['P'].values()),sum(inv['T'].values()),inv['S']) == (110536,22461,1424)
    assert Fraction(r58['crossing_upper']) == CROSSING
    net = Counter({int(k):v for k,v in inv['T'].items()})
    net.subtract({int(k):v for k,v in inv['P'].items()})
    directed = run_path(str(root/'inputs/7298/pricing.py'))['cost']
    old = directed(net,CROSSING)
    assert old[1] < 0
    check = controls(directed,net)
    word = decode(decompress(files[WORD]))
    stock, move_rank = scan_stock(word,deadline)
    if stock['complete']:
        reference = decode(files['inputs/7314/NATIVE-RESULT.json'])['native']['paid']
        assert {str(k):v for k,v in stock['native_paid'].items()} == reference
    rows = []
    keys = stock['keys']
    for item in keys[:128]:
        if monotonic() >= deadline:
            break
        geometry = price_window(word,item,move_rank)
        row = {'key':item,'geometry':geometry}
        if geometry['legal']:
            delta = Counter({k:17*v for k,v in geometry['old_local_paid'].items()})
            delta.subtract({k:17*v for k,v in geometry['new_local_paid'].items()})
            changed = net.copy()
            changed.update(delta)
            row['paid_old_minus_new'] = dict(delta)
            row['credit'] = list(map(str,directed(delta,CROSSING)))
            row['complete_margin'] = list(map(str,directed(changed,CROSSING)))
        rows.append(row)
    remaining = keys[len(rows):]
    upper = max([Fraction(0)]+[Fraction(r['credit'][1]) for r in rows if 'credit' in r])
    doc = {'head':HEAD,'caller':CALLER,'input_sha256':PINS,'crossing_upper':str(CROSSING),
           'old_margin':list(map(str,old)),'paid':inv['P'],'targets':inv['T'],'controls':check,
           'stock':stock,'rows':rows,'unvisited_keys':remaining,
           'whole_one_edit_upper_for_visited_keys':str(upper),'cases_cap':128,'seconds_cap':30}
    return doc,word


def support(price,word):
    tape = word['program']
    rows = []
    for row in price['rows']:
        key = row['key']
        before = action([tape[k] for k in key['clocks']],key['roles'])
        after = action([tape[k] for k in sorted(key['xy'],reverse=True)],key['roles'])
        exact = before == after
        funded = 'complete_margin' in row and Fraction(row['complete_margin'][0]) > 0
        rows.append({'key':key,'exact_identity':exact,'positive_price':funded,
                     'candidate':exact and funded})
    return {'head':HEAD,'all_verified_keys':rows,'survivors':[r['key'] for r in rows if r['candidate']],
            'unresolved':len(price['unvisited_keys'])+(not price['stock']['complete'])}


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('mode',choices=['price','support'])
    parser.add_argument('--price-sha')
    args = parser.parse_args()
    start = monotonic()
    frozen,word = build_price(args.root,auth(args.root),start+27)
    if args.mode == 'price':
        result = frozen
    else:
        raw = (args.root/'PRICE.json').read_bytes()
        assert sha256(raw).hexdigest() == args.price_sha
        assert decode(raw) == decode(dumps(frozen))
        result = support(frozen,word)
        result['price_sha256'] = args.price_sha
    print(dumps(result,sort_keys=True,indent=2))
