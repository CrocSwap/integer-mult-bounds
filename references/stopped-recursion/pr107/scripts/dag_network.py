#!/usr/bin/env python3
"""Conditional 2^-63 witness using shared cancellation-free computations."""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import json

from certify import A, LOG_BOUND, Parameters, certify_parameters, require, verify_sources
from exclusion_circuit import ExclusionCircuit
from reuse_network import triple_matching
from search_network import log_integer_bounds

ROOT=Path(__file__).resolve().parents[1]
BIT_SAVING=Q(187,10**11)


def counts(h=46,circuit=None):
    require(h>=6 and h%2==0,'Even ground size required')
    circuit=circuit or ExclusionCircuit(h-1)
    require(circuit.n==h-1,'Mismatched pair circuit')
    v=comb(h,3);N=v**3;m=h**3
    R=h*(circuit.additions+len(circuit.outputs))
    W=2*N+2*v*v*(R+h);L=3*v*v*h*h;D=N-2*L
    return dict(h=h,v=v,N=N,m=m,side_roles_per_invocation=R,
                additions_per_common_point=circuit.additions,
                output_slots_per_common_point=len(circuit.outputs),
                W=W,L=L,D=D,s=W*m-D,eta=Q(D,W*m))


def parameters():
    a=BIT_SAVING
    return Parameters(1-a,1-A,Q(1,21),9*a/10,1-19*a*a/20,
                      1-9*a*a/10,Q(1,2**63),beta=Q(9,10))


def certificate():
    circuit=ExclusionCircuit(45);n=counts(circuit=circuit)
    symbolic=circuit.verify();embedding=circuit.verify_embedding()
    _,log_hi=log_integer_bounds(n['m'])
    require(log_hi<LOG_BOUND and n['eta']>BIT_SAVING*LOG_BOUND,'Insufficient bit saving')
    cert=certify_parameters(parameters(),generalized_beta=True,strict_margin=True,
                            layout_model='nonadjacent')
    require(Q(cert['minimum_margin'])==3*BIT_SAVING**2/70,'Wrong minimum margin')
    return dict(status='CONDITIONAL 2^-63 WITNESS; general transfer proof supplied separately',
                upstream_commit=verify_sources(),bit_counts={k:str(v) for k,v in n.items()},
                circuit=symbolic,embedding=embedding,bit_saving=str(BIT_SAVING),
                complex_saving_unchanged=str(A),log_m_upper=str(LOG_BOUND),
                deficit_slack=str(n['eta']-BIT_SAVING*LOG_BOUND),witness=cert,
                scope='Exact symbolic support, reversible embedding, counts and parameter checks; conditional on the written frame-transfer proof and upstream interfaces')


def program(h):
    c=ExclusionCircuit(h-1);code=c.compile();q=code['roles']
    triples=list(combinations(range(h),3));index={t:i for i,t in enumerate(triples)}
    gates=[];sources=[];outputs=[]
    for common in range(h):
        points=[i for i in range(h) if i!=common];base=common*q
        for node,ins,outs in code['gates']:
            gates.append((tuple(base+i for i in ins),tuple(base+i for i in outs)))
        for pair,slot in code['sources'].items():
            triple=tuple(sorted((common,points[pair[0]],points[pair[1]])))
            sources.append((index[triple],base+slot))
        for pair,slot in code['outputs'].items():
            triple=tuple(sorted((common,points[pair[0]],points[pair[1]])))
            outputs.append((index[triple],base+slot))
    return dict(triples=triples,gates=gates,sources=sources,outputs=outputs,roles=h*q)


def invoke(x,y,scratch,center,code,inverse=False):
    def mix(backward=False):
        gates=reversed(code['gates']) if backward else code['gates']
        for ins,outs in gates:
            pivot=ins[0]
            if backward:
                for slot in outs[1:]:scratch[slot]^=scratch[pivot]
                for slot in ins[1:]:scratch[pivot]^=scratch[slot]
            else:
                for slot in ins[1:]:scratch[pivot]^=scratch[slot]
                for slot in outs[1:]:scratch[slot]^=scratch[pivot]
    def side():
        for t,slot in code['outputs']:y[t]^=scratch[slot]
    def copy():
        for t,slot in code['sources']:scratch[slot]^=x[t]
    def gather():
        for t,T in enumerate(code['triples']):
            for i in T:center[i]^=x[t]
    def scatter():
        for t,T in enumerate(code['triples']):
            for i in T:y[t]^=center[i]
    ops=('L','J','Li','R','V','G','R','L','J','Li','G','V')
    if inverse:ops=tuple({'L':'Li','Li':'L'}.get(op,op) for op in reversed(ops))
    for op in ops:
        if op=='L':mix()
        elif op=='Li':mix(True)
        elif op=='J':side()
        elif op=='R':scatter()
        elif op=='V':copy()
        else:gather()


def exact_invocation(h=6,inverse=False,code=None):
    code=code or program(h);v=len(code['triples']);R=code['roles']
    bits=[1<<i for i in range(2*v+R+h)]
    x=bits[:v];y=bits[v:2*v];scratch=bits[2*v:2*v+R];center=bits[2*v+R:]
    old=[list(z) for z in (x,y,scratch,center)]
    invoke(x,y,scratch,center,code,inverse)
    require(x==old[0] and y==[a^b for a,b in zip(old[0],old[1])],'Wrong shear')
    require(scratch==old[2] and center==old[3],'Scratch not restored')
    return dict(h=h,inverse=inverse,input_basis_vectors=len(bits),exact_linear_map=True)


def shared_scalar_model(h=6,seed=1,code=None):
    code=code or program(h);_,pi=triple_matching(h)
    v=len(code['triples']);N=v**3;R=code['roles'];q=R+h
    inv=[0]*v
    for i,j in enumerate(pi):inv[j]=i
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
                base=((a*v+b) if stage<2 else (inv[b]*v+a))*q
                scratch=bank[base:base+R];center=bank[base+R:base+q]
                x=[(Y if stage==1 else X)[i] for i in idx]
                y=[(X if stage==1 else Y)[i] for i in idx]
                invoke(x,y,scratch,center,code,inverse=(stage==1))
                for i,xx,yy in zip(idx,x,y):
                    if stage==1:Y[i]=xx;X[i]=yy
                    else:X[i]=xx;Y[i]=yy
                bank[base:base+q]=scratch+center
    require(X==old[1] and Y==old[0],'Full bank exchange failed')
    require(shared==old[2] and middle==old[3],'Shared scratch changed')
    return dict(h=h,roles=2*N+2*v*v*q,bank_exchange=True,all_scratch_restored=True)


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/dag-network.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS conditional shared-computation witness 2^-63; minimum',result['witness']['minimum_margin'])
