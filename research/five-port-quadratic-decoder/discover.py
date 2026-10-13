#!/usr/bin/env python3
"""Construct finite rank witnesses; not trusted by verify.py.

Copyright 2026 Ross Richardson. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
"""
from itertools import combinations, product
from pathlib import Path
import json
import random

HERE = Path(__file__).resolve().parent
PRIME = 65521
SEED = 40


def ports(p):
    return [sum(1 << (2 * i + b) for i, b in zip(indices, bits))
            for indices in combinations(range(p), 5)
            for bits in product(range(2), repeat=5)]


def gram(a, b):
    j = (a & b).bit_count()
    return 2 * (j - 1) * (j - 3)


def feature_basis(candidates, p, target_size):
    coordinates = [(i, j) for i in range(2 * p) for j in range(i + 1, 2 * p)
                   if i // 2 != j // 2]
    basis = {}
    chosen = []
    visited = 0
    for port in candidates:
        visited += 1
        row = [1] + [(port >> i) & 1 for i in range(2 * p)]
        row += [int(bool(port & (1 << i)) and bool(port & (1 << j)))
                for i, j in coordinates]
        for col in sorted(basis):
            if row[col]:
                factor = row[col]
                other = basis[col]
                row[col:] = [(x - factor * y) % PRIME
                             for x, y in zip(row[col:], other[col:])]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is None:
            continue
        inv = pow(row[pivot], -1, PRIME)
        basis[pivot] = [(x * inv) % PRIME for x in row]
        chosen.append(port)
        if len(chosen) == target_size:
            return chosen, visited
    raise RuntimeError((p, target_size, len(chosen)))


def minor(matrix):
    rows = [row[:] for row in matrix]
    original = list(range(len(rows)))
    row_ids, col_ids = [], []
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col] % PRIME), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        original[rank], original[pivot] = original[pivot], original[rank]
        row_ids.append(original[rank])
        col_ids.append(col)
        inv = pow(rows[rank][col], -1, PRIME)
        row = [(x * inv) % PRIME for x in rows[rank]]
        rows[rank] = row
        for i in range(rank + 1, len(rows)):
            factor = rows[i][col] % PRIME
            if factor:
                rows[i][col:] = [(x - factor * y) % PRIME
                                for x, y in zip(rows[i][col:], row[col:])]
        rank += 1
    return row_ids, col_ids


def determinant(matrix):
    rows = [row[:] for row in matrix]
    det = 1
    for col in range(len(rows)):
        pivot = next((i for i in range(col, len(rows)) if rows[i][col] % PRIME), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            det = -det
        value = rows[col][col] % PRIME
        det = det * value % PRIME
        inv = pow(value, -1, PRIME)
        for i in range(col + 1, len(rows)):
            factor = rows[i][col] * inv % PRIME
            if factor:
                rows[i][col:] = [(x - factor * y) % PRIME
                                for x, y in zip(rows[i][col:], rows[col][col:])]
    return det % PRIME


def main():
    witnesses = []
    target = sum(1 << (2 * i) for i in range(5))
    for p in range(5, 14):
        domain = ports(p)
        for kind in ('corrector', 'star'):
            if p == 13 and kind == 'star':
                continue
            if kind == 'corrector':
                candidates = [x for x in domain if (x & target).bit_count() in (1, 3)]
                size = {5: 15, 6: 50}.get(p, 2 * p * (p - 1) - 1)
            else:
                candidates = [x for x in domain if x & 1]
                size = {5: 11, 6: 35}.get(p, 2 * (p - 1) * (p - 2))
            random.Random(SEED + 100 * p + (kind == 'star')).shuffle(candidates)
            basis, visited = feature_basis(candidates, p, size)
            rows, cols = minor([[gram(a, b) for b in basis] for a in basis])
            left, right = [basis[i] for i in rows], [basis[i] for i in cols]
            det = determinant([[gram(a, b) for b in right] for a in left])
            if not det:
                raise RuntimeError('singular selected minor')
            witnesses.append(dict(p=p, kind=kind, target=target if kind == 'corrector' else 1,
                                  rank_lower=len(rows), rows=left, columns=right,
                                  determinant_mod_prime=det,
                                  candidate_count=len(candidates), candidates_visited=visited,
                                  feature_basis_size=len(basis)))
            print(p, kind, 'rank >=', len(rows), 'visited', visited, '/', len(candidates), flush=True)
    output = dict(schema='five-port-quadratic-rank-witnesses-v1', seed=SEED, prime=PRIME,
                  kernel_coefficients=[6, -8, 2], witnesses=witnesses)
    path = HERE / 'WITNESSES.json'
    if path.exists():
        raise SystemExit('refusing to overwrite WITNESSES.json')
    path.write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
