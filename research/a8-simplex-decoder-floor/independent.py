#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate geometric replay in standard eight-dimensional E8 coordinates.

No imports from verify.py or PR1224. Reconstructs the frozen A8 frame and
computes deficiency partners by annihilator enumeration, not the primary
pair-compatibility table. This is a second AI-written implementation, not
independent human review.
"""
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def need(x, message):
    if not x:
        raise ValueError(message)


def rank(vectors):
    # Low-bit pivot order, unlike the primary highest-bit implementation.
    pivots = [0] * 120
    for v in vectors:
        while v:
            p = (v & -v).bit_length() - 1
            if not pivots[p]:
                pivots[p] = v
                break
            v ^= pivots[p]
    return sum(bool(v) for v in pivots)


def main():
    raw = (P / 'FRAME.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == json.loads((P / 'SOURCES.json').read_text())['frame_sha256'],
         'exact predecessor frame pin')
    frame = json.loads(raw)['six_times_normals']
    roots = set()
    for a, b in combinations(range(8), 2):
        for sa, sb in product((-2, 2), repeat=2):
            v = [0] * 8
            v[a], v[b] = sa, sb
            roots.add(tuple(v))
    for signs in product((-1, 1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.add(signs)
    roots = sorted(v for v in roots if next(x for x in v if x) > 0)
    need(len(roots) == 120, '120 E8 root lines')
    scalar = lambda a, b: sum(x * y for x, y in zip(a, b))
    for j in range(9):
        for k in range(9):
            need(scalar(frame[j], frame[k]) == (32 if j == k else -4), 'simplex Gram')
    # 3r.b = dot(doubled_root, 6b)/4.
    coords = []
    for root in roots:
        v = []
        for f in frame:
            n = scalar(root, f)
            need(n % 4 == 0, 'integral triple coordinate')
            v.append(n // 4)
        need(sum(v) == 0 and scalar(v, v) == 18, 'sum-zero root embedding')
        coords.append(v)
    matrix = []
    for a in roots:
        row = 0
        for j, b in enumerate(roots):
            value = scalar(a, b)
            need(value % 4 == 0, 'integral E8 pairing')
            row |= (((value // 4 + 1) & 1) << j)
        matrix.append(row)
    need(rank(matrix) == 9, 'binary pairing rank')
    # Select independent pairing columns as explicit binary label coordinates.
    selected, cols = [], []
    for k in range(120):
        col = sum(((row >> k) & 1) << i for i, row in enumerate(matrix))
        if rank(cols + [col]) > len(cols):
            selected.append(k); cols.append(col)
    labels = [sum(((row >> k) & 1) << j for j, k in enumerate(selected)) for row in matrix]
    code = [sum(((u & w).bit_count() & 1) << i for i, u in enumerate(labels)) for w in range(512)]
    for k in range(9):
        need(rank(labels[i] for i in range(120) if coords[i][k]) == 9, 'column full rank')
    unequal = [[i for i in range(120) if coords[i][0] != coords[i][k]] for k in range(1, 9)]
    # Cache the span restrictions for each plane's support union; canonical
    # integer bitmasks here use unrelated, Gram-derived label coordinates.
    census = Counter()
    forced_counts = Counter()
    eight = 0
    total = 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if a ^ b < b:
                continue
            total += 1
            union = code[a] | code[b]
            partners = []
            for k, indices in enumerate(unequal, 1):
                constraints = [labels[i] for i in indices if union >> i & 1]
                r = rank(constraints)
                need(r >= 8, 'other annihilator dimension <=1')
                if r == 8:
                    # Solve by independently testing all 511 binary vectors.
                    w = next(w for w in range(1, 512)
                             if all((u & w).bit_count() % 2 == 0 for u in constraints))
                    partners.append((k, w))
                    f = [labels[i] for i in indices if code[w] >> i & 1]
                    rf = rank(f)
                    need(rf in (1, 7), 'forced rank 1 or 7')
                    if rf == 1:
                        edge = [i for i in range(120)
                                if sum(bool(x) for x in coords[i]) == 2 and coords[i][0] and coords[i][k]]
                        need(len(edge) == 1 and set(f) == {labels[edge[0]]}, 'rank-one edge constraint')
                    forced_counts[rf] += 1
            census[len(partners)] += 1
            if len(partners) == 8:
                eight += 1
                need(any(any((code[w] >> i & 1) and (code[z] >> i & 1) and coords[i][j] != coords[i][k]
                             for i in range(120))
                         for (j, w), (k, z) in combinations(partners, 2)), 'eight-partner conflict')
    expected = json.loads((P / 'CERTIFICATE.json').read_text())
    need(total == expected['planes'] == 43435, 'complete plane enumeration')
    need(dict(census) == {int(k): v for k, v in expected['partner_count_histogram'].items()}, 'partner census agreement')
    need(dict(forced_counts) == {int(k): v for k, v in expected['forced_rank_histogram'].items()}, 'forced rank agreement')
    need(eight == len(expected['all_eight_cases']) == 36, 'all-eight agreement')
    print('PASS_A8_SIMPLEX_INDEPENDENT E8_dimension=8 planes=43435 eight_partner_cases=36')


if __name__ == '__main__':
    main()
