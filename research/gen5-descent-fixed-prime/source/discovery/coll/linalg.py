"""Exact rational helpers for 24-dim frames (bases B, annihilators A) and the G=I-J/9 Gram form."""
from fractions import Fraction as Q
from math import gcd, lcm
import itertools, random

def rref(rows):
    M=[[Q(x) for x in r] for r in rows]; piv=[]; r=0
    ncol=len(M[0]) if M else 0
    for c in range(ncol):
        p=next((i for i in range(r,len(M)) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]; pv=M[r][c]; M[r]=[x/pv for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                m=M[i][c]; M[i]=[x-m*y for x,y in zip(M[i],M[r])]
        piv.append(c); r+=1
        if r==len(M): break
    return M[:r],piv

def rank(rows): return len(rref(rows)[0]) if rows else 0

def nullspace(rows, ncol=24):
    """integer basis of {x : rows x = 0}"""
    if not rows: return [[int(i==j) for j in range(ncol)] for i in range(ncol)]
    R,piv=rref(rows); free=[j for j in range(ncol) if j not in piv]; out=[]
    for fj in free:
        x=[Q(0)]*ncol; x[fj]=Q(1)
        for row,pc in zip(R,piv): x[pc]=-row[fj]
        out.append(integerize(x))
    return out

def integerize(x):
    d=lcm(*(q.denominator for q in x)) if x else 1
    v=[int(q*d) for q in x]; g=0
    for a in v: g=gcd(g,abs(a))
    if g>1: v=[a//g for a in v]
    # sign normalisation: first nonzero positive
    for a in v:
        if a: 
            if a<0: v=[-b for b in v]
            break
    return v

def intersect(frames_B, frames_A):
    """exact intersection of frames given by (B,A) pairs: nullspace of stacked annihilators, then confirm."""
    A=[row for a in frames_A for row in a]
    return nullspace(A)

def contains(big_rows, small_rows):
    """span(small) subseteq span(big)?"""
    if not small_rows: return True
    if not big_rows: return False
    return rank(list(big_rows)+list(small_rows))==rank(big_rows)

def gram(rows):
    s=[sum(r) for r in rows]
    return [[9*sum(a*b for a,b in zip(x,y))-s[i]*s[k] for k,y in enumerate(rows)] for i,x in enumerate(rows)]

def det(A):
    A=[list(r) for r in A];n=len(A)
    if not n:return 1
    sign=1;previous=1
    for k in range(n-1):
        pivot=next((i for i in range(k,n) if A[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:A[k],A[pivot]=A[pivot],A[k];sign=-sign
        p=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=A[i][j]*p-A[i][k]*A[k][j]
                assert v%previous==0
                A[i][j]=v//previous
            A[i][k]=0
        previous=p
    return sign*A[-1][-1]

def nondeg(rows): return det(gram(rows))!=0

def canon(rows):
    """canonical hashable key of a subspace"""
    R,_=rref(rows); return tuple(tuple(integerize(r)) for r in R)

def nondeg_subspaces(E, max_tries=200, seed=0):
    """for each e=1..dim E, one nondegenerate e-dim integer basis inside span(E), or None"""
    k=len(E); out={}
    if k==0: return out
    rng=random.Random(seed)
    ann=nullspace(E)   # annihilator rows of span(E)
    simple=[]
    for i in range(24):
        for j in range(i+1,24):
            if all(a[i]-a[j]==0 for a in ann):
                u=[0]*24; u[i]=1; u[j]=-1; simple.append(u)
    for e in range(k,0,-1):
        found=None
        if e==k and nondeg(E): found=[list(r) for r in E]
        if found is None:
            cands=[]
            if e==1: cands=[[u] for u in simple]+[[list(r)] for r in E]
            subs=list(itertools.combinations(range(k),e)) if e<k else [tuple(range(k))]
            if len(subs)>max_tries: subs=rng.sample(subs,max_tries)
            cands+= [[list(E[i]) for i in sub] for sub in subs]
            for c in cands:
                if nondeg(c): found=c; break
            if found is None:
                for _ in range(40):
                    rows=[]
                    for _ in range(e):
                        coef=[rng.choice((-1,0,1,1)) for i in range(k)]
                        rows.append([sum(coef[i]*E[i][c] for i in range(k)) for c in range(24)])
                    if rank(rows)==e and nondeg(rows): found=[integerize([Q(x) for x in r]) for r in rows]; break
        if found is not None: out[e]=found
    return out
