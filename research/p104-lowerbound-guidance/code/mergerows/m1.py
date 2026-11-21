"""MERGEROWS m1: regenerate Delta's Gram data (U), refactor the six saturated rows by G in GL6, measure alpha+beta (gauge climb)."""
import sys, pickle, numpy as np, sympy
sys.path.insert(0,'../iso3')
from gmax import *
rng=np.random.default_rng(1)
F0=sympy.zeros(8,8)
for t,i in enumerate(range(0,8,2)):
    for s,sg in enumerate((1,-1)): F0[2*t+s,i]=2; F0[2*t+s,i+1]=2*sg
L=std_set('HS64'); Q=Q_std(L); n=len(Q)
for trial in range(2):
    kind=trial%3
    if kind==0: U=rand_unimod(8,rng)*F0
    elif kind==1: U=F0*rand_unimod(8,rng)
rows=gram_rows_B(L,np.eye(8,dtype=int),U,8)
ref=pickle.load(open('../iso3/hs_kind1.pkl','rb'))
assert all(r[0]==s[0] and r[1]==s[1] for r,s in zip(rows,ref)), 'regen mismatch'
pickle.dump(U,open('delta_U.pkl','wb'))
print('Delta U regenerated; C',gauge_max(rows,Q,10,0)['C'])
six=[0,1,4,5,6,7]
def refactor(U,G):
    H=sympy.eye(8)
    for a,i in enumerate(six):
        for b,j in enumerate(six): H[i,j]=G[a,b]
    return H*U
if __name__=='__main__':
    seed=int(sys.argv[1]); N=int(sys.argv[2]); r2=np.random.default_rng(seed)
    for tr in range(N):
        if tr%2==0: G=rand_unimod(6,r2,8)
        else:
            while True:
                G=sympy.Matrix(6,6,lambda i,j:int(r2.integers(-3,4)))
                if G.det()!=0: break
        U2=refactor(U,G); rows2=gram_rows_B(L,np.eye(8,dtype=int),U2,8); assert check_decoder(rows2,Q)==0
        g=max((gauge_max(rows2,Q,600,sd) for sd in range(2)),key=lambda d:d['gmax_sum'])
        print(tr,'C',g['C'],'nrows',len(rows2),'S1 canon',g['canon_sum'],'gmax',g['gmax'],g['gmax_sum'],flush=True)
