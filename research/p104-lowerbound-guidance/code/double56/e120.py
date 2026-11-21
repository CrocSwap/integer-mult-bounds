import sys,json,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import D56
from rho import *
E=json.load(open(D56+'e8base.json')); print(E.keys()); C=np.array(E['C']); Gb=np.array(E['Gb']); print(C.shape)
G=C@Gb@C.T; print('diag',set(np.diag(G))); 
Q=(G%2==0).astype(np.int64); n=C.shape[0]
X=np.load('e8X.npy'); Y=np.load('e8Y.npy')
W=(C@X)%4; V=(C@Y)%4
print('decoder on all',n,check_decoder(W,V,Q),'C',cost(W,V,Q))
print('rho', trank(spaces_B(W,V,Q),n,2), trank(spaces_A(W,V,Q),n,2))
