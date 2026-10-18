"""The symplectic polar space W(2k-1,2) on F2^{2k}: points are nonzero ints below 4^k, b(p,q) = sum_i (p_{2i} q_{2i+1} + p_{2i+1} q_{2i}).
Generators (Lagrangians = maximal totally isotropic subspaces) are frozensets of their 2^k - 1 nonzero points."""
import random


def bf(p, q, k):
    m = int('01' * k, 2)
    return (((p & m) << 1) & q).bit_count() & 1 ^ (((p & (m << 1)) >> 1) & q).bit_count() & 1


def perp_points(basis, k):
    return [q for q in range(1, 4 ** k) if all(bf(q, s, k) == 0 for s in basis)]


def lagrangians(k):
    """All generators of W(2k-1,2) (count prod_{i=1..k} (2^i + 1))."""
    level = {frozenset([p]) for p in range(1, 4 ** k)}
    for _ in range(k - 1):
        nxt = set()
        for S in level:
            for p in perp_points(list(S), k):
                if p in S:
                    continue
                nxt.add(frozenset(S | {p} | {p ^ s for s in S}))
        level = nxt
    return level


def random_lagrangian(k, rng):
    S = set()
    basis = []
    for _ in range(k):
        cands = [q for q in perp_points(basis, k) if q not in S]
        p = rng.choice(cands)
        S |= {p} | {p ^ s for s in S}
        basis.append(p)
    assert len(S) == 2 ** k - 1
    return frozenset(S)
