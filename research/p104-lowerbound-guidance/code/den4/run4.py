"""DEN4 run4: E7 (63 lines orth to a0, std coords) decoders from random 7-line bases of a0^perp + a0; report e, C, forced bounds."""
import numpy as np, sympy
from qlib import *; from carrypoly import analyse; from quarter import quarter; from gauge import climb
Lall=std_lines(); a0=Lall[0]; L=std_set('E7s'); Q=Q_std(L); rng=np.random.default_rng(3); seen=set()
for trial in range(400):
    idx=rng.choice(len(L),7,replace=False); B=[list(map(int,L[i])) for i in idx]+[list(map(int,a0))]
    Mx=sympy.Matrix(B)
    if Mx.det()==0: continue
    rows=gram_rows_B(L.tolist(),np.eye(8,dtype=int),Mx,8)
    assert check_decoder(rows,Q)==0
    e,W,V,pr,D,S=normalise(rows,Q)
    key=(e,sum(pr))
    if key in seen: continue
    seen.add(key)
    r=analyse(e,W,V,pr,Q,'E7',verbose=False)
    line=dict(e=e,C=r['C'],rows=len(pr),toep=r['toeplitz'],poly=r['polyrank'],det=abs(Mx.det()))
    if e==2: line['master']=quarter(e,W,V,pr,Q,verbose=False)['master']
    print(line,flush=True)
    if len(seen)>=8: break
