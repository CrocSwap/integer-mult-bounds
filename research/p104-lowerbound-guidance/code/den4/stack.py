"""DEN4 stack.py (own code): hill-climb the STACK RANK  rank [ sum_k D(y_k^i) Q D(z_k^j) ]_{ij}  (<= C for every decoder, any denominators)."""
import numpy as np, sys
from qlib import *
from quarter import *
def stackrank(Ys,Zs,Q):
    # Ys: list over i of n x m 0/1 ; Zs: list over j
    blocks=[[((y@z.T)*Q)%2 for z in Zs] for y in Ys]
    return rk2(np.block(blocks))
def climb(Dm,Sm,Q,p,q,iters,seed,init=None):
    rng=np.random.default_rng(seed); n,m=Dm.shape
    if init: Ys,Zs=[x.copy() for x in init[0]],[x.copy() for x in init[1]]
    else:
        Ys=[(rng.random((n,m))<.5)*Dm for _ in range(p)]; Zs=[(rng.random((n,m))<.5)*Sm for _ in range(q)]
    best=stackrank(Ys,Zs,Q)
    for it in range(iters):
        side=rng.integers(2); L=Ys if side==0 else Zs; Mk=Dm if side==0 else Sm
        i=rng.integers(len(L)); nz=np.argwhere(Mk)
        t,k=nz[rng.integers(len(nz))]
        L[i][t,k]^=1; r=stackrank(Ys,Zs,Q)
        if r>=best: best=r
        else: L[i][t,k]^=1
    return best,Ys,Zs
if __name__=='__main__':
    L=std_set('HS64'); Q=Q_std(L); n=len(L)
    U=[[0]*8 for _ in range(8)]
    for t,i in enumerate(range(0,8,2)):
        for s,sg in enumerate((1,-1)):
            U[2*t+s][i]=2; U[2*t+s][i+1]=2*sg
    rows=gram_rows_std(L,U); e,W,V,pr,D,S=normalise(rows,Q)
    Dm=(W%8!=0).astype(np.int64); Sm=(V%8!=0).astype(np.int64)
    a=W%2; a1=(W>>1)&1; b=V%2; b1=(V>>1)&1
    print('canonical 2-stack (a1,a)x(b,b1):',stackrank([a1,a],[b,b1],Q),' C',sum(pr))
    for p,q in [(1,1),(2,2),(3,3)]:
        for seed in range(2):
            r,_,_=climb(Dm,Sm,Q,p,q,int(sys.argv[1]) if len(sys.argv)>1 else 1500,seed)
            print('p,q',p,q,'seed',seed,'stack rank',r)
