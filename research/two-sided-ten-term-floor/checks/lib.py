# TWINSWAP common: P112 data, exact decoder builder/checker. python = W/venv/bin/python
import json, os
from fractions import Fraction as Fr
_D=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'data.json')))
Lr=[[int(round(x*1)) if abs(x-round(x))<1e-9 else x for x in r] for r in _D['L']]
n=len(Lr)
C=[[int(x) for x in row] for row in _D['FC']]          # F0 coords c_t (entries 0,±1, four nonzero)
def dotL(a,b): return sum(x*y for x,y in zip(a,b))
G=[[dotL(Lr[t],Lr[s]) for s in range(n)] for t in range(n)]
Bd=[[1 if (t==s or abs(G[t][s])<1e-9) else 0 for s in range(n)] for t in range(n)]
LAB=_D['LAB']; ZF=_D['Z']
assert all(sum(C[t][i]*C[s][i] for i in range(8))==2*G[t][s] for t in range(n) for s in range(n))
# N0 = G/2 = C' C'^T with C' = C/2
def N0(t,s): return Fr(G[t][s])/2 if True else None
def f2rank(vs):
    basis=[]
    for v in vs:
        for b in basis: v=min(v,v^b)
        if v: basis.append(v)
    return len(basis)
def bdrank(R,A):
    # rank over F2 of Bd[R,A]
    rows=[]
    for t in R:
        x=0
        for j,s in enumerate(A):
            if Bd[t][s]: x|=1<<j
        rows.append(x)
    return f2rank(rows)
def Cvec(x):   # C' x as length-n vector (Fractions)
    return [sum(Fr(C[t][i],2)*x[i] for i in range(8) if x[i]) for t in range(n)]
def build(Xh,Yh,E,F):
    """Xh,Yh: lists of (x in K^8, x2 in K^s) / (y, y2 in K^t); E: list of s outside vectors, F: t outside vectors."""
    P=[];Q=[]
    for (x,x2) in Xh:
        p=Cvec(x)
        for a,c in enumerate(x2):
            if c: p=[p[t]+c*E[a][t] for t in range(n)]
        P.append(p)
    for (y,y2) in Yh:
        q=Cvec(y)
        for a,c in enumerate(y2):
            if c: q=[q[t]+c*F[a][t] for t in range(n)]
        Q.append(q)
    return P,Q
def check(P,Q,masked=True):
    bad=0
    for t in range(n):
        for s in range(n):
            if masked and not Bd[t][s]: continue
            v=sum(P[k][t]*Q[k][s] for k in range(len(P)) if P[k][t] and Q[k][s])
            if v!=N0(t,s): bad+=1
    return bad
def costs(P,Q):
    out=[]
    for p,q in zip(P,Q):
        R=[t for t in range(n) if p[t]!=0]; A=[t for t in range(n) if q[t]!=0]
        out.append(bdrank(R,A) if R and A else 0)
    return out
def delta(t):
    v=[Fr(0)]*n; v[t]=Fr(1); return v
def e(i): v=[Fr(0)]*8; v[i]=Fr(1); return v
def croot(t): return [Fr(x) for x in C[t]]
def supp8(t): return {i for i in range(8) if C[t][i]}


def bounded_integer_rank(rows):
    """Exact rational rank for <=8 columns with entries in {-1,0,1}.

    Every k-by-k minor has |det| <= k**(k/2) <= 4096 by Hadamard.
    Reduction modulo the prime 65537 therefore preserves every zero/nonzero
    minor, hence the rank over Q. Int64 elimination products stay below 2**33.
    Input guards are mandatory: this is not a general modular rank oracle.
    """
    import numpy as np
    raw = np.asarray(rows)
    if raw.size == 0:
        return 0
    if raw.ndim != 2 or not 1 <= raw.shape[1] <= 8:
        raise ValueError('bounded integer rank: shape outside proved domain')
    if not np.all((raw == -1) | (raw == 0) | (raw == 1)):
        raise ValueError('bounded integer rank: entries outside proved domain')
    prime = 65537
    a = raw.astype(np.int64, copy=True) % prime
    rank = 0
    for column in range(a.shape[1]):
        candidates = np.flatnonzero(a[rank:, column])
        if not len(candidates):
            continue
        pivot = rank + int(candidates[0])
        a[[rank, pivot]] = a[[pivot, rank]]
        a[rank] = a[rank] * pow(int(a[rank, column]), prime-2, prime) % prime
        if rank+1 < len(a):
            a[rank+1:] = (a[rank+1:] - a[rank+1:, column, None] * a[rank]) % prime
        rank += 1
        if rank == len(a):
            break
    return rank
