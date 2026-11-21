#!/usr/bin/env python3
"""Check the rational ranks of the 511 nonzero P104 label hyperplanes.

For a binary normal v, the outside rows are doubled E8 root rows r_p with
q_p dot v = 1.  Modular rank supplies a rigorous rational lower bound;
the 16 rows with modular rank 7 are also eliminated over exact rationals.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import lcm
from pathlib import Path

fixture_bytes = (Path(__file__).resolve().parent / "p104_roots.json").read_bytes()
assert sha256(fixture_bytes).hexdigest() == "2693077172c0e3036fdc293f1d8d71d5f20830a3eb2a88c0cc4fc0623e6310b7"
fixture = json.loads(fixture_bytes)
labs, codes = fixture["labs"], fixture["rootCode"]
roots = [[((c >> (3 * i)) & 7) - 2 for i in range(8)] for c in codes]
PRIME = 2_147_483_647


def rank_mod(rows):
    pivots = {}
    for row in rows:
        r = [x % PRIME for x in row]
        for j in range(8):
            if not r[j]:
                continue
            if j in pivots:
                scale = r[j]
                r = [(x-scale*y) % PRIME for x,y in zip(r,pivots[j])]
            else:
                scale = pow(r[j], -1, PRIME)
                pivots[j] = [(x*scale) % PRIME for x in r]
                break
        if len(pivots) == 8:
            break
    return len(pivots)


def echelon_q(rows):
    pivots = {}
    for row in rows:
        r = list(map(Fraction, row))
        for j in range(8):
            if not r[j]:
                continue
            if j in pivots:
                scale = r[j]
                r = [x-scale*y for x,y in zip(r,pivots[j])]
            else:
                scale = r[j]
                pivots[j] = [x/scale for x in r]
                break
    return pivots


def null_from_echelon(pivots):
    free = next(i for i in range(8) if i not in pivots)
    z = [Fraction(0) for _ in range(8)]
    z[free] = Fraction(1)
    for i in sorted(pivots, reverse=True):
        z[i] = -sum(pivots[i][j] * z[j] for j in range(i + 1, 8))
    return z


bad = []
bad_vectors = []
for normal in range(1, 512):
    rows = [r for q,r in zip(labs,roots) if (normal & q).bit_count() % 2]
    mr = rank_mod(rows)
    assert mr >= 7
    if mr < 8:
        pivots = echelon_q(rows)
        assert len(pivots) == 7
        z = null_from_echelon(pivots)
        # The unique functional has support exactly on the 52 inside ports.
        assert all(bool(sum(x*y for x,y in zip(r,z))) ==
                   (not ((normal & q).bit_count() % 2)) for q,r in zip(labs,roots))
        assert sum(not ((normal & q).bit_count() % 2) for q in labs) == 52
        bad.append(normal)
        den = lcm(*(x.denominator for x in z))
        integer_z = [int(den * x) for x in z]
        assert sum(x*x for x in integer_z) <= 8
        bad_vectors.append(integer_z)
assert bad == [7,25,42,52,67,76,82,97,104,127,137,162,266,289,448,491]
print("511 normals checked: 495 have rational rank 8; 16 have rational rank exactly 7")
print("rank-7 masks:", bad)
print("each rank-7 null functional has support exactly the 52 inside ports")
# Hadamard bounds every 8x8 determinant by sqrt(8)^8 = 4096 < PRIME.
# Therefore a determinant vanishes over Q iff it vanishes modulo PRIME.
bases = sum(rank_mod([bad_vectors[i] for i in choice]) == 8
            for choice in combinations(range(16), 8))
assert bases == 8766
print("8-element subsets whose nullvectors are Q-independent:", bases, "of 12870")
