#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate check: Gram-derived labels, annihilator algebra, Cartesian products.

No primary or predecessor imports. The primary checks nine anchors; here an
explicit frame stabilizer reduces the coverage to two orbits, {0,...,7}, {8}.
Separate implementation by the same AI assistant is not independent peer review.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import json
from pathlib import Path


def check(value, message):
    if not value:
        raise RuntimeError(message)


def rref(vectors, width=9):
    rows = sorted(set(vectors) - {0})
    n = 0
    for column in range(width):
        pivot = next((i for i in range(n, len(rows)) if (rows[i] >> column) & 1), None)
        if pivot is None:
            continue
        rows[n], rows[pivot] = rows[pivot], rows[n]
        for i in range(len(rows)):
            if i != n and ((rows[i] >> column) & 1):
                rows[i] ^= rows[n]
        n += 1
    return tuple(rows[:n])


@lru_cache(maxsize=100000)
def combine(a, b):
    return rref(a + b)


@lru_cache(maxsize=100000)
def annihilator(equations):
    pivots = [(x & -x).bit_length() - 1 for x in equations]
    answer = []
    for f in range(9):
        if f not in pivots:
            answer.append((1 << f) | sum(((x >> f) & 1) << p
                                         for x, p in zip(equations, pivots)))
    check(all((v & e).bit_count() % 2 == 0 for v in answer for e in equations),
          'annihilator equations')
    return tuple(answer)


def nonzero_span(basis):
    space = {0}
    for vector in basis:
        space |= {x ^ vector for x in tuple(space)}
    return tuple(sorted(space - {0}))


def geometry():
    roots = []
    for a in range(9):
        for b in range(a + 1, 9):
            row = [Fraction(0)] * 9
            row[a], row[b] = Fraction(1), Fraction(-1)
            roots.append(tuple(row))
    for subset in combinations(range(9), 3):
        roots.append(tuple(Fraction(int(k in subset)) - Fraction(1, 3) for k in range(9)))
    gram = [[sum(x * y for x, y in zip(a, b)) for b in roots] for a in roots]
    check(all(x.denominator == 1 for row in gram for x in row), 'integral Gram')
    pairing = [[(int(x) + 1) % 2 for x in row] for row in gram]
    columns, selected = [], []
    for j in range(120):
        column = sum(pairing[i][j] << i for i in range(120))
        if len(rref(columns + [column], 120)) > len(columns):
            columns.append(column)
            selected.append(j)
    check(len(columns) == 9, 'full pairing rank nine')
    labels = [sum(pairing[i][j] << p for p, j in enumerate(selected)) for i in range(120)]
    frame = (0, 15, 26, 33, 42, 89, 112, 119)
    check(all(gram[i][j] == 0 for i, j in combinations(frame, 2)), 'frame orthogonality')
    # Explicit generators preserve the puncture and are transitive on 0..7.
    swaps = [[(0, 1)], [(0, 2), (1, 3)], [(0, 4), (1, 5)], [(0, 6), (1, 7)]]
    lookup = {r: i for i, r in enumerate(roots)}
    permutations = []
    for exchanges in swaps:
        permutation = list(range(9))
        for a, b in exchanges:
            permutation[a], permutation[b] = permutation[b], permutation[a]
        images = []
        for root in roots:
            image = tuple(root[permutation[k]] for k in range(9))
            if image not in lookup:
                image = tuple(-x for x in image)
            check(image in lookup, 'root-line permutation')
            images.append(lookup[image])
        check({images[i] for i in frame} == set(frame), 'puncture stabilizer')
        permutations.append(permutation)
    orbit = {0}
    while True:
        new = orbit | {p[i] for p in permutations for i in orbit}
        if new == orbit:
            break
        orbit = new
    check(orbit == set(range(8)) and all(p[8] == 8 for p in permutations), 'anchor orbits')
    indices = [i for i in range(120) if i not in frame]
    live_roots = [roots[i] for i in indices]
    live_labels = [labels[i] for i in indices]
    for k in range(9):
        check(len(rref(u for u, r in zip(live_labels, live_roots) if r[k])) == 9,
              'column rank in Gram-derived label coordinates')
    # Direct ranks of the actual pairing submatrices, not the label shortcut.
    d = [[2 * (x - r[2 if i == 0 else 0]) for x in r] for i, r in enumerate(live_roots)]
    for i, row in enumerate(d):
        for j, root in enumerate(live_roots):
            check(sum(x * y for x, y in zip(row, root)) == 2 * gram[indices[i]][indices[j]],
                  'rational all-pairs identity')
    costs = []
    for k in range(9):
        ys = [indices[j] for j, r in enumerate(live_roots) if r[k]]
        matrix = [sum(pairing[indices[i]][j] << p for p, j in enumerate(ys))
                  for i, row in enumerate(d) if row[k]]
        costs.append(len(rref(matrix, len(ys))))
    check(costs == [1, 8, 8, 9, 9, 9, 9, 9, 9], 'direct pairing-rank witness price')
    return live_roots, live_labels, selected, permutations


