"""TAU48 canon.py: canonical function spaces on P104 (restricted polynomial codes R(d) in the 9 label coords) and their pairing ranks."""
import sys,numpy as np, itertools
from gibbs import *
def span_rank(rows): return f2rank([toint(r) for r in np.array(rows)%2])
cols=[Lab[:,i] for i in range(9)]
R={0:[np.ones(n,int)]}
R[1]=R[0]+cols
R[2]=R[1]+[cols[i]*cols[j] for i,j in itertools.combinations(range(9),2)]
R[3]=R[2]+[cols[i]*cols[j]*cols[k] for i,j,k in itertools.combinations(range(9),3)]
R[4]=R[3]+[cols[i]*cols[j]*cols[k]*cols[l] for i,j,k,l in itertools.combinations(range(9),4)]
def basis(rows):
    b=f2basis([toint(r) for r in rows]); return np.array([[ (x>>(n-1-s))&1 for s in range(n)] for x in b])
def perp(Bm):
    from e8xy_lib import nullsp
    return nullsp(Bm,range(n),n)
for d in range(5):
    B=basis(R[d]); P=perp(B); 
    print('R(%d) dim'%d,len(B),'perp dim',len(P),'rank pairing on perp',rk(P@P.T),'rank pairing on R',rk(B@B.T))
