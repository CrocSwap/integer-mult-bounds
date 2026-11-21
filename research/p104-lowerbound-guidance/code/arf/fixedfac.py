"""ARF fixedfac.py: fixed-Q mod-4 factorization Q = L L^T + 2 Pi^T Pi (mod 4) [checked]; E2 = Pi^T Pi.
For a decoder: U^full = sum_k a_k o R1, V^full; on (U^full)^perp x (V^full)^perp, x.y = x^T M y, M = sum_k D_ak E2 D_bk [P]."""
import sys,os,itertools,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); FARGS=sys.argv[1:]; sys.argv=sys.argv[:1]
sys.path.insert(0,HERE); from stats import *
from e8xy_lib import nullsp
pairs=list(itertools.combinations(range(9),2))
Pi=np.array([[L[t,i]*L[t,j] for (i,j) in pairs] for t in range(n)]).T
E2=(Pi.T@Pi)%2
assert (((L@L.T)+2*(Pi.T@Pi)-Q)%4==0).all(); print('[C] Q == L L^T + 2 Pi^T Pi mod 4: OK; rank E2',rk(E2))
def go(W,V,tag):
    W=W%4;V=V%4;a=W%2;b=V%2
    Uf=f2basis([toint(a[:,k]*L[:,i]) for k in range(W.shape[1]) for i in range(9)])
    Vf=f2basis([toint(b[:,k]*L[:,i]) for k in range(W.shape[1]) for i in range(9)])
    RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q)
    U=f2basis([x for t in range(n) for x in RA[t]]); Vv=f2basis([x for t in range(n) for x in RB[t]])
    Xs=nullsp(mat(Uf),range(n),n); Ys=nullsp(mat(Vf),range(n),n)
    M=sum((a[:,k][:,None]*E2*b[:,k][None,:]) for k in range(W.shape[1]))%2
    I=np.eye(n,dtype=int)
    print(tag,'dimU',len(U),'dimUfull',len(Uf),'dimV',len(Vv),'dimVfull',len(Vf),
      'rank x.y on Uf^perp x Vf^perp',rk(Xs@Ys.T),'identity (I+M) vanishes',not ((Xs@(I+M)@Ys.T)%2).any(),
      'rank E2 there',rk(Xs@E2@Ys.T))
go(np.load('../orbitlp/e8W.npy'),np.load('../orbitlp/e8V.npy'),'E8')
for p in FARGS: go(np.load(p.replace('XX','W')+'.npy'),np.load(p.replace('XX','V')+'.npy'),os.path.basename(p))
