import numpy as np, sympy, sys
from syl import *
rng=np.random.default_rng(1)
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
L=std_set('HS64'); Q=Q_std(L)
r=climb(gram_rows_std(L,F0.tolist()),Q,3,int(sys.argv[1]),0); print('HS64-D8',r,flush=True)
for trial in range(6):
    kind=trial%3
    if kind==0: U=rand_unimod(8,rng)*F0
    elif kind==1: U=F0*rand_unimod(8,rng)
    else: U=rand_unimod(8,rng)*F0*rand_unimod(8,rng,6)
    rows=gram_rows_B(L,np.eye(8,dtype=int),U,8)
    print('HS64 kind',kind,climb(rows,Q,4,int(sys.argv[1]),trial),flush=True)
