"""TAU48 gibbs3.py: long Gibbs walks (from E8-56+extra empty rows, or randfact m), report tau-rank every R steps; flag tau>48 at Rado-exact points."""
import sys,numpy as np
from gibbs import *
seed=int(sys.argv[1]); steps=int(sys.argv[2]); mode=sys.argv[3]; extra=int(sys.argv[4]); R=int(sys.argv[5])
rng=np.random.default_rng(seed)
if mode=='e8':
    W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4
    W=np.concatenate([W,np.zeros((n,extra),np.int64)],1); V=np.concatenate([V,np.zeros((n,extra),np.int64)],1)
else:
    W0=Cc%4; V0=(Cc@Gb)%4; m=extra
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T; W=(W0@Xm)%4; V=(V0@Ym)%4
mx=0
for s in range(steps+1):
    if s%R==0:
        tr,ex,rs=report(W,V,'%s s%d step%d'%(mode,seed,s))
        if ex: mx=max(mx,tr)
        if ex and tr>48: np.save('cex_W_%s%d.npy'%(mode,seed),W); np.save('cex_V_%s%d.npy'%(mode,seed),V); print('TAU48 VIOLATION saved',flush=True)
    t=int(rng.integers(n)); W,V=resample(W,V,t,rng,'W' if rng.random()<0.5 else 'V'); assert check(W,V)
print('MAX tau-rank at Rado-exact points',mx)
