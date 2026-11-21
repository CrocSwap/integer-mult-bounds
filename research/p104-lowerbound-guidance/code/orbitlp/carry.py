"""ORBITLP carry.py: carry identity pieces on E8-56: I = X + Y + Z over F2 (Y=sum diag(w')Qdiag(b), Z=sum diag(a)Qdiag(v'))."""
import numpy as np
from geo import *
def rk2(M):
    M=np.array(M)%2; rows=[int(''.join(map(str,r)),2) for r in M]
    piv={};r=0
    for x in rows:
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x;r+=1;break
    return r
W=np.load('e8W.npy'); V=np.load('e8V.npy'); m=W.shape[1]
a=W%2; w2=(W//2)%2; b=V%2; v2=(V//2)%2
Ak=[np.outer(a[:,k],b[:,k])*Q for k in range(m)]
cnt=sum(Ak)
X=((cnt//2)%2)*Q
Y=sum(np.outer(w2[:,k],b[:,k])*Q for k in range(m))%2
Z=sum(np.outer(a[:,k],v2[:,k])*Q for k in range(m))%2
I=np.eye(104,dtype=int)
print('mod2 law ok', ((cnt%2)*Q).sum()==0)
print('identity I=X+Y+Z on odd cells:', (((I+X+Y+Z)%2)*Q).sum()==0)
print('rank X',rk2(X),'rank Y',rk2(Y),'rank Z',rk2(Z),'rank Y+Z',rk2(Y+Z),'rank I+X',rk2(I+X))
print('Y==Z^T?', ((Y+Z.T)%2).sum()==0)
print('w2 nonzero',w2.sum(),'v2 nonzero',v2.sum())
Yk=[np.outer(w2[:,k],b[:,k])*Q%2 for k in range(m)]; Zk=[np.outer(a[:,k],v2[:,k])*Q%2 for k in range(m)]
print('rank Y_k',[rk2(y) for y in Yk]); print('rank Z_k',[rk2(z) for z in Zk]); print('rank B_k',[rk2(y+z) for y,z in zip(Yk,Zk)])
print('|w2_k|',w2.sum(0),'|v2_k|',v2.sum(0))
# partial sums
print('rank cumulative Y', [rk2(sum(Yk[:j+1])) for j in range(m)])
print('rank Q_bar (Q over F2)', rk2(Q))
