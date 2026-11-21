"""regenerate scan decoders (same RNG stream) and pickle E7 ones flagged LOW-ALL: (seed, trial)."""
import numpy as np, sympy, sys, pickle
from ilib import *
def gen(seed,N):
    rng=np.random.default_rng(seed); out=[]
    F0=sympy.zeros(8,8)
    for t,i in enumerate(range(0,8,2)):
        for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
    LH=std_set('HS64'); Lall=std_lines(); a0=Lall[0]; L7=std_set('E7s')
    for trial in range(N):
        kind=trial%3
        for name in ('HS64','E7'):
            if name=='HS64': base=F0; L=LH
            else:
                L=L7
                while True:
                    idx=rng.choice(len(L7),7,replace=False); base=sympy.Matrix([list(map(int,L7[i])) for i in idx]+[list(map(int,a0))])
                    if base.det()!=0: break
            U=base if kind==0 else (base*rand_unimod(8,rng) if kind==1 else rand_unimod(8,rng)*base*rand_unimod(8,rng,6))
            rows=gram_rows_B(L.tolist() if name=='E7' else L,np.eye(8,dtype=int),U,8)
            out.append((name,trial,rows))
    return out
if __name__=='__main__':
    seed=int(sys.argv[1]); want=[int(x) for x in sys.argv[2].split(',')]
    for name,trial,rows in gen(seed,max(want)+1):
        if name=='E7' and trial in want: pickle.dump(rows,open('scanE7_%d_%d.pkl'%(seed,trial),'wb')); print('saved',seed,trial)
