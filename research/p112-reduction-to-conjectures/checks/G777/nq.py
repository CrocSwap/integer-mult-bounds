# for every root line r: minimal leftovers of size 8 (r covered). Map Q -> roots.
import sys; sys.path.insert(0,'../CARRIER')
from lib import *
from collections import Counter, defaultdict
import pickle
Z=[0]*512
for a in range(1,512):
    m=0
    for t in range(n):
        if not par(a&lab[t]): m|=1<<t
    Z[a]=m
masks=sorted({Z[a]&Z[b] for a in range(1,512) for b in range(a+1,512)})
pc=lambda x: bin(x).count('1')
dot=lambda u,v: sum(x*y for x,y in zip(u,v))
Q2r=defaultdict(set); per=[]
for ri in range(n):
    r=lines[ri]; T=sum(1<<t for t in range(n) if dot(r,lines[t])!=0)
    A=sorted({m&T for m in masks},key=pc,reverse=True); sz=[pc(x) for x in A]
    need=pc(T)-11; L=set()
    for i,x in enumerate(A):
        if sz[i]+sz[0]<need: break
        for j in range(i,len(A)):
            if sz[i]+sz[j]<need: break
            u=x|A[j]
            if (u>>ri)&1 and pc(u)>=need: L.add(T&~u)
    mins=[e for e in L if not any((f!=e and f&e==f) for f in L)]
    per.append(Counter(pc(e) for e in mins))
    for e in mins: Q2r[e].add(ri)
print('per-root minimal leftover sizes (<=11):',Counter(tuple(sorted(c.items())) for c in per))
print('#distinct Q',len(Q2r),' N_Q distribution',Counter(len(v) for v in Q2r.values()))
print('roots of Q-family inside Q?',Counter(sum(1 for r in v if Q>>r&1) for Q,v in Q2r.items()))
# 4-flats with 8 lines in general
F4=Counter()
pickle.dump(dict(Q2r),open('Q2r.pkl','wb'))
