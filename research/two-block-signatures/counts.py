"""Exact labeled counts from pivot occupancies, without iterating seven-type profiles."""
from math import comb


def both(k):
    return 3**k - 2*(2**k) + 1


def positions(n, left, right):
    return comb(n,left) * comb(n-left,right)


def ordinary_count(p, q):
    n = p+q
    total = 0
    for left in range(p+1):
        for right in range(q+1):
            if left < p and right < q:
                labels = 3**(left+right)
            elif left == p and right < q:
                labels = both(p) * 3**right
            elif left < p and right == q:
                labels = 3**left * both(q)
            else:
                labels = 1 + 2*(2**p-1)*(2**q-1) + both(p)*both(q)
            total += positions(n,left,right) * labels
    return total


def odd_side(p, q):
    n = p+q
    return sum(positions(n,p-1,q-v)*3**(q-v) for v in range(3,q+1,2))


def exceptions(p, q):
    """Three disjoint families of signatures absent over F2."""
    left, right = p-1, q-1
    choices = 3**left + 3**right + 2**(left+right+1) - 2**(left+1) - 2**(right+1) + 1
    corner = positions(p+q,left,right)*choices
    return {"binary 1x1":corner, "binary one A":odd_side(p,q), "binary one B":odd_side(q,p)}
