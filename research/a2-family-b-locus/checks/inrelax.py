# Class-level relaxation for INSIDE decoders of G on L\X (rows and columns of X deleted), m'' terms, each deficient direction at most once per side (non-parallel normals after merging).
import os,sys
from a2lib import *
import networkx as nx
Xt=list(X); off=[u for u in range(v) if u not in Xt]
# deficient classes of the punctured Gram (rows = columns by symmetry): classes O with rank r(O \ X) <= 7
defc=[]
for co,w in cls.items():
    Oc=[u for u in bits(w) if u not in Xt]
    ns=nullspace([R[u] for u in Oc],8)
    if ns: defc.append((co,len(ns)))
print(UNIT,'deficient classes of G on L\\X:',len(defc),'dims',sorted(set(d for _,d in defc)))
sup=lambda co: [u for u in off if not (cls[co]>>u)&1]
dirs=[sup(co) for co,_ in defc]
f=[[blk(Brows,a,b) for b in dirs+[off]] for a in dirs+[off]]
n=len(dirs)
import collections
print('per-term min',min(min(r) for r in f),'histogram',collections.Counter(x for r in f for x in r))
def solve(mt):
    Gr=nx.DiGraph(); Gr.add_node('s',demand=-mt); Gr.add_node('t',demand=mt)
    for i in range(n+1): Gr.add_edge('s',('r',i),capacity=1 if i<n else mt,weight=0)
    for j in range(n+1): Gr.add_edge(('c',j),'t',capacity=1 if j<n else mt,weight=0)
    for i in range(n+1):
        for j in range(n+1): Gr.add_edge(('r',i),('c',j),capacity=mt,weight=f[i][j])
    fl=nx.min_cost_flow(Gr); return nx.cost_of_flow(Gr,fl),[(i,j,f[i][j]) for i in range(n+1) for j in range(n+1) if fl[('r',i)].get(('c',j),0)]
for mt in (8,9,10,11): print('m',mt,solve(mt))
