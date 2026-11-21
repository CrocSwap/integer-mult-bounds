import sys,json,numpy as np, collections; sys.path.insert(0,'../orbitlp')
from geo import Q, D56
from rho import *
E=json.load(open(D56+'e8base.json')); R=np.array(E['C'])[:104]
X=np.load('e8X.npy'); Y=np.load('e8Y.npy')
def sc(X,Y):
    W=(R@X)%4; V=(R@Y)%4
    return trank(spaces_B(W,V,Q),104,1), trank(spaces_A(W,V,Q),104,1), cost(W,V,Q)
cnt=collections.Counter()
for i in range(8):
  for j in range(8):
    if i==j: continue
    for c in (1,2,3):
      X2=X.copy(); Y2=Y.copy(); X2[:,j]=(X2[:,j]+c*X2[:,i])%4; Y2[:,i]=(Y2[:,i]-c*Y2[:,j])%4
      rb,ra,C=sc(X2,Y2); cnt[(ra+rb,C)]+=1
print('transvection nbrs (rho sum, C):',sorted(cnt.items()))
# splits: row k -> (x_k, y1),(x_k, y_k - y1) for random y1
rng=np.random.default_rng(0); cnt=collections.Counter()
for trial in range(150):
    k=int(rng.integers(8)); y1=rng.integers(0,4,8)
    X2=np.concatenate([X,X[:,[k]]],1); Y2=np.concatenate([Y,y1[:,None]],1); Y2[:,k]=(Y2[:,k]-y1)%4
    rb,ra,C=sc(X2,Y2); cnt[(ra+rb,C)]+=1
print('split nbrs:',sorted(cnt.items())[:10])
