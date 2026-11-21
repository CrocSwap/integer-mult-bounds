import numpy as np, sympy
from ilib import *
sys.path.insert(0,'<local-clone>/cards/WILD/NOVEL/den4')
from carrypoly import analyse
L=std_set('HS64'); Q=Q_std(L)
U=[[0]*8 for _ in range(8)]
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)):
        U[2*t+s][i]=2; U[2*t+s][i+1]=2*sg
rows=gram_rows_std(L,U); e,W,V,pr,D,S=normalise(rows,Q)
print('HS64-D8',e,iso(e,W,V,pr,Q,D,S))
# E7 basis decoders
Lall=std_lines(); a0=Lall[0]; L7=std_set('E7s'); Q7=Q_std(L7); rng=np.random.default_rng(3); seen=set()
for trial in range(400):
    idx=rng.choice(len(L7),7,replace=False); B=[list(map(int,L7[i])) for i in idx]+[list(map(int,a0))]
    Mx=sympy.Matrix(B)
    if Mx.det()==0: continue
    rows=gram_rows_B(L7.tolist(),np.eye(8,dtype=int),Mx,8); e,W,V,pr,D,S=normalise(rows,Q7)
    if (e,sum(pr)) in seen: continue
    seen.add((e,sum(pr))); print('E7',e,iso(e,W,V,pr,Q7,D,S),flush=True)
    if len(seen)>=6: break
