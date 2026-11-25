#!/usr/bin/env python3
"""Exact rational-frame audit with fixed invocation boundaries; no new kappa."""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import json
import random

from audit_cancellation import line_projection
from audit_fused_block import rational_rank
from certify import require, verify_sources
from paired_network import circuit
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def matrix(rows):return tuple(tuple(Q(x) for x in row) for row in rows)
def eye(h):return matrix([[int(i==j) for j in range(h)] for i in range(h)])
def zero(h):return matrix([[0]*h for _ in range(h)])
def sub(A,B):return tuple(tuple(x-y for x,y in zip(a,b)) for a,b in zip(A,B))
def add(A,B):return tuple(tuple(x+y for x,y in zip(a,b)) for a,b in zip(A,B))
def scale(A,c):return tuple(tuple(c*x for x in a) for a in A)


@lru_cache(maxsize=32768)
def rank(A):return rational_rank(A)


def row_basis(rows):
    basis={}
    for row in rows:
        r=[Q(x) for x in row]
        for p,b in sorted(basis.items()):
            c=r[p]
            r=[x-c*y for x,y in zip(r,b)]
        pivot=next((i for i,x in enumerate(r) if x),None)
        if pivot is not None:
            c=r[pivot];basis[pivot]=[x/c for x in r]
    return tuple(tuple(b) for _,b in sorted(basis.items()))


def inverse(A):
    n=len(A);rows=[list(a)+list(b) for a,b in zip(A,eye(n))]
    for j in range(n):
        p=next((i for i in range(j,n) if rows[i][j]),None)
        require(p is not None,'Singular Gram matrix')
        rows[j],rows[p]=rows[p],rows[j]
        c=rows[j][j];rows[j]=[x/c for x in rows[j]]
        for i in range(n):
            if i!=j:
                c=rows[i][j];rows[i]=[x-c*y for x,y in zip(rows[i],rows[j])]
    return matrix([r[n:] for r in rows])


def product(A,B):
    return matrix([[sum(x*y for x,y in zip(a,b)) for b in zip(*B)] for a in A])


def span_projection(rows,h):
    U=row_basis(rows)
    if not U:return zero(h)
    H=matrix([[Q(int(i==j))-Q(1,9) for j in range(h)] for i in range(h)])
    Ut=matrix(zip(*U));UH=product(U,H)
    return product(product(Ut,inverse(product(UH,Ut))),UH)


def paired_invocation(h=6):
    """Build every physical edge of the forward paired invocation.

    Terminals are active-factor cuts, not the negative X source terminals
    of the complete three-stage network. All scalar gates retain their
    published grouping. The returned graph admits arbitrary gate matrices.
    """
    c=circuit(h);code=c.compile();v=len(c.inputs);R=code['roles']
    I=eye(h);Z=zero(h)
    P=[matrix(line_projection(h,t)) for t in c.inputs]
    spans={}
    labels={}
    for node in sorted(c.active):
        if c.args[node]:
            a,b=c.args[node];spans[node]=row_basis(spans[a]+spans[b])
        else:
            t=c.inputs[node-1];spans[node]=(tuple(Q(i in t) for i in range(h)),)
        labels[node]=span_projection(spans[node],h)
        require(product(labels[node],labels[node])==labels[node],'Not a projection')
    groups=['X']*v+['Y']*v+['side']*R+['center']*h
    starts=P+[Z]*v+[Z]*(R+h)
    ends=[I]*v+[sub(I,p) for p in P]+[I]*(R+h)
    frames={('in',i):M for i,M in enumerate(starts)}
    last=[('in',i) for i in range(len(starts))];edges=[]
    def gate(name,roles,M):
        require(name not in frames,'Repeated vertex')
        frames[name]=M
        for r in sorted(set(roles)):
            edges.append((last[r],name,groups[r]));last[r]=name
    sources={t:[] for t in c.inputs};outputs={t:[] for t in c.inputs}
    for t,s in code['sources'].items():sources[t].append(2*v+s)
    for (_,t),s in code['outputs'].items():outputs[t].append(2*v+s)
    centers=list(range(2*v+R,2*v+R+h))
    ops=('L','J','Li','R','V','G','R','L','J','Li','G','V')
    central=[]
    for step,op in enumerate(ops):
        if op in ('L','Li'):
            gates=code['gates'] if op=='L' else reversed(code['gates'])
            for node,ins,outs in gates:
                M=labels[node] if step==7 else I if step==9 else Z
                gate((step,node),[2*v+s for s in set(ins+outs)],M)
        elif op in ('V','J'):
            for j,t in enumerate(c.inputs):
                if op=='V':roles=[j]+sources[t];M=P[j] if step==4 else I
                else:roles=[v+j]+outputs[t];M=Z if step==1 else sub(I,P[j])
                gate((step,j),roles,M)
        else:
            gate((step,'central'),list(range(v)) if op=='G' else list(range(v,2*v)),
                 I if op=='G' else Z)
            # The scalar central gate is common to the data bank AND centers.
            name=(step,'central')
            for r in centers:
                edges.append((last[r],name,groups[r]));last[r]=name
            central.append(name)
    for r,M in enumerate(ends):
        name=('out',r);frames[name]=M;edges.append((last[r],name,groups[r]))
    return dict(h=h,v=v,R=R,frames=frames,edges=edges,central=central)


