#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite lemmas for the A8 simplex floor; no predecessor code imported."""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = 511


def require(condition, message):
    if not condition:
        raise ValueError(message)


def model():
    # Integer coordinates v=3r in the sum-zero subspace of Q^9.
    rows = []
    for a, b in combinations(range(9), 2):
        v = tuple(3 if k == a else -3 if k == b else 0 for k in range(9))
        rows.append((FULL ^ (1 << a) ^ (1 << b), v))
    for subset in combinations(range(9), 3):
        u = sum(1 << k for k in subset)
        rows.append((u, tuple(2 if u >> k & 1 else -1 for k in range(9))))
    return rows


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def model_checks(rows):
    require(len(rows) == 120 and len({u for u, _ in rows}) == 120, '120 distinct labels')
    require(rank(u for u, _ in rows) == 9, 'full label rank')
    for u, v in rows:
        require(sum(v) == 0 and dot(v, v) == 18, 'norm-two sum-zero roots')
        for w, z in rows:
            gram, rem = divmod(dot(v, z), 9)
            require(rem == 0, 'integral Gram')
            require(((u & w).bit_count() & 1) == ((gram + 1) & 1), 'label/Gram pairing')
    for k in range(9):
        require(rank(u for u, v in rows if v[k]) == 9, 'column support full rank')
    # Coordinate permutations preserve the root lines (up to sign), labels,
    # pairing and zero-ratio equality. Adjacent transpositions generate S9.
    lookup = {v: u for u, v in rows}
    for k in range(8):
        for u, v in rows:
            p = list(v)
            p[k], p[k + 1] = p[k + 1], p[k]
            p = tuple(p)
            if p not in lookup:
                p = tuple(-x for x in p)
            w = u
            if (u >> k & 1) != (u >> (k + 1) & 1):
                w ^= (1 << k) | (1 << (k + 1))
            require(lookup.get(p) == w, 'S9 root-label action')


def make_tables(rows):
    words = [sum((((u & w).bit_count() & 1) << i) for i, (u, _) in enumerate(rows))
             for w in range(512)]
    unequal = {(j, k): sum((v[j] != v[k]) << i for i, (_, v) in enumerate(rows))
               for j, k in combinations(range(9), 2)}
    def compatible(j, w, k, z):
        return not (words[w] & words[z] & unequal[min(j, k), max(j, k)])
    allowed = {(k, a): sum(1 << b for b in range(1, 512) if compatible(0, a, k, b))
               for k in range(1, 9) for a in range(1, 512)}
    forced = {}
    for k in range(1, 9):
        for b in range(1, 512):
            mask = words[b] & unequal[0, k]
            labels = [u for i, (u, _) in enumerate(rows) if mask >> i & 1]
            forced[k, b] = (rank(labels), labels)
    return words, unequal, compatible, allowed, forced


