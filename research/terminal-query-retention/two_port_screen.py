#!/usr/bin/env python3
"""Exact bounded two-port/common-frame and paired-center screen, no solver."""
from itertools import combinations,product
from collections import Counter
import json
def rank(vs):
    b={}
    for v in vs:
        while v:
            k=v.bit_length()
            if k in b:v^=b[k]
            else:b[k]=v;break
    return len(b)
def ports(p):
    return [sum(1<<(2*i+b) for i,b in zip(I,B))
            for I in combinations(range(p),3) for B in product(range(2),repeat=3)]
def main():
    q=ports(11);overlap=Counter((x&y).bit_count() for x,y in combinations(q,2))
    # An orthogonal coordinate two-anchor chart requires the same Gram matrix.
    assert all((x.bit_count()%2)==1 for x in q)
    rejected=sum(n for k,n in overlap.items() if k%2)
    # Explicit perfect matching: flip the bit in the largest occupied pair.
    matched=set()
    for x in q:
        i=(x.bit_length()-1)//2;y=x^(3<<(2*i))
        assert y in q and (x&y).bit_count()==2 and x!=y
        matched.add(tuple(sorted((x,y))))
    assert len(matched)==660
    # For a*Si+b*Sj the support is constant in each of these EXACT cases:
    # a=0, b=0, a+b=0, and all a,b,a+b nonzero. No real-valued sampling gap.
    hist=Counter();witnesses=[]
    for i,j in combinations(range(22),2):
        for a,b in [(1,0),(0,1),(1,-1),(1,1)]:
            s=[v for v in q if a*((v>>i)&1)+b*((v>>j)&1)]
            r=rank(s);hist['%s:%s'%(('same-pair' if i//2==j//2 else 'different-pair'),(a,b)) ,r]+=1
            if a and b:assert r>=21
            else:assert r==20
            if (i,j) in [(0,1),(0,2)]:witnesses.append(dict(i=i,j=j,a=a,b=b,support=len(s),rank=r))
    # A fully mixed invertible 2x2 change has two rows with both entries nonzero.
    # Even granting free mixing and no extra moves, 2*21^(1-a)>2*20^(1-a)
    # for every 0<a<1. A triangular nontrivial change worsens at least one row.
    print(json.dumps(dict(status='PASS_EXACT_BOUNDED_SCREEN',ports=len(q),
      unordered_port_pairs=sum(overlap.values()),overlap_histogram=dict(overlap),
      incompatible_orthonormal_two_anchor_pairs=rejected,
      explicit_orthogonal_perfect_matching_pairs=len(matched),
      center_support_patterns_checked=231*4,center_examples=witnesses,
      optimistic_obstruction='With producer/endpoints otherwise fixed, nontrivial two-center mixing raises at least one copied-child rank from20 to>=21. Even free mixing cannot improve any moment with0<a<1.',
      exclusions='No claim about jointly redesigned producers, general higher-rank couplings, or complete two-port supplier. Gram compatibility is necessary not a phase/endpoint certificate.'),indent=2))
if __name__=='__main__':main()