def score_graph(graph,changes=None):
    frames=graph['frames']|dict(changes or {});score=Counter()
    require(all(k in graph['frames'] and k[0] not in ('in','out')
                for k in (changes or {})),'Only internal gates may change')
    for u,v,kind in graph['edges']:score[kind]+=rank(sub(frames[v],frames[u]))
    return dict(score)


def invocation_counts(h,R):
    v=comb(h,3)
    return dict(h=h,v=v,side_roles=R,data_rank=2*v*(h-1),
                side_rank=R*h,center_rank=3*h*h,
                total_rank=R*h+2*v*(h-1)+3*h*h,
                center_return_loss=h*h,density=Q(v,h),
                density_minus_center_roles=Q(v,h)-h)


def central_score(h,D,A,C,B):
    """Exact data and center path charge after eliminating side gates.

    Paths: P_t -> A -> B -> I; 0 -> D -> C -> I-P_t;
    and h copies of 0 -> D -> A -> C -> B -> I.
    """
    I=eye(h);Z=zero(h);v=comb(h,3)
    data=sum(rank(sub(A,matrix(line_projection(h,t))))+
             rank(sub(sub(I,matrix(line_projection(h,t))),C))
             for t in combinations(range(h),3))
    data+=v*(rank(sub(B,A))+rank(sub(I,B))+rank(D)+rank(sub(C,D)))
    center=h*(rank(D)+rank(sub(A,D))+rank(sub(C,A))+rank(sub(B,C))+rank(sub(I,B)))
    return data+center


def central_lower_bound(h,A,C):
    """All-rational-matrix bound, proved in the accompanying note."""
    I=eye(h);v=comb(h,3)
    x=h-rank(A);y=h-rank(sub(I,C))
    u=rank(A)+rank(sub(I,A))-h
    w=rank(C)+rank(sub(I,C))-h
    return (v-h)*(u+w)+2*(Q(v,h)-h)*(x+y)


def density_control(h,M):
    k=rank(M);v=comb(h,3)
    actual=sum(rank(sub(M,matrix(line_projection(h,t))))
               for t in combinations(range(h),3))
    lower=v*(k-1)+2*Q(v,h)*(h-k)
    require(actual>=lower,'Rational rank-density inequality failed')
    return actual,lower


def rational_controls(h=10):
    """Bounded nonsymmetric, nonprojector controls, not the general proof."""
    rng=random.Random(10959);I=eye(h);Z=zero(h)
    P=matrix(line_projection(h,(0,1,2)))
    E=matrix([[int(i==0 and j==1) for j in range(h)] for i in range(h)])
    matrices=[Z,I,P,sub(I,P),scale(P,Q(2,3)),E,sub(I,E)]
    for _ in range(5):
        U=matrix([[rng.randrange(-2,3) for _ in range(2)] for _ in range(h)])
        V=matrix([[Q(rng.randrange(-2,3),3) for _ in range(h)] for _ in range(2)])
        matrices.append(product(U,V))
    for M in matrices:density_control(h,M)
    S0=2*comb(h,3)*(h-1)+3*h*h
    records=[]
    for j,M in enumerate(matrices):
        A=M;C=matrices[-1-j]
        # Noncanonical outer gates ensure both sides of each change are charged.
        D=matrices[(j+2)%len(matrices)];B=matrices[(j+3)%len(matrices)]
        actual=central_score(h,D,A,C,B)
        lower=central_lower_bound(h,A,C)
        require(actual-S0>=lower>=0,'Central all-matrix lower bound failed')
        records.append(dict(score=actual,lower_excess=lower))
    require(central_score(h,Z,I,Z,I)==S0,'Baseline central score changed')
    return dict(h=h,matrix_controls=len(matrices),central_controls=records,
                baseline_central_score=S0)


def certificate():
    graph=paired_invocation(6);scores=score_graph(graph)
    n=invocation_counts(6,graph['R'])
    require(scores==dict(X=n['data_rank']//2,Y=n['data_rank']//2,
                        side=n['side_rank'],center=n['center_rank']),
            'Physical edge score does not reproduce formula')
    # Read the published exact role count without changing that certificate.
    published=json.loads((ROOT/'certificates/paired-network.json').read_text())['bit_counts']
    full=invocation_counts(50,int(published['side_roles_per_invocation']))
    require(full['center_return_loss']*3*full['v']**2==int(published['L']),
            'Local loss does not reproduce published loss')
    return dict(status='FIXED-BOUNDARY BIT INVOCATION RANK OPTIMALITY; NO NEW KAPPA',
                upstream_commit=verify_sources(),small_physical_graph=n,
                physical_edge_scores=scores,physical_edges=len(graph['edges']),
                rational_controls=rational_controls(),published_invocation=full,
                theorem='For h>=10, arbitrary rational internal active-factor matrices cannot lower the complete rank score with fixed invocation boundaries, side-role count, and the four grouped central gates.',
                scope='Allows joint copy, injection, side and central frame changes. Retains active-factor embedding and all boundary matrices. Does not exclude new cross-invocation boundaries, changed central gate grouping, fewer roles or new scalar topology.',
                next_step='Optimize a region crossing invocation boundaries or split the grouped central gates; optimizing only internal matrices of the present invocation is exhausted in this model.')


if __name__=='__main__':
    (ROOT/'certificates/joint-frame-audit.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS fixed-boundary rational-frame audit; no new kappa.')
