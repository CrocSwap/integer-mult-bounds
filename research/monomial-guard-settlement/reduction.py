"""Bounded checks of the 3-PARTITION embedding, separate from the hardness proof."""
from functools import lru_cache
from itertools import combinations_with_replacement, combinations
from math import isqrt

from settlement import partition


class PrimeAddition:
    def __init__(self,p):
        self.add=[[(a+b)%p for b in range(p)] for a in range(p)]


def triples_exist(values,B):
    triples=[]
    for triple in combinations(range(len(values)),3):
        if sum(values[i] for i in triple)==B:
            triples.append(sum(1<<i for i in triple))

    @lru_cache(None)
    def cover(mask):
        if not mask:
            return True
        bit=mask & -mask
        return any(t & bit and mask & t == t and cover(mask^t) for t in triples)
    return cover((1<<len(values))-1)


def collect():
    records=[]
    for n,B in ((2,12),(2,16),(2,20),(2,24),(2,28),(3,15),(3,17),(3,20)):
        p=next(i for i in range(n*B+1,2*n*B+1) if all(i%d for d in range(2,isqrt(i)+1)))
        field=PrimeAddition(p)
        counts=[0,0]
        first=[None,None]
        for v in combinations_with_replacement(range(B//4+1,(B+1)//2),3*n):
            if sum(v)!=n*B:
                continue
            charges=[(x,) for x in v]+[(p-B,)]*n
            cost=4*n-len(partition(field,charges))
            possible=triples_exist(v,B)
            if (cost<=3*n)!=possible:
                raise ValueError("3-partition embedding")
            counts[possible]+=1
            if first[possible] is None:
                first[possible]=dict(values=v,paid_cost=cost)
        records.append(dict(n=n,B=B,p=p,no=counts[0],yes=counts[1],examples=first))
    if not all(sum(r[k] for r in records)>0 for k in ("yes","no")):
        raise ValueError("3-partition controls lack both signs")
    return records
