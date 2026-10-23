from base import *
from collections import Counter
import time
t0=time.time(); MX=masks(); print('masks',len(MX),'sizes',Counter(MX.sum(1)),time.time()-t0)
np.save('masks.npy',MX)
for cls in ('A8','E7'):
  ch=chain(cls); X=xvals(ch)
  for a in range(8):
    Ma=np.zeros(120,bool)
    for t in range(120):
      c=Counter(X[t]); lv,n=c.most_common(1)[0]
      if n>=5 and X[t,a]!=lv: Ma[t]=True
    d=(Ma[None,:]&~MX).sum(1)
    print(cls,a,'|M_a|',Ma.sum(),'min deficit',d.min(),'#masks at min',(d==d.min()).sum())
