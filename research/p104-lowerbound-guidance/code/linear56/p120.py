"""LINEAR56 p120.py: [C] port-general check on P120 (all 120 E8 root lines): liftable Kbar and tight vectors."""
import numpy as np, itertools
from lcore import *

LAB120=X120; n=120
Q120=np.array([[1 if s==t else (1+Bf(LAB120[s],LAB120[t]))%2 for t in range(n)] for s in range(n)])
cells=[(t,s) for t in range(n) for s in range(n) if Q120[t,s]]
A=np.array([np.outer(C120[t],C120[s]).ravel() for t,s in cells],dtype=np.int64)%4
r=np.array([2 if t==s else 0 for t,s in cells],dtype=np.int64)
K2=kernel(A); phis=[((A@k)%4)//2 for k in K2]
M=np.concatenate([np.array(phis).T,A%2],1); base=solve2(M,(r//2)%2); hom=kernel(M)
dirs=[(h[:len(K2)]@K2)%2 for h in hom]; nd=f2rank(np.array(dirs)) if dirs else 0
Kb0=(base[:len(K2)]@K2)%2
print('P120: mod2 kernel dim',len(K2),'| liftable Kbar affine dim',nd,'| Kbar==B',(Kb0.reshape(8,8)==Bm).all())
allx=np.array(list(itertools.product(range(4),repeat=8)),dtype=np.int64)
vals=(C120@allx.T)%4; tight=(~(vals==2).any(0))&((allx%2).any(1)); print('P120 tight vectors',tight.sum())
