import numpy as np, sympy, sys
from syl import *
rng=np.random.default_rng(1)
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
L=std_set('HS64'); Q=Q_std(L)
for trial in range(2):
    kind=trial%3
    if kind==0: U=rand_unimod(8,rng)*F0
    elif kind==1: U=F0*rand_unimod(8,rng)
rows=gram_rows_B(L,np.eye(8,dtype=int),U,8)
VW,VU=vals(rows,len(Q))
import collections
for k in range(len(rows)):
    print(k,'VW',collections.Counter(VW[:,k].tolist()),'VU',collections.Counter(VU[:,k].tolist()),'prod',collections.Counter((VW[:,k]+VU[:,k]).tolist()))
import pickle; pickle.dump(rows,open('hs_kind1.pkl','wb'))
