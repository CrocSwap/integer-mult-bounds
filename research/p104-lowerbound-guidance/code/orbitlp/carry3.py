"""ORBITLP carry3.py: test [CONJ] rank Y + rank Z <= C on varied mod-4 decoders."""
import numpy as np
from geo import *
from carry import rk2
from carry2 import price
W0=np.load('e8W.npy'); V0=np.load('e8V.npy')
I=np.eye(104,dtype=int)
def check(W,V,name):
    W=W%4; V=V%4; m=W.shape[1]
    Mm=(W@V.T)%4
    bad=int(((Mm-2*I)%4*Q).astype(bool).sum())
    a=W%2; w2=(W//2)%2; b=V%2; v2=(V//2)%2
    Y=sum(np.outer(w2[:,k],b[:,k])*Q for k in range(m))%2
    Z=sum(np.outer(a[:,k],v2[:,k])*Q for k in range(m))%2
    p=price(W,V); C=sum(p)
    ry,rz=rk2(Y),rk2(Z)
    print('%-28s viol %d C %d rkY %d rkZ %d sum %d %s'%(name,bad,C,ry,rz,ry+rz,'OK' if ry+rz<=C else 'FAIL'))
check(I,2*I,'trivial e_t/2e_t')
check(2*I,I,'trivial 2e_t/e_t')
check(I,2*I+0,'x')
# zeroed ports
rng=np.random.default_rng(5)
for z in [1,2,3,5,8]:
    Zs=rng.choice(104,z,replace=False)
    W=W0.copy(); V=V0.copy(); W[Zs,:]=0
    E=np.zeros((104,z),int); E2=np.zeros((104,z),int)
    for j,h in enumerate(Zs): E[h,j]=1; E2[h,j]=2
    check(np.hstack([W,E]),np.hstack([V,E2]),'zeroW %d'%z)
    W=W0.copy(); V=V0.copy(); V[Zs,:]=0
    check(np.hstack([W,E2]),np.hstack([V,E]),'zeroV %d'%z)
# split a row: D_k partition
for k in range(3):
    D=np.nonzero(W0[:,k])[0]; part=rng.random(len(D))<0.5
    w1=np.zeros(104,int); w2_=np.zeros(104,int); w1[D[part]]=W0[D[part],k]; w2_[D[~part]]=W0[D[~part],k]
    W=np.hstack([W0[:,:k],w1[:,None],w2_[:,None],W0[:,k+1:]]); V=np.hstack([V0[:,:k],V0[:,k:k+1],V0[:,k:k+1],V0[:,k+1:]])
    check(W,V,'split row %d'%k)
# add a row pair that cancels: (x,y) and (x,-y)
for t in range(3):
    x=rng.integers(0,4,104); y=rng.integers(0,4,104)
    check(np.hstack([W0,x[:,None],x[:,None]]),np.hstack([V0,y[:,None],(-y)[:,None]]),'cancel pair %d'%t)
    check(np.hstack([W0,x[:,None],(2*x)[:,None]]),np.hstack([V0,(2*y)[:,None],(y)[:,None]]),'2-cancel pair %d'%t)
# rescale rows by 2-swap: (w,v)->(w*u,v*u^-1) units
for t in range(2):
    u=rng.choice([1,3],(8,)); check(W0*u,V0*u,'unit scale')
