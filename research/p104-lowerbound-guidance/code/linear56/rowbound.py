"""LINEAR56 rowbound.py: [C] checks for the per-row price bound of linear rows.
(1) Q[t,s] = beta(h_t,h_s), h_t=(1,cbar_t) in F2^9, beta = 1 (+) B nondegenerate.
(2) for every nonzero affine function a = eps + <x,c> on F2^8 (x != 0, eps in F2) the homogenised span of
    {t in P104 : a(c_t)=1} is the 8-dim hyperplane {(e,c): <x,c> = (1+eps) e}; and for a == 1 it is F2^9.
(3) min over linear rows (x,y != 0) of rank Q[{a=1},{b=1}] (exact, all 255^2 pairs)."""
import numpy as np, itertools
from lcore import *
def f2rank(M):
    M=(np.array(M)%2).astype(np.uint8); r=0
    for c in range(M.shape[1]):
        p=np.nonzero(M[r:,c])[0]
        if len(p)==0: continue
        p=p[0]+r; M[[r,p]]=M[[p,r]]
        nz=np.nonzero(M[:,c])[0]; nz=nz[nz!=r]; M[nz]^=M[r]
        r+=1
        if r==M.shape[0]: break
    return r
n=104; Xb=X120[:n]; H=np.concatenate([np.ones((n,1),np.int64),Xb],1)
beta=np.zeros((9,9),np.int64); beta[0,0]=1; beta[1:,1:]=Bm
assert ((H@beta@H.T)%2==Q).all(); print('(1) Q = H beta H^T ok; det beta mod2 rank',f2rank(beta))
NZ=[np.array(v) for v in itertools.product([0,1],repeat=8) if any(v)]
bad=0
for x in NZ:
    for eps in (0,1):
        sel=((Xb@x+eps)%2==1)
        if f2rank(H[sel])!=8: bad+=1
print('(2) affine sections not spanning a hyperplane:',bad,'of',2*255, '| a==1 spans', f2rank(H))
# (3) exact min rank over linear (eps=0) rows, and affine rows
mn=99; mnA=99
secs={}
for x in NZ:
    for eps in (0,1): secs[(tuple(x),eps)]=H[((Xb@x+eps)%2==1)]
for kx,Hx in secs.items():
    for ky,Hy in secs.items():
        r=f2rank(Hx@beta@Hy.T)
        mnA=min(mnA,r)
        if kx[1]==0 and ky[1]==0: mn=min(mn,r)
print('(3) min price linear rows',mn,' min price affine rows',mnA)
