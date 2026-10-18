# unit-generic exact helpers (UNIT env: P112 | P104 | E8); A2 triangle selection (A2TRI / A2SEED env), A2-family realisations and an exact decoder evaluator.
# (merged from the working cards A2COST/a2lib.py and HUNT-A2/a2lib.py)
import os,sys
from setup9 import *          # load, E8, setup, colspace_vectors, B0rows, blk ...
from fractions import Fraction as Fr
UNIT=os.environ.get('UNIT','P112')
if UNIT=='E8':
    L=list(E8); v=len(L)
    basis=colspace_vectors(B0rows(L),v); h=len(basis)
    cls={}
    for co in range(1,1<<h):
        w=0
        for i in range(h):
            if co>>i&1: w^=basis[i]
        cls[co]=w
else:
    L,v,G,frames,nbar,h,basis,cls=load(UNIT)
Brows=B0rows(L)
def nullspace(rows,n):
    A=[list(map(Fr,r)) for r in rows]; piv=[]; r=0
    for c in range(n):
        p=next((i for i in range(r,len(A)) if A[i][c]!=0),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]; pv=A[r][c]; A[r]=[x/pv for x in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]!=0:
                f=A[i][c]; A[i]=[a-f*b for a,b in zip(A[i],A[r])]
        piv.append(c); r+=1
        if r==len(A): break
    free=[c for c in range(n) if c not in piv]; out=[]
    for f in free:
        x=[Fr(0)]*n; x[f]=Fr(1)
        for i,c in enumerate(piv): x[c]=-A[i][f]
        out.append(x)
    return out
def rank(rows,n): return n-len(nullspace(rows,n))
def bits(m): return [i for i in range(v) if m>>i&1]
R=[[Fr(x) for x in r] for r in L]
dot=lambda x,y: sum(a*b for a,b in zip(x,y))
def find_a2_first():
    for i in range(v):
        for j in range(i+1,v):
            g=dot(R[i],R[j])
            if g==0: continue
            s=1 if g>0 else -1
            w=[a-s*b for a,b in zip(R[i],R[j])]
            for k in range(v):
                if k in(i,j): continue
                if w==R[k] or w==[-x for x in R[k]]: return [i,j,k]

def all_a2():
    out=set()
    for i in range(v):
        for j in range(i+1,v):
            g=dot(R[i],R[j])
            if g==0: continue
            s=1 if g>0 else -1
            w=[a-s*b for a,b in zip(R[i],R[j])]
            for k in range(v):
                if k in(i,j): continue
                if w==R[k] or w==[-x for x in R[k]]: out.add(tuple(sorted((i,j,k))))
    return sorted(out)
def find_a2():
    if os.environ.get('A2TRI'): return list(map(int,os.environ['A2TRI'].split(',')))
    sd=os.environ.get('A2SEED')
    if not sd: return find_a2_first()
    import random
    T=all_a2(); t=random.Random(int(sd)).choice(T); return list(t)

# ---- A2-family realisations and decoder evaluation (HUNT-A2) ----
Gm=[[dot(R[i],R[j]) for j in range(v)] for i in range(v)]
X=tuple(find_a2())
r1,r2,r3=R[X[0]],R[X[1]],R[X[2]]
O=[[s for s in range(v) if Gm[X[i]][s]==0] for i in range(3)]
def gvecs(th):
    al2,be2,al3,be3=th
    return [[Fr(0)]*8,[al2*a+be2*b for a,b in zip(r1,r2)],[al3*a+be3*b for a,b in zip(r1,r2)]]
def build(th,zX):
    g=gvecs(th); z=[None]*v
    for s in range(v):
        vals=set(-dot(g[i],R[s]) for i in range(3) if Gm[X[i]][s]==0)
        assert len(vals)<=1
        z[s]=vals.pop() if vals else None
    for i in range(3): z[X[i]]=Fr(zX[i])
    assert all(x is not None for x in z)
    A=[R[s]+[Fr(0)] for s in range(v)]
    for i in range(3): A[X[i]]=[a+b for a,b in zip(R[X[i]],g[i])]+[Fr(1)]
    B=[R[s]+[z[s]] for s in range(v)]
    return A,B
def Mof(A,B): return [[dot(A[i],B[j]) for j in range(v)] for i in range(v)]
def pattern_ok(M):
    return sum(1 for i in range(v) for j in range(v) if (M[i][j]==0)!=(Gm[i][j]==0 and i!=j))
def inv(Mx):
    n=len(Mx); A=[list(map(Fr,r))+[Fr(int(i==j)) for j in range(n)] for i,r in enumerate(Mx)]
    for c in range(n):
        p=next((i for i in range(c,n) if A[i][c]!=0),None)
        if p is None: return None
        A[c],A[p]=A[p],A[c]; pv=A[c][c]; A[c]=[x/pv for x in A[c]]
        for i in range(n):
            if i!=c and A[i][c]!=0:
                f=A[i][c]; A[i]=[a-f*b for a,b in zip(A[i],A[c])]
    return [r[n:] for r in A]
def evaluate(A,B,xs,check=True):
    """xs: 9 row normals (list of 9-vectors). Returns (cost, per-term costs, supports). Exactness checked exactly."""
    Xm=[[xs[j][k] for j in range(9)] for k in range(9)]   # columns = x_j
    Xi=inv(Xm)
    if Xi is None: return None
    # Y = X^{-T}: y_j = column j of X^{-T} = row j of X^{-1}
    ys=[Xi[j] for j in range(9)]
    P=[[dot(A[u],xs[j]) for j in range(9)] for u in range(v)]
    Q=[[dot(B[s],ys[j]) for j in range(9)] for s in range(v)]
    if check:
        M=Mof(A,B)
        for u in range(v):
            for s in range(v):
                assert sum(P[u][j]*Q[s][j] for j in range(9))==M[u][s]
    costs=[]; sup=[]
    for j in range(9):
        Rj=[u for u in range(v) if P[u][j]!=0]; Aj=[s for s in range(v) if Q[s][j]!=0]
        costs.append(blk(Brows,Rj,Aj) if Rj and Aj else 0); sup.append((Rj,Aj))
    return sum(costs),costs,sup,ys
def catalogue(A,B):
    out={}
    for co,w in cls.items():
        Os=bits(w)
        nr=nullspace([A[t] for t in Os],9); nc=nullspace([B[t] for t in Os],9)
        if nr or nc: out[co]=(len(Os),nr,nc)
    return out
