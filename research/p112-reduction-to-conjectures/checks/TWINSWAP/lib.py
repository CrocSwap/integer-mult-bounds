# TWINSWAP common: P112 data, exact decoder builder/checker. python = W/venv/bin/python
import json, os
from fractions import Fraction as Fr
_D=json.load(open(os.path.join(os.path.dirname(__file__),'../OS-CHARGE2/data.json')))
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
