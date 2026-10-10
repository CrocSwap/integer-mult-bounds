"""Exact basis helpers derived from PR271's sandwich263.py.

Source: https://github.com/CrocSwap/integer-mult-bounds/pull/271
Retained rational_basis, rank_mod_prime, and annihilator routines; no PR271
cleanup selection or word rewrite is imported. The exact emitted-frame Gram
and prime audits are independently performed in cleanup_emit.py.
"""
import sys
if not __debug__: raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode = True
from fractions import Fraction as Q
from math import lcm
H = 24
PRIME = 1000003

def rational_basis(rows):
    """Reduced integer basis of the rational row space."""
    basis = {}
    for values in rows:
        row = list(map(Q, values))
        for p, b in sorted(basis.items()):
            if row[p]:
                row = [x - row[p] * y for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            basis[p] = [x / row[p] for x in row]
    out = []
    for _, row in sorted(basis.items()):
        d = lcm(*(x.denominator for x in row))
        out.append([int(x * d) for x in row])
    return out


def rank_mod_prime(rows):
    basis = {}
    for row in rows:
        row = [x % PRIME for x in row]
        for p, b in sorted(basis.items()):
            if row[p]:
                c = row[p]
                row = [(x - c * y) % PRIME for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            inv = pow(row[p], -1, PRIME)
            basis[p] = [x * inv % PRIME for x in row]
    return len(basis)


def annihilator(B):
    """Rational basis of {x : B x = 0} for a reduced basis B."""
    pivots = [next(i for i, x in enumerate(row) if x) for row in B]
    out = []
    for free in sorted(set(range(H)) - set(pivots)):
        v = [Q(i == free) for i in range(H)]
        for p, row in reversed(list(zip(pivots, B))):
            v[p] = -sum(Q(row[j]) * v[j] for j in range(p + 1, H)) / row[p]
        out.append([str(x) for x in v])
    return out

