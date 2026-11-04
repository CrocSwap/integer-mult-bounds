"""All named guard subsets, checked against literal permutation histograms."""
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
from math import factorial

from literal import complement, reduce_matrix
from monomial import flat_rows, passing_permutations
from settlement import Field


def mixed(f,m):
    """Normalized with scattered nonzero entries and a zero image coordinate."""
    u=[1,0]+[(2*i+1)%f.q for i in range(2,m-1)]+[1]
    b=[(i+2)%f.q for i in range(m-1)]
    w=[(2*i+1)%f.q for i in range(m-1)]
    b.append(f.add[1][f.neg[f.dot(b,u[:-1])]])
    w.append(f.neg[f.dot(w,u[:-1])])
    return tuple(u),tuple(b),tuple(w)


def mask_counts(q,u,b,w):
    f=Field(q);m=len(u)
    rows=flat_rows(f,b,[w])
    matrices=[complement(f,u,row) for row in rows]
    if not any(w) or any(f.dot(u,v)!=1 for v in rows):
        raise ValueError("unnormalized mask sweep")
    possible={}
    for n in range(1,m):
        for idx in combinations(range(m),n):
            key=sum(1<<i for i in idx)
            mask=0
            for j,mat in enumerate(matrices):
                sub=[[mat[i][l] for l in idx] for i in idx]
                if reduce_matrix(f,sub)[0]:
                    mask|=1<<j
            possible[key]=mask
    hist=Counter()
    digest=sha256()
    for order in permutations(range(m)):
        mask=(1<<q)-1
        used=0
        for i in order[:-1]:
            used |= 1<<i
            mask &= possible[used]
        hist[mask]+=1
        digest.update(bytes(order)+mask.to_bytes((q+7)//8,"little"))
    for required in range(1<<q):
        chosen=[v for j,v in enumerate(rows) if required & (1<<j)]
        predicted=passing_permutations(f,u,chosen)
        if predicted!=sum(c for mask,c in hist.items() if mask & required==required):
            raise ValueError("literal named permutation subsets vs prefix DP")
    if sum(hist.values())!=factorial(m):
        raise ValueError("labeled order inventory")
    return dict(q=q,m=m,u=u,b=b,w=w,orders=factorial(m),named_subsets=1<<q,
                exact_masks=dict(sorted(hist.items())),order_mask_sha256=digest.hexdigest())


def collect():
    data=[mask_counts(5,(1,)*5,(0,0,0,0,1),w) for w in [(1,4,2,3,0),(1,1,1,2,0)]]
    for q,m in [(2,6),(3,6),(4,6),(5,6),(7,7),(8,7),(9,7)]:
        data.append(mask_counts(q,*mixed(Field(q),m)))
    return data
