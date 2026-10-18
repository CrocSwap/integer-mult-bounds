import os as _os; ROOT=_os.path.abspath(_os.path.join(_os.path.dirname(__file__),'..','..'))
# B214 Q1c: support of I-K = {t odd}; B=(t mod 2) is alternating of F2-rank 16 => port labels l_v in F2^16, B=l M l^T.
import sys;sys.dont_write_bytecode=True
import numpy as np
from collections import Counter
P=np.load('b214_P.npy'); N=len(P)
tm=lambda I,J:(P[I]@P[J].T)//4
# find 16 ports R with B[R,R] invertible over F2 (greedy)
def f2inv(A):
    n=len(A);W=np.concatenate([A%2,np.eye(n,dtype=np.int64)],1)
    for c in range(n):
        p=[r for r in range(c,n) if W[r,c]]
        if not p: return None
        W[[c,p[0]]]=W[[p[0],c]]
        for r in range(n):
            if r!=c and W[r,c]: W[r]^=W[c]
    return W[:,n:]
rng=np.random.default_rng(3); R=None
for trial in range(2000):
    cand=rng.choice(N,16,replace=False); A=tm(cand,cand)&1
    M=f2inv(A)
    if M is not None: R=cand;break
print('invertible 16x16 principal minor found at trial',trial)
L=np.concatenate([(tm(np.arange(s,min(s+3000,N)),R)&1) for s in range(0,N,3000)],0)  # N x 16
chk=rng.choice(N,3000,replace=False)
Bc=(tm(chk,chk)&1); Bp=(L[chk]@M@L[chk].T)%2
print('B == l M l^T on 3000x3000 sample:',np.array_equal(Bc,Bp))
lab=L@(1<<np.arange(16)); cnt=Counter(lab.tolist())
print('distinct labels',len(cnt),'of 65536; max multiplicity',max(cnt.values()),' multiplicity histogram',sorted(Counter(cnt.values()).items()))
# exact decomposition of off-diagonal I-K
ii=rng.choice(N,800,replace=False);jj=rng.choice(N,800,replace=False)
t=tm(ii,jj);K=(t**3-4.0*t)/48;Bm=(t&1);mask=ii[:,None]!=jj[None,:]
IK=-K*Bm
form=(t/16.0)*Bm-(np.abs(t)==3)*np.sign(t)*0.5
print('I-K == (T o B)/16 - (1/2)sgn(t)[|t|=3]  max err',np.abs((IK-form)*mask).max())
print('T o B = sum_c D_c B D_c over 16 coordinate columns c (T=X X^T, X=P/2): 16 diag-twisted copies of B=(J-W)/2, W=(-1)^{l M l} Walsh submatrix')
# the |t|=3 correction E: count and Kronecker form
cnt3=0
for s in range(0,N,2000):
    cnt3+=int((np.abs(tm(np.arange(s,min(s+2000,N)),np.arange(N)))==3).sum())
print('|t|=3 ordered pairs',cnt3,' = %.3f%% of nnz'%(100*cnt3/480337920))
