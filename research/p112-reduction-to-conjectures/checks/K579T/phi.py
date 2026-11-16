from base import *
from collections import Counter
MX=np.load('masks.npy')
ch=chain('A8'); X=xvals(ch)
maj=[];r=[];c=[]
for t in range(120):
  cc=Counter(X[t]).most_common(); maj.append(cc[0][1]); r.append(cc[1][1]); c.append(8-cc[0][1])
maj=np.array(maj);r=np.array(r);c=np.array(c)
w=r/maj
for a in range(2):
  inmaj=np.array([Counter(X[t]).most_common(1)[0][0]==X[t,a] for t in range(120)])
  delta=(~inmaj[None,:]&~MX).sum(1); eps=(inmaj[None,:]&MX).sum(1); epsw=(MX*(inmaj*w)[None,:]).sum(1)
  for lam in (0,0.2,0.4,0.6,0.8):
    v=(1-lam)*delta+lam*eps-epsw
    print(a,lam,'min',round(v.min(),3),'x8',round(8*v.min(),2))
a=0
inmaj=np.array([Counter(X[t]).most_common(1)[0][0]==X[t,a] for t in range(120)])
delta=(~inmaj[None,:]&~MX).sum(1); epsw=(MX*(inmaj*w)[None,:]).sum(1); v=delta-epsw
for th in (10,12,14,16,18,20,22): print('v<=',th,(v<=th+1e-9).sum())
print('delta dist of v<=22',Counter(delta[v<=22+1e-9]))
