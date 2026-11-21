"""MERGEROWS m3: hunt a RIGID counter-decoder: Gram-class decoder with no cost-safe transvection (any coefficient
pattern is tested with c=1 and c=2; safety depends on supports only, generic c) and gauge-max alpha+beta < threshold."""
import sys, pickle, numpy as np, sympy
from fractions import Fraction as Fr
from m2 import *
setn=sys.argv[1]; thr=int(sys.argv[2]); seed=int(sys.argv[3]); N=int(sys.argv[4])
L=std_set(setn); Q=Q_std(L); n=len(Q); rng=np.random.default_rng(seed)
Lall=std_lines()
if setn=='HS64':
    F0=sympy.zeros(8,8)
    for t,i in enumerate(range(0,8,2)):
        for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
else:
    a0=Lall[0]; fr=[a0]
    for l in Lall:
        if all(int(l.dot(f))==0 for f in fr): fr.append(l)
        if len(fr)==8: break
    F0=sympy.Matrix([list(map(int,f)) for f in fr])
def randrootbasis():
    while True:
        idx=rng.choice(len(Lall),8,replace=False); B=sympy.Matrix([list(map(int,Lall[i])) for i in idx])
        if B.det()!=0: return B
stats=[]
for tr in range(N):
    kind=tr%4 if len(sys.argv)<6 else int(sys.argv[5][tr%len(sys.argv[5])])
    if kind==0: U=F0*rand_unimod(8,rng,int(rng.integers(1,6)))
    elif kind==1: U=rand_unimod(8,rng,int(rng.integers(1,6)))*F0
    elif kind==2: U=randrootbasis()
    else: U=rand_unimod(8,rng,int(rng.integers(1,4)))*randrootbasis()
    rows=gram_rows_B(L,np.eye(8,dtype=int),U,8)
    if check_decoder(rows,Q)!=0: continue
    pr=prices(rows,Q); sp=rigid(rows,Q)
    g=gauge_max(rows,Q,300,tr)['gmax_sum']
    stats.append((g,len(sp),sum(pr)))
    flag=' <-- RIGID LOW' if (g<thr and not sp) else (' low' if g<thr else '')
    print(tr,'kind',kind,'C',sum(pr),'prices',pr,'safe',len(sp),'S1',g,flag,flush=True)
    if g<thr: pickle.dump(rows,open('m3_%s_%d_%d.pkl'%(setn,seed,tr),'wb'))
