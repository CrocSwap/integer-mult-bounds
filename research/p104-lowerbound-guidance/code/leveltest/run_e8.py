import numpy as np,sys
from lt import *
rng=np.random.default_rng(0)
W=np.load('../orbitlp/e8W.npy')%4;V=np.load('../orbitlp/e8V.npy')%4
info=rows_info(Q104,W,V); print('rows (dim a, price):',info)
print('dim b:',[a-p for a,p in info])
print(evaluate(Q104,W,V,rng,nrand=20))
# which rows carry which levels
for l,R in enumerate(levels(info,9),1): print('level',l,'rows',R)
