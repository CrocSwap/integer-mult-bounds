# Independent re-implementation of the L3 clique test (no null.pkl/compat from clique.py):
# compat via exact Bd-rank (TWINSWAP lib), edge via row-space criterion: e_i, e_i2 not in rowspace(FC[Theta][:,S]).
import sys, itertools, numpy as np, networkx as nx
from lib import bdrank, LAB, C, n
from collections import Counter
FC=np.array(C,dtype=float); par=lambda x: bin(x).count('1')&1
O={z:frozenset(t for t in range(n) if par(z&LAB[t])) for z in range(1,512)}
offs=[[t for t in range(n) if C[t][i]!=0] for i in range(8)]
compat={i:[z for z in range(1,512) if bdrank(offs[i],[t for t in range(n) if t not in O[z]])==7] for i in range(8)}
rk=np.linalg.matrix_rank
Ic=tuple(map(int,sys.argv[1].split(','))) if len(sys.argv)>1 and sys.argv[1] else ()
I=[i for i in range(8) if i not in Ic]
V=[(i,z) for i in I for z in compat[i]]
Gr=nx.Graph(); Gr.add_nodes_from(V)
for a in range(len(V)):
    i,z=V[a]
    for b in range(a+1,len(V)):
        i2,z2=V[b]
        if i2==i or z2==z: continue
        Th=sorted(O[z]&O[z2]); S=sorted(set([i,i2])|set(Ic))
        if not Th: Gr.add_edge(V[a],V[b]); continue
        B=FC[Th][:,S]; r=rk(B)
        ei=np.zeros(len(S)); ei[S.index(i)]=1; ej=np.zeros(len(S)); ej[S.index(i2)]=1
        if rk(np.vstack([B,ei]))>r and rk(np.vstack([B,ej]))>r: Gr.add_edge(V[a],V[b])
cs=Counter(len(c) for c in nx.find_cliques(Gr))
print('VERIFY Ic',Ic,'vertices',len(V),'edges',Gr.number_of_edges(),'maximal clique sizes',sorted(cs.items()),flush=True)
