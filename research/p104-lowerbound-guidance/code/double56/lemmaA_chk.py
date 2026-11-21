"""DOUBLE56 lemmaA_chk.py: check ISOTROPIC-PAIR LEMMA on P104 decoders: for Rado sets J,J' (greedy),
Xs = F2^J ∩ U_{J'}^perp, Ys = F2^{J'} ∩ V_J^perp satisfy x^T(I+X)y = 0, and rho_A+rho_B >= 104 - rank(X|XsxYs)."""
import sys,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import Q
from rho import *
from sa import complete
from e8xy_lib import xy_spaces
n=104; rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
W8=np.load('../orbitlp/e8W.npy')%4; V8=np.load('../orbitlp/e8V.npy')%4
def run(W,V,name):
    W=W%4;V=V%4; a=W%2;b=V%2; N=(a@b.T)*Q; assert not (N%2).any(); X=(N//2)%2; I=np.eye(n,dtype=np.int64)
    RB=spaces_B(W,V,Q); RA=spaces_A(W,V,Q); rb=trank(RB,n,2); ra=trank(RA,n,2)
    Xs,Ys,vb,va=xy_spaces(RB,RA,n)
    rkIX=f2rank([toint(r) for r in (Xs@((I+X)%2)@Ys.T)%2]) if len(Xs) and len(Ys) else 0
    rkX=f2rank([toint(r) for r in (Xs@X@Ys.T)%2]) if len(Xs) and len(Ys) else 0
    assert rkIX==0 and ra+rb>=n-rkX and vb>=rb and va>=ra
    print('%-10s C=%3d rhoA=%3d rhoB=%3d (Rado ub %d,%d) dimXs=%d dimYs=%d rank tau-form=%d bound=%d'%(name,cost(W,V,Q),ra,rb,va,vb,len(Xs),len(Ys),rkX,n-rkX),flush=True)
run(W8,V8,'E8-56')
for trial in range(4):
    m=int(rng.integers(1,4)); Ws=rng.integers(0,4,(n,m))*(rng.random((n,m))<0.15); Vs=rng.integers(0,4,(n,m))*(rng.random((n,m))<0.15)
    k=int(rng.integers(1,8)); keep=list(rng.choice(8,k,replace=False))
    W,V=complete(np.concatenate([W8[:,keep],Ws],1),np.concatenate([V8[:,keep],Vs],1),Q)
    run(W,V,'E8%d+%d+cmp'%(k,m))
