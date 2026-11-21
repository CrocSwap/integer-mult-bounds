"""HALVPAY ebound.py (own code). Exact Z/4 potential bounds E_lam, E_psi = pot(S0+T) - pot(S0) - public climbs for a set of
public registers given by (start chart, start value, final chart, final value); values in (1/2)Z^W.
lam = Z/4 length; psi = lam - lam(2S) = dim S[2]; lam(2S) = rank_F2(generators mod 2).  Selftest vs brute force included."""
import numpy as np, itertools, random, sys
from fractions import Fraction as Fr
def z4len(A):
    A=(np.array(A,dtype=np.int64)%4).astype(np.int64)
    if A.size==0: return 0
    L=0
    while True:
        A=A[(A!=0).any(1)]
        if A.shape[0]==0: return L
        odd=np.argwhere(A%2==1)
        if len(odd)==0: break
        i,j=odd[0]; r=A[i].copy(); r=(r*(1 if r[j]==1 else 3))%4
        A=np.delete(A,i,0); A=(A-np.outer(A[:,j],r))%4; L+=2
    return L+f2rank(A//2)
def f2rank(B):
    B=(np.array(B)%2).astype(np.uint8)
    if B.size==0: return 0
    B=np.packbits(B,axis=1); rows=[int.from_bytes(r.tobytes(),'big') for r in B]
    piv={}; rk=0
    for v in rows:
        while v:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; rk+=1; break
    return rk
def gens(C,w,n,cols):
    """generators of C^ (x) [w]; C = list of basis ints of an F2-subspace of F2^n; w = dict sym->Fraction; cols = sym->index"""
    W=len(cols); c=np.zeros(W,dtype=np.int64)
    for s,v in w.items():
        y=2*Fr(v); assert y.denominator==1; c[cols[s]]=int(y)%4
    if not c.any(): return []
    out=[]
    for b in C:
        g=np.zeros((n,W),dtype=np.int64)
        for i in range(n):
            if (b>>i)&1: g[i]=c
        out.append(g.reshape(-1)%4)
    for i in range(n):
        g=np.zeros((n,W),dtype=np.int64); g[i]=2*c; out.append(g.reshape(-1)%4)
    return out
def basis(S):
    rows=[]
    for v in sorted(S):
        for r in rows: v=min(v,v^r)
        if v: rows.append(v)
    return rows
def pots(G):
    if not G: return 0,0
    lam=z4len(G); return lam, lam-f2rank(np.array(G)%2)
def ebound(pubs,n,cols):
    S0=[g for (C0,w0,C1,w1) in pubs for g in gens(basis(C0),w0,n,cols)]
    T=[g for (C0,w0,C1,w1) in pubs for g in gens(basis(C1),w1,n,cols)]
    climb=sum((len(C1).bit_length()-1)-(len(C0).bit_length()-1) for (C0,w0,C1,w1) in pubs)
    l0,p0=pots(S0); l1,p1=pots(S0+T)
    return dict(lam0=l0,lam1=l1,psi0=p0,psi1=p1,climb=climb,E_lam=l1-l0-climb,E_psi=p1-p0-climb)
def selftest(nt=300):
    rng=random.Random(7); bad=0
    for _ in range(nt):
        N=rng.randint(1,4); m=rng.randint(1,4); rows=[[rng.choice([0,0,1,2,3]) for _ in range(N)] for _ in range(m)]
        sp={tuple([0]*N)}
        while True:
            new=set(sp)|{tuple((a+b)%4 for a,b in zip(s,r)) for s in sp for r in rows}
            if new==sp: break
            sp=new
        L=len(sp).bit_length()-1
        tors=sum(1 for s in sp if all((2*a)%4==0 for a in s)); psi=tors.bit_length()-1
        l,p=pots([np.array(r) for r in rows])
        bad+=(l!=L)+(p!=psi)
    return bad
if __name__=='__main__': print('selftest mismatches (lam,psi) of 300:',selftest())
