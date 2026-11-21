# THINQ tq1: numeric scout. Can a role set F touched only by ONE host s and j thins have |F| > j (prod = -I, all hosts lambda != -1)?
# events: host s (rank 2, touches F and C), m other hosts (rank 2, C only), j thins touching F (any rows), t2 thins on C only.
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import sys, numpy as np
from scipy.optimize import least_squares
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
def run(nF,nC,m,j,t2,order,trials=40):
    n=nF+nC; best=None
    ev=[]  # (kind, rank, rowmask)
    for e in order: ev.append(e)
    def unpack(x):
        mats=[];i=0
        for kind,r in ev:
            A=x[i:i+n*r].reshape(n,r);i+=n*r;B=x[i:i+n*r].reshape(n,r);i+=n*r
            if kind=='h': A=A.copy();B=B.copy();A[:nF]=0;B[:nF]=0
            if kind=='c': A=A.copy();B=B.copy();A[:nF]=0;B[:nF]=0
            mats.append((kind,A,B))
        return mats
    N=sum(2*n*r for _,r in ev)
    def res(x):
        P=np.eye(n)
        for kind,A,B in unpack(x): P=(np.eye(n)+A@B.T)@P
        out=[(P+np.eye(n)).ravel()]
        # penalise lambda=-1 at hosts: det K_tt >= 0.3 softly
        for kind,A,B in unpack(x):
            if A.shape[1]==2:
                d=abs(np.linalg.det(2*np.eye(2)+B.T@A)); out.append([max(0,0.3-d)*10])
        return np.concatenate([np.ravel(o) for o in out])
    for t in range(trials):
        x0=rng.normal(size=N)
        r=least_squares(res,x0,method='lm' if len(res(x0))>=N else 'trf',max_nfev=4000)
        v=np.linalg.norm(res(r.x))
        if best is None or v<best[0]: best=(v,r.x)
        if v<1e-10: break
    v,x=best
    dets=[abs(np.linalg.det(2*np.eye(2)+B.T@A)) for k,A,B in unpack(x) if A.shape[1]==2]
    return v,min(dets)
if __name__=='__main__':
    for nF,nC,m,j,t2 in [(1,2,2,0,0),(1,0,0,1,0),(2,0,0,1,0),(2,2,2,1,0),(2,2,3,1,0),(2,4,4,1,0),(3,2,3,1,0),(3,2,3,2,0),(2,2,2,1,1),(2,4,4,1,2)]:
        for perm in range(3):
            evs=[('s',2)]+[('h',2)]*m+[('t',1)]*j+[('c',1)]*t2
            order=[evs[i] for i in rng.permutation(len(evs))]
            v,d=run(nF,nC,m,j,t2,order)
            print(f'nF{nF} nC{nC} hosts+{m} thinF{j} thinC{t2} order {"".join(e[0] for e in order)}: res {v:.2e} min detK {d:.3f}',flush=True)