def audit_anchor(roots, labels, anchor):
    others = [k for k in range(9) if k != anchor]
    equations = {}
    for k in others:
        relevant = [(u, r) for u, r in zip(labels, roots) if r[k] != r[anchor]]
        equations[k] = [rref(u for u, _ in relevant if (u & w).bit_count() % 2)
                        for w in range(512)]
    configs = {}
    dimension_hist = Counter()
    # Enumerate planes using RREF bases, not the primary's sorted nonzero pairs.
    plane_bases = set()
    for a in range(1, 512):
        for b in range(a + 1, 512):
            plane_bases.add(rref((a, b)))
    check(len(plane_bases) == 43435, 'all planes by canonical RREF')
    for a, b in sorted(plane_bases):
        spaces = tuple(nonzero_span(annihilator(combine(equations[k][a], equations[k][b])))
                       for k in others)
        dims = tuple(sorted((len(h) + 1).bit_length() - 1 for h in spaces))
        check(max(dims) <= 2, 'partner space dimensions')
        dimension_hist[dims] += 1
        configs[spaces] = configs.get(spaces, 0) + 1
    options_cache = {}
    for spaces in configs:
        for k, h in zip(others, spaces):
            key = (k, h)
            if key in options_cache:
                continue
            subspaces = [()] + [(z,) for z in h]
            if len(h) == 3:
                subspaces.append(rref(h))
            result = []
            for basis in subspaces:
                constraints = rref(x for z in basis for x in equations[k][z])
                zero_rows = frozenset(i for i, u in enumerate(labels)
                                     if any((u & z).bit_count() % 2 for z in basis))
                result.append((len(basis), constraints, zero_rows))
            options_cache[key] = result
    compatible_count = raw_count = 0
    maximum_hist = Counter()
    for spaces in configs:
        maximum = 0
        for choices in product(*(options_cache[k, h] for k, h in zip(others, spaces))):
            raw_count += 1
            # Test rowwise consistency directly: all forced-zero coordinates at
            # a row must have the same coefficient. No bitset compatibility table.
            consistent = True
            forced_value = {}
            for k, (_, _, zero_rows) in zip(others, choices):
                for row in zero_rows:
                    value = roots[row][k]
                    if row in forced_value and forced_value[row] != value:
                        consistent = False
                        break
                    forced_value[row] = value
                if not consistent:
                    break
            if not consistent:
                continue
            compatible_count += 1
            constraints = rref(x for _, equations_, _ in choices for x in equations_)
            score = 9 - len(constraints) + sum(dim for dim, _, _ in choices)
            check(score <= 10, 'deficiency upper bound')
            maximum = max(maximum, score)
        maximum_hist[maximum] += 1
    return {'anchor': anchor, 'planes': len(plane_bases), 'configurations': len(configs),
            'compatible_leaves': compatible_count, 'raw_products': raw_count,
            'maximum_histogram': {str(k): v for k, v in sorted(maximum_hist.items())},
            'partner_dimension_histogram': [{'dimensions': list(k), 'planes': v}
                                           for k, v in sorted(dimension_hist.items())]}


def main():
    roots, labels, selected, permutations = geometry()
    receipt = json.loads((Path(__file__).resolve().parent / 'CERTIFICATE.json').read_text())
    results = [audit_anchor(roots, labels, a) for a in (0, 8)]
    for result in results:
        anchors = range(8) if result['anchor'] == 0 else (8,)
        for a in anchors:
            for key in ('planes', 'configurations', 'compatible_leaves', 'maximum_histogram',
                        'partner_dimension_histogram'):
                check(result[key] == receipt['anchors'][a][key], 'primary receipt mismatch: ' + key)
    check(receipt['sharp_copy_cost'] == 71 and receipt['active_witness_costs'] ==
          [1, 8, 8, 9, 9, 9, 9, 9, 9], 'price receipt')
    print('PASS_A8_P112_INDEPENDENT anchors=2 transported=9 planes=86870 '
          'compatible_leaves=92317 cost=71')


if __name__ == '__main__':
    main()
