import numpy as np, sympy, sys, collections, pickle
from gmax import *
rng=np.random.default_rng(int(sys.argv[1]))
Lall=std_lines(); a0=Lall[0]; L7=std_set('E7s'); Q7=Q_std(L7)
# E7 'frame' decoders: rows = a basis F of the E7 root lattice (+a0) times unimodular on the right (kind1 analog)
res=[]
for trial in range(int(sys.argv[2])):
    while True:
        idx=rng.choice(len(L7),7,replace=False); B=sympy.Matrix([list(map(int,L7[i])) for i in idx]+[list(map(int,a0))])
        if B.det()!=0: break
    kind=trial%3
    if kind==0: U=B
    elif kind==1: U=B*rand_unimod(8,rng)
    else: U=rand_unimod(8,rng)*B*rand_unimod(8,rng,6)
    rows=gram_rows_B(L7.tolist(),np.eye(8,dtype=int),U,8); assert check_decoder(rows,Q7)==0
    g=gauge_max(rows,Q7,300,trial)
    print('E7 kind',kind,g,flush=True); res.append((g['gmax_sum'],kind,g['C']))
    if g['gmax_sum']<41: pickle.dump(rows,open('e7_low_%d_%d.pkl'%(int(sys.argv[1]),trial),'wb'))
print(sorted(res)[:5])
