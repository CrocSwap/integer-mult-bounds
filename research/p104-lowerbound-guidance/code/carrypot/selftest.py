# brute-force check of z4len and compress on small random matrices
import random, itertools
from z4pot import z4len, compress
rng=random.Random(5); bad=0
for it in range(400):
    N=rng.randint(1,4); m=rng.randint(1,4)
    rows=[[rng.choice([0,0,1,2,3]) for _ in range(N)] for _ in range(m)]
    span={tuple([0]*N)}
    for r in rows:
        new=set(span)
        for s in span:
            for c in (1,2,3): new.add(tuple((a+c*b)%4 for a,b in zip(s,r)))
        span=new
        # closure
    while True:
        new=set(span)
        for s in span:
            for r in rows:
                new.add(tuple((a+b)%4 for a,b in zip(s,r)))
        if new==span: break
        span=new
    L=len(span).bit_length()-1
    if z4len(rows,N)!=L or z4len(compress(rows,N),N)!=L: bad+=1
print('selftest mismatches',bad,'of 400')
