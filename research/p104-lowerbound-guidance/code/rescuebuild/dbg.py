import sys;sys.path.insert(0,'.')
from rb6 import *
k=4;F=frozenset
O=options(k)
want=[(F(range(4)),(),F(range(4)))]*2+[(F(p),(F(p),),F()) for p in [(0,1),(0,2),(1,3),(2,3)]]
idx=[O.index(w) for w in want];print(idx)
for drop in [None,'cross','pfix','rescue','adj']:
    m,c,O2,val=build(k,bar=Dm('124'),cellrank=False)
    for i in range(len(O)):m.Add(c[i]==sum(1 for j in idx if j==i))
    sv=cp_model.CpSolver();sv.parameters.num_workers=1;print(sv.StatusName(sv.Solve(m)));break
print(float(sum(val[i] for i in idx)*104/k))
