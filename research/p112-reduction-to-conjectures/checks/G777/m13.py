# rows 592-595 (c_S=12,13): E (<=13 lines) contains an r0-leftover WLOG. served(E) = roots outside E having a minimal leftover (r covered) inside E.
import sys; sys.path.insert(0,'../CARRIER')
from lib import *
from collections import defaultdict, Counter
import numpy as np
Z=[0]*512
for a in range(1,512):
    m=0
    for t in range(n):
        if not par(a&lab[t]): m|=1<<t
    Z[a]=m
masks=sorted({Z[a]&Z[b] for a in range(1,512) for b in range(a+1,512)})
pc=lambda x: bin(x).count('1'); dot=lambda u,v: sum(x*y for x,y in zip(u,v))
X2r=defaultdict(set)
for ri in range(n):
    r=lines[ri]; T=sum(1<<t for t in range(n) if dot(r,lines[t])!=0)
    A=sorted({m&T for m in masks},key=pc,reverse=True); sz=[pc(x) for x in A]
    need=pc(T)-13; Ls=set()
    for i,x in enumerate(A):
        if sz[i]+sz[0]<need: break
        for j in range(i,len(A)):
            if sz[i]+sz[j]<need: break
            u=x|A[j]
            if (u>>ri)&1 and pc(u)>=need: Ls.add(T&~u)
    for e in Ls:
        if not any(f!=e and f&e==f for f in Ls): X2r[e].add(ri)
print('leftover sets',Counter(pc(e) for e in X2r),'roots per set',Counter((pc(e),len(v)) for e,v in X2r.items()),flush=True)
Qs=[e for e in X2r if pc(e)==8]; Ms=[e for e in X2r if pc(e)==12]
Qlo=np.array([q&((1<<64)-1) for q in Qs],dtype=np.uint64); Qhi=np.array([q>>64 for q in Qs],dtype=np.uint64)
Qroots=[X2r[q] for q in Qs]
Mset=set(Ms)
best=0; arg=None
for M in [e for e in Ms if 0 in X2r[e]]:
    for l in [None]+[t for t in range(n) if not M>>t&1]:
        E=M if l is None else M|(1<<l)
        el=np.uint64(E&((1<<64)-1)); eh=np.uint64(E>>64)
        sub=np.nonzero(((Qlo&~el)==0)&((Qhi&~eh)==0))[0]
        srv=set()
        for k in sub: srv|=Qroots[k]
        bits=[t for t in range(n) if E>>t&1]
        for x in ([None] if l is None else [])+bits:
            Y=E if x is None else E&~(1<<x)
            if Y in Mset: srv|=X2r[Y]
        if l is None and E in Mset: srv|=X2r[E]
        srv={r for r in srv if not E>>r&1}
        if len(srv)>best: best=len(srv); arg=(pc(E),len(sub))
print('max served roots over E = M (+1 line), M an r0 12-leftover:',best,arg,' kill 592-595 iff 13+best<36')
