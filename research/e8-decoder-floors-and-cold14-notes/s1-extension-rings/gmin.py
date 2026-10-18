import sys,time; sys.path.insert(0,sys.path[0])
from gauss_geom import *
import networkx as nx
from minrank_sat import solve_asym
lines,J=gaussian_e8(); NO=nonorth(lines,J); v=60
g=nx.Graph([(i,j) for i in range(v) for j in range(i+1,v) if NO[i,j]])
K=sorted(max(nx.find_cliques(g),key=len))
pat={(i,j) for i in range(v) for j in range(v) if NO[i,j]}
c=int(sys.argv[1])
r=solve_asym(v,pat,None,c,'none',K)
print(c,len(K),r['result'],r['sec'],flush=True)
if r['result']=='SAT':
    import numpy as np; np.save('gauss_B_c%d.npy'%c,r['B'])
