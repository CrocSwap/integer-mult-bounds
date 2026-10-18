# B-locus class-level relaxation with e9 row (R=X) and e9 column (A=supp beta, subset of X). Prints optimum and configuration.
import sys,os
from iib import *
import itertools
def solve2(rows, cols, mt, names_r, names_c):
    full=list(range(v))
    f=[[blk(Brows,a,b) for b in cols+[full]] for a in rows+[full]]
    nr,nc=len(rows),len(cols)
    Gr=nx.DiGraph(); Gr.add_node('s',demand=-mt); Gr.add_node('t',demand=mt)
    for i in range(nr+1): Gr.add_edge('s',('r',i),capacity=1 if i<nr else mt,weight=0)
    for j in range(nc+1): Gr.add_edge(('c',j),'t',capacity=1 if j<nc else mt,weight=0)
    for i in range(nr+1):
        for j in range(nc+1): Gr.add_edge(('r',i),('c',j),capacity=mt,weight=f[i][j])
    fl=nx.min_cost_flow(Gr); cost=nx.cost_of_flow(Gr,fl)
    conf=[]
    for i in range(nr+1):
        for j in range(nc+1):
            k=fl[('r',i)].get(('c',j),0)
            if k: conf.append(((names_r+['full'])[i],(names_c+['full'])[j],f[i][j],k))
    return cost,conf,f
rows=[sup_avoid([a]) for a in rowdef]+[Xs]
nr=['R%d%s'%(a,'T' if a in Tg else ('S' if a in colS else '')) for a in rowdef]+['e9row']
base=[sup_avoid([c]) for c in colS]+[sup_avoid([t]) for t in Tg]
nc=['S%d'%c for c in colS]+['T%d'%t for t in Tg]
print(UNIT,'X',Xs,'rowdef',len(rowdef),'colS',len(colS),'Tg',Tg)
for sb in [Xs[:1],Xs[:2],Xs]:
    for mt in (9,10,11):
        c,conf,f=solve2(rows,base+[sb],mt,nr,nc+['e9col%d'%len(sb)])
        print('suppbeta',len(sb),'m',mt,'cost',c); 
        if mt==10: print('   ',conf)
c,conf,f=solve2(rows,base,10,nr,nc); print('no e9col m10',c,conf)
