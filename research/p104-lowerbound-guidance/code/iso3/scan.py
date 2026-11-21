"""ISO3 scan: random Gram-class decoders on HS64 / E7; S1 gauge-max (gmax) and S_l/T_l gauge climb (syl). Flags < threshold."""
import numpy as np, sympy, sys
from syl import climb
from gmax import gauge_max
from ilib import *
rng=np.random.default_rng(int(sys.argv[1])); N=int(sys.argv[2])
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
LH=std_set('HS64'); QH=Q_std(LH); Lall=std_lines(); a0=Lall[0]; L7=std_set('E7s'); Q7=Q_std(L7)
for trial in range(N):
    kind=trial%3
    for name,L,Q,thr in (('HS64',LH,QH,38),('E7',L7,Q7,41)):
        if name=='HS64': base=F0
        else:
            while True:
                idx=rng.choice(len(L7),7,replace=False); base=sympy.Matrix([list(map(int,L7[i])) for i in idx]+[list(map(int,a0))])
                if base.det()!=0: break
        U=base if kind==0 else (base*rand_unimod(8,rng) if kind==1 else rand_unimod(8,rng)*base*rand_unimod(8,rng,6))
        rows=gram_rows_B(L.tolist() if name=='E7' else L,np.eye(8,dtype=int),U,8); assert check_decoder(rows,Q)==0
        g=gauge_max(rows,Q,300,trial); c=climb(rows,Q,3,40,trial)
        ba=c['bestall']; idl=max(ba.values())
        flag=' LOW-S1' if g['gmax_sum']<thr else ''
        flag+=' LOW-ALL' if idl<thr else ''
        print(name,'kind',kind,'C',g['C'],'S1gmax',g['gmax_sum'],'e',g['e'],'climb',ba,'thr',thr,flag,flush=True)
