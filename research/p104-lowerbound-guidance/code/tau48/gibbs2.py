import sys,numpy as np
from gibbs import *
seed=int(sys.argv[1]); steps=int(sys.argv[2]); extra=int(sys.argv[3])
rng=np.random.default_rng(seed)
W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4
W=np.concatenate([W,np.zeros((n,extra),np.int64)],1); V=np.concatenate([V,np.zeros((n,extra),np.int64)],1)
report(W,V,'start'); best=None
for s in range(steps):
    t=int(rng.integers(n)); W,V=resample(W,V,t,rng,'W' if rng.random()<0.5 else 'V'); assert check(W,V)
    if (s+1)%(steps//8)==0:
        tr,ex,rs=report(W,V,'step%d'%(s+1))
        if ex and tr>48: np.save('cex_W_%d.npy'%seed,W); np.save('cex_V_%d.npy'%seed,V); print('TAU48 VIOLATION saved')
np.save('g_W_%d_%d.npy'%(seed,extra),W); np.save('g_V_%d_%d.npy'%(seed,extra),V)
