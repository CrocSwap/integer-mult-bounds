import sys,json,numpy as np; sys.path.insert(0,'../orbitlp'); sys.path.insert(0,'../double56')
from geo import Q, D56
from rho import *
def rk(M): return f2rank([toint(r) for r in M%2])
W=np.load('../orbitlp/e8W.npy')%4;V=np.load('../orbitlp/e8V.npy')%4
a=W%2;b=V%2;N=(a@b.T)*Q;X=(N//2)%2;n=104;I=np.eye(n,dtype=int)
Y=((W//2)@b.T)*Q%2; Z=(a@(V//2).T)*Q%2
print('rank X',rk(X),'rank I+X',rk((I+X)%2),'rank Y',rk(Y),'rank Z',rk(Z),'rank Q',rk(Q))
print('odd counts per row a',a.sum(0),'b',b.sum(0),'high w',(W//2).sum(0),'high v',(V//2).sum(0))
print('W values',np.unique(W,return_counts=True),'V',np.unique(V,return_counts=True))
E=json.load(open(D56+'e8base.json')); print(E.keys()); print(np.array(E['Gb']))
