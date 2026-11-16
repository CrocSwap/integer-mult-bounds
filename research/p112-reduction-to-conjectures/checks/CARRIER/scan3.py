import ast, itertools
from collections import Counter
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
N={1:1,2:3,3:6,4:12,5:20,6:36,7:63,8:120}
rows=[ast.literal_eval(l[5:].strip()) for l in open('/tmp/dom_out.txt') if l.startswith('LEFT')]
c=Counter(); ex=[]
for d,s,ws,e in rows:
    if s!=7: continue          # ClassI forced only for s=7
    a=len(ws); idxs=range(a)
    capc=lambda S: sum(g[ws[i]] for i in S)
    # K subsets of size d-1; complement C
    fam=[]
    for K in itertools.combinations(idxs,d-1):
        comp=tuple(i for i in idxs if i not in K)
        cp=capc(comp)
        if cp<57: c['infeasible complement (kill)']+=1; fam=None; break
        if cp<78: fam.append(comp)
    if fam is None: continue
    # greedy injective subfamily: comps whose pairwise intersection cap<57
    chosen=[]
    for comp in sorted(fam,key=lambda x:capc(x)):
        if all(capc(tuple(set(comp)&set(o)))<57 for o in chosen): chosen.append(comp)
    if len(chosen)>N[d]: c['root counting kill (greedy %d > N_%d)'%(len(chosen),d)]+=1
    else: c['survives both']+=1
print(sorted(c.items(),key=lambda x:-x[1]))
