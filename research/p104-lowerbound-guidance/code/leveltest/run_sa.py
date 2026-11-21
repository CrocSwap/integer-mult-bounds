# SA over Gibbs-resample moves minimising the lift-independent F2 floor sum_l rank_F2(Mbar_l) (fwd orientation); verifies S with lifts at the best states.
import numpy as np,sys,math
sys.argv=[sys.argv[0]]+sys.argv[1:]
seed=int(sys.argv[1]); steps=int(sys.argv[2]); mode=sys.argv[3]; extra=int(sys.argv[4]); T=float(sys.argv[5])
import run_gibbs_lib as G
from lt import *
rng=G.rng=np.random.default_rng(seed)
if mode=='e8':
    W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4
    W=np.concatenate([W,np.zeros((104,extra),np.int64)],1); V=np.concatenate([V,np.zeros((104,extra),np.int64)],1)
else:
    from run_all_inv import inv4
    W0=C104%4; V0=(C104@Gb)%4; m=extra
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T; W=(W0@Xm)%4; V=(V0@Ym)%4
def f2floor(W,V,orient):
    A,B=(W,V) if orient=='fwd' else (V,W)
    info=rows_info(Q104,A,B); tot=0
    for R in levels(info,9):
        if R:
            M2=(A[:,R]%2)@(B[:,R]%2).T%2; tot+=f2rank_rows([toint(r) for r in M2])
    return tot,sum(p for _,p in info)
cur=f2floor(W,V,'fwd'); best=cur; print('start',cur,flush=True)
for s in range(steps):
    t=int(rng.integers(104)); W2,V2=G.resample(W,V,t,'W' if rng.random()<0.5 else 'V')
    c2=f2floor(W2,V2,'fwd')
    if c2[0]<=cur[0] or rng.random()<math.exp(-(c2[0]-cur[0])/T):
        W,V,cur=W2,V2,c2
        if cur[0]<best[0]:
            best=cur; np.save('sa_W_%s%d.npy'%(mode,seed),W); np.save('sa_V_%s%d.npy'%(mode,seed),V)
    if s%100==0: print(s,'cur f2,D',cur,'best',best,flush=True)
print('BEST f2floor,D',best)
r=evaluate(Q104,W,V,rng,nrand=10); print('final state',r)
