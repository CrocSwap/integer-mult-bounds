#!/usr/bin/env python3
"""Exact E8 root-pair signature gate: pair sums are not root-line labels."""
from itertools import combinations,product
roots=[]
for i,j in combinations(range(8),2):
    for ai,aj in product((2,-2),repeat=2):
        x=[0]*8;x[i]=ai;x[j]=aj;roots.append(tuple(x))
for x in product((1,-1),repeat=8):
    if x.count(-1)%2==0: roots.append(x)
def canon(v):
    return v if next(x for x in v if x)>0 else tuple(-x for x in v)
L=sorted({canon(v) for v in roots})
assert len(L)==120
N=[sum(((sum(a*b for a,b in zip(x,y))//4+1)&1)<<j
       for j,y in enumerate(L)) for x in L]
assert len(set(N))==120
pair_count=0
for i,j in combinations(range(120),2):
    assert (N[i]^N[j]) not in set(N)
    pair_count+=1
assert pair_count==7140
print('PASS_ROOT_LINE_GATE roots=120 pair_sums=7140 direct_root_adapters=0')
