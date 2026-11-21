# UNIFY: verify the ZIGZAG counterexample from zz5_0.5.log #7 (h=5, D=4, e=1): legality, level sum, own-price, mass at budgets 5 and 6.
import sys; sys.path.insert(0,'../netattr')
from common import *
from netgen import net_M
from exact import min_mass
from zz_level import levelsum
h=5; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
I={'A': [0, 3, 5, 6, 8, 11, 13, 14, 16, 19, 21, 22, 24, 27, 29, 30], 'B': [0, 13, 21, 24], 'A2': [0, 7, 10, 13, 18, 21, 24, 31], 'B2': [0, 18], 'F': [[0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]], 'G': [[0, 1], [0, 0], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 1], [0, 0], [0, 1], [1, 0], [0, 1], [1, 0], [0, 1]]}
A,B,A2,B2=(frozenset(I[k]) for k in ('A','B','A2','B2')); F,G=I['F'],I['G']; H=[[0,0],[1,0]]
nodes=[(A,B),(A2,B2)]
assert B<=A and B2<=A2 and B<=A2
for k,(a,b) in enumerate(nodes):
    for p in range(n):
        if F[k][p]: assert labs[p] in a
        if G[p][k]: assert all(dot(labs[p],y)==0 for y in b)
D=sum(dimof(a)-dimof(b) for a,b in nodes); e=dimof(A2)-dimof(B)
M,N=net_M(G,H,F); Qm=[[dot(s,t) for t in labs] for s in labs]
T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
own=sum(price([labs[t] for t in range(n) if G[t][k]],[labs[p] for p in range(n) if F[k][p]]) for k in range(2))
print('legal; D',D,'e',e,'level sum',levelsum(h,nodes,F,G,N),'own-price',own)
print('gathers j',[labs[p] for p in range(n) if F[0][p]],'k',[labs[p] for p in range(n) if F[1][p]],'deposits j',[labs[t] for t in range(n) if G[t][0]],'k',[labs[t] for t in range(n) if G[t][1]])
print('nonzero off-diag odd cells',sum(1 for t in range(n) for p in range(n) if t!=p and T[t][p]))
for Bud in (5,6):
    st,c,R,res=min_mass(h,labs,T,Qm,Bud,timeout=900,diagfree=True)
    print('budget',Bud,st,'covers',len(res),'prices',[R[i][2] for i in c] if c else None,flush=True)
