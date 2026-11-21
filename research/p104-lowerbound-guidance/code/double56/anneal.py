"""DOUBLE56 anneal.py: search linear decoders W=RX, V=RY (X Y^T = Gb mod 4) minimizing rho_A+rho_B (cost irrelevant)."""
import sys,json,numpy as np, time; sys.path.insert(0,'../orbitlp')
from geo import Q, D56
from rho import *
E=json.load(open(D56+'e8base.json')); R=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
seed=int(sys.argv[1]); steps=int(sys.argv[2]); start=sys.argv[3] if len(sys.argv)>3 else 'e8'
rng=np.random.default_rng(seed)
X=np.load('e8X.npy'); Y=np.load('e8Y.npy')
if start=='rand':
    for _ in range(200):
        i,j=rng.choice(X.shape[1],2,replace=False); c=int(rng.integers(1,4))
        X[:,j]=(X[:,j]+c*X[:,i])%4; Y[:,i]=(Y[:,i]-c*Y[:,j])%4
def score(X,Y):
    keep=[k for k in range(X.shape[1]) if X[:,k].any() and Y[:,k].any()]
    W=(R@X[:,keep])%4; V=(R@Y[:,keep])%4
    RB=spaces_B(W,V,Q); RA=spaces_A(W,V,Q)
    return trank(RB,104,1,int(rng.integers(1<<30)))+trank(RA,104,1,int(rng.integers(1<<30)))
cur=score(X,Y); best=cur; T=1.0; t0=time.time()
for it in range(steps):
    X2=X.copy(); Y2=Y.copy(); m=X.shape[1]; mv=rng.random()
    if mv<0.15 and m<16:   # split: add zero row then transvect
        X2=np.concatenate([X2,np.zeros((8,1),np.int64)],1); Y2=np.concatenate([Y2,np.zeros((8,1),np.int64)],1); m+=1
    i,j=rng.choice(m,2,replace=False); c=int(rng.integers(1,4))
    X2[:,j]=(X2[:,j]+c*X2[:,i])%4; Y2[:,i]=(Y2[:,i]-c*Y2[:,j])%4
    keep=[k for k in range(m) if X2[:,k].any() and Y2[:,k].any()]
    X2=X2[:,keep]; Y2=Y2[:,keep]
    assert ((X2@Y2.T-Gb)%4==0).all()
    s=score(X2,Y2)
    if s<=cur or rng.random()<np.exp((cur-s)/T):
        X,Y,cur=X2,Y2,s
        if s<best:
            best=s; np.save(f'best_{seed}_X.npy',X); np.save(f'best_{seed}_Y.npy',Y)
    T=max(0.05,T*0.999)
    if it%200==0: print(it,'cur',cur,'best',best,'m',X.shape[1],'%.0fs'%(time.time()-t0),flush=True)
print('final best',best)
