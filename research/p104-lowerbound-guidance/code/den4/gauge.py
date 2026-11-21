"""DEN4 gauge.py (own code): forced bounds are not gauge invariant. Gauges (mod 2^(e+1)): row units lam_k, port units mu_t:
w_k(t) -> lam_k mu_t w_k(t), v_k(t) -> lam_k^-1 mu_t^-1 v_k(t). Decoder unchanged (M o Q = I kept). Hill-climb the forced bounds."""
import numpy as np, sys
from qlib import *; from carrypoly import analyse; from quarter import quarter
def apply(e,W,V,lam,mu):
    M=2**(e+1); inv=lambda x: pow(int(x),-1,M)
    W2=(W*lam[None,:]*mu[:,None])%M
    V2=(V*np.array([inv(x) for x in lam])[None,:]*np.array([inv(x) for x in mu])[:,None])%M
    return W2,V2
def score(e,W,V,pr,Q,key):
    if key=='toeplitz': return analyse(e,W,V,pr,Q,verbose=False)['toeplitz']
    return quarter(e,W,V,pr,Q,verbose=False)['master']
def climb(e,W,V,pr,Q,key,iters,seed):
    rng=np.random.default_rng(seed); n,m=W.shape; M=2**(e+1); units=list(range(1,M,2))
    lam=np.ones(m,dtype=np.int64); mu=np.ones(n,dtype=np.int64)
    if seed>0: lam=rng.choice(units,m); mu=rng.choice(units,n)
    best=score(e,*apply(e,W,V,lam,mu),pr,Q,key); start=best
    for it in range(iters):
        arr=lam if rng.random()<.25 else mu; i=rng.integers(len(arr)); old=arr[i]; arr[i]=rng.choice(units)
        s=score(e,*apply(e,W,V,lam,mu),pr,Q,key)
        if s>=best: best=s
        else: arr[i]=old
    return start,best
if __name__=='__main__':
    L=std_set('HS64'); Q=Q_std(L)
    U=[[0]*8 for _ in range(8)]
    for t,i in enumerate(range(0,8,2)):
        for s,sg in enumerate((1,-1)):
            U[2*t+s][i]=2; U[2*t+s][i+1]=2*sg
    rows=gram_rows_std(L,U); e,W,V,pr,D,S=normalise(rows,Q)
    it=int(sys.argv[1])
    for key in ('toeplitz','master'):
        for seed in range(3):
            print(key,'seed',seed,'start,best',climb(e,W,V,pr,Q,key,it,seed),'C',sum(pr),flush=True)
