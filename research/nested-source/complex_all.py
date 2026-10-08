#!/usr/bin/env python3
"""Full proper-residual complex batching research audit, preserving PR7 gates."""
from collections import Counter
from fractions import Fraction as Q
from math import comb, log
from pathlib import Path
import argparse,json,sys
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'scripts'))

from paired_complex import PairedComplex
from complex_circuit import compile_roles,Checks,verify_role_frames
from prime_field_network import complex_counts
from controlled_bit_rank_moment import rational_log_bounds,log_integer_upper

def invocation(c,code,reverse=False):
    h=c.h;v=len(c.triples);R=c.roles;n=2*v+R+h+1
    frame=[1]*v+[0]*(n-v);depth=frame.copy();descent=[0]*n
    hist=Counter();classes={};descending=[];count=0
    index={T:i for i,T in enumerate(c.triples)}
    centers=list(range(2*v+R,n))
    dims={node:1 if c.kind[node]=='in' else c.cover(node).bit_count()
        if c.kind[node]=='d0' else c.support[node].bit_count() for node in c.active}
    def gate(wires,dim,name):
        nonlocal count
        wires=set(wires)
        if not wires:return
        rank=[abs(frame[w]-dim) for w in wires]
        ds=[max(0,frame[w]-dim) for w in wires]
        hist.update(rank);classes.setdefault(name,Counter()).update(rank)
        dp=max(depth[w]+r for w,r in zip(wires,rank))
        de=max(descent[w]+s for w,s in zip(wires,ds))
        for w,r,s in zip(wires,rank,ds):
            if s:descending.append((name,w,s))
            frame[w]=dim;depth[w]=dp;descent[w]=de
        count+=len(wires)
        assert dp-dim<=2*de
    def label(mode,node=None):
        return {'low':0,'high':h,'line':1,'perp':h-1}.get(mode,
            dims[node] if mode=='node' else h-dims[node] if mode=='complement' else None)
    def mix(mode,inv=False):
        for node,ins,outs in reversed(code['gates']) if inv else code['gates']:
            gate([2*v+s for s in ins+outs],label(mode,node),'L_'+mode)
    def copy(bank,mode):
        for T,slot in code['sources'].items():
            gate([bank+index[T],2*v+slot],label(mode),'V_'+mode)
    def inject(bank,mode):
        groups=[[] for _ in range(v)]
        for i,slot in code['outputs'].items():groups[index[c.pieces[i][0]]].append(2*v+slot)
        for j,slots in enumerate(groups):gate([bank+j]+slots,label(mode),'J_'+mode)
    def central(bank,mode,name):gate(list(range(bank,bank+v))+centers,label(mode),name)
    if not reverse:
        mix('low');inject(v,'low');mix('low',True);central(v,'low','R_early')
        copy(0,'line');central(0,'high','G_middle');central(v,'low','R_return')
        mix('node');inject(v,'perp');mix('high',True)
        central(0,'high','G_cleanup');copy(0,'high')
    else:
        copy(v,'low');central(v,'low','G_early');mix('low');inject(0,'line')
        mix('complement',True);central(0,'high','R_middle')
        central(v,'low','G_return');copy(v,'perp');central(0,'high','R_cleanup')
        mix('high');inject(0,'high');mix('high',True)
    for j in range(v):gate([j],h,'sink_X');gate([v+j],h-1,'sink_Y')
    for w in range(2*v,n):gate([w],h,'sink_aux')
    expected='G_return' if reverse else 'R_return'
    assert len(descending)==h+1
    assert all(name==expected and w in centers and loss==h for name,w,loss in descending)
    rank_sum=sum(r*cnt for r,cnt in hist.items())
    assert rank_sum==n*h-2*v+2*h*(h+1)
    assert max(descent)==h and max(depth)==3*h
    return dict(h=h,reverse=reverse,roles=n,side_roles=R,physical_edges=count,
        rank_sum=rank_sum,histogram=dict(sorted(hist.items())),
        classes={k:dict(sorted(v.items())) for k,v in classes.items()},
        decreasing_edges=len(descending),decreasing_rank=h*(h+1),
        maximum_path_rank_with_source_envelope=max(depth),max_path_decrease=max(descent))

def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x

