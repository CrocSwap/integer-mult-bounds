"""ISO3 gmax: max of alpha+beta over 2-power gauges (row shifts s_k, port shifts c_t, level e).
Raw decoder: rows (w,u) Fractions with sum_k w_k u_k^T o Q = I on Q-cells. Gauge: w_k(t)*2^(s_k+c_t), u_k(t)*2^(e-s_k-c_t), all 2-integral.
a_k(t) = [valuation of new w == 0], b_k(t) = [valuation of new v == 0]. C >= alpha+beta for every legal gauge (A0 B0 = 0 needs e >= 1)."""
import numpy as np
from ilib import *
BIG=10**6
def vals(rows,n):
    VW=np.array([[v2(w[t]) if w[t]!=0 else BIG for t in range(n)] for w,u in rows]).T   # n x m
    VU=np.array([[v2(u[t]) if u[t]!=0 else BIG for t in range(n)] for w,u in rows]).T
    return VW,VU
def ab_of(VW,VU,s,c,e,Q,D,S):
    W=VW+s[None,:]+c[:,None]; U=VU+e-s[None,:]-c[:,None]
    if (W<0).any() or (U<0).any(): return None
    a=(W==0).astype(np.int64); b=(U==0).astype(np.int64); m=VW.shape[1]
    Al=[a[:,[k]]*Q[:,S[k]] for k in range(m) if S[k]]; Br=[(Q[D[k],:]*b[:,k][None,:]) for k in range(m) if D[k]]
    al=rk2(np.concatenate(Al,1)) if Al else 0; be=rk2(np.concatenate(Br,0).T) if Br else 0
    return al,be
def canon(VW,VU):
    n,m=VW.shape
    mu=np.array([VW[:,k].min() for k in range(m)]); nu=np.array([VU[:,k].min() for k in range(m)])
    s=-mu; e=max(1,int(max(-(mu+nu))))
    return s,np.zeros(n,dtype=np.int64),e
def gauge_max(rows,Q,iters=400,seed=0):
    n=len(Q); m=len(rows); VW,VU=vals(rows,n)
    D=[[t for t in range(n) if VW[t,k]<BIG] for k in range(m)]; S=[[t for t in range(n) if VU[t,k]<BIG] for k in range(m)]
    s,c,e=canon(VW,VU); rng=np.random.default_rng(seed)
    best=ab_of(VW,VU,s,c,e,Q,D,S); start=best; bs=sum(best)
    for it in range(iters):
        s2=s.copy(); c2=c.copy(); e2=e; r=rng.random()
        if r<0.5: k=rng.integers(m); s2[k]+=rng.choice([-1,1])
        elif r<0.9: t=rng.integers(n); c2[t]+=rng.choice([-1,1])
        else: e2=max(1,e+rng.choice([-1,1]))
        x=ab_of(VW,VU,s2,c2,e2,Q,D,S)
        if x is None: continue
        if sum(x)>=bs: s,c,e,best,bs=s2,c2,e2,x,sum(x)
    C=sum(rk2(Q[np.ix_(D[k],S[k])]) if D[k] and S[k] else 0 for k in range(m))
    assert C>=bs
    return dict(C=C,canon=start,canon_sum=sum(start),gmax=best,gmax_sum=bs,e=e)
