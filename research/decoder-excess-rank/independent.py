#!/usr/bin/env python3
"""Standalone integer replay of the stored P112 complex symmetric witness.

Imports neither verify.py nor predecessor code. This separate implementation is
by the same assisted author, not independent human review. Apache-2.0.
"""
import json
from fractions import Fraction
from itertools import combinations, product
from math import lcm
from pathlib import Path


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def model():
    lines = []
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, sign * 2
            lines.append(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.append((1, *signs))
    require(len(lines) == len(set(lines)) == 120, 'independent root count')
    removed = set()
    for a in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[a + 1] = 2, sign * 2
            removed.add(tuple(row))
    roots = sorted(set(lines) - removed)
    require(len(roots) == 112, 'P112 size')
    require(all(sum(r[a] * r[b] for r in roots) == 112 * (a == b)
                for a in range(8) for b in range(8)), 'full root rank from Gram identity')
    return roots


def binary_rank(rows):
    # Low-pivot row elimination, separate from PR1077's high-pivot dictionary.
    rows = list(rows)
    rank = 0
    for c in range(112):
        pivot = next((j for j in range(rank, len(rows)) if rows[j] & (1 << c)), None)
        if pivot is None:
            continue
        rows[pivot], rows[rank] = rows[rank], rows[pivot]
        for j in range(rank + 1, len(rows)):
            if rows[j] & (1 << c):
                rows[j] ^= rows[rank]
        rank += 1
    return rank


def identity(roots, matrix, denominator, hermitian=False):
    for a, ra in enumerate(roots):
        for b, rb in enumerate(roots):
            real = imag = 0
            for (x, y), (u, v) in zip(matrix[a], matrix[b]):
                if hermitian:
                    v = -v
                real += x * u - y * v
                imag += x * v + y * u
            if imag or 2 * real != denominator ** 2 * sum(x * y for x, y in zip(ra, rb)):
                return False
    return True


def bill(roots, matrix):
    answer = []
    pairing = [sum((((sum(x * y for x, y in zip(ra, rb)) // 4) + 1) % 2) << b
                   for b, rb in enumerate(roots)) for ra in roots]
    require(binary_rank(pairing) == 9, 'label rank')
    for k in range(10):
        support = [a for a, row in enumerate(matrix) if row[k] != (0, 0)]
        mask = sum(1 << a for a in support)
        answer.append(binary_rank([pairing[a] & mask for a in support]))
    return answer


def run(path=None):
    path = path or Path(__file__).with_name('RESULT.json')
    receipt = json.loads(path.read_text())
    require(len(receipt['representatives']) == 1, 'witness inventory')
    witness = receipt['representatives'][0]
    require(witness['domain'] == 'P112', 'witness domain')
    encoded = witness['D']
    require(len(encoded) == 112 and all(len(row) == 10 for row in encoded), 'witness shape')
    require(all(len(z) == 2 and all(type(x) is str for x in z) for row in encoded for z in row),
            'exact rational encoding')
    parsed = [[tuple(Fraction(x) for x in z) for z in row] for row in encoded]
    den = lcm(*(x.denominator for row in parsed for z in row for x in z))
    matrix = [[tuple(int(x * den) for x in z) for z in row] for row in parsed]
    roots = model()
    require(identity(roots, matrix, den), 'ordinary transpose identity')
    require(not identity(roots, matrix, den, True), 'Hermitian counterexample')
    # Compute 112*P*D with P=I-S*S^T/112, using integer pairs throughout.
    std = [[tuple(sum(roots[j][a] * matrix[j][k][part] for j in range(112)) for part in range(2))
            for k in range(10)] for a in range(8)]
    residual = [[tuple(112 * matrix[j][k][part] - sum(roots[j][a] * std[a][k][part] for a in range(8))
                       for part in range(2)) for k in range(10)] for j in range(112)]
    require(all(row[k] == (0, 0) for row in residual for k in range(8)), 'core residuals vanish')
    require(any(row[8][0] for row in residual), 'nonzero outside-code direction')
    require(all(row[8][1] == 0 and row[9] == (0, row[8][0]) for row in residual), 'rank-one isotropic pair')
    require(all(any(row[k] != (0, 0) for row in matrix) for k in range(10)), 'all terms active')
    mixed = []
    for row in matrix:
        sums = [sum(z[part] for z in row) for part in range(2)]
        mixed.append([tuple(5 * z[part] - sums[part] for part in range(2)) for z in row])
    require(identity(roots, mixed, 5 * den), 'Householder identity')
    costs = bill(roots, matrix)
    mixed_costs = bill(roots, mixed)
    require(costs == [8] * 8 + [9, 9] == witness['costs'], '82-copy invoice')
    require(mixed_costs == [9] * 10 == witness['mixed_costs'], '90-copy invoice')
    return {'ordinary_identity_entries': 12544, 'mixed_identity_entries': 12544,
            'residual_rank': 1, 'cost_before': sum(costs), 'cost_after': sum(mixed_costs)}


if __name__ == '__main__':
    print('PASS_INDEPENDENT_DECODER_WITNESS ' + json.dumps(run(), sort_keys=True))
