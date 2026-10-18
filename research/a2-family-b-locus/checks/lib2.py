import sys
from common2 import *   # E8,E7,E6,D4,D5,D6, Gmat, B0rows, blk, rank_f2, dot
import networkx as nx
def nonorth_graph(L):
    G=Gmat(L); v=len(L); g=nx.Graph(); g.add_nodes_from(range(v))
    g.add_edges_from((t,s) for t in range(v) for s in range(t+1,v) if G[t][s]!=0); return g
