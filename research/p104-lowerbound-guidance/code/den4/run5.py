import numpy as np, sympy
from qlib import *; from carrypoly import analyse; from gauge import climb
Lall=std_lines(); a0=Lall[0]; L=std_set('E7s'); Q=Q_std(L); rng=np.random.default_rng(3); done=set()
for trial in range(400):
    idx=rng.choice(len(L),7,replace=False); B=[list(map(int,L[i])) for i in idx]+[list(map(int,a0))]
    Mx=sympy.Matrix(B)
    if Mx.det()==0: continue
    rows=gram_rows_B(L.tolist(),np.eye(8,dtype=int),Mx,8); e,W,V,pr,D,S=normalise(rows,Q)
    if e in done: continue
    done.add(e); print('E7 e',e,'C',sum(pr),'toeplitz canonical/gauge-max',climb(e,W,V,pr,Q,'toeplitz',120,0),flush=True)
    if len(done)==2: break
