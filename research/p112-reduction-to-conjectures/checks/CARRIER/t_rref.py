import random
from cov import rref_basis, inspan, remove_cover
from lib import f2rank
random.seed(1)
bad=0
for _ in range(3000):
    k=random.randint(1,12); vs=[random.randint(1,511) for _ in range(k)]
    b=rref_basis(vs)
    if len(b)!=f2rank(vs): bad+=1
    # canonical: permuted input gives same basis
    vs2=vs[:]; random.shuffle(vs2)
    if rref_basis(vs2)!=b: bad+=1
    for v in vs:
        if not inspan(v,b): bad+=1
    # remove_cover brute force check
    w=random.randint(1,4); s=random.randint(0,2)
    import itertools
    brute=any(f2rank([vs[i] for i in range(k) if i not in E])<=w for sz in range(0,s+1) for E in itertools.combinations(range(k),sz))
    if brute!=remove_cover(tuple(vs),w,s): bad+=1
print('bad',bad)
