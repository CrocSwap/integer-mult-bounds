import sys, itertools, numpy as np
sys.path.insert(0,'/Users/joelpulikkan/imb-main/research/format-limits/scripts')
from e8units import standard_e8
import networkx as nx
L,G=standard_e8()   # doubled coords, norm 8
roots=np.vstack([L,-L])
J=np.zeros((8,8),int)
for a in range(4):
    J[2*a+1,2*a]=1; J[2*a,2*a+1]=-1   # J e_{2a}=e_{2a+1}, J e_{2a+1}=-e_{2a}
assert (J@J==-np.eye(8)).all()
S=set(map(tuple,roots))
assert all(tuple(J@r) in S for r in roots)
# complex lines: orbits under <J>
seen=set(); lines=[]
for r in roots:
    t=tuple(r)
    if t in seen: continue
    orb=[r, J@r, -r, -(J@r)]
    for o in orb: seen.add(tuple(o))
    lines.append(r)
lines=np.array(lines); v=len(lines); print('complex lines',v)
# Hermitian non-orth: <r,s>!=0 or <r,Js>!=0
R=lines@lines.T; I=lines@(J@lines.T)
nonorth=(R!=0)|(I!=0)
np.fill_diagonal(nonorth,False)
print('deg nonorth',set(nonorth.sum(1)))
g=nx.Graph(); g.add_nodes_from(range(v))
for i in range(v):
    for j in range(i+1,v):
        if nonorth[i,j]: g.add_edge(i,j)
w=max(len(c) for c in nx.find_cliques(g))
print('clique number of nonorth graph',w)
from minrank_sat import solve_minrank
K=max(nx.find_cliques(g),key=len)
pairs=[(i,j) for i in range(v) for j in range(i+1,v) if nonorth[i,j]]
for c in range(12,17):
    for sym in (True,False):
        r=solve_minrank(v,pairs,c,sym,K if len(K)==c else None)
        print('c',c,'sym',sym,r,flush=True)
        if r[0]=='SAT': break
