"""Exact signed Laurent root-factorization gate for the Round 54 cut stock."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import lcm, prod
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
CALLER = '7113/CALLER.json'
REFERENCE = '7113/check_odd_caller_exact_grid.py'
BODY = 'r54/BODY1.json'
PRICE = 'r54/PRICE.json'
PINS = {
    CALLER: '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    REFERENCE: 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
    BODY: 'aed2b0c41cf13c50eea98dac41c05d584fd7358da0ddfff876c2a0ca9e8d4d2a',
    PRICE: '8df5a1b86b5c2429f1581dcf4216d51e45f4297fa94fabc7f9847b128d7568e2',
}


def decode(raw):
    def unique(pairs):
        result = dict(pairs)
        assert len(result)==len(pairs), 'duplicate JSON key'
        return result
    return json.loads(raw,object_pairs_hook=unique)


def write(out,name,obj):
    tmp=out/(name+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    tmp.replace(out/name)


def body(j):
    return 1 << (8*(j-1))


def monomial(q=0,m=0,value=1):
    c=Q(value)
    return ((c.numerator,0,c.denominator,q,m),)


def compile_events(c):
    events = []
    occurrences = Counter()
    alpha = Q(c['types']['A']['alpha2'])
    for e in c['events']:
        if e[0]=='J':
            _,j,(u,v,x,y),(s,t,a,b)=e
            assert (Q(a),Q(b))==(Q(-1),Q(1,2))
            assert len({u,v,x,y,s,t})==6
            operations=[('ADD',v,u,monomial(q=-1)),('ADD',x,y,monomial(q=1,value=alpha)),
                        ('ADD',s,t,monomial(q=1,value=-1)),('ADD',t,s,monomial(q=-1,value=Q(1,2)))]
            operations += [('SCALE',r,r,monomial(m=body(j))) for r in (u,v,x,y,s,t)]
            occurrences[j]+=1
        else:
            _,op,r,*args=e
            if op=='SWAP':
                s,=args
                operations=[('SWAP',r,s,())]
            elif op=='ADD':
                s,value=args
                operations=[('ADD',r,s,monomial(value=value))]
            elif op=='QUERY':
                s,q=args
                operations=[('ADD',r,s,monomial(q=q))]
            elif op=='LAMBDA':
                a,=args
                operations=[('SCALE',r,r,((1,a,2,0,0),(1,-a,2,2,0)))]
            elif op=='SCALE':
                operations=[('SCALE',r,r,monomial(value=args[0]))]
            else:
                assert op in ('IDLE_ONE','IDLE_ODD')
                stages=args[0]
                assert len(stages)==len(set(stages))
                occurrences.update(stages)
                operations=[('SCALE',r,r,monomial(q=args[1] if op=='IDLE_ODD' else 0,
                                                  m=sum(body(j) for j in stages)))]
        events.append(operations)
    assert set(occurrences)==set(range(1,c['stages']+1)) and max(occurrences.values())<256
    # Each original factor occurs at most once along a coefficient path.
    # Using their product as a common grid makes both sweep directions exact.
    grid=prod(lcm(*(term[2] for term in factor)) for ops in events for _,_,_,factor in ops)
    return events,grid,occurrences


def add_scaled(dst,src,factor):
    for a,b,den,q,m in factor:
        for (i,k,d),(x,y) in src.items():
            rr,re=divmod(a*x-b*y,den)
            ii,im=divmod(a*y+b*x,den)
            assert not re and not im, 'inexact integer grid division'
            key=(i,(k+q)%4,d+m)
            u,v=dst.get(key,(0,0))
            value=(u+rr,v+ii)
            if value==(0,0):
                dst.pop(key,None)
            else:
                dst[key]=value


def apply(rows,operations,transpose=False):
    for op,r,s,factor in reversed(operations) if transpose else operations:
        if op=='SWAP':
            rows[r],rows[s]=rows[s],rows[r]
        elif op=='SCALE':
            image={}
            add_scaled(image,rows[r],factor)
            rows[r]=image
        else:
            assert op=='ADD' and r!=s
            if transpose:
                r,s=s,r
            add_scaled(rows[r],rows[s],factor)


def basis(n,grid):
    return [{(i,0,0):(grid,0)} for i in range(n)]


def factorization(phase,degree,n):
    digits=[(degree>>(8*j))&255 for j in range(n)]
    if degree>>(8*n) or any(x>1 for x in digits):
        return 'body_stages_outside_factorization',None
    if phase not in (0,3):
        return 'central_axis_outside_factorization',None
    m=sum(digits)
    left,right=8*m+(phase==3),8*(n-m)+(phase==0)
    if not left or not right:
        return 'zero_rank_side',None
    return 'positive_factorization',([j+1 for j,v in enumerate(digits) if v],left,right)


def assess(rows,root,slot,n):
    row=rows[slot]
    outside_row=sorted({i for i,_,_ in row if i!=root})
    outside_column=[r for r,v in enumerate(rows) if r!=slot and any(i==root for i,_,_ in v)]
    result=dict(outside_row_columns=outside_row,outside_column_rows=outside_column)
    if outside_row or outside_column:
        result['status']='row_and_column_nonisolated' if outside_row and outside_column else (
            'row_nonisolated' if outside_row else 'column_nonisolated')
        return result
    if len(row)!=1:
        result.update(status='isolated_not_monomial',isolated_terms=len(row))
        return result
    (i,phase,degree),value=next(iter(row.items()))
    assert i==root and value!=(0,0)
    status,witness=factorization(phase,degree,n)
    result.update(status=status,phase=phase,degree=degree,scaled_scalar=value)
    if witness:
        stages,r,s=witness
        result.update(prefix_stages=stages,suffix_stages=[j for j in range(1,n+1) if j not in stages],ranks=[r,s])
    return result


def check_body_one(rows,case,grid):
    r,p=case['root'],case['slot']
    for q,field in ((1,'q_plus'),(-1,'q_minus')):
        collapsed=defaultdict(lambda:(0,0))
        for (i,k,_),(a,b) in rows[p].items():
            x,y=collapsed[i]
            collapsed[i]=(x+q**k*a,y+q**k*b)
        assert {i:v for i,v in collapsed.items() if v!=(0,0)}=={r:(Q(case[field][0])*grid,0)}
        for s,row in enumerate(rows[:36]):
            if s==p:
                continue
            a=b=0
            for (i,k,_),(x,y) in row.items():
                if i==r:
                    a+=q**k*x
                    b+=q**k*y
            assert (a,b)==(0,0)


def controls():
    rows=basis(3,4)
    apply(rows,[('SCALE',0,0,monomial(q=3,m=body(1)))])
    assert assess(rows,0,0,17)['ranks']==[9,128]
    apply(rows,[('ADD',1,0,monomial(value=Q(-1,2)))])
    assert assess(rows,0,0,17)['status']=='column_nonisolated'
    rows=basis(3,4)
    apply(rows,[('ADD',0,1,monomial(value=Q(1,2)))])
    assert assess(rows,0,0,17)['status']=='row_nonisolated'
    assert factorization(0,2*body(1),17)[0]=='body_stages_outside_factorization'
    assert factorization(2,body(1),17)[0]=='central_axis_outside_factorization'
    assert factorization(0,0,17)[0]=='zero_rank_side'
    rows=basis(3,4)
    apply(rows,[('ADD',0,1,monomial(q=-1,value=Q(1,2)))],transpose=True)
    assert rows[1][0,3,0]==(2,0)
    return ['positive_complementary_partition','row_and_column_nonisolation_controls',
            'duplicate_stage_wrong_phase_and_zero_rank_rejected','transpose_signed_division']


def load(root):
    files={}
    for name,h in PINS.items():
        raw=(root/name).read_bytes()
        assert sha256(raw).hexdigest()==h,('changed dependency',name)
        files[name]=raw
    return [decode(files[name]) for name in (CALLER,BODY,PRICE)]


def run(root,out,seconds,start):
    control=controls()
    c,body_receipt,price=load(root)
    assert body_receipt['head']==price['head']==HEAD and body_receipt['price_sha256']==PINS[PRICE]
    assert body_receipt['root_cases_visited']==9568 and body_receipt['unresolved_boundary_interval'] is None
    cases=[r for r in body_receipt['witnesses'] if not r['endpoint']]
    keys=[(r['boundary'],r['root'],r['slot']) for r in cases]
    assert len(keys)==len(set(keys))==body_receipt['counts']['interior_support_only']==241
    assert all(0<k<len(c['events']) and r in (0,18) and 0<=p<36 for k,r,p in keys)
    schedule=defaultdict(list)
    for r in cases:
        schedule[r['boundary']].append(r)
    price_class={(r['prefix_stage_count'],r['prefix_central_axis']):r for r in price['stage_partition_classes']}
    events,grid,stage_counts=compile_events(c)
    n=c['stages']
    assert n==17 and c['roles']==72 and len(events)==4783
    rows=basis(c['roles'],grid)
    decisions={}
    candidates={}
    deadline=start+seconds-2
    boundary=0
    endpoint=False
    for boundary in range(1,len(events)+1):
        if monotonic()>=deadline:
            break
        apply(rows,events[boundary-1])
        for case in schedule.get(boundary,()):
            r,p=case['root'],case['slot']
            check_body_one(rows,case,grid)
            result=assess(rows,r,p,n)
            key=(boundary,r,p)
            result.update(boundary=boundary,root=r,slot=p)
            decisions[key]=result
            if result['status']=='positive_factorization':
                quoted=price_class[len(result['prefix_stages']),result['phase']==3]
                assert quoted['ranks']==result['ranks']
                result['optimistic_complete_margin_interval']=quoted['complete_margin_interval']
                result['optimistic_credit_interval']=quoted['credit_interval']
                x,y=result['scaled_scalar']
                result['prefix_scalar']=[str(Q(x,grid)),str(Q(y,grid))]
                result['suffix_scalar']=[str(Q(grid*x,x*x+y*y)),str(Q(-grid*y,x*x+y*y))]
                result['suffix_checked']=False
                candidates[key]=result
    else:
        for ty in c['types'].values():
            for i,(q,z,*bits) in enumerate(ty['diagonal'],ty['offset']):
                assert z==0 and len(bits)==n and set(bits)<={0,1}
                degree=sum(v*body(j) for j,v in enumerate(bits,1))
                assert rows[i]=={(i,q%4,degree):(grid,0)},('old signed endpoint mismatch',i)
        endpoint=True
    if candidates:
        todo=defaultdict(list)
        for key,row in candidates.items():
            todo[key[0]].append(row)
        full=sum(body(j) for j in range(1,n+1))
        adjoint=basis(c['roles'],grid)
        for k in range(len(events),min(todo)-1,-1):
            if monotonic()>=deadline:
                break
            for row in todo.get(k,()):
                p,r=row['slot'],row['root']
                x,y=map(Q,row['suffix_scalar'])
                want={(r,(3-row['phase'])%4,full-row['degree']):(x*grid,y*grid)}
                assert adjoint[p]==want,('signed suffix factor mismatch',k,r,p)
                row['suffix_checked']=True
            if k>min(todo):
                apply(adjoint,events[k-1],transpose=True)
    unresolved=[key for key in keys if key not in decisions or key in candidates and not candidates[key]['suffix_checked']]
    witnessed=[row for row in candidates.values() if row['suffix_checked']]
    complete=endpoint and not unresolved
    counts=dict(Counter(row['status'] for row in decisions.values()))
    report=dict(head=HEAD,pins=PINS,controls=control,seconds_cap=seconds,initial_cases=241,
                tested=len(decisions),unresolved=unresolved,full_old_endpoint_checked=endpoint,
                body_one_specializations_reconciled=len(decisions),grid_bits=grid.bit_length(),
                max_stage_occurrences=max(stage_counts.values()),counts=counts,rows=list(decisions.values()),
                witnessed=witnessed,exhausted=complete,
                status='support_only' if witnessed else 'excluded' if complete else 'incomplete')
    write(out,'RESULT.json',report)
    print(json.dumps({k:report[k] for k in ('tested','unresolved','full_old_endpoint_checked','counts','status')},sort_keys=True))


def main():
    p=ArgumentParser()
    p.add_argument('dependencies',type=Path,nargs='?',default=Path(__file__).resolve().parent/'dependencies')
    p.add_argument('out',type=Path,nargs='?')
    p.add_argument('--seconds',type=int,default=90,choices=range(3,91),metavar='3..90')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if a.out is None:
        p.error('fresh output directory required')
    a.out.mkdir()

    def limit(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,limit)
    alarm(a.seconds)
    try:
        run(a.dependencies,a.out,a.seconds,monotonic())
    except TimeoutError:
        write(a.out,'TIMEOUT.json',dict(head=HEAD,status='hard_timeout',unverified=241,seconds_cap=a.seconds))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    assert __debug__
    main()
