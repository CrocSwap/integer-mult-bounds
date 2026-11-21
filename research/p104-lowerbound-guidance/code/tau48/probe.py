"""TAU48 probe.py: how Xs, Ys sit relative to canonical codes R(d), R(d)^perp."""
import sys,numpy as np
from gibbs import *
from canon import basis, R, perp
from e8xy_lib import nullsp
def dim(A): return f2rank([toint(r) for r in A%2]) if len(A) else 0
def inter_basis(A,B):
    # basis of A ∩ B (rows)
    if len(A)==0 or len(B)==0: return np.zeros((0,n),int)
    Bp=perp(basis(B)); # x in A with x ⊥ Bp
    coeff=nullsp((A@Bp.T%2).T if len(Bp) else np.zeros((0,len(A)),int),range(len(A)),len(A))
    return (coeff@A)%2 if len(coeff) else np.zeros((0,n),int)
codes={}
for d in (1,2,3):
    B=basis(R[d]); codes['R%d'%d]=B; codes['R%dp'%d]=perp(B)
def go(W,V,tag):
    W=W%4;V=V%4;RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q); Xs,Ys,_,_=xy_spaces(RB,RA,n)
    out=[tag,'tau',rk(Xs@Ys.T),'dims',len(Xs),len(Ys)]
    for name,B in codes.items():
        Xi=inter_basis(Xs,B); out+=[name,'dimX∩',len(Xi),'rk(X∩,Ys)',rk(Xi@Ys.T) if len(Xi) else 0]
    print(*out,flush=True)
go(np.load('../orbitlp/e8W.npy'),np.load('../orbitlp/e8V.npy'),'E8')
for f in sys.argv[1:]: go(np.load('g_W_%s.npy'%f),np.load('g_V_%s.npy'%f),f)
