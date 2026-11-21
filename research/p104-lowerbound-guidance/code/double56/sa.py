"""DOUBLE56 sa.py: random/SA search for mod-4 decoders with small rho_A+rho_B on a small port set Q.
State: free rows (w,v) in Z4^n; completion: for each port t a row (e_t, residual_t) [mode 'row'] so the decoder is always valid."""
import sys,numpy as np, itertools
from rho import *
def complete(Ws,Vs,Q):
    n=Q.shape[0]
    T=((2*np.eye(n,dtype=np.int64)-Ws@Vs.T)%4)*Q
    rows=[t for t in range(n) if T[t].any()]
    Wc=np.zeros((n,len(rows)),np.int64); Vc=np.zeros((n,len(rows)),np.int64)
    for j,t in enumerate(rows): Wc[t,j]=1; Vc[:,j]=T[t]
    W=np.concatenate([Ws,Wc],1); V=np.concatenate([Vs,Vc],1)
    assert check_decoder(W,V,Q)
    return W,V
def score(Ws,Vs,Q):
    W,V=complete(Ws,Vs,Q); n=Q.shape[0]
    return trank(spaces_B(W,V,Q),n,2)+trank(spaces_A(W,V,Q),n,2), cost(W,V,Q)
def sa(Q,steps,seed,m0=4,T0=1.0):
    n=Q.shape[0]; rng=np.random.default_rng(seed)
    Ws=rng.integers(0,4,(n,m0)); Vs=rng.integers(0,4,(n,m0))
    cur,_=score(Ws,Vs,Q); best=(cur,Ws,Vs); T=T0
    for it in range(steps):
        W2=Ws.copy(); V2=Vs.copy(); r=rng.random(); m=W2.shape[1]
        if r<0.1 and m<3*n: W2=np.concatenate([W2,rng.integers(0,4,(n,1))],1); V2=np.concatenate([V2,rng.integers(0,4,(n,1))],1)
        elif r<0.2 and m>1:
            k=int(rng.integers(m)); W2=np.delete(W2,k,1); V2=np.delete(V2,k,1)
        else:
            k=int(rng.integers(m)); t=int(rng.integers(n))
            if rng.random()<0.5: W2[t,k]=rng.integers(0,4)
            else: V2[t,k]=rng.integers(0,4)
        s,_=score(W2,V2,Q)
        if s<=cur or rng.random()<np.exp((cur-s)/T):
            Ws,Vs,cur=W2,V2,s
            if s<best[0]: best=(s,Ws.copy(),Vs.copy())
        T=max(0.02,T*0.998)
    return best
def symp_ports(k,plus=True,subset=None):
    # quadratic form on F2^{2k}: sum x_{2i}x_{2i+1} (+ x0^2+x1^2 for minus); B standard symplectic
    pts=[]
    for x in range(1,1<<(2*k)):
        b=[(x>>i)&1 for i in range(2*k)]
        q=sum(b[2*i]*b[2*i+1] for i in range(k))+( (b[0]+b[1]) if not plus else 0)
        if q%2==1: pts.append(b)
    def B(p,r): return sum(p[2*i]*r[2*i+1]+p[2*i+1]*r[2*i] for i in range(k))%2
    if subset is not None: pts=[pts[i] for i in subset]
    n=len(pts); Q=np.array([[1-B(p,r) for r in pts] for p in pts],dtype=np.int64)
    return Q
if __name__=='__main__':
    name=sys.argv[1]; steps=int(sys.argv[2]); seeds=int(sys.argv[3])
    if name=='star': Q=np.array([[1,0,0,1],[0,1,0,1],[0,0,1,1],[1,1,1,1]],dtype=np.int64)
    elif name.startswith('J'): Q=np.ones((int(name[1:]),)*2,dtype=np.int64)
    elif name=='plus4': Q=symp_ports(2,True)
    elif name=='minus4': Q=symp_ports(2,False)
    elif name=='plus6': Q=symp_ports(3,True)
    elif name=='minus6': Q=symp_ports(3,False)
    elif name=='minus4b': Q=symp_ports(2,False)
    print(name,'n',Q.shape[0],'odd offdiag pairs',(Q.sum()-Q.shape[0])//2)
    for sd in range(seeds):
        b=sa(Q,steps,sd)
        W,V=complete(b[1],b[2],Q); print('seed',sd,'best rho sum',b[0],'C of it',cost(W,V,Q),flush=True)
