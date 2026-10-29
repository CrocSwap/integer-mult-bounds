from base import *
from collections import Counter
for cls in ('A8','E7'):
  ch=chain(cls); X=xvals(ch)
  cnt=Counter(); tot=0
  for t in range(120):
    lv=sorted(Counter(X[t]).values(),reverse=True); cnt[tuple(lv)]+=1; tot+=8-lv[0]
  print(cls,dict(cnt),'sum c_t',tot)
