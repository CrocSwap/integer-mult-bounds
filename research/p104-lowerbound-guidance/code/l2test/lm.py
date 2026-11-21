import numpy as np
from base import Q
def fitlm(X,r,tries=8,seed=0,iters=300,verbose=False):
    n=len(X); q=Q[np.ix_(X,X)].copy()
    off=[(i,j) for i in range(n) for j in range(n) if q[i,j] and i!=j]
    I=np.array([a for a,b in off]); J=np.array([b for a,b in off]); m=n+len(I)
    rng=np.random.default_rng(seed); best=1e9; bestx=None
    def unpack(x): return x[:n*r].reshape(n,r), x[n*r:].reshape(n,r)
    def res(x):
        W,U=unpack(x); return np.concatenate([(W*U).sum(1)-1,(W[I]*U[J]).sum(1)])
    rowsA=np.arange(n)
    def jac(x):
        W,U=unpack(x); Jm=np.zeros((m,2*n*r))
        for k in range(r):
            Jm[rowsA,rowsA*r+k]=U[:,k]; Jm[rowsA,n*r+rowsA*r+k]=W[:,k]
            ks=np.arange(len(I))
            Jm[n+ks,I*r+k]=U[J,k]; Jm[n+ks,n*r+J*r+k]=W[I,k]
        return Jm
    for t in range(tries):
        x=rng.normal(size=2*n*r)*0.7; lam=1.0; f=res(x); c=f@f
        for it in range(iters):
            Jm=jac(x); g=Jm.T@f; H=Jm.T@Jm
            ok=False
            for _ in range(12):
                try: dx=np.linalg.solve(H+lam*np.eye(len(x)),-g)
                except Exception: lam*=10; continue
                f2=res(x+dx); c2=f2@f2
                if c2<c: x=x+dx; f=f2; c=c2; lam=max(lam/3,1e-12); ok=True; break
                lam*=4
            if not ok or c<1e-22: break
        mx=np.abs(f).max(); 
        if mx<best: best=mx; bestx=x
        if verbose: print(' try',t,'max resid',mx,'it',it)
        if best<1e-9: return best,bestx
    return best,None
