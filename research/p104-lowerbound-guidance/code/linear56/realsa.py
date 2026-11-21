"""LINEAR56 realsa.py: annealing over REAL linear decoders (X,Y in Z4^{8xm}, XY^T = K fixed) minimising f (exact UV).
Moves preserve XY^T exactly: Z4 transvection, split, merge, half-row pair insert/remove. args: seed iters start(e8|rand)"""
import sys, numpy as np, math, time
from lcore import *
rng=np.random.default_rng(int(sys.argv[1])); iters=int(sys.argv[2]); start=sys.argv[3]
T=np.load('tightX.npy')
def ok(X,Y): return X.shape[1]>0
def clean(X,Y):
    keep=[k for k in range(X.shape[1]) if (X[:,k]%4).any() and (Y[:,k]%4).any()]
    return X[:,keep]%4,Y[:,keep]%4
def move(X,Y):
    X=X.copy(); Y=Y.copy(); m=X.shape[1]; t=rng.integers(0,4)
    if t==0 and m>=2:
        i,j=rng.choice(m,2,replace=False); s=int(rng.integers(1,4))
        X[:,i]=(X[:,i]+s*X[:,j])%4; Y[:,j]=(Y[:,j]-s*Y[:,i])%4      # x_i y_i + x_j y_j invariant
    elif t==1 and m<14:
        i=rng.integers(m); r=T[rng.integers(len(T))] if rng.random()<.6 else rng.integers(0,4,8)
        if rng.random()<.5: X=np.concatenate([X,X[:,[i]]],1); Y=np.concatenate([Y,(Y[:,[i]]-r[:,None])%4],1); Y[:,i]=r
        else: Y=np.concatenate([Y,Y[:,[i]]],1); X=np.concatenate([X,(X[:,[i]]-r[:,None])%4],1); X[:,i]=r
    elif t==2 and m>=2:
        i,j=rng.choice(m,2,replace=False)
        if (X[:,i]==X[:,j]).all(): Y[:,i]=(Y[:,i]+Y[:,j])%4; X=np.delete(X,j,1); Y=np.delete(Y,j,1)
        elif (Y[:,i]==Y[:,j]).all(): X[:,i]=(X[:,i]+X[:,j])%4; X=np.delete(X,j,1); Y=np.delete(Y,j,1)
        elif ((X[:,i]+X[:,j])%4==0).all(): Y[:,i]=(Y[:,i]-Y[:,j])%4; X=np.delete(X,j,1); Y=np.delete(Y,j,1)
    else:
        i=rng.integers(m); s=int(rng.choice([1,3]))
        if rng.random()<.5: X[:,i]=(s*X[:,i])%4; Y[:,i]=(s*Y[:,i])%4
        else:
            j=rng.integers(m); 
            if i!=j:
                X[:,[i,j]]=X[:,[j,i]]
                Y[:,[i,j]]=Y[:,[j,i]]
    return clean(X,Y)
def ev(X,Y):
    W=C104@X%4; V=C104@Y%4; return f_val(*UV(W,V))[0], cost(W,V)
if start=='e8': X=np.load('../double56/e8X.npy')%4; Y=np.load('../double56/e8Y.npy')%4
else:
    raise SystemExit("only e8 start")
X0=X.copy(); Y0=Y.copy(); K=(X@Y.T)%4
cur,cc=ev(X,Y); best=cur; t0=time.time(); hist={}
for it in range(iters):
    Tp=float(sys.argv[4]) if len(sys.argv)>4 else max(0.2,2.0*(1-it/iters))
    X2,Y2=move(X,Y)
    if X2.shape[1]==0: continue
    assert ((X2@Y2.T-K)%4==0).all()
    f2,c2=ev(X2,Y2)
    if f2<=cur or rng.random()<math.exp((cur-f2)/Tp):
        X,Y,cur=X2,Y2,f2; hist[cur]=hist.get(cur,0)+1
        if cur<best or (cur<56):
            best=min(best,cur); print('it',it,'f',cur,'C',c2,'m',X.shape[1],flush=True)
            if cur<56: np.save(f'realsa_low_{sys.argv[1]}.npy',np.concatenate([X,Y],0))
print('best',best,'hist',dict(sorted(hist.items())),'time',round(time.time()-t0))
