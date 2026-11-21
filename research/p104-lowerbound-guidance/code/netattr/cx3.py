# NETATTR MINIMAL counterexample: h=3, n=4 ports, 2 nodes, 1 relay, D=2; min decoder mass of T=M o Q is > 2.
import itertools
from common import *
from netgen import net_M
from exact import min_mass
h=3; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
I={'A': [0, 1, 4, 5], 'B': [0, 5], 'A2': [0, 2, 5, 7], 'B2': [0, 2], 'F': [[2, 0, 2, 0], [0, -1, 0, 2]], 'G': [[0, 3], [-2, 0], [0, 3], [1, 0]], 'H': [[0, 0], [-2, 0]]}
F,G,H=I['F'],I['G'],I['H']; A,B,A2,B2=map(frozenset,(I['A'],I['B'],I['A2'],I['B2']))
assert B<=A and B2<=A2 and B<=A2 and A==span(A) and B==span(B) and A2==span(A2) and B2==span(B2)
for k,(a,b) in enumerate([(A,B),(A2,B2)]):
    for p in range(n):
        if F[k][p]: assert labs[p] in a
        if G[p][k]: assert all(dot(labs[p],y)==0 for y in b)
D=(dimof(A)-dimof(B))+(dimof(A2)-dimof(B2))
Qm=[[dot(s,t) for t in labs] for s in labs]
M,_=net_M(G,H,F); T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
print('labels',labs,'D',D); print('Q'); [print(r) for r in Qm]; print('M'); [print(r) for r in M]; print('T=M o Q'); [print(r) for r in T]
odd=[(t,p) for t in range(n) for p in range(n) if Qm[t][p]]; nz=[c for c in odd if T[c[0]][c[1]]]
# brute force: all rectangles (any subsets of all ports), price<=D, all covers of nz
rects=[]
for r1 in range(1,n+1):
  for Ds in itertools.combinations(range(n),r1):
    for r2 in range(1,n+1):
      for Ss in itertools.combinations(range(n),r2):
        pr=price([labs[t] for t in Ds],[labs[p] for p in Ss])
        if 1<=pr<=D: rects.append((frozenset(Ds),frozenset(Ss),pr))
cells=frozenset(nz); cv=[frozenset(c for c in cells if c[0] in R[0] and c[1] in R[1]) for R in rects]
found=set()
def rec(ch,cov,bud):
    if cov==cells: found.add(tuple(sorted(ch))); return
    c=min(cells-cov)
    for i in range(len(rects)):
        if rects[i][2]<=bud and c in cv[i]: rec(ch+[i],cov|cv[i],bud-rects[i][2])
rec([],frozenset(),D)
print('rects',len(rects),'minimal covers (sum price<=D):',len(found))
for f in sorted(found): print('  ',[(sorted(labs[t] for t in rects[i][0]),sorted(labs[p] for p in rects[i][1]),rects[i][2]) for i in f])
for Bud in (D,D+1):
    st,c,R,res=min_mass(h,labs,T,Qm,Bud,timeout=60); print('exact solver budget',Bud,st,[r for _,r in res])
