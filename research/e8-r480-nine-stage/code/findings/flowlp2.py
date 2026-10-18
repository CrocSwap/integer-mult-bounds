"""Min-flow LP driven by the junk-dimension lemma (node inflow lower bounds), no keeper constraints.
 cell node C: registers at the cell >= n_C (cross 3, matching 4); edges: one donor per line (L->C >=1), one wire per quad (C->Q1, C->Q2 >=1)."""
import itertools
import numpy as np
from scipy.optimize import linprog
lines='abcd'; cells=[''.join(c) for c in itertools.combinations(lines,2)]; match={'ab','cd'}
nodes=['0']+['L'+x for x in lines]+['C'+c for c in cells]+['Q1'+c for c in cells]+['Q2'+c for c in cells]
idx={n:i for i,n in enumerate(nodes)}
def run(inflow_lb, junk=True):
    edges=[];lb=[]
    def E(u,v,l=0.0): edges.append((u,v)); lb.append(l)
    for x in lines: E('0','L'+x)
    for c in cells:
        E('0','C'+c)
        for x in c: E('L'+x,'C'+c,1.0)
        E('C'+c,'Q1'+c,1.0); E('C'+c,'Q2'+c,1.0)
    n=len(nodes); m=len(edges)
    A=np.zeros((n,m+n)); b=np.zeros(n)
    for j,(u,v) in enumerate(edges): A[idx[v],j]+=1; A[idx[u],j]-=1
    for v in range(n): A[v,m+v]=-1
    for x in lines: b[idx['L'+x]]=-1.0
    keep=[i for i in range(n) if nodes[i]!='0']
    # node inflow >= inflow_lb[c]
    Aub=[];bub=[]
    if junk:
        for c in cells:
            row=np.zeros(m+n)
            for j,(u,v) in enumerate(edges):
                if v=='C'+c: row[j]=-1
            Aub.append(row); bub.append(-inflow_lb[c])
    cost=np.zeros(m+n)
    for j,(u,v) in enumerate(edges):
        if u=='0': cost[j]=1
    res=linprog(cost,A_eq=A[keep],b_eq=b[keep],A_ub=np.array(Aub) if Aub else None,b_ub=np.array(bub) if bub else None,bounds=[(l,None) for l in lb]+[(0,None)]*n,method='highs')
    return res.fun
nb={c:(4 if c in match else 3) for c in cells}
print('no junk lemma (donors + 2 wires per cell only):',run(nb,junk=False),'per 4-frame')
print('junk lemma node inflow cross>=3, matching>=4:',run(nb),'per 4-frame ->',30*run(nb),'+9 totals =',30*run(nb)+9)
