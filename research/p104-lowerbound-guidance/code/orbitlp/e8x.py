"""ORBITLP e8x.py: per-frame structure of I+X, Y, Z on E8-56; diagonal of X; N distribution."""
import numpy as np, collections
from geo import *
from carry import rk2
W=np.load('e8W.npy'); V=np.load('e8V.npy'); m=8
a=W%2; w2=(W//2)%2; b=V%2; v2=(V//2)%2
N=(a@b.T)*Q; X=(N//2)%2; I=np.eye(104,dtype=int)
Y=((w2@b.T)%2)*Q; Z=((a@v2.T)%2)*Q; E=((w2@v2.T)%2)*Q
print('N values on odd offdiag',collections.Counter(N[(Q==1)&(I==0)].tolist()),'diag',collections.Counter(np.diag(N).tolist()))
F=frames()
c=collections.Counter()
for T in F:
    T=list(T); c[(rk2((I+X)[np.ix_(T,T)]),rk2(Y[np.ix_(T,T)]),rk2(Z[np.ix_(T,T)]))]+=1
print('per-frame (rank I+X, rank Y, rank Z):',c)
big=np.block([[Y,E],[np.zeros_like(Y),Z]])
print('rank [[Y,E],[0,Z]]',rk2(big),'rank Y',rk2(Y),'rank Z',rk2(Z),'rank I+X',rk2(I+X),'I+X symmetric?',((I+X-(I+X).T)%2==0).all())
print('X diag ones',int(np.diag(X).sum()))
