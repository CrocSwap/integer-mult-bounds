"""DEN4 run2: forced quarter bounds on random Gram-class decoders (HS64, E7s, P120s std coords; P104 root coords) + controls."""
import numpy as np, sympy, sys
from qlib import *; from carrypoly import analyse; from quarter import quarter; from gauge import climb
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
sets={'HS64':std_set('HS64'),'E7s':std_set('E7s'),'P120s':std_set('P120s')}
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)):
        F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
out=[]
for name,L in sets.items():
    Q=Q_std(L)
    for trial in range(int(sys.argv[2]) if len(sys.argv)>2 else 3):
        kind=trial%3
        if kind==0: U=rand_unimod(8,rng)*F0
        elif kind==1: U=F0*rand_unimod(8,rng)
        else: U=rand_unimod(8,rng)*F0*rand_unimod(8,rng,6)
        rows=gram_rows_B(L,np.eye(8,dtype=int),U,8)
        assert check_decoder(rows,Q)==0
        e,W,V,pr,D,S=normalise(rows,Q)
        if e<1: continue
        r=analyse(e,W,V,pr,Q,name,verbose=False)
        g=climb(e,W,V,pr,Q,'toeplitz',40,1)
        line=dict(set=name,kind=kind,n=len(L),e=e,C=r['C'],toep=r['toeplitz'],toep_gauge=g[1],poly=r['polyrank'])
        if e==2: line['master']=quarter(e,W,V,pr,Q,verbose=False)['master']
        print(line,flush=True); out.append(line)
