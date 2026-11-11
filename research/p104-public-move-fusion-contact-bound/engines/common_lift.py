"""Exact price and local contact gate for one public MOVE fusion with one ADD."""
from argparse import ArgumentParser
from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
WORD = 'dependencies/round30/complex/source/inputs/WORD.json.gz'
EARLY = 'dependencies/round30/complex/source/inputs/EARLY-RESULT.json'
CALLER = 'dependencies/round30/complex/source/inputs/CALLER.json'
PINS = {
    WORD: '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    EARLY: '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
    CALLER: '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'lead/screen.py': 'c026ccad84094bc5a204aaad462c04dc0b63d92ed4a857fa5445a03b2cc0dbe1',
    'run/PRICE.json': 'b98a469e5250a7644b6e81ade01eb896b5f91bca18465a3166217e03fa35a306',
    'run/SUPPORT.json': '32d05c4efa4c3f6e3cf08fc9dd21478e0fb5218a38556e290966e64193fe2d80',
    'dependencies/7298/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}


def decode(raw):
    def unique(pairs):
        result = dict(pairs)
        assert len(result) == len(pairs), 'duplicate JSON key'
        return result
    return json.loads(raw, object_pairs_hook=unique)


def save(out, name, data):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    tmp.replace(out / name)


def index_contacts(program):
    chains = defaultdict(list)
    for t, event in enumerate(program):
        roles = event[1:3] if event[0] in ('ADD','COPY') else event[1:2]
        assert len(set(roles)) == len(roles)
        for r in roles:
            chains[r].append(t)
    return chains


def next_contact(chain, t):
    i = bisect_right(chain, t)
    return chain[i] if i < len(chain) else None


def contact_gate(program, contacts, row, public):
    t, u = row['moves']
    v, = row['contacts']
    r = row['role']
    a,b,c = row['charts']
    assert t < v < u and r < public
    assert list(program[t]) == ['MOVE',r,a,b,False] and list(program[u]) == ['MOVE',r,b,c,False]
    op,d,s,q,frame = program[v]
    assert op == 'ADD' and frame == b and r in (d,s) and d != s and Q(q)
    peer = s if r == d else d
    own = peer >= public
    assert next_contact(contacts[r],t) == v and next_contact(contacts[r],v) == u
    peer_move = next_contact(contacts[peer],v)
    result = dict(role=r,moves=[t,u],charts=[a,b,c],add_clock=v,add=list(program[v]),
                  other_role=peer,first_other_contact=peer_move)
    if peer_move is None or list(program[peer_move]) != ['MOVE',peer,b,c,own]:
        result.update(status='other_first_contact_not_required_lift',
                      blocking_event=None if peer_move is None else list(program[peer_move]))
        return result
    later = max(u,peer_move)
    assert peer_move != u
    next_r = next_contact(contacts[r],u)
    next_s = next_contact(contacts[peer],peer_move)
    result.update(other_lift_clock=peer_move,later_lift_clock=later,
                  next_moved_role_contact=next_r,next_other_role_contact=next_s)
    if any(clock is not None and clock <= later for clock in (next_r,next_s)):
        result['status'] = 'post_lift_contact_before_join'
        return result
    result.update(status='support_only',remove=[t,v],replace_clock=u,
                  replacement=['MOVE',r,a,c,False],insert_after_clock=later,
                  retimed_add=['ADD',d,s,q,c],unchanged_other_move=list(program[peer_move]))
    return result


def controls():
    positive = [
        ['MOVE',0,0,1,False], ['ADD',0,1,'-3/2',1], ['MOVE',1,1,2,False],
        ['SCALE',2,'2',1], ['MOVE',0,1,2,False], ['ADD',1,0,'1',2],
    ]
    row = dict(moves=[0,4],contacts=[1],role=0,charts=[0,1,2])
    yes = contact_gate(positive,index_contacts(positive),row,3)
    assert yes['status']=='support_only' and yes['retimed_add']==['ADD',0,1,'-3/2',2]
    blocked = positive.copy()
    blocked[3] = ['ADD',2,1,'2',2]
    assert contact_gate(blocked,index_contacts(blocked),row,3)['status']=='post_lift_contact_before_join'
    wrong = positive.copy()
    wrong[2] = ['SCALE',1,'1',1]
    assert contact_gate(wrong,index_contacts(wrong),row,3)['status']=='other_first_contact_not_required_lift'
    reverse = positive[:2]+[positive[4],positive[3],positive[2],positive[5]]
    rev = contact_gate(reverse,index_contacts(reverse),row | {'moves':[0,2]},3)
    assert rev['status']=='support_only' and rev['insert_after_clock']==4
    return ['other_lift_first', 'moved_role_lift_first', 'intervening_read_blocks', 'wrong_first_lift_rejected']


def run(root, out, cap, seconds, start):
    raw = {}
    for name, pin in PINS.items():
        raw[name] = (root/name).read_bytes()
        assert sha256(raw[name]).hexdigest() == pin, ('changed dependency',name)
    word = decode(gzip.decompress(raw[WORD]))
    early,caller = (decode(raw[x]) for x in (EARLY,CALLER))
    old, support = (decode(raw[x]) for x in ('run/PRICE.json','run/SUPPORT.json'))
    assert old['head'] == support['head'] == HEAD and support['scope_exhausted']
    assert not old['unresolved_price'] and not support['unresolved']
    full = old['records']
    prior = support['records']
    assert len(full) == len(prior) == old['pair_scope'] == 4732
    copies,k = old['copies'],Q(old['crossing_upper'])
    assert [e[1] for e in caller['events'] if e[0]=='J'] == list(range(1,18))
    assert copies == 17 and k == Q(early['price']['independent_raw_bracket'][1])
    paid,productive = (Counter({int(r):n for r,n in early['invoice'][key].items()}) for key in ('P','T'))
    assert dict(paid)=={int(r):n for r,n in old['old_full_paid'].items()}
    assert dict(productive)=={int(r):n for r,n in old['old_full_targets'].items()}
    assert sum(paid.values())==110536 and sum(productive.values())==22461
    cost = runpy.run_path(str(root/'dependencies/7298/pricing.py'))['cost']
    matching = runpy.run_path(str(root/'lead/screen.py'))['stock']
    net = productive.copy()
    net.subtract(paid)
    interval = lambda pair: list(map(str,pair))
    baseline = interval(cost(net,k))
    assert baseline == old['old_margin'] and Q(baseline[1]) < 0
    program = word['program']

    @cache
    def quote(x,y):
        delta = Counter({x:copies})
        delta[y] += copies
        delta[x+y] -= copies
        edited = net.copy()
        edited.update(delta)
        return interval(cost(delta,k)),interval(cost(edited,k)),{str(r):n for r,n in delta.items()}

    def key(row):
        return tuple(row['moves'])

    stock, credits = [], {}
    for original,evidence in zip(full,prior,strict=True):
        assert key(original)==key(evidence) and original['role']==evidence['role']
        if len(original['contacts']) != 1:
            continue
        clock = original['contacts'][0]
        if program[clock][0] != 'ADD':
            continue
        assert evidence['status']=='scalar_exclusion' and evidence['scalar_evidence']==[[clock,'nonzero_add_source']]
        assert original['fused_rank']==sum(original['ranks'])
        saving,margin,delta = quote(*original['ranks'])
        assert (saving,margin,delta)==(original['saving'],original['complete_margin'],original['full_paid_old_minus_new'])
        assert key(original) not in credits
        credits[key(original)] = max(Q(0),Q(saving[1]))
        stock.append(original)
    assert len(stock)==len(credits)==1922

    def upper(retained):
        return str(matching(full,[credits.get(key(row),Q(0)) if key(row) in retained else Q(0) for row in full]))

    whole = upper(credits.keys())
    save(out,'PRICE.json',dict(head=HEAD,pins=PINS,crossing_upper=str(k),copies=copies,
        baseline_interval=baseline,original_paid=dict(paid),original_productive=dict(productive),
        eligible_stock=len(stock),whole_compatible_upper=whole,
        cap=cap,seconds_cap=seconds,records=stock,
        grant='One alternative at a time. Whole upper uses each old moved-role MOVE at most once and grants cross-role conflicts and added costs free.'))
    if Q(whole) <= 0:
        return
    chains = index_contacts(program)
    records = []
    for row in stock:
        if len(records)==cap or monotonic()>=start+seconds-1:
            break
        decision = contact_gate(program,chains,row,word['public'])
        decision['complete_margin'] = row['complete_margin']
        decision['directed_paid_lower_positive'] = Q(row['complete_margin'][0])>0
        if decision['status']=='support_only':
            b,c=row['charts'][1:]
            decision['retimed_add_chart_dimensions']=[len(word['frames'][b]),len(word['frames'][c])]
        records.append(decision)
    remaining=stock[len(records):]
    survives=[r for r in records if r['status']=='support_only']
    retained={key(r) for r in remaining+survives}
    save(out,'SUPPORT.json',dict(head=HEAD,pins=PINS,controls=controls(),
        price_sha256=sha256((out/'PRICE.json').read_bytes()).hexdigest(),
        checked=len(records),counts=dict(Counter(r['status'] for r in records)),remaining=[r['moves'] for r in remaining],
        post_support_compatible_upper=upper(retained),survivors=survives,records=records,
        gate='Support and paid price only. Signed native phase, fully charged ordinary work, precision, tape and complete verification pending.'))


def main():
    p=ArgumentParser()
    p.add_argument('round48',type=Path,nargs='?')
    p.add_argument('out',type=Path,nargs='?')
    p.add_argument('--cap',type=int,default=1922,choices=range(1,1923),metavar='1..1922')
    p.add_argument('--seconds',type=int,default=25,choices=range(2,26),metavar='2..25')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if a.round48 is None or a.out is None:
        p.error('explicit Round 48 dependency root and fresh output required')
    a.out.mkdir()

    def timeout(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,timeout)
    alarm(a.seconds)
    try:
        run(a.round48,a.out,a.cap,a.seconds,monotonic())
    except TimeoutError:
        save(a.out,'TIMEOUT.json',dict(head=HEAD,status='hard_timeout',unverified=1922,
                                     price_saved=(a.out/'PRICE.json').exists()))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    main()
