"""LINEAR56 quadtr.py: [C, randomized] quad-part transversal rank of {c_t ^ P_t}, P_t = span{p_k : B(q_k,c_t)=1},
for random mod-2 decompositions sum q_k p_k^T = B^-1 (m rows).  If always 28 then rho_B >= 28 (projection argument)."""
import sys, numpy as np, itertools
sys.path.insert(0,'../double56'); import rho as R
from lcore import *
PAIRS=list(itertools.combinations(range(8),2))
def wedge(a,b): return np.array([(a[i]*b[j]+a[j]*b[i])%2 for i,j in PAIRS],dtype=np.int64)
def decomp(m,rng):
    # random: start from random basis Q, dual P, then add (m-8) random cancelling-free perturbations via splits
    while True:
        Qm=rng.integers(0,2,(8,8))
        if f2rank(Qm)==8: break
    Rr,_=rref(np.concatenate([Qm,np.eye(8,dtype=np.int64)],1)); Qi=Rr[:,8:].astype(np.int64)
    Pm=((Qi@Binv)%2).T; rows=[(Qm[:,k],Pm[:,k]) for k in range(8)]
    while len(rows)<m:
        i=rng.integers(len(rows)); q,p=rows[i]; r=rng.integers(0,2,8)
        if rng.random()<.5:
            if (r==0).all() or (r==p).all(): continue
            rows[i]=(q,r); rows.append((q,(p+r)%2))
        else:
            if (r==0).all() or (r==q).all(): continue
            rows[i]=(r,p); rows.append(((q+r)%2,p))
        # random transvection mixing
        if len(rows)>=2:
            i,j=rng.choice(len(rows),2,replace=False); (qi,pi),(qj,pj)=rows[i],rows[j]
            nqi=(qi+qj)%2; npj=(pi+pj)%2
            if nqi.any() and npj.any(): rows[i]=(nqi,pi); rows[j]=(qj,npj)
    S=np.zeros((8,8),np.int64)
    for q,p in rows: S^=np.outer(q,p)
    assert (S==Binv).all()
    return rows
def quad_tr(rows,trials=2):
    fam=[]
    for t in range(104):
        c=Xb[t]; vecs=[wedge(c,p) for q,p in rows if (q@Bm@c)%2==1]
        fam.append([R.toint(v) for v in (rref(np.array(vecs))[0] if vecs else [])])
    return R.trank(fam,28,trials)
if __name__=="__main__":
    rng=np.random.default_rng(int(sys.argv[1])); hist={}
    for it in range(int(sys.argv[2])):
        m=8+int(rng.integers(0,9)); rows=decomp(m,rng); r=quad_tr(rows); hist[r]=hist.get(r,0)+1
        if r<28: print('LOW',r,m,flush=True); np.save(f'low_{sys.argv[1]}_{it}.npy',np.array([[*q,*p] for q,p in rows]))
    print('hist',hist)