def census(rows, tables):
    words, unequal, compatible, allowed, forced = tables
    counts, forced_counts = Counter(), Counter()
    all_eight = []
    plane_count = 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            # The unique increasing pair a<b<a^b represents each binary plane.
            if (a ^ b) < b:
                continue
            plane_count += 1
            options = [allowed[k, a] & allowed[k, b] for k in range(1, 9)]
            require(all(x.bit_count() <= 1 for x in options), 'other deficiency dimension <=1')
            live = [(k, options[k - 1].bit_length() - 1)
                    for k in range(1, 9) if options[k - 1]]
            counts[len(live)] += 1
            for k, w in live:
                r, labels = forced[k, w]
                require(r in (1, 7), 'forced constraint rank is 1 or 7')
                if r == 1:
                    require(set(labels) == {FULL ^ 1 ^ (1 << k)}, 'rank-one edge label')
                forced_counts[r] += 1
            if len(live) == 8:
                conflicts = [(j, k) for (j, w), (k, z) in combinations(live, 2)
                             if not compatible(j, w, k, z)]
                require(conflicts, 'eight nonzero partners are incompatible')
                all_eight.append({'plane': [a, b], 'partners': [w for _, w in live],
                                  'first_conflict': list(conflicts[0])})
    require(plane_count == 511 * 510 // 6, 'complete binary-plane coverage')
    require(rank(FULL ^ 1 ^ (1 << k) for k in range(1, 9)) == 8, 'edge-label independence')
    return {'planes': plane_count, 'partner_count_histogram': dict(sorted(counts.items())),
            'forced_rank_histogram': dict(sorted(forced_counts.items())),
            'all_eight_cases': all_eight}


def witness(rows, active):
    # D=C/3, T=v/3. C=2(v-v_anchor) gives DT^t=2G.
    C = [tuple(2 * (x - v[1 if active and i == 0 else 0]) for x in v)
         for i, (_, v) in enumerate(rows)]
    check_identity(rows, C)
    costs = [rank(u for i, (u, _) in enumerate(rows) if C[i][k]) for k in range(9)]
    require(sum(costs) == 72, 'attaining total')
    if active:
        require(min(costs) > 0, 'nine active terms')
    return C, costs


def check_identity(rows, C):
    require(len(C) == 120 and all(len(c) == 9 for c in C), 'decoder shape')
    for i, (_, v) in enumerate(rows):
        for _, z in rows:
            require(dot(C[i], z) == 2 * dot(v, z), 'exact all-pairs decoder')


def controls(rows, tables, C):
    words, unequal, compatible, allowed, forced = tables
    count = 0
    def rejected(call):
        try:
            call()
        except ValueError:
            return
        raise ValueError('negative control unexpectedly accepted')
    bad = list(C)
    bad[0] = tuple(x + (1 if k == 0 else 0) for k, x in enumerate(bad[0]))
    rejected(lambda: check_identity(rows, bad)); count += 1
    bad = list(C)
    bad[0] = tuple(0 if k == 0 else x for k, x in enumerate(bad[0]))
    rejected(lambda: check_identity(rows, bad)); count += 1
    corrupted = list(rows)
    corrupted[0] = (rows[0][0] ^ 1, rows[0][1])
    rejected(lambda: model_checks(corrupted)); count += 1
    # A single deficiency vector really can have many partners. The plane
    # premise is necessary; replacing a plane by its first vector is invalid.
    require(max(x.bit_count() for x in allowed.values()) == 255, 'single-vector control'); count += 1
    # Pairwise compatibility to column 0 alone permits the false total 2+8=10.
    a, b = 1, 254
    partners = [(k, (allowed[k, a] & allowed[k, b]).bit_length() - 1) for k in range(1, 9)]
    require(all(w > 0 for _, w in partners), 'false-relaxation witness')
    require(any(not compatible(j, w, k, z) for (j, w), (k, z) in combinations(partners, 2)),
            'mutual constraint catches false saving'); count += 1
    # No cancellation (generic complex shift) gives full row supports, cost 81.
    require(sum(rank(u for u, _ in rows) for _ in range(9)) == 81, 'generic-shift control'); count += 1
    return count


def compute():
    rows = model()
    model_checks(rows)
    tables = make_tables(rows)
    result = census(rows, tables)
    _, dropped = witness(rows, False)
    C, active = witness(rows, True)
    result.update({'schema_version': 1, 'model': 'P120 A8 simplex, all-pairs, nine separate terms',
                   'all_pair_entries': 14400, 'column_label_ranks': [9] * 9,
                   'sharp_cost': 72, 'active_witness_costs': active, 'dropped_witness_costs': dropped,
                   'semantic_controls': controls(rows, tables, C)})
    # JSON normalization also normalizes integer dictionary keys.
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='explicitly regenerate CERTIFICATE.json')
    args = parser.parse_args()
    result = compute()
    path = HERE / 'CERTIFICATE.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(path.read_text()) == result, 'certificate differs from exact replay')
    print('PASS_A8_SIMPLEX_DECODER_FLOOR planes=43435 eight_partner_cases=36 cost=72 controls=6')


if __name__ == '__main__':
    main()
