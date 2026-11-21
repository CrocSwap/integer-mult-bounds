import numpy as np, sympy
from qlib import *; from deep import deepcheck
rng=np.random.default_rng(11)
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
for name in ('HS64','E7s','P120s'):
    L=std_set(name); Q=Q_std(L)
    for trial in range(4):
        U=rand_unimod(8,rng)*F0*sympy.diag(*[2 if i<trial else 1 for i in range(8)])*rand_unimod(8,rng,6)
        rows=gram_rows_B(L.tolist(),np.eye(8,dtype=int),U,8); e,W,V,pr,D,S=normalise(rows,Q)
        if e>=1: deepcheck(e,W,V,pr,Q,name)
