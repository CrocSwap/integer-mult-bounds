# THINQ tq2: numeric scout of the Q-chart MASKS: h full hubs + d leaves (degree-1 roles) per stage, T thins (rank 1, any support),
# k rank-2 hosts in order 0..k-1, thins interleaved at given slots. prod = -I, every host det(2I + B_t^T A_t) kept >= 0.3 (lambda != -1).
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import sys, numpy as np
from scipy.optimize import least_squares
def build(k,h,d,T,slots):
    n=h+d*k
    sup=[list(range(h))+[h+d*t+i for i in range(d)] for t in range(k)]
    ev=[]
    for t in range(k):
        for _ in range(slots.count(t)): ev.append(('t',None))
        ev.append(('h',t))
    for _ in range(slots.count(k)): ev.append(('t',None))
    sizes=[(len(sup[t])*2*2 if kind=='h' else 2*n) for kind,t in ev]
    def mats(x):
        out=[];i=0
        for (kind,t),sz in zip(ev,sizes):
            if kind=='h':
                m=len(sup[t]);A=np.zeros((n,2));B=np.zeros((n,2))
                A[sup[t]]=x[i:i+2*m].reshape(m,2);B[sup[t]]=x[i+2*m:i+4*m].reshape(m,2)
            else:
                A=x[i:i+n].reshape(n,1);B=x[i+n:i+2*n].reshape(n,1)
            i+=sz;out.append((kind,A,B))
        return out
    def res(x):
        P=np.eye(n);pen=[]
        for kind,A,B in mats(x):
            P=(np.eye(n)+A@B.T)@P
            if kind=='h': pen.append(10*max(0,0.3-abs(np.linalg.det(2*np.eye(2)+B.T@A))))
        return np.concatenate([(P+np.eye(n)).ravel(),pen])
    return n,sum(sizes),res,mats
def scout(k,h,d,T,slots,trials,seed):
    rng=np.random.default_rng(seed)
    n,N,res,mats=build(k,h,d,T,slots);best=9e9
    for _ in range(trials):
        r=least_squares(res,rng.normal(size=N),method='trf',max_nfev=3000)
        v=np.linalg.norm(res(r.x));best=min(best,v)
        if v<1e-10: break
    return n,best
if __name__=='__main__':
    seed=int(sys.argv[1])
    cases=[ # (k,h,d,T,slots)
        (3,2,2,4,[0,1,2,3]),(3,2,2,4,[0,0,3,3]),(3,2,2,4,[1,1,2,2]),(3,2,2,3,[0,1,3]),
        (3,2,1,1,[0]),(3,2,1,1,[2]),(3,2,1,2,[0,3]),
        (4,2,2,4,[0,1,3,4]),(4,2,2,4,[2,2,2,2]),(4,2,1,2,[0,4]),
        (3,2,2,5,[0,1,2,3,3]),(3,2,2,6,[0,1,1,2,2,3]),(4,2,2,6,[0,1,2,3,4,4]),(4,2,2,8,[0,1,1,2,2,3,3,4])]
    for c in cases:
        n,b=scout(*c,trials=25,seed=seed)
        print(f'k{c[0]} hubs{c[1]} leaves/stage{c[2]} T{c[3]} slots{c[4]} n{n} Q{n-2*c[0]+2}: best res {b:.2e}',flush=True)
