# NETATTR minimal chain counterexample (h=4, 2 nodes, 1 relay, D=3): exact checks
from common import *
from netgen import net_M
from exact import min_mass
h=4; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
I={'A': [0, 7, 10, 13], 'B': [0, 10], 'A2': [0, 4, 10, 14], 'B2': [0], 'F': [[0, 0, 0, -1, 0, 0, 2, 0], [0, 0, -2, 0, 0, 0, 0, 2]], 'G': [[1, 3], [0, -2], [-1, 1], [0, 2], [0, -1], [3, 0], [0, 0], [-1, 2]], 'H': [[0, 0], [3, 0]]}
F,G,H=I['F'],I['G'],I['H']
A,B,A2,B2=map(frozenset,(I['A'],I['B'],I['A2'],I['B2']))
# legality
assert B<=A and B2<=A2 and B<=A2
for k,(a,b) in enumerate([(A,B),(A2,B2)]):
    for p in range(n):
        if F[k][p]: assert labs[p] in a
        if G[p][k]: assert all(dot(labs[p],y)==0 for y in b)
Qm=[[dot(s,t) for t in labs] for s in labs]
M,_=net_M(G,H,F)
T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
print('labels',labs); print('T = M o Q:')
for t in range(n): print(labs[t],T[t])
for B_ in (3,4):
    st,c,R,res=min_mass(h,labs,T,Qm,B_,timeout=120)
    print('budget',B_,st,'covers',len(res),[ (sorted(labs[t] for t in R[i][0]),sorted(labs[p] for p in R[i][1]),R[i][2]) for i in (c or [])])
    for cc,r in res: print('   cover',[ (sorted(labs[t] for t in R[i][0]),sorted(labs[p] for p in R[i][1]),R[i][2]) for i in cc],r)
