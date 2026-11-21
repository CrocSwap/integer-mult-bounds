"""TAU48 fam.py: tau-form rank at (greedy) Rado minimisers across decoder families."""
import sys,json,numpy as np; sys.path.insert(0,'../orbitlp'); sys.path.insert(0,'../double56')
from geo import Q, D56
from rho import *
from tk import analyse
from lin import inv4
from sa import complete
E=json.load(open(D56+'e8base.json')); Cc=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0); n=104
W0=Cc%4; V0=(Cc@Gb)%4
def rep(W,V,name):
    rb,ra,_,_=rhos(W,V,Q,2); print('  true rhoB',rb,'rhoA',ra,'sum',ra+rb); analyse(W,V,name)
for t in range(3):
    m=8+int(rng.integers(0,5))
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T
    rep((W0@Xm)%4,(V0@Ym)%4,'randfact m=%d'%m)
X8=np.load('../double56/e8X.npy'); Y8=np.load('../double56/e8Y.npy')
for (i,j,c) in [(0,1,1),(2,5,2),(3,7,3)]:
    X2=X8.copy(); Y2=Y8.copy(); X2[:,j]=(X2[:,j]+c*X2[:,i])%4; Y2[:,i]=(Y2[:,i]-c*Y2[:,j])%4
    rep((Cc@X2)%4,(Cc@Y2)%4,'transv %d%d%d'%(i,j,c))
W8=np.load('../orbitlp/e8W.npy')%4; V8=np.load('../orbitlp/e8V.npy')%4
for k in (1,3,5,7):
    keep=list(range(k)); W,V=complete(W8[:,keep],V8[:,keep],Q); rep(W,V,'E8 first %d + completion'%k)
