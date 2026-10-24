"""Check scalar factors for every complete-minor size on the actual core."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from math import lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
INTERFACE = HERE.parents[1] / 'new-core-transfer-20261017/INTERFACE.json'
PIN = 'c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746'
C = 112
MINORS = [
    [0,7,20,27,36,46,57,111], [21,37,47,76,81,87,92,110],
    [1,6,22,28,33,49,58,109], [2,9,14,19,88,95,101,106],
    [3,8,15,18,89,94,102,105], [4,11,12,17,90,97,99,104],
    [5,10,13,16,91,96,100,103], [23,30,60,75,82,85,98,108],
    [24,34,50,74,83,86,93,107], [25,35,41,48,52,59,61,84],
    [26,38,43,53,54,68,71,79], [29,32,40,45,55,66,73,80],
    [31,39,42,63,64,67,72,78], [44,51,56,62,65,69,70,77],
]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def add(dst, src, scale=F(1)):
    for j, x in src.items():
        value = dst.get(j, F(0)) + scale*x
        if value: dst[j] = value
        else: dst.pop(j, None)


def product(a, b):
    out = []
    for row in a:
        target = {}
        for j, x in row.items(): add(target, b[j], x)
        out.append(target)
    return out


def split(denominator):
    two = 0
    while denominator % 2 == 0:
        denominator //= 2
        two += 1
    return two, denominator


def price(event):
    if event[0] == 'clear': return 2
    if event[0] == 'divide_odd': return 0
    q = F(event[-1])
    if event[0] == 'add':
        need(abs(q) == 1, 'Unit ADD only')
        return 8
    need(event[0] == 'scale', 'Scalar grammar')
    a, b = abs(q.numerator), q.denominator
    need(a and not a & (a-1) and not b & (b-1), 'Signed binary SCALE')
    return 2*(abs(a.bit_length()-b.bit_length()) + int(q < 0))


def factor(r, selected, kind):
    ordinary = set(range(112)) - selected
    k = len(selected)//8
    if kind in ('H','inverse','fused') and not ordinary:
        return [], 1
    events = []
    if kind in ('content','content_inverse'):
        events += [['scale', p, '-1'] for p in sorted(selected)]
    events.append(['clear', C])
    divisor = -4 if kind == 'H' else 4*(k-1 if kind == 'content_inverse' else k-13)
    need(divisor, 'Nonsingular denominator')
    t, odd = split(abs(divisor))
    for row in r:
        query = range(112) if kind in ('content','content_inverse') else sorted(ordinary)
        for p in query:
            if p in row:
                sign = -1 if kind == 'content' and p in selected else 1
                events.append(['add', C, p, str(sign*row[p])])
        events.append(['scale', C, str(F(1, 2**t))])
        if odd > 1: events.append(['divide_odd', C, odd])
        scatter = sorted(ordinary) if kind in ('H','inverse') else range(112)
        for p in scatter:
            if p in row:
                sign = -1 if divisor < 0 else 1
                if kind == 'content_inverse' and p in selected: sign *= -1
                events.append(['add', p, C, str(sign*row[p])])
        events.append(['clear', C])
    return events, odd


def replay(events, odd):
    state = [{j:F(1)} for j in range(113)]
    max_norm, binary, checks = F(1), 0, 0
    predivision = []
    for event in events:
        kind, target = event[:2]
        if kind == 'clear':
            need(target == C, 'Owned clear')
            state[target] = {}
        elif kind == 'add':
            need(target != event[2], 'Distinct ADD fields')
            add(state[target], state[event[2]], F(event[3]))
        else:
            if kind == 'divide_odd':
                need(target == C and event[2] == odd, 'Fixed odd divisor')
                height = lcm(*(split(x.denominator)[1] for x in state[target].values()))
                need(height == 1, 'The completed query has no new odd denominator')
                predivision.append(height)
                q = F(1, odd)
            else:
                need(kind == 'scale', 'Event grammar')
                q = F(event[2])
                need(target == C or q == -1, 'Only data signs or C0 scales')
            state[target] = {j:q*x for j,x in state[target].items()}
        max_norm = max(max_norm, sum(map(abs, state[target].values()),F(0)))
        for x in state[target].values():
            t, d = split(x.denominator)
            binary = max(binary,t)
            need(odd % d == 0, 'One local odd factor at every prefix')
            checks += 1
    if events:
        need(not state[C] and all(C not in row for row in state), 'All C0 columns cleared')
    return state, {'old_real_primitives':sum(map(price,events)),
                   'real_odd_scans':2*sum(e[0]=='divide_odd' for e in events),
                   'odd_divisor':odd, 'additional_binary_height':binary,
                   'prefix_odd_denominator_divides':odd, 'max_row_l1':str(max_norm),
                   'complete_query_odd_divisors':predivision,
                   'literal_events':len(events), 'coefficient_prefix_checks':checks,
                   'events':dict(Counter(e[0] for e in events))}


def division_checks(p):
    for c in range(p):
        for b in (0,1):
            a=(b-c)%2; nxt=(c+p*a-b)//2
            need(0<=nxt<p and 2*nxt==c+p*a-b,'Finite division transition')
    count=0
    for w in range(1,11):
        for n in range(-(1<<(w-1)),1<<(w-1)):
            u=n%(1<<w); c=0; q=0
            for i in range(w):
                b=(u>>i)&1; a=(b-c)%2
                q|=a<<i; c=(c+p*a-b)//2
            sn=(u>>(w-1))&1; sq=(q>>(w-1))&1
            valid=c==p*sq-sn
            need(valid==(n%p==0),'Signed divisibility')
            need(not valid or p*(q-(1<<w)*sq)==n,'Signed quotient')
            count+=1
    return {'odd_divisor':p,'transition_cases':2*p,'signed_inputs':count}


def main(out):
    need(sha256(INTERFACE.read_bytes()).hexdigest()==PIN,'Actual interface pin')
    r=[{int(p):F(x) for p,x in row.items()} for row in json.loads(INTERFACE.read_text())['R']]
    need(sorted(p for minor in MINORS for p in minor)==list(range(112)),'Minor partition')
    for minor in MINORS:
        need(all(sum(r[i].get(p,0)*r[j].get(p,0) for p in minor)==(4 if i==j else 0)
                 for i in range(8) for j in range(8)),'Every actual minor has Gram4I')
        need(all(sum(p in row for p in minor)==4 for row in r),'Four unit entries per minor row')
    eye=[{p:F(1)} for p in range(112)]
    gram=[{q:sum(r[i].get(p,0)*r[i].get(q,0) for i in range(8))
           for q in range(112)} for p in range(112)]
    gram=[{q:x for q,x in row.items() if x} for row in gram]
    reports={}; packets={}; odds=set()
    for k in range(15):
        selected=set(p for minor in MINORS[:k] for p in minor)
        ordinary=set(range(112))-selected
        ru=[{p:x for p,x in row.items() if p in ordinary} for row in r]
        need(all(sum(ru[i].get(p,0)*ru[j].get(p,0) for p in ordinary)==(4*(14-k) if i==j else 0)
                 for i in range(8) for j in range(8)),'Ordinary row Gram')
        restricted=[{q:x for q,x in row.items() if q in ordinary} if p in ordinary else {}
                    for p,row in enumerate(gram)]
        h=deepcopy(eye)
        for p in ordinary: add(h[p],restricted[p],F(-1,4))
        if k==13:
            need(all(not h[p] for p in ordinary),'The8ordinary channels are zero at k13')
            reports[str(k)]={'status':'SINGULAR_ORDINARY_BLOCK','nullity':8}
            continue
        hi=deepcopy(eye); fused=deepcopy(eye)
        for p in range(112):
            add(hi[p],restricted[p],F(1,4*(k-13)))
            add(fused[p],{q:x for q,x in gram[p].items() if q in ordinary},F(1,4*(k-13)))
        need(product(h,hi)==product(hi,h)==eye,'Both ordinary inverse orders')
        e=[{p:F(-1 if p in selected else 1)} for p in range(112)]
        content=deepcopy(e)
        for p in range(112): add(content[p],gram[p],F(1,4*(k-13)))
        targets={'H':h,'inverse':hi,'fused':fused,'content':content}
        if k!=1:
            ci=deepcopy(e)
            for p in range(112):
                add(ci[p],{q:x*(-1 if p in selected else 1)*(-1 if q in selected else 1)
                           for q,x in gram[p].items()},F(1,4*(k-1)))
            need(product(content,ci)==product(ci,content)==eye,'Both content inverse orders')
            targets['content_inverse']=ci
        else:
            ek=[{i:F(-1 if p in selected else 1,4)*r[i].get(p,0)
                 for i in range(8) if r[i].get(p,0)} for p in range(112)]
            need(product(r,ek)==[{i:F(12)} for i in range(8)],'Eight independent kernel channels')
            need(product(content,ek)==[{} for _ in range(112)],'Content kernel at k1')
        row={}; packet={}
        for name,target in targets.items():
            events,odd=factor(r,selected,name)
            actual,receipt=replay(events,odd)
            need(actual[:112]==target,'Literal complete data columns')
            need(not events or len([x for x in events if x[0]=='clear'])==9,'Nine-clear schedule')
            if events:
                wrong=deepcopy(events)
                add_site=next(i for i,x in enumerate(wrong) if x[0]=='add' and x[1]!=C)
                wrong[add_site][-1]=str(-F(wrong[add_site][-1]))
                try:
                    wrong_rows, _ = replay(wrong,odd)
                except ValueError as error:
                    need(str(error) in ('The completed query has no new odd denominator',
                                        'One local odd factor at every prefix'),
                         'Expected denominator rejection for the wrong scatter')
                    receipt['wrong_scatter_control'] = str(error)
                else:
                    need(wrong_rows[:112]!=target,'Wrong scatter sign control')
                    receipt['wrong_scatter_control'] = 'Endpoint mismatch'
            row[name]=receipt; packet[name]=events
            if odd>1: odds.add(odd)
        row['selected_fields']=8*k
        row['predicted_local']={
            'balanced_F_old':164514+416*k+14+row['H']['old_real_primitives'],
            'balanced_B_old':164514+208*k+14+row['inverse']['old_real_primitives'],
            'fused_B_old':164514+208*k+14+row['fused']['old_real_primitives'],
            'B_odd_scans':row['inverse']['real_odd_scans'], 'B_odd_divisor':row['inverse']['odd_divisor'],
            'native_mass':5073}
        reports[str(k)]=row; packets[str(k)]=packet
        print('PASS_MINOR_SIZE',k,row['predicted_local'],flush=True)
    report={'status':'PASS_ALL_COMPLETE_MINOR_SCALAR_FACTORS','interface_sha256':PIN,
            'minors':MINORS,'cases':reports,'fixed_odd_divisors':sorted(odds),
            'uniform_odd_multiple':lcm(*odds),
            'signed_scan_checks':[division_checks(p) for p in sorted(odds)],
            'scope':'All actual scalar columns and every prefix. Literal native transfer, full controller, and complete supplier cost remain separate.'}
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (out.parent/'MINOR-FACTOR-WORDS.json').write_text(json.dumps(packets,separators=(',',':'),sort_keys=True)+'\n')
    print(report['status'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    main(parser.parse_args().out)
