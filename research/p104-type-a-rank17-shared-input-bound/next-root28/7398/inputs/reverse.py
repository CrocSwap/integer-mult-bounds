"""Reconstruct selected exact signed prefix columns by inverting the caller."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal

CALLER_SHA = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
ZERO = (0,)*17
ONE = (1,)*17
ROOTS = (0,18)


def update(out,source,real=Q(1),imag=Q(0),q=0,stages=ZERO):
    for (phase,body),(a,b) in source.items():
        key = (phase+q)%4, tuple(x+y for x,y in zip(body,stages,strict=True))
        c,d = out.get(key,(0,0))
        value = c+real*a-imag*b,d+imag*a+real*b
        if any(value):
            out[key] = value
        else:
            out.pop(key,None)


def mapped(source,**kw):
    out = {}
    update(out,source,**kw)
    return out


def negative_stages(mask):
    stages = [0]*17
    for stage in mask:
        assert 1 <= stage <= 17 and not stages[stage-1]
        stages[stage-1] = -1
    return tuple(stages)


def undo(rows,event,alpha):
    if event[0]=='J':
        _,stage,(u,v,x,y),_ = event
        for r in (u,v,x,y):
            rows[r] = mapped(rows[r],stages=negative_stages([stage]))
        update(rows[v],rows[u],real=Q(-1),q=-1)
        update(rows[x],rows[y],real=-alpha,q=1)
        return
    if event[0]!='A':
        return
    _,op,r,*args = event
    if op=='SWAP':
        s = args[0]
        rows[r],rows[s] = rows[s],rows[r]
    elif op in ('QUERY','ADD'):
        update(rows[r],rows[args[0]],real=-Q(args[1]) if op=='ADD' else Q(-1),q=args[1] if op=='QUERY' else 0)
    elif op=='SCALE':
        rows[r] = mapped(rows[r],real=1/Q(args[0]))
    elif op=='LAMBDA':
        sign = args[0]
        assert sign in (-1,1)
        source = rows[r]
        rows[r] = mapped(source,real=Q(1,2),imag=Q(-sign,2))
        update(rows[r],source,real=Q(1,2),imag=Q(sign,2),q=2)
    else:
        assert op=='IDLE_ONE'
        rows[r] = mapped(rows[r],stages=negative_stages(args[0]))


def case(rows,slot):
    if [i for i,v in enumerate(rows) if v] != [slot]:
        return {'decision':'multiple_or_different_slot'}
    cell = rows[slot]
    if len(cell)!=1:
        return {'decision':'not_monomial','terms':len(cell)}
    (phase,stages),scalar = next(iter(cell.items()))
    out = {'phase':phase,'body':list(stages),'coefficient':list(map(str,scalar))}
    if any(v not in (0,1) for v in stages):
        return dict(out,decision='not_body_partition')
    first = 8*sum(stages)+(phase%2)
    out['ranks'] = [first,137-first]
    return dict(out,decision='positive_column_only' if 0 < first < 137 else 'zero_rank_side')


def control():
    v = {(0,ZERO):(Q(1),Q(0))}
    before = [v,{}]
    rows = [v.copy(),{}]
    undo(rows,['A','LAMBDA',0,1],Q(1))
    undo(rows,['A','LAMBDA',0,-1],Q(1))
    assert rows==before
    undo(rows,['A','QUERY',1,0,1],Q(1))
    assert case(rows,0)['decision']=='multiple_or_different_slot'
    assert case([v],0)['decision']=='zero_rank_side'
    monomial = {(3,(1,)*8+(0,)*9):(Q(1),Q(0))}
    assert case([monomial],0)['ranks']==[65,72]
    assert case([monomial],0)['decision']=='positive_column_only'
    return ['lambda_inverse','nonisolated_column','zero_rank_control','positive_65_72_control']


def run(caller,prior,prior_hash):
    assert prior['root_cases_visited']==9568 and prior['counts']['interior_support_only']==241
    events=caller['events']; kind=caller['types']['A']; alpha=Q(kind['alpha2'])
    cases = [x for x in prior['witnesses'] if not x['endpoint']]
    assert len(cases)==241 and {x['root'] for x in cases}==set(ROOTS)
    report=[]
    for r in ROOTS:
        row = kind['diagonal'][r]
        assert row[0]==-1 and row[1]==0 and tuple(row[2:])==ONE
        rows = [{} for _ in range(kind['roles'])]
        rows[r] = {(3,ONE):(Q(1),Q(0))}
        boundary = {x['boundary']:x['slot'] for x in cases if x['root']==r}
        assert len(boundary)==sum(x['root']==r for x in cases)
        for i in reversed(range(len(events))):
            if i+1 in boundary:
                slot=boundary[i+1]
                report.append(dict(root=r,boundary=i+1,slot=slot,**case(rows,slot)))
            undo(rows,events[i],alpha)
        assert rows[r]=={(0,ZERO):(Q(1),Q(0))} and all(not v for i,v in enumerate(rows) if i!=r)
    assert len(report)==241
    return {'caller_sha256':CALLER_SHA,'body_one_sha256':prior_hash,'controls':control(),
            'endpoints_recovered':len(ROOTS),'counts':dict(Counter(row['decision'] for row in report)),
            'positive_column_only':[r for r in report if r['decision']=='positive_column_only'],'records':report}


if __name__=='__main__':
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument('caller',type=Path)
    p.add_argument('body_one',type=Path)
    p.add_argument('--body-one-sha',required=True)
    a=p.parse_args()
    def limit(*_):
        raise TimeoutError('independent reverse runner watchdog')
    signal(SIGALRM,limit)
    alarm(60)
    c,b = a.caller.read_bytes(),a.body_one.read_bytes()
    assert sha256(c).hexdigest()==CALLER_SHA and sha256(b).hexdigest()==a.body_one_sha
    print(json.dumps(run(json.loads(c),json.loads(b),a.body_one_sha),indent=2,sort_keys=True))
    alarm(0)
