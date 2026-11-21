import numpy as np, sympy, sys
from gmax import *
rng=np.random.default_rng(int(sys.argv[1]))
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
L=std_set('HS64'); Q=Q_std(L)
print('HS64-D8',gauge_max(gram_rows_std(L,F0.tolist()),Q),flush=True)
for trial in range(int(sys.argv[2])):
    kind=trial%3
    if kind==0: U=rand_unimod(8,rng)*F0
    elif kind==1: U=F0*rand_unimod(8,rng)
    else: U=rand_unimod(8,rng)*F0*rand_unimod(8,rng,6)
    rows=gram_rows_B(L,np.eye(8,dtype=int),U,8); assert check_decoder(rows,Q)==0
    print('HS64 kind',kind,gauge_max(rows,Q,300,trial),flush=True)
Lall=std_lines(); a0=Lall[0]; L7=std_set('E7s'); Q7=Q_std(L7)
cnt=0
while cnt<int(sys.argv[2]):
    idx=rng.choice(len(L7),7,replace=False); B=[list(map(int,L7[i])) for i in idx]+[list(map(int,a0))]
    Mx=sympy.Matrix(B)
    if Mx.det()==0: continue
    if rng.random()<0.5: Mx=rand_unimod(8,rng,6)*Mx
    rows=gram_rows_B(L7.tolist(),np.eye(8,dtype=int),Mx,8); assert check_decoder(rows,Q7)==0
    print('E7',gauge_max(rows,Q7,300,cnt),flush=True); cnt+=1
