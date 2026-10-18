# P104: orbits of A2 triangles under signed permutations (even sign changes) preserving the line set L
import itertools
from a2lib import *
assert UNIT=='P104'
def key(r):
    i=next(k for k in range(8) if r[k]!=0); s=1 if r[i]>0 else -1; return tuple(s*x for x in r)
Lk=[key(tuple(int(2*x) for x in r)) for r in L]; Lpos={k:i for i,k in enumerate(Lk)}; Lset=set(Lk)
perms=[]
pairs=[(0,1),(2,3),(4,5),(6,7)]
for pp in itertools.permutations(range(4)):
  for flips in itertools.product([0,1],repeat=4):
    perm=[]
    for k in range(4):
        a,b=pairs[pp[k]]
        perm+= [b,a] if flips[k] else [a,b]
    for sg in itertools.product([1,-1],repeat=8):
        if sg.count(-1)%2: continue
        img=[key(tuple(sg[i]*r[perm[i]] for i in range(8))) for r in Lk]
        if all(k in Lset for k in img): perms.append([Lpos[k] for k in img])
print('automorphisms found',len(perms))
T=all_a2(); Tid={t:i for i,t in enumerate(T)}; par=list(range(len(T)))
def find(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for p in perms:
    for t in T:
        u=tuple(sorted(p[i] for i in t)); a,b=find(Tid[t]),find(Tid[u])
        if a!=b: par[a]=b
comps={}
for t in T: comps.setdefault(find(Tid[t]),[]).append(t)
print('triangles',len(T),'orbits',len(comps),'reps',[c[0] for c in comps.values()],'sizes',sorted(len(c) for c in comps.values()))
