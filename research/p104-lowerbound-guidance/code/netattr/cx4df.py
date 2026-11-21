# NETATTR diag-free minimal counterexample (h=4, 0/1 network, 2 nodes, 1 relay, D=2). brute-force covers over ALL port subsets.
import itertools
from common import *
from netgen import net_M
h=4; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs); L={x:i for i,x in enumerate(labs)}
A,B,A2,B2=span([1,4]),span([5]),span([2,5]),span([7])
F=[[0]*n for _ in range(2)]; G=[[0]*2 for _ in range(n)]
F[0][L[1]]=F[0][L[4]]=1; F[1][L[2]]=1; G[L[7]][0]=1; G[L[11]][1]=G[L[14]][1]=1; H=[[0,0],[1,0]]
assert B<=A and B2<=A2 and B<=A2
for k,(a,b) in enumerate([(A,B),(A2,B2)]):
    for p in range(n):
        if F[k][p]: assert labs[p] in a
        if G[p][k]: assert all(dot(labs[p],y)==0 for y in b)
D=dimof(A)-dimof(B)+dimof(A2)-dimof(B2); print('D',D,'e',dimof(A2)-dimof(B),'xf',dimof(A)-dimof(A&A2),'xb',dimof(span(list(B)+list(B2)))-dimof(B2))
Qm=[[dot(s,t) for t in labs] for s in labs]; M,_=net_M(G,H,F)
odd=[(t,p) for t in range(n) for p in range(n) if Qm[t][p] and t!=p]
T={c:M[c[0]][c[1]] for c in odd}; nz=[c for c in odd if T[c]]
print('nonzero off-diag odd cells',[(labs[t],labs[p],T[(t,p)]) for t,p in nz])
print('zero off-diag odd cells inside readers{7,11,14}x gathers{1,2,4}:',[(labs[t],labs[p]) for t,p in odd if not T[(t,p)] and labs[t] in (7,11,14) and labs[p] in (1,2,4)])
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
z=(L[7],L[2])
print('rects',len(rects),'minimal covers',len(found))
print('every cover: 2 rows of price 1, BOTH containing the zero cell (7,2), each row containing a 3-cell path forcing value 1 there:')
ok=True
for f in found:
    rs=[rects[i] for i in f]
    both=all(z[0] in r[0] and z[1] in r[1] for r in rs)
    # forced value: each row contains an "L" (t,p),(t,p'),(t',p') with t=7? check rank-1 forcing: row contains (7,p),(t',p),(t',2) all nonzero-target cells covered only by it
    ok&= (len(rs)==2 and both)
print('claim holds:',ok)
for f in sorted(found)[:10]: print('  ',[(sorted(labs[t] for t in rects[i][0]),sorted(labs[p] for p in rects[i][1]),rects[i][2]) for i in f])
