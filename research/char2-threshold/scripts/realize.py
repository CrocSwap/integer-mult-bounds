import numpy as np,itertools,sys
def lm(zero_pairs,v,T,seed=0,iters=300,verbose=False):
    rng=np.random.RandomState(seed)
    X=rng.randn(2*v*T)*0.7   # [p;q]
    zp=np.array(zero_pairs);nz=len(zp)
    def resid(X):
        P=X[:v*T].reshape(v,T);Q=X[v*T:].reshape(v,T)
        r1=np.einsum('ij,ij->i',P[zp[:,0]],Q[zp[:,1]])
        r2=np.einsum('ij,ij->i',P,Q)-1.0
        return np.concatenate([r1,r2])
    def jac(X):
        P=X[:v*T].reshape(v,T);Q=X[v*T:].reshape(v,T)
        J=np.zeros((nz+v,2*v*T))
        for k,(t,s) in enumerate(zp):
            J[k,t*T:(t+1)*T]=Q[s];J[k,v*T+s*T:v*T+(s+1)*T]=P[t]
        for t in range(v):
            J[nz+t,t*T:(t+1)*T]=Q[t];J[nz+t,v*T+t*T:v*T+(t+1)*T]=P[t]
        return J
    lam=1.0;r=resid(X);f=r@r
    for it in range(iters):
        J=jac(X);g=J.T@r;A=J.T@J
        while True:
            try: dx=np.linalg.solve(A+lam*np.eye(len(X)),-g)
            except np.linalg.LinAlgError: lam*=10;continue
            r2=resid(X+dx);f2=r2@r2
            if f2<f: X=X+dx;r=r2;f=f2;lam=max(lam/3,1e-12);break
            lam*=4
            if lam>1e12: return f,X
        if f<1e-22: break
    return f,X
def sp_points(m):
    k=2*m;pts=[tuple(x) for x in itertools.product((0,1),repeat=k) if any(x)]
    def om(a,b): return sum(a[i]*b[i+m]+a[i+m]*b[i] for i in range(m))%2
    return pts,om
def zero_pairs_of(pts,om):
    v=len(pts);return [(t,s) for t in range(v) for s in range(v) if t!=s and om(pts[t],pts[s])==0]
if __name__=='__main__':
    m=int(sys.argv[1]);T=int(sys.argv[2]);seeds=int(sys.argv[3])
    pts,om=sp_points(m);zp=zero_pairs_of(pts,om);v=len(pts)
    for sd in range(seeds):
        f,X=lm(zp,v,T,sd,iters=200)
        print('Sp',2*m,'v',v,'T',T,'seed',sd,'resid^2',f,flush=True)
