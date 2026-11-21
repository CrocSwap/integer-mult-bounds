# greedy shrink of a chain counterexample (diag-free): set scalars to +-1/0 while min mass stays > D. own code
import sys, itertools, random
from common import *
from netgen import net_M
from exact import min_mass
h=4; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
I={'A': [0, 1, 4, 5], 'B': [0, 5], 'A2': [0, 2, 5, 7], 'B2': [0, 7], 'F': [[1, 0, 3, 0, 0, 0, 0, 0], [0, -1, 0, 2, 0, 0, 0, 0]], 'G': [[0, 0], [2, 0], [0, 0], [3, 0], [3, 3], [0, 1], [3, 2], [0, 3]], 'H': [[0, 0], [-2, 0]]}
Qm=[[dot(s,t) for t in labs] for s in labs]; D=2
def fails(F,G,H):
    M,_=net_M(G,H,F); T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if all(T[t][p]==0 for t in range(n) for p in range(n) if t!=p): return False
    st,c,R,res=min_mass(h,labs,T,Qm,D,timeout=30,diagfree=True); return st=='NONE'
F=[r[:] for r in I['F']]; G=[r[:] for r in I['G']]; H=[r[:] for r in I['H']]
assert fails(F,G,H)
# 1) try making all nonzero scalars 1
F1=[[int(x!=0) for x in r] for r in F]; G1=[[int(x!=0) for x in r] for r in G]; H1=[[int(x!=0) for x in r] for r in H]
print('all-ones version fails:',fails(F1,G1,H1))
if fails(F1,G1,H1): F,G,H=F1,G1,H1
# 2) greedily zero entries
changed=True
while changed:
    changed=False
    for (Mx,i,j) in [('F',i,j) for i in range(2) for j in range(n)]+[('G',i,j) for i in range(n) for j in range(2)]:
        X={'F':F,'G':G}[Mx]
        if X[i][j]==0: continue
        old=X[i][j]; X[i][j]=0
        if fails(F,G,H): changed=True
        else: X[i][j]=old
print('F',F); print('G',G); print('H',H)
M,_=net_M(G,H,F); T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
for t in range(n):
    if any(T[t]): print(labs[t],T[t])
