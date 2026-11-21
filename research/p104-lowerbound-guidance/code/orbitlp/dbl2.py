"""ORBITLP dbl2.py: test MASTER form: C >= rank(sum diag(y_k)Q diag(b_k)) + rank(sum diag(a_k)Q diag(z_k)) for ANY y_k ⊆ D_k, z_k ⊆ S_k."""
import numpy as np
from geo import Q
from dbl import rk2
W=np.load('e8W.npy')%4; V=np.load('e8V.npy')%4; m=8
a=W%2; b=V%2; Dm=(W>0).astype(int); Sm=(V>0).astype(int)
rng=np.random.default_rng(0)
best=0
for trial in range(40):
    p=rng.random()
    y=(rng.random(Dm.shape)<p).astype(int)*Dm; z=(rng.random(Sm.shape)<rng.random()).astype(int)*Sm
    if trial==0: y=Dm.copy(); z=Sm.copy()
    Y=((y@b.T)%2)*Q; Z=((a@z.T)%2)*Q
    s=rk2(Y)+rk2(Z); best=max(best,s)
    if trial<3 or s>56: print(trial,'rkY',rk2(Y),'rkZ',rk2(Z),'sum',s)
print('max over trials',best,'(C=56)')
