# leftover sets (r0 covered) of size <= K for Off_E(r0) vs two 7-flats; classify
import sys; sys.path.insert(0,'../CARRIER')
from lib import *
from collections import Counter
import pickle
K=int(sys.argv[1]); ri=int(sys.argv[2]) if len(sys.argv)>2 else 0
Z=[0]*512
for a in range(1,512):
    m=0
    for t in range(n):
        if not par(a&lab[t]): m|=1<<t
    Z[a]=m
masks=sorted({Z[a]&Z[b] for a in range(1,512) for b in range(a+1,512)})
pc=lambda x: bin(x).count('1')
dot=lambda u,v: sum(x*y for x,y in zip(u,v))
r=lines[ri]; T=sum(1<<t for t in range(n) if dot(r,lines[t])!=0)
A=sorted({m&T for m in masks},key=pc,reverse=True); sz=[pc(x) for x in A]
need=pc(T)-K; L=set()
for i,x in enumerate(A):
    if sz[i]+sz[0]<need: break
    for j in range(i,len(A)):
        if sz[i]+sz[j]<need: break
        u=x|A[j]
        if not (u>>ri)&1: continue
        if pc(u)>=need: L.add(T&~u)
mins=[e for e in L if not any((f!=e and f&e==f) for f in L)]
bits=lambda m:[t for t in range(n) if m>>t&1]
print('root',ri,'K',K,'leftovers',len(L),'minimal',len(mins),Counter(pc(e) for e in mins))
print('label-rank of minimal leftovers',Counter((pc(e),f2rank([lab[t] for t in bits(e)])) for e in mins))
pickle.dump((ri,K,mins),open('left_%d_%d.pkl'%(ri,K),'wb'))