def run(h=28,full=False):
    c=PairedComplex(h);code=compile_roles(c)
    check=Checks(c)
    interfaces={}
    if full:
        interfaces={'labels':check.verify_labels(),'roles':verify_role_frames(c,check,code)}
        for node in c.active:
            dim=1 if c.kind[node]=='in' else c.cover(node).bit_count() if c.kind[node]=='d0' else c.support[node].bit_count()
            assert len(check.label(node).basis)==dim
    forward=invocation(c,code);reverse=invocation(c,code,True)
    assert forward['histogram']==reverse['histogram']
    v=comb(h,3);m=h**3;N=v**3;aux=c.roles+h+1;B=v*v*aux
    W=2*v*v*(v+aux);L=3*v*v*h*(h+1);D=2*N-2*L;s=W*m-D
    hist=Counter()
    for row,times in ((forward,2*v*v),(reverse,v*v)):
        for r,cnt in row['histogram'].items():hist[r]+=cnt*times
    external=[
        dict(name='shared_stage1_stage3_auxiliary_join',rank=m-2*h,copies=B),
        dict(name='stage2_auxiliary_sink',rank=m-h*h,copies=B),
        dict(name='stage2_auxiliary_entrance',rank=h*h-h,copies=B),
        dict(name='stage2_data_entrance',rank=(h-1)**2,copies=2*N),
        dict(name='stage3_data_entrance',rank=(h*h-1)*(h-1),copies=2*N)]
    for row in external:hist[row['rank']]+=row['copies']
    assert sum(r*cnt for r,cnt in hist.items())==s
    if h==28:
        cn=complex_counts(c)
        assert all(cn[k]==val for k,val in [('W',W),('L',L),('s',s),('D',D)])
    zero=hist.pop(0,0)
    assert max(hist)<m and min(hist)>=1
    log_bounds={}
    for r in hist:
        if r==1:
            from search_network import log_integer_bounds
            log_bounds[r]=log_integer_bounds(m)
        else:
            # rational_log_bounds converges slowly for large m/r. Extract powers of 2.
            x=Q(m,r);k=0
            while x>=2:x/=2;k+=1
            a,b=rational_log_bounds(x);l2,u2=rational_log_bounds(Q(2))
            log_bounds[r]=(a+k*l2,b+k*u2)
    eta=Q(D,W*m)
    derivative_low=sum((Q(cnt*r,W*m)*log_bounds[r][0] for r,cnt in hist.items()),Q(0))
    derivative_high=sum((Q(cnt*r,W*m)*log_bounds[r][1] for r,cnt in hist.items()),Q(0))
    moments={}
    for a in (Q(1,2**19),Q(21,10**7),Q(25,10**7),Q(3,10**6),Q(4,10**6),Q(419,10**8)):
        upper=sum((Q(cnt*r,W*m)/(1-a*log_bounds[r][1]) for r,cnt in hist.items()),Q(0))
        moments[str(a)]=dict(upper=upper,strict_gap=1-upper,passed=upper<1)
    # Maximize sum a_i^rho under each edge rank <=M and sum a_i<=q.
    q=m+6*h;M=max(hist);rem=q-M
    assert M<q<2*M and rem>0
    rho=Q(3,2);t=Q(m-M,m);y=Q(rem,m)
    # Taylor: (1-t)^1.5 <=1-1.5t+(3/8)t^2/(1-t).
    # Choose an integer reciprocal upper bound on sqrt(y).
    k=1
    while (k+1)**2*y<=1:k+=1
    power_M_upper=1-rho*t+Q(3,8)*t*t/(1-t)
    power_rem_upper=y/k
    theta_bound=power_M_upper+power_rem_upper
    theta=Q(999,1000)
    assert k*k*y<=1 and theta_bound<theta<1
    E=64*(W+m+1)**3
    assert 36*W**3+4*s+4*W+8*m+4<E
    Cdep=1000*(E+16*m+1)
    assert Cdep*(1-theta)>=E and Cdep>=16*m
    beta=Q(1,1000);zeta=Q(1,10000)
    C1=rho-(rho-1)*beta+zeta
    C0=-(- (128*m*(1+1/zeta)*Cdep).numerator//(128*m*(1+1/zeta)*Cdep).denominator)
    return dict(status='FINITE EDGE-RANK AND COMPLEX MOMENT AUDIT; NO NEW MULTIPLICATION CLAIM',
        interfaces=interfaces,local_forward=forward,local_reverse=reverse,
        global_counts=dict(h=h,v=v,m=m,N=N,side_roles=c.roles,auxiliary_roles=aux,
            W=W,L=L,D=D,s=s,eta=eta,zero_rank_edges=zero),
        external_classes=external,global_histogram=dict(sorted(hist.items())),
        all_residuals_proper=True,full_rank_residuals=0,rank_sum_matches=True,
        logarithm_bounds=log_bounds,derivative_lower=derivative_low,derivative_upper=derivative_high,
        fixed_moment_saving_ceiling=eta/derivative_low,
        complex_saving_moments=moments,
        guard=dict(q=q,M=M,remaining_rank=rem,rho=rho,sqrt_remainder_reciprocal=k,
            largest_edge_power_upper=power_M_upper,remainder_power_upper=power_rem_upper,
            path_moment_upper=theta_bound,theta=theta,E=E,Cdep=Cdep,beta=beta,zeta=zeta,C1=C1,C0=C0),
        scope='Exact dimensions and all physical local compiled edges. Full labels and role frames only if --full; coefficient map and dirty scratch unchanged from PR7. Global interface proofs and PR10 batching retained. Bit side not improved here.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');ap.add_argument('--h',type=int,default=28);ap.add_argument('--output',type=Path,default=Path(__file__).with_name('certificate.json'));args=ap.parse_args()
    result=run(args.h,args.full);args.output.write_text(json.dumps(js(result),indent=2)+'\n')
    print('Ranks:',result['global_histogram'])
    print('Moment saving ceiling:',float(result['fixed_moment_saving_ceiling']))
    for a, row in result['complex_saving_moments'].items():print(a,row['passed'],float(row['strict_gap']))
    print('Guard:',result['guard']['rho'],float(result['guard']['path_moment_upper']))
