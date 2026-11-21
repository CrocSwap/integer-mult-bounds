"""ARF theta.py: Z/8 refinement on Z=(U+V)^perp: sigma(x)=sum_k (x o w_k)^T Q (x o v_k) mod 8 (lifts in 0..3);
validity => sigma = 2|x| mod 4 on Z. theta=(sigma-2|x|)/4 mod 2. Test: well-defined under w->w+4? (trivial), quadratic?, Arf."""
import sys,os,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); TARGS=sys.argv[1:]; sys.argv=sys.argv[:1]
sys.path.insert(0,HERE); from stats import *
from e8xy_lib import nullsp
rng=np.random.default_rng(5)
def go(W,V,tag):
    W=W%4;V=V%4
    RB=spaces_B(W,V,Q);RA=spaces_A(W,V,Q)
    UV=f2basis([x for t in range(n) for x in RA[t]]+[x for t in range(n) for x in RB[t]])
    Z=nullsp(mat(UV),range(n),n); d=len(Z)
    def sig(x): return int(sum((x*W[:,k])@Q@(x*V[:,k]) for k in range(W.shape[1])))%8
    def th(c):
        x=(c@Z)%2; s=sig(x); assert (s-2*x.sum())%4==0; return ((s-2*x.sum())//4)%2
    # polar form on basis, test bilinearity on random triples
    E=np.eye(d,dtype=int); t0=[th(E[i]) for i in range(d)]
    B=np.array([[ (th((E[i]+E[j])%2)+t0[i]+t0[j])%2 if i!=j else 0 for j in range(d)] for i in range(d)])
    ok=True
    for _ in range(200):
        c=rng.integers(0,2,d); e=rng.integers(0,2,d)
        pred=(th(c)+th(e)+c@B@e)%2  # if quadratic with polar B (B symmetric, diag handled by th)
        if th((c+e)%2)!=pred: ok=False;break
    lin_ok=all(th(c)==(sum(t0[i] for i in range(d) if c[i])+sum(B[i,j] for i in range(d) for j in range(i+1,d) if c[i] and c[j]))%2 for c in rng.integers(0,2,(100,d)))
    r=rk(B); print(tag,'dimZ',d,'quadratic',ok and lin_ok,'rank polar',r,'symmetric',(B==B.T).all())
    if ok and lin_ok:
        # Arf: theta on radical of B must be linear; check if zero on radical, then Arf via counting on random? exact via Gauss sum over d<=~70 impossible; use symplectic reduction
        rad=nullsp(B,range(d),d)
        trad=[th(v) for v in rad]
        print('   theta on radical (dim %d): nonzero count'%len(rad), sum(trad))
        if sum(trad)==0:
            # symplectic basis reduction: Arf = sum theta(e_i)theta(f_i)
            vecs=[E[i] for i in range(d)]; arf=0; basis=list(np.eye(d,dtype=int))
            Bf=lambda x,y:int(x@B@y)%2
            pool=[v for v in basis]
            # Gram-Schmidt symplectic
            S=[]
            while pool:
                e=pool.pop(0)
                j=next((i for i,f in enumerate(pool) if Bf(e,f)),None)
                if j is None: continue
                f=pool.pop(j); arf^=th(e)&th(f)
                pool=[(p+Bf(p,f)*e+Bf(p,e)*f)%2 for p in pool]
            print('   Arf',arf)
go(np.load('../orbitlp/e8W.npy'),np.load('../orbitlp/e8V.npy'),'E8')
for p in TARGS: go(np.load(p.replace('XX','W')+'.npy'),np.load(p.replace('XX','V')+'.npy'),os.path.basename(p))
