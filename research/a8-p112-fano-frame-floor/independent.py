#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate finite replay: Gram labels, annihilators and forced-value products.

Imports neither verify.py nor the predecessor. This is a second implementation
by the same AI assistant, not independent human review. The mathematical method
is credited to PR1248/PR1304 in README.md.
"""

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATCHING = (0, 15, 26, 33, 42, 89, 112, 119)
FANO = (0, 85, 94, 99, 105, 108, 112, 113)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask -= b


def echelon(vectors):
    basis = {}
    for v in vectors:
        while v:
            i = v.bit_length() - 1
            if i not in basis:
                basis[i] = v
                break
            v ^= basis[i]
    return basis


def annihilator(vectors):
    rows = echelon(vectors)
    generators = []
    for free in sorted(set(range(9)) - rows.keys()):
        x = 1 << free
        for pivot in sorted(rows):
            if (rows[pivot] & x).bit_count() % 2:
                x |= 1 << pivot
        check(all((v & x).bit_count() % 2 == 0 for v in rows.values()),
              'nullspace equation')
        generators.append(x)
    span = [0]
    for x in generators:
        span += [v ^ x for v in span]
    return tuple(sorted(v for v in span if v))


def roots():
    out = []
    for i, j in combinations(range(9), 2):
        r = [0] * 9
        r[i], r[j] = 3, -3
        out.append(tuple(r))
    for triple in combinations(range(9), 3):
        r = [-1] * 9
        for i in triple:
            r[i] = 2
        out.append(tuple(r))
    return out


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def all_frames(rs):
    neighbors = [{j for j in range(120) if j != i and dot(rs[i], rs[j]) == 0}
                 for i in range(120)]
    frames = set()

    def extend(prefix, candidates):
        if len(prefix) == 8:
            frames.add(prefix)
            return
        for i in sorted(candidates):
            rest = {j for j in candidates & neighbors[i] if j > i}
            if len(rest) >= 7 - len(prefix):
                extend(prefix + (i,), rest)

    extend((), set(range(120)))
    return frames


def matchings(xs):
    if not xs:
        yield ()
    else:
        for b in xs[1:]:
            for tail in matchings(tuple(x for x in xs[1:] if x != b)):
                yield ((xs[0], b),) + tail


def combinatorial_orbits(rs):
    pairs = {tuple(i for i, x in enumerate(r) if x): n for n, r in enumerate(rs[:36])}
    triples = {tuple(i for i, x in enumerate(r) if x == 2): n
               for n, r in enumerate(rs) if n >= 36}
    matching = set()
    for singleton in range(9):
        for blocks in matchings(tuple(i for i in range(9) if i != singleton)):
            f = [pairs[b] for b in blocks]
            f += [triples[tuple(sorted((*b, singleton)))] for b in blocks]
            matching.add(tuple(sorted(f)))
    template = [tuple(i - 2 for i, x in enumerate(rs[n]) if x == 2) for n in FANO[1:]]
    systems = {tuple(sorted(tuple(sorted(p[i] for i in line)) for line in template))
               for p in permutations(range(7))}
    check(len(systems) == 30, 'thirty labelled Fano planes')
    fano = set()
    for pair in pairs:
        remaining = [i for i in range(9) if i not in pair]
        for lines in systems:
            f = [pairs[pair]] + [triples[tuple(remaining[i] for i in line)] for line in lines]
            fano.add(tuple(sorted(f)))
    check(len(matching) == 945 and len(fano) == 1080, 'combinatorial orbit counts')
    check(not matching & fano, 'orbits disjoint')
    check(matching | fano == all_frames(rs), 'all frames covered by explicit coordinate images')
    return matching, fano


def stabilizer_orbits(rs, frame):
    lookup = {r: n for n, r in enumerate(rs)}
    lookup.update({tuple(-x for x in r): n for n, r in enumerate(rs)})
    actions = []
    if frame == FANO:
        for tail in permutations(range(2, 9)):
            p = (0, 1) + tail
            image = {lookup[tuple(rs[n][p[i]] for i in range(9))] for n in frame}
            if image == set(frame):
                actions.append(p)
        check(len(actions) == 168, 'Fano automorphism count')
        actions.append((1, 0, 2, 3, 4, 5, 6, 7, 8))
    else:
        for i in (0, 2, 4, 6):
            p = list(range(9))
            p[i], p[i + 1] = p[i + 1], p[i]
            actions.append(tuple(p))
        for i in (0, 2, 4):
            p = list(range(9))
            p[i:i + 4] = p[i + 2:i + 4] + p[i:i + 2]
            actions.append(tuple(p))
    for p in actions:
        check({lookup[tuple(rs[n][p[i]] for i in range(9))] for n in frame} == set(frame),
              'anchor transport must preserve puncture')
    result = []
    remaining = set(range(9))
    while remaining:
        orbit = {min(remaining)}
        while True:
            expanded = orbit | {p[i] for i in orbit for p in actions}
            if expanded == orbit:
                break
            orbit = expanded
        result.append(sorted(orbit))
        remaining -= orbit
    return result


def gram_model(rs, frame):
    live = [r for n, r in enumerate(rs) if n not in frame]
    check(all(sum(r) == 0 and dot(r, r) == 18 for r in rs), 'E8 norms and sum-zero space')
    gram = [[dot(r, s) for s in live] for r in live]
    check(all(g % 9 == 0 for row in gram for g in row), 'integral normalized Gram matrix')
    parity = [sum(((g // 9 + 1) % 2) << j for j, g in enumerate(row)) for row in gram]
    pivots = sorted(echelon(parity))
    check(len(pivots) == 9, 'Gram pairing rank nine')
    labels = [sum(((row >> p) & 1) << j for j, p in enumerate(pivots)) for row in parity]
    check(len(echelon(labels)) == 9, 'injective row-space coordinates')
    for k in range(9):
        check(len(echelon(l for l, r in zip(labels, live) if r[k])) == 9,
              'each column support spans nine')
    # Rank modulo 101 proves rank at least eight over Q; sum zero proves at most eight.
    basis = {}
    for r in live:
        v = [x % 101 for x in r]
        for j in range(9):
            if v[j]:
                if j in basis:
                    c = v[j]
                    v = [(x - c * y) % 101 for x, y in zip(v, basis[j])]
                else:
                    inv = pow(v[j], -1, 101)
                    basis[j] = [(x * inv) % 101 for x in v]
                    break
    check(len(basis) == 8, 'live root rank eight')
    return live, labels, parity


def anchor_census(live, labels, anchor):
    evaluations = [sum(((l & w).bit_count() % 2) << i for i, l in enumerate(labels))
                   for w in range(512)]
    others = [k for k in range(9) if k != anchor]
    unequal = {k: sum((r[k] != r[anchor]) << i for i, r in enumerate(live)) for k in others}

    @lru_cache(None)
    def partner(cut):
        h = annihilator(labels[i] for i in bits(cut))
        check(len(h) in (0, 1, 3), 'partner dimension exceeds two')
        return h

    configurations = set()
    plane_count = 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if b < (a ^ b):
                plane_count += 1
                cut = evaluations[a] | evaluations[b]
                configurations.add(tuple(partner(cut & unequal[k]) for k in others))
    check(plane_count == 43435, 'exhaustive plane enumeration')
    values = sorted({x for r in live for x in r})
    row_values = {k: [sum((r[k] == v) << i for i, r in enumerate(live)) for v in values]
                  for k in others}

    @lru_cache(None)
    def options(k, h):
        subspaces = [(0, ())] + [(1, (w,)) for w in h]
        if len(h) == 3:
            check(h[0] ^ h[1] == h[2], 'plane closure')
            subspaces.append((2, h))
        result = []
        for dimension, vectors in subspaces:
            forced = 0
            for w in vectors:
                forced |= evaluations[w]
            result.append((dimension, tuple(forced & m for m in row_values[k]),
                           forced & unequal[k]))
        return tuple(result)

    @lru_cache(None)
    def rank_cut(cut):
        return len(echelon(labels[i] for i in bits(cut)))

    maxima = Counter()
    leaves = 0
    for hs in configurations:
        maximum = 0
        for choice in product(*(options(k, h) for k, h in zip(others, hs))):
            assigned = [0] * len(values)
            assigned_any = constraints = dimensions = 0
            valid = True
            for dimension, masks, cut in choice:
                if any(mask & (assigned_any ^ assigned[i]) for i, mask in enumerate(masks)):
                    valid = False
                    break
                for i, mask in enumerate(masks):
                    assigned[i] |= mask
                    assigned_any |= mask
                constraints |= cut
                dimensions += dimension
            if valid:
                leaves += 1
                maximum = max(maximum, 9 - rank_cut(constraints) + dimensions)
        check(maximum <= 10, 'total deficiency exceeds ten')
        maxima[maximum] += 1
    return {'anchor': anchor, 'planes': plane_count, 'configurations': len(configurations),
            'compatible_leaves': leaves, 'maximum_histogram': dict(sorted(maxima.items()))}


def witness(live, parity):
    coefficients = [tuple(2 * (x - r[2 if i == 0 else 0]) for x in r)
                    for i, r in enumerate(live)]
    check(all(dot(c, s) == 2 * dot(r, s) for c, r in zip(coefficients, live) for s in live),
          'full all-pairs witness identity')
    costs = []
    for k in range(9):
        columns = sum((r[k] != 0) << i for i, r in enumerate(live))
        costs.append(len(echelon(row & columns for row, c in zip(parity, coefficients) if c[k])))
    check(costs == [1, 8, 8, 9, 9, 9, 9, 9, 9], 'direct pairing-submatrix costs')
    return costs


def main():
    receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
    check(receipt['sharp_copy_cost'] == 71 and receipt['frames'] == 2025, 'headline receipt')
    rs = roots()
    matching, fano = combinatorial_orbits(rs)
    total_planes = total_leaves = 0
    for name, frame, orbit in [('matching', MATCHING, matching), ('fano', FANO, fano)]:
        expected = next(x for x in receipt['orbits'] if x['name'] == name)
        check(expected['frame'] == list(frame) and expected['orbit_size'] == len(orbit), 'frame receipt')
        coordinate_orbits = stabilizer_orbits(rs, frame)
        check(coordinate_orbits == ([list(range(8)), [8]] if name == 'matching' else
                                     [[0, 1], list(range(2, 9))]), 'anchor orbit partition')
        live, labels, parity = gram_model(rs, frame)
        check(witness(live, parity) == expected['active_witness_costs'], 'witness receipt')
        check([a['anchor'] for a in expected['anchors']] == list(range(9)), 'all anchors recorded')
        for orbit in coordinate_orbits:
            result = anchor_census(live, labels, orbit[0])
            for a in orbit:
                for key in ('planes', 'configurations', 'compatible_leaves', 'maximum_histogram'):
                    check(json.loads(json.dumps(result[key])) == expected['anchors'][a][key],
                          f'{name} anchor {a}: independent {key} mismatch')
            total_planes += result['planes']
            total_leaves += result['compatible_leaves']
    print(f'PASS_A8_P112_INDEPENDENT frames=2025 anchors=4 transported=18 '
          f'planes={total_planes} compatible_leaves={total_leaves} sharp_cost=71')


if __name__ == '__main__':
    main()
