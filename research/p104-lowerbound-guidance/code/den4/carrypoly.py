"""DEN4 carrypoly.py (own code): CARRY-POLYNOMIAL bound. Digits a_i (of w mod 2^(e+1)), b_j; P_l = sum_{i+j=l} G[a_i,b_j] (F2).
Forced: P_l = K_l (l<e), I+K_e (l=e), K_l = carry into level l. Bound: C >= rank T_{e+1} - rank T_e (Toeplitz), and C >= rank_F2(x) P(x)."""
import numpy as np
from qlib import *
from gf import polyrank
def G(x,y,Q): return ((x@y.T)*Q)%2
def toeplitz(Ps,s):
    n=Ps[0].shape[0]; Z=np.zeros((n,n),dtype=np.int64)
    return np.block([[Ps[j-i] if j>=i else Z for j in range(s)] for i in range(s)])
def analyse(e,W,V,pr,Q,name='',verbose=True):
    n=len(Q); I=np.eye(n,dtype=np.int64); m=e+1; M=2**m
    Wr=W%M; Vr=V%M
    A=[(Wr>>i)&1 for i in range(m)]; B=[(Vr>>j)&1 for j in range(m)]
    Ps=[]
    for l in range(2*m-1):
        P=np.zeros((n,n),dtype=np.int64)
        for i in range(m):
            j=l-i
            if 0<=j<m: P=(P+G(A[i],B[j],Q))%2
        Ps.append(P)
    # carries: K_l = floor(sum_{i+j<l} 2^{i+j} Ghat_ij / 2^l) mod 2 ; check P_l = K_l + [l=e] I for l<=e
    Sacc=np.zeros((n,n),dtype=object)
    for l in range(e+1):
        K=((Sacc//(2**l))%2).astype(np.int64)
        assert (((Ps[l]+K+(I if l==e else 0))%2)*Q==0).all(), ('carry identity fails at level',l)
        for i in range(m):
            j=l-i
            if 0<=j<m: Sacc=Sacc+(2**l)*((A[i]@B[j].T)*Q).astype(object)
    Cst=sum(pr)
    tb=rk2(toeplitz(Ps,e+1))-rk2(toeplitz(Ps,e))
    pz=polyrank(Ps,trials=2)
    assert Cst>=tb and Cst>=pz, (Cst,tb,pz)
    res=dict(name=name,n=n,e=e,C=Cst,toeplitz=tb,polyrank=pz,rkP=[rk2(P) for P in Ps[:e+1]])
    if verbose: print(res)
    return res
