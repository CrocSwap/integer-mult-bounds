"""rb11: sanity - every built frame (C1, c33) must pass all rb6 laws (incl. CELLRANK)."""
import sys;sys.path.insert(0,'.')
from rb6 import *
from rb9 import C33
from rb1 import C1
def check(k,R,mainsfn=None):
    O=options(k);m,c,O2,val=build(k,bar=Dm(0),cellrank=True)
    cnt={}
    for M,P in R:
        U=frozenset().union(*P) if P else frozenset()
        o=(M,tuple(sorted(P,key=sorted)),M-U);j=O.index(o);cnt[j]=cnt.get(j,0)+1
    for i in range(len(O)):m.Add(c[i]==cnt.get(i,0))
    sv=cp_model.CpSolver();sv.parameters.num_workers=1;return sv.StatusName(sv.Solve(m))
print('C1',check(3,C1));print('c33',check(6,C33))
