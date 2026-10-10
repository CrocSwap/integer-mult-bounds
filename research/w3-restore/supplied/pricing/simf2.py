import numpy as np, json, sys, time
from cost import load_snapshot
def simulate(rec, n, v, work, seed=1, words=2):
    rng=np.random.default_rng(seed)
    R=n+1
    val=rng.integers(0,2**63,size=(R,words),dtype=np.uint64)
    val[work]=0
    init=val.copy()
    ops=rec[:,0]; A=rec[:,1]; B=rec[:,2]; C=rec[:,3]
    t=time.time()
    for k in range(len(rec)):
        op=ops[k]
        if op==1:
            if C[k]&1: val[A[k]]^=val[B[k]]
        elif op==2:   # copy center A into temp B
            val[B[k]]=val[A[k]]
        elif op==3:
            val[B[k]]=0
    ok_x=np.array_equal(val[:v],init[:v])
    ok_y=np.array_equal(val[v:2*v],init[v:2*v]^init[:v])
    ok_h=np.array_equal(val[2*v:n],init[2*v:n])
    return ok_x,ok_y,ok_h,time.time()-t
if __name__=='__main__':
    s,fr,dim,rec=load_snapshot(sys.argv[1])
    n=s['n'];v=s['v']
    print('work stream index check:', set(rec[rec[:,0]==2][:,2].tolist()))
    print(simulate(rec,n,v,n))
