#!/usr/bin/env python3
"""Characteristic-two counterpart of the public six-field mixed root.

The public construction's rational bases are not reduced modulo two.
Instead the seven canonical nilpotents are verified directly, and binary
commuting stage projectors are synthesized from exact invariant subspaces.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import json,time
H=Path(__file__).resolve().parent
N=6;ALL=(1<<N)-1;I=tuple(1<<j for j in range(N))

def bits(v):
    while v:
        q=v&-v;yield q.bit_length()-1;v^=q

def mm(A,B):
    rows=[]
    for r in A:
        v=0
        for j in bits(r):v^=B[j]
        rows.append(v)
    return tuple(rows)

def add(A,B):return tuple(x^y for x,y in zip(A,B))
def commute(A,B):return mm(A,B)==mm(B,A)
def rank(rows):
    b={}
    for v in rows:
        while v:
            p=v.bit_length()-1
            if p not in b:b[p]=v;break
            v^=b[p]
    return len(b)

def inv(A):
    rows=[r|(1<<(N+j))for j,r in enumerate(A)]
    for j in range(N):
        k=next(k for k in range(j,N)if rows[k]>>j&1);rows[j],rows[k]=rows[k],rows[j]
        for k in range(N):
            if k!=j and rows[k]>>j&1:rows[k]^=rows[j]
    return tuple(r>>N for r in rows)

def span(B):
    vs=[0]
    for v in B:vs += [w^v for w in vs]
    return sum(1<<v for v in vs)

def subspaces(r):
    out=[]
    for piv in combinations(range(N),r):
        pos=[(i,j)for i,p in enumerate(piv)for j in range(p+1,N)if j not in piv]
        for mask in range(1<<len(pos)):
            B=[1<<p for p in piv]
            for k,(i,j)in enumerate(pos):
                if mask>>k&1:B[i]|=1<<j
            out.append((tuple(B),span(B)))
    return out

def projector(U,W):
    cols=U+W;C=tuple(sum(((v>>i)&1)<<j for j,v in enumerate(cols))for i in range(N));ci=inv(C)
    cr=tuple(r&((1<<len(U))-1)for r in C)
    return mm(cr,ci)

def mask_profile(P):
    counts={}
    for m in range(16):
        Q=I
        for j,A in enumerate(P):Q=mm(Q,A if m>>j&1 else add(I,A))
        r=rank(Q)
        if r:counts[str(m)]=r
    assert sum(counts.values())==N
    return counts

def main():
    t=time.monotonic();zero=(0,)*N
    R=[tuple((ALL^(1<<i))if j==i else 0 for j in range(N))for i in range(N)]+[(ALL,)*N]
    S=[];Q=zero
    for A in R:
        assert mm(A,A)==zero and rank(A)==1;Q=add(Q,A);S.append(Q)
    assert Q==I
    sub={r:subspaces(r)for r in (2,3,4)};sets=[];sites=(0,1,5,6);ranks=(2,3,3,2)
    for site,r in zip(sites,ranks):
        u=(1<<site)if site<6 else ALL;v=(ALL^(1<<site))if site<6 else ALL
        Us=[B for B,sp in sub[r]if sp>>u&1 and any((v&w).bit_count()%2 for w in B)]
        Ws=[B for B,sp in sub[N-r]if not any((v&w).bit_count()%2 for w in B)]
        pp=[]
        for U in Us:
            su=span(U)
            for W in Ws:
                if su&span(W)!=1:continue
                P=projector(U,W)
                assert mm(P,P)==P and rank(P)==r
                assert mm(P,R[site])==R[site]and mm(R[site],P)==R[site]
                if commute(P,S[site]):pp.append(P)
        pp=sorted(set(pp));sets.append(pp);print('SITE',site,'RANK',r,'PROJECTORS',len(pp),'seconds',time.monotonic()-t,flush=True)
    # Desired support: A subset B, D subset C, B cap C = A cap D a line.
    before={j:[i for i,A in enumerate(sets[0])if mm(A,B)==A and mm(B,A)==A]for j,B in enumerate(sets[1])}
    after={j:[i for i,D in enumerate(sets[3])if mm(D,C)==D and mm(C,D)==D]for j,C in enumerate(sets[2])}
    hits=[];pairs=0
    for bi,B in enumerate(sets[1]):
        for ci,C in enumerate(sets[2]):
            if not commute(B,C):continue
            T=mm(B,C)
            if rank(T)!=1:continue
            pairs+=1
            aa=[i for i in before[bi]if commute(sets[0][i],C)and mm(sets[0][i],T)==T]
            dd=[i for i in after[ci]if commute(sets[3][i],B)and mm(sets[3][i],T)==T]
            for ai in aa:
                A=sets[0][ai]
                for di in dd:
                    D=sets[3][di]
                    if not commute(A,D)or mm(A,D)!=T:continue
                    P=[A,B,C,D];profile=mask_profile(P)
                    assert profile=={'0':1,'2':1,'3':1,'4':1,'12':1,'15':1}
                    hits.append(dict(projectors=P,masks=profile,indices=[ai,bi,ci,di]))
    out=dict(status='PASS_BINARY_MIXED_ROOT_PROJECTOR_SEARCH',fields=N,nilpotents=R,prefixes=S,sum_nilpotents_identity=True,query_identity='For t=q+1 with t^2=0, product_i(I+t R_i)=I+t sum_iR_i=q I6.',full_sites=sites,stage_ranks=ranks,candidate_projector_counts=list(map(len,sets)),commuting_middle_pairs_with_rank1_intersection=pairs,matching_roots=len(hits),roots=hits,projector_sets=sets,seconds=time.monotonic()-t,scope='Exact binary six-field controller core. Native child substitution, stage-coefficient replay, output normalizers, physical rank routes and complete paid/productive invoice remain separate gates.')
    (H/'BINARY-ROOT-SEARCH.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k not in ('roots','projector_sets','nilpotents','prefixes')},indent=2))

if __name__=='__main__':main()
