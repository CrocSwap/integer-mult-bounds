# (S3') for E8: f fixed; u,u' in Nbar(f), u' not in {u, antipode(u)}: r(O_f ∩ O_u ∩ O_u') spans <f,u,u'>^perp (dim 5).
# (W2) max number of directions w_u = proj_{f^perp} r_u (u in Nbar(f)) in a 2-plane.
import sys, os as _o; sys.path.insert(0,_o.path.dirname(_o.path.abspath(__file__)))
from e8lib import *
from fractions import Fraction as Fr
import sympy, itertools
def rank(rows):
    return sympy.Matrix(rows).rank() if rows else 0
f=0; S=[u for u in range(N) if G[u][f]!=0 and u!=f]
bad=0; cnt=0
for u,v in itertools.combinations(S,2):
    if G[u][v]!=0 and abs(G[u][v])!=0:
        # antipode test: f,u,v span 2 dims
        if rank([E[f],E[u],E[v]])==2: continue
    com=[s for s in O[f] if s in O[u] and s in O[v]]
    cnt+=1
    if rank([E[s] for s in com])!=5: bad+=1
print('S3prime pairs',cnt,'bad',bad)
W=[[Fr(x)-Fr(dot(E[u],E[f]),dot(E[f],E[f]))*Fr(y) for x,y in zip(E[u],E[f])] for u in S]
dirs=[]
for w in W:
    if not any(rank([w,d])==1 for d in dirs): dirs.append(w)
print('directions',len(dirs))
mx=0
for a,b in itertools.combinations(range(len(dirs)),2):
    c=sum(1 for d in dirs if rank([dirs[a],dirs[b],d])==2)
    mx=max(mx,c)
print('max directions in a 2-plane',mx)
assert bad==0 and len(dirs)==28 and mx==2
print('PASS spans3: (S3prime) over %d pairs and (W2): 28 directions, no 3 in a 2-plane'%cnt)
