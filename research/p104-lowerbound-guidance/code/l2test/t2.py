# numeric minrank over R: find W,U in R^{n x r}: W_p.U_p=1, W_p.U_q=0 (Q_pq=1 odd). LM from random starts.
from base import *
import pickle, sys, time
from scipy.optimize import least_squares
def fit(X,r,tries=6,seed=0):
    n=len(X); q=Q[np.ix_(X,X)].copy()
    off=[(i,j) for i in range(n) for j in range(n) if q[i,j] and i!=j]
    I=np.array([a for a,b in off]); J=np.array([b for a,b in off])
    rng=np.random.default_rng(seed); best=1e9
    def res(x):
        W=x[:n*r].reshape(n,r); U=x[n*r:].reshape(n,r)
        return np.concatenate([(W*U).sum(1)-1,(W[I]*U[J]).sum(1)])
    def jac(x):
        W=x[:n*r].reshape(n,r); U=x[n*r:].reshape(n,r)
        m=n+len(I); Jm=np.zeros((m,2*n*r))
        for i in range(n):
            Jm[i,i*r:(i+1)*r]=U[i]; Jm[i,n*r+i*r:n*r+(i+1)*r]=W[i]
        for k,(a,b) in enumerate(zip(I,J)):
            Jm[n+k,a*r:(a+1)*r]=U[b]; Jm[n+k,n*r+b*r:n*r+(b+1)*r]=W[a]
        return Jm
    for t in range(tries):
        x0=rng.normal(size=2*n*r)*0.7
        s=least_squares(res,x0,jac=jac,method='lm',max_nfev=400)
        best=min(best,np.abs(s.fun).max())
        if best<1e-9: return best,s.x
    return best,None
if __name__=='__main__':
    nn=int(sys.argv[1])
    rows=pickle.load(open('t1_%d.pkl'%nn,'rb')); S=sections(nn); out={}
    for u,sz,w,r8 in rows:
        if w<r8:
            X=S[u]; t0=time.time(); found=None
            for r in range(w,r8+1):
                b,x=fit(X,r)
                if x is not None: found=r; break
            out[u]=(sz,w,r8,found,round(b,4)); print(u,sz,w,r8,'min numeric rank found',found,'resid',round(b,4),'%.0fs'%(time.time()-t0),flush=True)
    pickle.dump(out,open('t2_%d.pkl'%nn,'wb'))
