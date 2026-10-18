#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent geometry/elimination and integer-root budget check; no source imports."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def roots():
    vectors = []
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            v = [0] * 8
            v[a], v[b] = 2, 2 * sign
            vectors.append(tuple(v))
    for rest in product((-1, 1), repeat=7):
        v = (1,) + rest
        if sum(x < 0 for x in v) % 2 == 0:
            vectors.append(v)
    return sorted(vectors, reverse=True)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def reduce_binary(rows):
    """Gauss-Jordan rows, using low pivots; differs from predecessor elimination."""
    work = list(dict.fromkeys(rows))
    rank = 0
    for bit in range(max(work, default=0).bit_length()):
        pivot = next((j for j in range(rank, len(work)) if work[j] >> bit & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for j in range(len(work)):
            if j != rank and work[j] >> bit & 1:
                work[j] ^= work[rank]
        rank += 1
    return work[:rank]


def binary_rank(rows):
    return len(reduce_binary(rows))


def solve(matrix, target):
    n = len(matrix)
    work = [[F(x) for x in row] + [F(target[i])] for i, row in enumerate(matrix)]
    for k in range(n):
        p = next(i for i in range(k, n) if work[i][k])
        work[p], work[k] = work[k], work[p]
        d = work[k][k]
        work[k] = [x / d for x in work[k]]
        for i in range(n):
            if i != k:
                d = work[i][k]
                work[i] = [x - d * y for x, y in zip(work[i], work[k])]
    return [row[-1] for row in work]


def build():
    vectors = roots()
    need(len(vectors) == 120 and len(set(vectors)) == 120, '120 distinct roots')
    gram = [[dot(x, y) // 4 for y in vectors] for x in vectors]
    pairing = [sum(((entry + 1) % 2) << j for j, entry in enumerate(row)) for row in gram]
    frame = []
    for i in range(120):
        if all(gram[i][j] == 0 for j in frame):
            frame.append(i)
    need(len(frame) == 8, 'puncture frame')
    indices = [i for i in range(120) if i not in frame]
    live = sum(1 << i for i in indices)
    normals = [[F(x) for x in row] for row in [
        [1, 1] + [F(-1, 3)] * 6, [-1, -1] + [F(-1, 3)] * 6,
        [0, 0] + [F(2, 3)] * 6, [2, -2, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, -2, 0, 0, 0, 0], [0, 0, 2, 0, -2, 0, 0, 0],
        [0, 0, 2, 0, 0, -2, 0, 0], [0, 0, 2, 0, 0, 0, -2, 0],
        [0, 0, 2, 0, 0, 0, 0, -2]]]
    matrix = [[normals[j][i] for j in range(1, 9)] for i in range(8)]
    base = {i: [F(0)] + solve(matrix, [2 * x for x in vectors[i]]) for i in indices}
    return vectors, gram, pairing, frame, indices, live, normals, base


def charges(pairing, indices, rows, normals, vectors):
    x = [sum(1 << i for i in indices if rows[i][k]) for k in range(9)]
    y = [sum(1 << i for i in indices if dot(vectors[i], normal)) for normal in normals]
    return [binary_rank([pairing[i] & y[k] for i in indices if rows[i][k]]) for k in range(9)], x, y


def identity(gram, vectors, indices, normals, rows):
    reader = {i: [dot(vectors[i], normal) / 4 for normal in normals] for i in indices}
    return all(dot(rows[i], reader[j]) == 2 * gram[i][j] for i in indices for j in indices)


def power_lower(rank, scale):
    """floor(scale*(rank/73)^(624/625)), proved by adjacent integer powers."""
    numerator = pow(scale, 625) * pow(rank, 624)
    denominator = pow(73, 624)
    low, high = 0, scale
    while high - low > 1:
        middle = (low + high) // 2
        if pow(middle, 625) * denominator <= numerator:
            low = middle
        else:
            high = middle
    need(pow(low, 625) * denominator <= numerator < pow(low + 1, 625) * denominator,
         'integer root adjacent bounds')
    return F(low, scale)


def run():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], 'source pin')
    saved = json.loads((HERE / 'RESULT.json').read_text())
    vectors, gram, pairing, frame, indices, live, normals, base = build()
    need(frame == saved['puncture'], 'puncture binding')
    need([[str(x) for x in row] for row in normals] == saved['normal_vectors_doubled'], 'normal binding')
    need(binary_rank([pairing[i] for i in indices]) == 9, 'live label span')
    costs, _, columns = charges(pairing, indices, base, normals, vectors)
    need(costs[3:] == [8, 8, 9, 9, 9, 9], 'fixed bill')
    need([binary_rank([pairing[i] for i in indices if columns[k] >> i & 1]) for k in range(3)] == [9]*3,
         'variable column supports have full label rank')
    basis = reduce_binary(pairing)
    chars = [0]
    for b in basis:
        chars += [v ^ b for v in chars]
    need(len(set(chars)) == 512, 'complete binary character code')
    pairs = list(combinations(range(3), 2))
    relations = {}
    for pair in pairs:
        conflict = sum(1 << i for i in indices if base[i][pair[0]] != base[i][pair[1]])
        # A different character basis changes exceptional IDs, but not the theorem.
        tables = []
        for a in chars:
            mask = a & conflict
            tables.append({j for j, b in enumerate(chars) if not (mask & b)})
        exceptional = [(i, len(s)) for i, s in enumerate(tables) if i and len(s) > 4]
        need(len(exceptional) == 1, 'unique pair exception')
        need(exceptional[0][1] == (512 if pair == (0, 1) else 256), 'pair exception dimension')
        expected = saved['pair_compatibility'][str(pair)]['sizes']
        need(Counter(len(s) for s in tables[1:]) == {int(k): v for k, v in expected.items()}, 'pair histogram')
        relations[pair] = tables
    for k in range(3):
        j, ell = [q for q in range(3) if q != k]
        ab = relations[tuple(sorted((k, j)))]; ac = relations[tuple(sorted((k, ell)))]
        bc = relations[tuple(sorted((j, ell)))]
        histogram, large = Counter(), []
        for u in range(1, 512):
            for v in bc[u] - {0}:
                common = ab[u] & ac[v]
                histogram[len(common)] += 1
                if len(common) > 4:
                    large.append((u, v, common))
        need(len(large) == 1 and len(large[0][2]) == (128 if k == 2 else 256), 'triple unique exception')
        need(histogram == {int(a): b for a, b in saved['triple_compatibility'][k]['sizes'].items()}, 'triple census')
        need(1 << binary_rank(large[0][2]) == len(large[0][2]), 'large common subspace')
    rows = {i: [base[i][k] + (4 if i == 45 and k < 3 else 0) for k in range(9)] for i in indices}
    need(identity(gram, vectors, indices, normals, rows), 'all 12544 rational identities')
    costs, x, y = charges(pairing, indices, rows, normals, vectors)
    need(costs == [1, 8, 8, 8, 8, 9, 9, 9, 9] and sum(costs) == 69, 'all-active attaining cost')
    need([hex(v) for v in x] == saved['witness']['row_supports_hex'], 'actual row supports')
    need([hex(v) for v in y] == saved['witness']['column_supports_hex'], 'actual column supports')
    # Independently enclose the conditional optimistic moment at a=1/625.
    local = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 9: F(69, 9), 51: F(1646, 51)}
    lower = sum(n * power_lower(r, 10**15) for r, n in local.items()) / F(896, 9)
    need(lower > 1, 'integer-power optimistic budget rejects a=1/625')
    print('PASS_INDEPENDENT_A2_E6 copy=69 entries=12544 character_bases=independent moment_lower=' + str(lower))


if __name__ == '__main__':
    run()
