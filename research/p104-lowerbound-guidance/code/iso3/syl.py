"""ISO3 syl: Sylvester-length family.  P(x)=A(x)B(x) over F2[[x]] (A: n x C, B: C x n, block k factors through Q[D_k,S_k]).
Lemma S_l [P]: l*C >= rk T_l(A) + rk T_l(B) - rk T_l(P)  (Sylvester for lengths over F2[x]/x^l).  l=1, P0=0: C >= alpha+beta.
Also Toeplitz (DEN4): C >= rk T_{l+1}(P) - rk T_l(P).
Gauge: rows (w,u) Fractions; w'=2^(s_k+c_t) lam_k mu_t w, u'=2^(e-s_k-c_t) (lam_k mu_t)^-1 u (2-integral)."""
import numpy as np
from ilib import *
from gmax import vals, BIG
def toep(Ms,l):
    r,c=Ms[0].shape; Z=np.zeros((r,c),dtype=np.int64)
    return np.block([[Ms[j-i] if j>=i else Z for j in range(l)] for i in range(l)])
def residues(rows,n,s,c,e,lam,mu,L):
    M=2**L; m=len(rows)
    W=np.zeros((n,m),dtype=np.int64); V=np.zeros((n,m),dtype=np.int64)
    for k,(w,u) in enumerate(rows):
        for t in range(n):
            if w[t]!=0:
                x=Fr(w[t])*Fr(2)**int(s[k]+c[t])*int(lam[k])*int(mu[t]); W[t,k]=mod2k(x,L)
            if u[t]!=0:
                y=Fr(u[t])*Fr(2)**int(e-s[k]-c[t])/(int(lam[k])*int(mu[t])); V[t,k]=mod2k(y,L)
    return W,V
def bounds(rows,Q,s,c,e,lam,mu,lmax,D,S,pr):
    n=len(Q); m=len(rows); L=lmax+1
    W,V=residues(rows,n,s,c,e,lam,mu,L)
    a=[(W>>i)&1 for i in range(L)]; b=[(V>>i)&1 for i in range(L)]
    ks=[k for k in range(m) if D[k] and S[k]]
    Ai=[np.concatenate([a[i][:,[k]]*Q[:,S[k]] for k in ks],1)%2 for i in range(L)]
    Bi=[np.concatenate([Q[D[k],:]*b[i][:,k][None,:] for k in ks],0)%2 for i in range(L)]
    Pi=[]
    for l in range(L):
        P=np.zeros((n,n),dtype=np.int64)
        for i in range(l+1): P=(P+((a[i]@b[l-i].T)*Q))%2
        Pi.append(P)
    assert (Pi[0]==0).all()
    C=sum(pr); out={}
    rP=[0]+[rk2(toep(Pi,l)) for l in range(1,L+1)]
    for l in range(1,lmax+1):
        rA=rk2(toep(Ai,l)); rB=rk2(toep(Bi,l).T)
        sy=-(-(rA+rB-rP[l])//l)
        assert l*C>=rA+rB-rP[l]
        out['S%d'%l]=sy
    for l in range(1,lmax+1):
        out['T%d'%(l+1)]=rP[l+1]-rP[l]
        assert C>=out['T%d'%(l+1)]
    return out
def setup(rows,Q):
    n=len(Q); m=len(rows); VW,VU=vals(rows,n)
    D=[[t for t in range(n) if VW[t,k]<BIG] for k in range(m)]; S=[[t for t in range(n) if VU[t,k]<BIG] for k in range(m)]
    pr=[rk2(Q[np.ix_(D[k],S[k])]) if D[k] and S[k] else 0 for k in range(m)]
    mu_=np.array([VW[:,k].min() for k in range(m)]); nu_=np.array([VU[:,k].min() for k in range(m)])
    s=-mu_; e=max(1,int(max(-(mu_+nu_))))
    return VW,VU,D,S,pr,s,np.zeros(n,dtype=np.int64),e
def legal(VW,VU,s,c,e):
    return not ((VW+s[None,:]+c[:,None]<0).any() or (VU+e-s[None,:]-c[:,None]<0).any())
def climb(rows,Q,lmax=3,iters=200,seed=0,key=None):
    n=len(Q); m=len(rows); VW,VU,D,S,pr,s,c,e=setup(rows,Q); rng=np.random.default_rng(seed)
    lam=[1]*m; mu=[1]*n
    f=lambda o: max(o.values()) if key is None else o[key]
    cur=bounds(rows,Q,s,c,e,lam,mu,lmax,D,S,pr); start=dict(cur); best=f(cur); bestall=dict(cur)
    for it in range(iters):
        s2,c2,e2,lam2,mu2=s.copy(),c.copy(),e,list(lam),list(mu); r=rng.random()
        if r<0.2: k=rng.integers(m); s2[k]+=rng.choice([-1,1])
        elif r<0.4: t=rng.integers(n); c2[t]+=rng.choice([-1,1])
        elif r<0.45: e2=max(1,e+rng.choice([-1,1]))
        elif r<0.65: lam2[rng.integers(m)]=int(rng.choice([1,3,5,7,9,11,13,15]))
        else: mu2[rng.integers(n)]=int(rng.choice([1,3,5,7,9,11,13,15]))
        if not legal(VW,VU,s2,c2,e2): continue
        o=bounds(rows,Q,s2,c2,e2,lam2,mu2,lmax,D,S,pr)
        for kk,v in o.items(): bestall[kk]=max(bestall.get(kk,0),v)
        if f(o)>=best: s,c,e,lam,mu,best,cur=s2,c2,e2,lam2,mu2,f(o),o
    return dict(C=sum(pr),start=start,best=best,bestall=bestall)
