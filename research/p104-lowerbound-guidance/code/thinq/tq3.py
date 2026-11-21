# THINQ tq3: thin deletion reduces the Q>=1 frame to a HOST-ONLY product P_h with rank(P_h + I) <= T  [P: deleting a rank-1 factor
# changes the product by a rank-1 term].  Scout: can leaves (degree-1 roles) be "cheaper" than one thin each, i.e. rank(P_h+I) < #leaves?
# masks: list per stage of role sets; leaves = roles in exactly one mask. Minimise the (n-r) smallest singular values of P_h+I.
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import sys, numpy as np
from scipy.optimize import least_squares
def scout(n,masks,r,trials,seed,detmin=0.3):
    rng=np.random.default_rng(seed); k=len(masks)
    sz=[len(m)*4 for m in masks]; N=sum(sz)
    def mats(x):
        out=[];i=0
        for m in masks:
            A=np.zeros((n,2));B=np.zeros((n,2));L=len(m)
            A[m]=x[i:i+2*L].reshape(L,2);B[m]=x[i+2*L:i+4*L].reshape(L,2);i+=4*L;out.append((A,B))
        return out
    def res(x):
        P=np.eye(n);pen=[]
        for A,B in mats(x):
            P=(np.eye(n)+A@B.T)@P; pen.append(10*max(0,detmin-abs(np.linalg.det(2*np.eye(2)+B.T@A))))
        sv=np.linalg.svd(P+np.eye(n),compute_uv=False)
        sc=np.linalg.norm(P)+1
        return np.r_[sv[r:]/sc,pen, 1e-3*max(0,np.linalg.norm(x)-30)]
    best=9e9
    for _ in range(trials):
        x=least_squares(res,rng.normal(size=N),method='trf',max_nfev=2000).x
        v=np.linalg.norm(res(x)); best=min(best,v)
        if v<1e-9: break
    return best
def chart(k,h=2,d=2):
    n=h+d*k; return n,[list(range(h))+[h+d*t+i for i in range(d)] for t in range(k)]
if __name__=='__main__':
    seed=int(sys.argv[1])
    tests=[]
    for k in (2,3,4):
        n,m=chart(k)
        for r in (n-2*k-2+2, 2*k-1, 2*k, 2*k+1):   # n-(2k-2)... controls/targets
            tests.append((f'chart k{k} 2hub+2leaf n{n} leaves{2*k} rank<={r}',n,m,r))
    # control without leaves: Q=0 C1-like hubs+pure pairs (n=2k-2) must reach rank 0
    tests.insert(0,('control k3 n4 (CallerSignInst masks) rank<=0',4,[[0,1,2,3],[0,1,2,3],[0,1,2,3]],0))
    for name,n,m,r in tests:
        if r<0: continue
        b=scout(n,m,r,trials=12,seed=seed)
        print(f'{name}: best {b:.2e}',flush=True)
