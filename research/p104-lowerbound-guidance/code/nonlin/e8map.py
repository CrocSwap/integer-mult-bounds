from ncore import *
import pickle
W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4
print(W.shape,V.shape)
Vz=(C@G@Z.T)%4   # 104 x 16 tight columns
FE=np.load('zfeas.npy')
rows={}
for k in range(V.shape[1]):
    for z in range(16):
        if ((V[:,k]-Vz[:,z])%4==0).all(): rows[k]=(z,1)
        if ((V[:,k]+Vz[:,z])%4==0).all(): rows[k]=(z,-1)
print('E8 V columns -> Z16:',rows)
Kt=[sum(1<<rows[k][0] for k in range(8) if W[t,k]%4) for t in range(n)]
print('all ports feasible:',all(FE[t,Kt[t]] for t in range(n)))
from zsub import pr
tot=0
for k in range(8):
    D=tuple(np.nonzero(W[:,k])[0]); tot+=pr(rows[k][0],D)
print('cost',tot)
pickle.dump(Kt,open('e8_Kt.pkl','wb'))
