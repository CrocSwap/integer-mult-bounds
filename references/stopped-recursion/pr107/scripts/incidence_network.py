#!/usr/bin/env python3
"""Rectangle side circuits with arbitrary scratch restoration and exact counts.

The frame proof is in docs/research/incidence-network.md. This is conditional
on the upstream transfer machinery, not an independent proof of multiplication.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import json

from certify import A, LOG_BOUND, Parameters, certify_parameters, require, verify_sources
from incidence_rectangles import best, rectangles, verify_partition
from reuse_network import triple_matching
from search_network import log_integer_bounds

ROOT=Path(__file__).resolve().parents[1]
BIT_SAVING=Q(46,10**11)


def counts(h=46):
    require(h>=6 and h%2==0,'Even ground size required for stage matching')
    v=comb(h,3);N=v**3;m=h**3
    p=best(h-1,2,2)
    R=h*p.score()
    W=2*N+2*v*v*(R+h)
    L=3*v*v*h*h
    D=N-2*L
    return dict(h=h,v=v,N=N,m=m,rectangles=h*p.count,
                side_roles_per_invocation=R,central_roles_per_invocation=h,
                shared_roles=v*v*(R+h),W=W,L=L,D=D,s=W*m-D,eta=Q(D,W*m))


def parameters():
    a=BIT_SAVING
    return Parameters(1-a,1-A,Q(1,21),9*a/10,1-19*a*a/20,
                      1-9*a*a/10,Q(1,2**67),beta=Q(9,10))


def certificate():
    n=counts()
    partition=verify_partition(45)
    _,log_hi=log_integer_bounds(n['m'])
    require(n['eta']>BIT_SAVING*log_hi,'Insufficient primitive saving')
    require(log_hi<LOG_BOUND and n['eta']>BIT_SAVING*LOG_BOUND,'Simple logarithm bound failed')
    cert=certify_parameters(parameters(),generalized_beta=True,strict_margin=True,
                            layout_model='nonadjacent')
    require(Q(cert['minimum_margin'])==3*BIT_SAVING**2/70,'Wrong minimum margin')
    return dict(status='CONDITIONAL 2^-67 WITNESS; see written scalar and frame proof',
                upstream_commit=verify_sources(),
                bit_counts={k:str(v) for k,v in n.items()},
                pair_partition=partition,bit_saving=str(BIT_SAVING),
                log_m_upper=str(log_hi),deficit_slack=str(n['eta']-BIT_SAVING*log_hi),
                complex_saving_unchanged=str(A),witness=cert,
                verification_boundary='Exact counts, complete pair-partition enumeration and parameter arithmetic; general frame and transfer arguments are written proofs, not formal theorem checking')


def channels(h):
    triples=list(combinations(range(h),3));index={t:i for i,t in enumerate(triples)}
    out=[];offset=0
    p=best(h-1,2,2)
    for common in range(h):
        points=tuple(i for i in range(h) if i!=common)
        for S,T in rectangles(p,points):
            sources=tuple(index[tuple(sorted((common,)+s))] for s in S)
            targets=tuple(index[tuple(sorted((common,)+t))] for t in T)
            ins=tuple(range(offset,offset+len(S)))
            outs=(offset,)+tuple(range(offset+len(S),offset+len(S)+len(T)-1))
            out.append((sources,targets,ins,outs))
            offset+=len(S)+len(T)-1
    require(offset==counts(h)['side_roles_per_invocation'],'Wrong channel count')
    return triples,out,offset


def invoke(x,y,scratch,center,triples,rects,inverse=False):
    def mix(backward=False):
        for sources,targets,ins,outs in rects:
            pivot=ins[0]
            if backward:
                for j in outs[1:]:scratch[j]^=scratch[pivot]
                for i in ins[1:]:scratch[pivot]^=scratch[i]
            else:
                for i in ins[1:]:scratch[pivot]^=scratch[i]
                for j in outs[1:]:scratch[j]^=scratch[pivot]
    def side():
        for sources,targets,ins,outs in rects:
            for t,j in zip(targets,outs):y[t]^=scratch[j]
    def copy():
        for sources,targets,ins,outs in rects:
            for s,i in zip(sources,ins):scratch[i]^=x[s]
    def gather():
        for t,T in enumerate(triples):
            for i in T:center[i]^=x[t]
    def scatter():
        for t,T in enumerate(triples):
            for i in T:y[t]^=center[i]
    ops=('L','J','Li','R','V','G','R','L','J','Li','G','V')
    if inverse:
        ops=tuple({'L':'Li','Li':'L'}.get(op,op) for op in reversed(ops))
    for op in ops:
        if op=='L':mix()
        elif op=='Li':mix(True)
        elif op=='J':side()
        elif op=='R':scatter()
        elif op=='V':copy()
        else:gather()


def exact_invocation(h=6,inverse=False):
    triples,rects,R=channels(h);v=len(triples)
    bits=[1<<i for i in range(2*v+R+h)]
    x=bits[:v];y=bits[v:2*v];scratch=bits[2*v:2*v+R];center=bits[2*v+R:]
    old=[list(z) for z in (x,y,scratch,center)]
    invoke(x,y,scratch,center,triples,rects,inverse)
    require(x==old[0] and y==[a^b for a,b in zip(old[0],old[1])], 'Wrong shear')
    require(scratch==old[2] and center==old[3],'Scratch not restored')
    return dict(h=h,inverse=inverse,input_basis_vectors=len(bits),exact_linear_map=True)


def shared_scalar_model(h=6,seed=1):
    triples,rects,R=channels(h);_,pi=triple_matching(h)
    v=len(triples);N=v**3;q=R+h
    inverse=[0]*v
    for i,j in enumerate(pi):inverse[j]=i
    def payload(i):return ((i*2654435761+seed*2246822519)^(i*i*97))&0xffffffff
    X=[payload(i) for i in range(N)];Y=[payload(N+i) for i in range(N)]
    shared=[payload(2*N+i) for i in range(v*v*q)]
    middle=[payload(2*N+v*v*q+i) for i in range(v*v*q)]
    old=[list(z) for z in (X,Y,shared,middle)]
    def flat(a,b,c):return (a*v+b)*v+c
    for stage in range(3):
        for a in range(v):
            for b in range(v):
                idx=[flat(t,a,b) if stage==0 else flat(a,t,b) if stage==1
                     else flat(a,b,t) for t in range(v)]
                bank=middle if stage==1 else shared
                base=((a*v+b) if stage<2 else (inverse[b]*v+a))*q
                scratch=bank[base:base+R];center=bank[base+R:base+q]
                x=[(Y if stage==1 else X)[i] for i in idx]
                y=[(X if stage==1 else Y)[i] for i in idx]
                invoke(x,y,scratch,center,triples,rects,inverse=(stage==1))
                for i,xx,yy in zip(idx,x,y):
                    if stage==1:Y[i]=xx;X[i]=yy
                    else:X[i]=xx;Y[i]=yy
                bank[base:base+q]=scratch+center
    require(X==old[1] and Y==old[0],'Full network is not a bank exchange')
    require(shared==old[2] and middle==old[3],'Shared arbitrary scratch changed')
    return dict(h=h,seed=seed,roles=2*N+2*v*v*q,payload_bits=32,
                bank_exchange=True,all_scratch_restored=True)


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/incidence-network.json').write_text(
        json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS conditional incidence-network witness 2^-67; minimum',result['witness']['minimum_margin'])
