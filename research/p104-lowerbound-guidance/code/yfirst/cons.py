import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter, defaultdict
paths={r:[dim[W['initial'][r]]] for r in range(n)}
for e in P:
    if e[0]=='MOVE' and e[1]<n: paths[e[1]].append(dim[e[3]])
# for ops at chart dims 1..4: classify (dst kind, src kind)
c=Counter(); ex=defaultdict(list)
for i,e in enumerate(P):
    if e[0] in('ADD','COPY'):
        d=dim[e[4]]
        if 1<=d<=4:
            k=(d,kind(e[1]),kind(e[2])); c[k]+=1
            if len(ex[k])<3: ex[k].append(i)
for k in sorted(c): print(k,c[k],ex[k])
# helpers that receive at dims 1-4 from tree helpers but are not tree helpers (path not starting 0,1,..)
