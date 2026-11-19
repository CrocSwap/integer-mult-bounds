"""Count occupied adjoint coefficients on any raw coordinate using binary subspaces."""
from functools import cache
from math import prod


def rank(values):
    pivots = {}
    for vector in values:
        while vector and vector.bit_length() in pivots:
            vector ^= pivots[vector.bit_length()]
        if vector:
            pivots[vector.bit_length()] = vector
    return len(pivots)


def epimorphisms(domain, codomain):
    if codomain > domain:
        return 0
    return prod((1 << domain) - (1 << i) for i in range(codomain))


@cache
def subspaces(n):
    zero = frozenset({0})
    spaces = {zero}
    todo = [zero]
    while todo:
        space = todo.pop()
        for v in range(1, 1 << n):
            if v not in space:
                bigger = space.union(w ^ v for w in space)
                if bigger not in spaces:
                    spaces.add(bigger)
                    todo.append(bigger)
    return tuple(spaces)


def census(n, row_columns):
    """By Hadamard rank, return (occupied fibres, nonzero Pauli coefficients)."""
    if not 1 <= n <= 4 or not row_columns:
        raise ValueError("Supply 1..4 qubits and at least one coordinate pair")
    q = 1 << n
    if any(not (0 <= r < q and 0 <= c < q) for r, c in row_columns):
        raise ValueError("Invalid computational address")
    r0, c0 = row_columns[0]
    diffs = [(r ^ r0, c ^ c0) for r, c in row_columns[1:]]
    s = rank(c for _, c in diffs)
    parabolic = (1 << (n*(n+1)//2))*epimorphisms(n,n)
    by_rank = [0]*(n+1)
    for H in subspaces(n):
        h = len(H).bit_length()-1
        m = n-h
        # A pivot need not be chosen in X/H: use the smallest integer in each coset.
        prescribed = [(min(r ^ a for a in H), c) for r,c in diffs]
        if rank((r << n) | c for r,c in prescribed) != s:
            continue
        b = rank(r for r,_ in prescribed)
        extensions = (1 << (b*(n-s))) * epimorphisms(n-s,m-b)
        weight, rem = divmod(parabolic, epimorphisms(n,m))
        if rem:
            raise ValueError("Invalid parabolic multiplicity")
        by_rank[h] += extensions * weight * (1 << (h*(h+1)//2))
    return tuple((count,count*(q << h)) for h,count in enumerate(by_rank))
