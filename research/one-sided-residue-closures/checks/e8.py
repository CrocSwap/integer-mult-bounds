# AUDIT-SC independent E8 model: roots in SIMPLE-ROOT coordinates generated from the E8 Cartan matrix
# (no reuse of CARRIER/lib.py). Labels = (1, coefficient vector mod 2) in F2^9.
import itertools, numpy as np
# E8 Dynkin: chain 0-1-2-3-4-5-6 with node 7 attached to node 4 (Bourbaki-like; any E8 labelling works)
edges=[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(4,7)]
C=np.eye(8,dtype=int)*2
for a,b in edges: C[a,b]=C[b,a]=-1
assert round(np.linalg.det(C))==1
def ip(u,v): return int(np.array(u)@C@np.array(v))
simple=[tuple(int(i==k) for i in range(8)) for k in range(8)]
roots=set(simple)|{tuple(-x for x in s) for s in simple}
frontier=list(roots)
while frontier:
    new=[]
    for r in frontier:
        for s in simple:
            c=ip(r,s); t=tuple(x-c*y for x,y in zip(r,s))
            if t not in roots: roots.add(t); new.append(t)
    frontier=new
roots=sorted(roots); assert len(roots)==240
pos=[r for r in roots if any(r) and next(x for x in r if x)>0]
lines=sorted(pos); assert len(lines)==120
assert all(ip(r,r)==2 for r in lines)
cls=[sum((x%2)<<k for k,x in enumerate(r)) for r in lines]   # E8/2E8 classes in F2^8
assert len(set(cls))==120 and 0 not in cls
G=np.array(lines)@C   # row l: functional <l,.>  (so <l,h> = G[l]@h for h in simple coords)
