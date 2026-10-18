#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Second arithmetic implementation: Gram labels, nullspaces, Cartesian products.

Adapted from commdata2338's PR1304 independent.py at a052f0da36a3845c2ec785fd44e5b9e50de3b688
(original blob 02035af27f93aee0f0205b69a3be99fe4362fd13, Apache-2.0).
Changes: the one-pair puncture and its explicitly checked stabilizer,
anchor representatives 0 and 2, and the complementary orbit's exact receipts.
No primary or predecessor imports. Both adaptations are by the same assistant;
this is not independent peer review. Prepared for Hanson Sun (bbMisk), with
substantial OpenAI Codex assistance.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
import hashlib
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


def check_frame_coverage(roots, gram, frame):
    """Set-clique census plus the pair/Fano construction; no orbit-BFS reuse."""
    neighbors = [{j for j in range(i + 1, 120) if gram[i][j] == 0}
                 for i in range(120)]
    frames = set()

    def extend(prefix, candidates):
        if len(prefix) == 8:
            frames.add(prefix)
            return
        for i in sorted(candidates):
            remaining = candidates & neighbors[i]
            if len(prefix) + 1 + len(remaining) >= 8:
                extend(prefix + (i,), remaining)

    extend((), set(range(120)))
    check(len(frames) == 2025, 'complete rational Gram frame census')
    one_pair = {f for f in frames if sum(i < 36 for i in f) == 1}
    matching = {f for f in frames if sum(i < 36 for i in f) == 4}
    check(len(one_pair) == 1080 and len(matching) == 945 and
          one_pair | matching == frames, 'independent frame partition')
    # The representative's seven triple roots give a labeled Fano plane.
    lines = [tuple(k - 2 for k, x in enumerate(roots[i]) if x > 0)
             for i in frame if i >= 36]
    check(len(lines) == 7 and all(len(t) == 3 for t in lines), 'Fano seed')
    planes = {tuple(sorted(tuple(sorted(p[k] for k in t)) for t in lines))
              for p in permutations(range(7))}
    check(len(planes) == 30, 'all coordinate images of the Fano plane')
    lookup = {r: i for i, r in enumerate(roots)}
    constructed = set()
    for a, b in combinations(range(9), 2):
        others = [k for k in range(9) if k not in (a, b)]
        pair = tuple(Fraction(int(k == a) - int(k == b)) for k in range(9))
        for plane in planes:
            indices = [lookup[pair]]
            for t in plane:
                triple = {others[k] for k in t}
                root = tuple(Fraction(int(k in triple)) - Fraction(1, 3) for k in range(9))
                indices.append(lookup[root])
            constructed.add(tuple(sorted(indices)))
    check(constructed == one_pair, 'Fano construction exactly covers the complementary orbit')
    def digest(fs):
        return hashlib.sha256(json.dumps(sorted(fs), separators=(',', ':')).encode()).hexdigest()
    return {'all_frames_sha256': digest(frames), 'one_pair_orbit_sha256': digest(one_pair)}


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
    frame = (0, 85, 94, 99, 105, 108, 112, 113)
    check(all(gram[i][j] == 0 for i, j in combinations(frame, 2)), 'frame orthogonality')
    frame_coverage = check_frame_coverage(roots, gram, frame)
    # Explicit puncture stabilizer; the two anchor orbits are {0,1}, {2,...,8}.
    permutations = [
        [1, 0, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 3, 2, 4, 5, 7, 6, 8],
        [0, 1, 4, 2, 3, 5, 8, 6, 7],
        [0, 1, 5, 2, 6, 3, 7, 4, 8],
        [0, 1, 6, 2, 5, 3, 8, 4, 7],
        [0, 1, 7, 2, 8, 3, 5, 4, 6],
        [0, 1, 8, 2, 7, 3, 6, 4, 5],
    ]
    lookup = {r: i for i, r in enumerate(roots)}
    for permutation in permutations:
        check(sorted(permutation) == list(range(9)), 'coordinate permutation')
        images = []
        for root in roots:
            image = tuple(root[permutation[k]] for k in range(9))
            if image not in lookup:
                image = tuple(-x for x in image)
            check(image in lookup, 'root-line permutation')
            images.append(lookup[image])
        check({images[i] for i in frame} == set(frame), 'puncture stabilizer')
    for representative, expected in [(0, {0, 1}), (2, set(range(2, 9)))]:
        orbit = {representative}
        while True:
            new = orbit | {p[i] for p in permutations for i in orbit}
            if new == orbit:
                break
            orbit = new
        check(orbit == expected, 'anchor orbit')
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
    return live_roots, live_labels, selected, permutations, frame_coverage


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
    roots, labels, selected, permutations, frame_coverage = geometry()
    receipt = json.loads((Path(__file__).resolve().parent / 'CERTIFICATE.json').read_text())
    for key, value in frame_coverage.items():
        check(value == receipt['frame_partition'][key], 'frame census receipt: ' + key)
    results = [audit_anchor(roots, labels, a) for a in (0, 2)]
    for result in results:
        anchors = (0, 1) if result['anchor'] == 0 else range(2, 9)
        for a in anchors:
            for key in ('planes', 'configurations', 'compatible_leaves', 'maximum_histogram',
                        'partner_dimension_histogram'):
                check(result[key] == receipt['anchors'][a][key], 'primary receipt mismatch: ' + key)
    check(receipt['sharp_copy_cost'] == 71 and receipt['active_witness_costs'] ==
          [1, 8, 8, 9, 9, 9, 9, 9, 9], 'price receipt')
    print('PASS_A8_ONE_PAIR_SECOND_CHECK anchors=2 transported=9 planes=86870 '
          f"compatible_leaves={sum(r['compatible_leaves'] for r in results)} cost=71")


if __name__ == '__main__':
    main()
