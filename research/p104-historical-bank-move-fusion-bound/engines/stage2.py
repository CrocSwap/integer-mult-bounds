"""Exact reverse span for at most six highest-priced support survivors."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
CASE_CAP,SECONDS=6,45


def stop(*_):
    raise TimeoutError('45-second exact stage2 cap')


def capture(word, cases):
    n=word['public']
    charts=word['initial']+[None]*word['owned_fields']
    starts={}
    finished={}
    cuts={c['clocks'][2]+1:c for c in cases}
    asks={c['clocks'][1]:c for c in cases}
    banks={}
    for t,e in enumerate(word['program']):
        if t in asks:
            c=asks[t]
            assert e[:3]==['ADD',c['role'],c['peer']]
        if t in cuts:
            c=cuts[t]
            roles=[r for r,x in enumerate(charts) if x==c['chart'] and r!=c['role']]
            assert len(roles)==c['bank_count']
            assert sha256(dumps(roles).encode()).hexdigest()==c['bank_role_sha256']
            banks[tuple(c['clocks'])]=(roles,{r:starts[r] for r in roles if r>=n})
        op,d,*args=e
        if op=='MOVE':
            assert charts[d]==args[0]
            charts[d]=args[1]
        elif op=='INIT':
            assert charts[d] is None
            charts[d]=args[0]
            starts[d]=t
        elif op=='CLEAR':
            assert charts[d]==args[0]
            charts[d]=None
            finished[d,starts.pop(d)]=t
    assert len(banks)==len(cases) and not starts
    return {key:(roles,{r:[t,finished[r,t]] for r,t in init.items()}) for key,(roles,init) in banks.items()}


def exact_dot(row, dual):
    d,denom=row
    return sum((Q(d.get(j,0),denom)*x for j,x in dual.items()),Q(0))


def validate(decision, bank, target):
    if decision['status']=='exact_rank_exclusion':
        dual={int(j):Q(v) for j,v in decision['separating_covector'].items()}
        assert all(not exact_dot(r,dual) for _,r in bank)
        assert exact_dot(target,dual)==Q(decision['separated_target'])!=0
    elif decision['status']=='absent_exterior_coordinate':
        j=decision['coordinate']
        assert all(j not in row for _,(row,_) in bank)
        assert exact_dot(target,{j:Q(1)})==Q(decision['target_coefficient'])!=0
    else:
        assert decision['status']=='exact_span'
        rows=dict(bank)
        out=defaultdict(Q)
        for role,coef in decision['coefficients'].items():
            row,denom=rows[int(role)]
            for j,x in row.items():
                out[j]+=Q(x,denom)*Q(coef)
        row,denom=target
        assert {j:x for j,x in out.items() if x}=={j:Q(x,denom) for j,x in row.items()}


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    until=monotonic()+SECONDS-1
    prior=run_path(str(ROOT/'stage1.py'))
    stage1_raw=(ROOT/'STAGE1.json').read_bytes()
    old=loads(stage1_raw,object_pairs_hook=prior['unique'])
    assert not old['capped'] and not old['unvisited'] and len(old['records'])==967
    assert old['head']==prior['HEAD'] and old['caller']==prior['CALLER'] and old['pins']==prior['PINS']
    survivors=old['screen_survivors']
    assert survivors==sorted(survivors,key=lambda c:(-Q(c['gross'][0]),c['clocks']))
    selected=survivors[:CASE_CAP]
    keys=[c['clocks'] for c in selected]
    rows_examined=0
    checked=[]
    winner=None
    cap=None
    try:
        data=decompress(prior['read']('inputs/7334-WORD.json.gz'))
        assert sha256(data).hexdigest()==prior['PAYLOAD']
        word=loads(data,object_pairs_hook=prior['unique'])
        banks=capture(word,selected)
        prior['read']('inputs/reverse_span.py')
        engine=run_path(str(ROOT/'inputs/reverse_span.py'))
        requests=defaultdict(list)
        ids={}
        for c in selected:
            a,m,b=c['clocks']
            roles,_=banks[a,m,b]
            for clock,role in [(m,c['peer']),*((b+1,r) for r in roles)]:
                if (clock,role) not in ids:
                    ids[clock,role]=len(ids)
                    requests[clock].append((role,ids[clock,role]))
        results=engine['transpose_prefix'](word,requests,len(ids),until)
        assert len(results)==len(ids)
        rows_examined=len(results)
        for c in selected:
            a,m,b=c['clocks']
            roles,lifetimes=banks[a,m,b]
            target=results[ids[m,c['peer']]]
            assert {str(j):str(Q(x,target[1])) for j,x in target[0].items()}==c['target_row']
            bank=[(r,results[ids[b+1,r]]) for r in roles]
            decision=engine['exact_span'](bank,target)
            validate(decision,bank,target)
            record={'clocks':c['clocks'],'role':c['role'],'peer':c['peer'],'chart':c['chart'],
                    'bank_cut':b+1,'bank_roles':roles,'bank_rows':bank,'target':target,
                    'gross':c['gross'],'ranks':c['ranks'],'decision':decision}
            checked.append(record)
            if decision['status']=='exact_span':
                coeffs={int(r):Q(x) for r,x in decision['coefficients'].items()}
                winner={**record,'active_donor_lifetimes':{r:lifetimes.get(r,'public') for r in coeffs},
                        'ordinary_add_count':len(coeffs),'dyadic':all(x.denominator.bit_count()==1 for x in coeffs.values()),
                        'remaining_gate':'exact physical signed forward/adjoint and direct MOVE composition, full ordinary/precision/ownership/tape/recurrence invoice and complete independent replay'}
                break
    except TimeoutError as err:
        cap=str(err)
    finally:
        alarm(0)
    visited={tuple(c['clocks']) for c in checked}
    print(dumps({'head':old['head'],'caller':old['caller'],'stage1_sha256':sha256(stage1_raw).hexdigest(),
                 'case_cap':CASE_CAP,'seconds_cap':SECONDS,'checked':checked,'frozen_keys':keys,
                 'unresolved_within_top_six':[k for k in keys if tuple(k) not in visited],
                 'outside_top_six_unresolved_count':len(survivors)-len(selected),
                 'reconstructed_rows':rows_examined,'capped':cap is not None,'cap_reason':cap,
                 'winner':winner},sort_keys=True,indent=2,default=str))
    if cap:
        raise SystemExit(2)


if __name__=='__main__':
    main()
