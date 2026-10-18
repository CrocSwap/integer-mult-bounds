# s56 with deleted rows / columns (exceptional lines): env DR="i,j" rows deleted, DC="..." columns deleted (indices into S, 0..55)
import sys, itertools, os
from blib import *
f1=0
S=[u for u in sorted(UNITS['E8']) if G[u][f1]!=0 and u!=f1]; n=len(S)
DR=set(int(x) for x in os.environ.get('DR','').split(',') if x); DC=set(int(x) for x in os.environ.get('DC','').split(',') if x)
rows=[i for i in range(n) if i not in DR]; cols=[j for j in range(n) if j not in DC]
Gam=[[j for j in range(n) if S[j] in O[S[i]]] for i in range(n)]   # symmetric orthogonality
nv=[0]; cl=[]
def new(): nv[0]+=1; return nv[0]
def eqvars(idx):
    V={}
    for i,j in itertools.combinations(idx,2): V[(i,j)]=V[(j,i)]=new()
    for i,j,k in itertools.combinations(idx,3):
        a,b,c=V[(i,j)],V[(j,k)],V[(i,k)]
        cl.extend([[-a,-b,c],[-a,-c,b],[-b,-c,a]])
    return V
Fp=eqvars(rows); El=eqvars(cols)
# points = rows, lines = columns; incident when orthogonal
Gr={i:[j for j in Gam[i] if j in cols] for i in rows}      # columns adjacent to row i
Gc={j:[i for i in Gam[j] if i in rows] for j in cols}      # rows adjacent to column j
for i,j in itertools.combinations(rows,2):
    com=sorted(set(Gr[i])&set(Gr[j]))
    for s,t in itertools.combinations(com,2): cl.append([Fp[(i,j)],El[(s,t)]])
for s,t in itertools.combinations(cols,2):
    com=sorted(set(Gc[s])&set(Gc[t]))
    for i,j in itertools.combinations(com,2): cl.append([El[(s,t)],Fp[(i,j)]])
# negated conclusion: no point class meets Gamma(s) for every column s ; no line class meets Gamma(u) for every row u
for i in rows:
    opts=[]
    for s in cols:
        if i in Gc[s]: continue
        w=new(); opts.append(w)
        for u in Gc[s]: cl.append([-w,-Fp[(i,u)]])
    cl.append(opts)
for j in cols:
    opts=[]
    for u in rows:
        if j in Gr[u]: continue
        w=new(); opts.append(w)
        for s in Gr[u]: cl.append([-w,-El[(j,s)]])
    cl.append(opts)
with open(sys.argv[1],'w') as fh:
    fh.write(f'p cnf {nv[0]} {len(cl)}\n')
    for c in cl: fh.write(' '.join(map(str,c))+' 0\n')
print(nv[0],len(cl))
