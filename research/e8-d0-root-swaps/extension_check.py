#!/usr/bin/env python3
"""Two-model checks for the cost-seven root-only extension and C1 subcase.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The model and predecessor geometric reduction are credited in PROOF.md.
This module imports no primary verifier and does not rerun its C7 checks.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json

import geometry_audit


class ExtensionError(ValueError):
    """A mathematical assertion or coverage check failed."""


def need(condition, message):
    if not condition:
        raise ExtensionError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def canonical(vector):
    return tuple(vector) if next(x for x in vector if x) > 0 else tuple(-x for x in vector)


def rank(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def compact_labels(values):
    """Coordinates in a basis of the Gram-character image, without an E8 chart."""
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot][0]
            else:
                pivots[pivot] = (value, 1 << len(pivots))
                break
    need(len(pivots) == 9, 'Gram-character label image is not nine-dimensional')
    result = []
    for value in values:
        coordinate = 0
        while value:
            basis, bit = pivots[value.bit_length() - 1]
            value ^= basis
            coordinate ^= bit
        result.append(coordinate)
    return result


def integral_lines(fours, twos):
    result = set()
    for large in combinations(range(8), fours):
        for small in combinations([i for i in range(8) if i not in large], twos):
            for signs in product((-1, 1), repeat=fours + twos):
                vector = [0] * 8
                for i, sign in zip(large + small, signs):
                    vector[i] = sign * (4 if i in large else 2)
                if sum(vector) % 4 == 0:
                    result.add(canonical(vector))
    return result


def half_lines(count=0, large=3):
    result = set()
    for positions in combinations(range(8), count):
        for signs in product((-1, 1), repeat=8):
            vector = tuple(sign * (large if i in positions else 1) for i, sign in enumerate(signs))
            if sum(vector) % 4 == 0:
                result.add(canonical(vector))
    return result


def simple_supports(roots):
    # Only parabolic membership uses this rational basis. Labels below use
    # all 120 Gram characters, independently of simple-root coordinates.
    simple = ((1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0),
              (-2, 2, 0, 0, 0, 0, 0, 0), (0, -2, 2, 0, 0, 0, 0, 0),
              (0, 0, -2, 2, 0, 0, 0, 0), (0, 0, 0, -2, 2, 0, 0, 0),
              (0, 0, 0, 0, -2, 2, 0, 0), (0, 0, 0, 0, 0, -2, 2, 0))
    rows = [[Fraction(simple[j][i]) for j in range(8)]
            + [Fraction(i == j) for j in range(8)] for i in range(8)]
    for column in range(8):
        pivot = next(i for i in range(column, 8) if rows[i][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(8):
            if i != column:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[column])]
    coordinates = [tuple(dot(row[8:], root) for row in rows) for root in roots]
    need(all(x.denominator == 1 for row in coordinates for x in row), 'nonintegral root coordinates')
    return [sum(1 << i for i, x in enumerate(row) if x) for row in coordinates]


def direct_model():
    roots = sorted(integral_lines(0, 2) | half_lines())
    raw = [1 | sum(((dot(root, other) // 4) % 2) << (i + 1)
                   for i, other in enumerate(roots)) for root in roots]
    norm4 = integral_lines(1, 0) | integral_lines(0, 4) | half_lines(1)
    norm8 = (integral_lines(2, 0) | integral_lines(1, 4) | integral_lines(0, 8)
             | half_lines(3) | half_lines(1, 5)) - {tuple(2 * x for x in r) for r in roots}
    return roots, compact_labels(raw), simple_supports(roots), sorted(norm4), sorted(norm8)


def cartan_model():
    model = geometry_audit.CartanModel()
    pairs = sorted((canonical(model.to_doubled(root)), i) for i, root in enumerate(model.roots))
    roots = [root for root, _ in pairs]
    labels = [model.labels[i] for _, i in pairs]
    supports = [sum(1 << j for j, x in enumerate(model.roots[i]) if x) for _, i in pairs]
    normals = []
    for norm, count in ((4, 1080), (8, 8640)):
        seeds = [tuple(model.inverse[i][j] for i in range(8)) for j in range(8)]
        seed = next(vector for vector in seeds if model.inner(vector, vector) == norm)
        normals.append(sorted(canonical(model.to_doubled(vector))
                              for vector in model.vector_orbit(seed, count)))
    return roots, labels, supports, *normals


def pair_certificate(points, pairs, labels):
    need(len(points) == 12 and len(pairs) == 6, 'six-pair certificate cardinality')
    need(len({i for pair in pairs for i in pair}) == 12, 'six-pair disjoint cover')
    need({i for pair in pairs for i in pair} == set(points), 'six-pair point inventory')
    xors = {labels[a] ^ labels[b] for a, b in pairs}
    need(len(xors) == 1 and 0 not in xors, 'six-pair common nonzero XOR')
    need(rank(labels[i] for i in points) == 7, 'deletion rank seven')
    for first, second in combinations(pairs, 2):
        need(rank(labels[i] for i in first + second) == 3, 'pair-union four-element circuit')


def check_model(model):
    roots, labels, supports, norm4, norm8 = model
    need(len(roots) == len(set(roots)) == 120 and len(set(labels)) == 120, 'root/label inventory')
    need(rank(labels) == 9 and len(norm4) == 1080 and len(norm8) == 8640, 'model dimensions')
    need(all(dot(r, r) == 8 for r in roots) and all(dot(h, h) == 16 for h in norm4)
         and all(dot(h, h) == 32 for h in norm8), 'root and normal norms')
    frame = []
    for sign in (1, -1):
        for pair in range(4):
            root = [0] * 8
            root[2 * pair], root[2 * pair + 1] = 2, 2 * sign
            frame.append(roots.index(tuple(root)))
    p = [i for i in range(120) if i not in frame]
    p_mask = sum(1 << i for i in p)
    index = {root: i for i, root in enumerate(roots)}
    cuts = [sum(1 << i for i in p if (normal & labels[i]).bit_count() % 2)
            for normal in range(1, 512)]
    def mask_points(mask):
        while mask:
            bit = mask & -mask
            yield bit.bit_length() - 1
            mask ^= bit
    def off(normal):
        return sum(1 << i for i in p if dot(normal, roots[i]))
    types = Counter((subset.bit_count(), sum(s & ~subset == 0 for s in supports))
                    for subset in range(255))
    large = sorted(key for key in types if key[1] >= 27)
    need(large == [(6, 30), (6, 36), (7, 28), (7, 37), (7, 42), (7, 63)]
         and all(types[key] == 1 for key in large), 'threshold-27 proper parabolics')
    profile = Counter()
    critical = {}
    fixture = None
    for h in norm4:
        source = off(h)
        for cut in cuts:
            deletion = source & cut
            if deletion.bit_count() > 21:
                continue
            points = list(mask_points(deletion))
            r = rank(labels[i] for i in points)
            profile[(len(points), r)] += 1
            if r != 7:
                continue
            need(h not in critical, 'multiple critical cuts for one normal')
            need(set(points) == {i for i in p if abs(dot(h, roots[i])) == 8}, 'critical deletion coordinates')
            pairs = set()
            for i in points:
                oriented = roots[i] if dot(h, roots[i]) > 0 else tuple(-x for x in roots[i])
                partner = canonical(tuple(x - y for x, y in zip(h, oriented)))
                need(partner in index and index[partner] != i, 'root pair closure')
                pairs.add(tuple(sorted((i, index[partner]))))
            pairs = sorted(pairs)
            pair_certificate(points, pairs, labels)
            critical[h] = deletion
            if h == (2, 2, 2, 2, 0, 0, 0, 0):
                fixture = h, source, deletion, points, pairs
    need(profile == Counter({(12, 7): 56, (13, 8): 896, (14, 8): 128}), 'norm-four small-deletion profile')
    frame_pairs = {canonical(tuple(x + sign * y for x, y in zip(roots[a], roots[b])))
                   for a, b in combinations(frame, 2) for sign in (-1, 1)}
    need(set(critical) == frame_pairs and len(frame_pairs) == 56, 'critical normals exactly frame sums/differences')
    norm8_extra = Counter()
    for h in norm8:
        source = off(h)
        if source.bit_count() == 85:
            norm8_extra[min((source & cut).bit_count() for cut in cuts)] += 1
    need(norm8_extra == Counter({25: 3584}), 'norm-eight Off85 extension')
    root_off = [sum(1 << j for j, other in enumerate(roots) if dot(root, other)) for root in roots]
    planes = {root_off[i] | root_off[j] for i, j in combinations(range(120), 2)
              if not dot(roots[i], roots[j])}
    need(len(planes) == 3780, 'orthogonal-root plane inventory')
    plane_extra = Counter()
    for source in planes:
        source &= p_mask
        if source.bit_count() == 85:
            plane_extra[min((source & cut).bit_count() for cut in cuts)] += 1
    need(plane_extra == Counter({25: 448}), 'orthogonal-plane Off85 extension')
    blocks = {frozenset(j for j, f in enumerate(frame) if dot(roots[i], roots[f])) for i in p}
    need(len(blocks) == 14 and all(len(block) == 4 for block in blocks), 'nonframe four-incidence')
    need(all(len(a & b) % 2 == 0 for a, b in combinations(blocks, 2)), 'even frame-support intersections')
    private = {}
    for count in (4, 5, 6):
        available = [sum(any(block & set(chosen) == {j} for block in blocks) for j in chosen)
                     for chosen in combinations(range(8), count)]
        private[count] = max(available)
    need(private == {4: 4, 5: 1, 6: 0}, 'four-private sharp control / five-private exclusion')
    need(fixture is not None, 'displayed dimension-one fixture was not checked')
    h, source, deletion, points, pairs = fixture
    corrected = source ^ deletion
    need(dot(h, h) == 16 and rank(labels[i] for i in points) == 7, 'dimension-one cost-seven fixture')
    need(all(any(h[i] * r[j] != h[j] * r[i] for i, j in combinations(range(8), 2)) for r in roots),
         'dimension-one direction must be nonroot')
    tau = {i: -dot(h, roots[i]) // 4 for i in points}
    coefficients = {i: dot(h, roots[i]) // 4 + tau.get(i, 0) for i in p}
    need({i for i, value in coefficients.items() if value} == set(mask_points(corrected)),
         'literal correction coefficients')
    need(rank(labels[i] for i in mask_points(corrected)) == 8, 'dimension-one corrected weight eight')
    need(all(rank([labels[i] for i in mask_points(corrected)] + [labels[t]]) == 9 for t in points),
         'all twelve correction coordinates are essential')
    eligible = [t for t in points if all(dot(roots[t], roots[s]) for s in points if s != t)]
    need(not eligible, 'dimension-one fixture is not an exact-root-swap counterexample')
    hyperplane_basis = []
    for i in mask_points(corrected):
        if rank([labels[j] for j in hyperplane_basis] + [labels[i]]) > len(hyperplane_basis):
            hyperplane_basis.append(i)
    need(len(hyperplane_basis) == 8, 'fixture hyperplane basis')
    need(all(rank([labels[i] for i in hyperplane_basis] + [labels[f]]) == 9 for f in frame),
         'fixture hyperplane excludes all frame labels')
    # A real cost-eight boundary, not a decoder or a C1 counterexample.
    h8 = (2, 2, 2, 0, 2, 0, 0, 0)
    unit = index[(0, 0, 2, 0, 2, 0, 0, 0)]
    d8 = [i for i in p if abs(dot(h8, roots[i])) == 8]
    d0 = [i for i in d8 if i != unit]
    need(h8 in norm4 and unit in d8 and len(d8) == 13 and len(d0) == 12, 'cost-eight boundary supports')
    need(rank(labels[i] for i in d0) == 7 and rank(labels[i] for i in d8) == 8,
         'cost-eight basis and union lower bound')
    q0 = {i: -dot(h8, roots[i]) // 4 for i in d0}
    corrected8 = [i for i in p if dot(h8, roots[i]) // 4 + q0.get(i, 0) - 2 * (i == unit)]
    alone8 = [i for i in p if dot(h8, roots[i]) // 4 + q0.get(i, 0)]
    need(len(corrected8) == 60 and rank(labels[i] for i in corrected8) == 8
         and rank(labels[i] for i in alone8) == 9, 'cost-eight literal corrected weights')
    need(set(corrected8) == {i for i in p if (dot(h8, roots[i]) // 4) % 2}, 'cost-eight hyperplane equation')
    carrying = [j for j, f in enumerate(frame) if rank([labels[i] for i in corrected8] + [labels[f]]) == 8]
    need(carrying == [1, 2, 5, 6] and all(dot(h8, roots[frame[j]]) for j in carrying),
         'cost-eight actual span carries four relevant frame labels')
    need(all(any(h8[i] * r[j] != h8[j] * r[i] for i, j in combinations(range(8), 2)) for r in roots),
         'cost-eight boundary direction must be nonroot')
    need(min((off(h8) & cut).bit_count() for cut in cuts) == 13, 'cost-eight necessary deletion control')
    rejected = 0
    damaged = [pairs[:-1], pairs[:-1] + [pairs[0]],
               [(pairs[0][0], pairs[1][0]), (pairs[0][1], pairs[1][1])] + pairs[2:]]
    for wrong in damaged:
        try:
            pair_certificate(points, wrong, labels)
        except ExtensionError:
            rejected += 1
    need(rejected == 3, 'corrupt pair certificates were accepted')
    return {'parabolic_threshold': 27, 'large_proper_types': [list(key) for key in large],
            'norm4_small_deletions': [list(key) + [value] for key, value in sorted(profile.items())],
            'connected_rank7_deletions': len(critical), 'common_xor_pairs_per_deletion': 6,
            'four_circuits_per_deletion': 15, 'norm8_off85': [85, 25, 3584],
            'orthogonal_plane_off85': [85, 25, 448], 'frame_support_blocks': len(blocks),
            'maximum_private_choices': {str(key): value for key, value in private.items()},
            'dimension_one_fixture': {'h_doubled': list(h), 'tau_support': len(points),
                                      'tau_weight': 7, 'corrected_weight': 8, 'essential_coordinates': 12,
                                      'tau_entries': [[list(roots[i]), tau[i]] for i in points],
                                      'hyperplane_basis_doubled': [list(roots[i]) for i in hyperplane_basis],
                                      'hyperplane_carries_frame': False,
                                      'eligible_root_count': len(eligible)},
            'dimension_two_cost_eight_fixture': {
                'scope': 'correction-space boundary only', 'h_doubled': list(h8),
                'basis_weights': [7, 1], 'dimension': 2, 'exact_cost': 8, 'union_label_rank': 8,
                'q0_entries': [[list(roots[i]), q0[i]] for i in d0],
                'unit_root_doubled': list(roots[unit]), 'tau_unit_coefficient': -2,
                'tau_support': len(d8), 'q0_alone_corrected_weight': 9,
                'corrected_support': 60, 'corrected_weight': 8, 'carried_frame_indices': carrying},
            'negative_controls_rejected': rejected}


def f1_checks(model, use_cartan):
    """Sharp support-cardinality boundary: F1 holds through24, fails at25."""
    roots, labels, supports, norm4, _ = model
    frame = []
    for sign in (1, -1):
        for j in range(4):
            vector = [0] * 8
            vector[2 * j], vector[2 * j + 1] = 2, 2 * sign
            frame.append(roots.index(tuple(vector)))
    p = [i for i in range(120) if i not in frame]
    p_mask = sum(1 << i for i in p)
    root_off = [sum(1 << j for j, root in enumerate(roots) if dot(h, root)) for h in roots]
    ov = {v: p_mask ^ ((root_off[v] & p_mask) ^ (1 << v)) for v in p}
    need(all(mask.bit_count() == 60 for mask in ov.values()), 'F1 orthogonality-set definition')
    types = sorted((subset.bit_count(), sum(s & ~subset == 0 for s in supports))
                   for subset in range(255) if sum(s & ~subset == 0 for s in supports) >= 35)
    need(types == [(6, 36), (7, 37), (7, 42), (7, 63)], 'F1 threshold-35/36 parabolics')
    if use_cartan:
        cartan = geometry_audit.CartanModel()
        seed = next(tuple(cartan.inverse[i][j] for i in range(8)) for j in range(8)
                    if cartan.inverse[j][j] == 6)
        norm6 = [canonical(cartan.to_doubled(h)) for h in cartan.vector_orbit(seed, 3360)]
    else:
        norm6 = integral_lines(1, 2) | integral_lines(0, 6) | half_lines(2)
    need(len(norm6) == 3360 and all(dot(h, h) == 24 for h in norm6), 'F1 norm-six inventory')
    minima = {}
    relevant6 = 0
    histogram6 = Counter()
    for family, normals in ((4, norm4), (6, norm6)):
        minimum = 112
        minimum_off = 112
        for h in normals:
            source = sum(1 << i for i in p if dot(h, roots[i]))
            minimum_off = min(minimum_off, source.bit_count())
            if family == 6 and source.bit_count() > 77:
                continue
            relevant6 += family == 6
            for v in p:
                size = (source & ov[v]).bit_count()
                minimum = min(minimum, size)
                if family == 6:
                    histogram6[size] += 1
        minima[family] = (minimum_off, minimum)
    need(minima == {4: (70, 30), 6: (77, 25)} and relevant6 == 2688, 'F1 nonroot deletion minima')
    planes = {root_off[i] | root_off[j] for i, j in combinations(range(120), 2) if dot(roots[i], roots[j])}
    need(len(planes) == 1120 and min((mask & p_mask).bit_count() for mask in planes) == 78,
         'F1 A2-plane minimum support')
    root_min = min((root_off[t] & ov[v]).bit_count() for v in p for t in range(120) if t != v)
    need(root_min == 26, 'F1 other-root minimum')
    h = (0, 0, 0, 2, -4, 0, -2, 0)
    v = roots.index((0, 0, 0, 2, 0, 0, 2, 0))
    deletion = [i for i in p if ov[v] >> i & 1 and dot(h, roots[i])]
    tau = {i: -dot(h, roots[i]) // 4 for i in deletion}
    g = {i: dot(h, roots[i]) // 4 + tau.get(i, 0) for i in p}
    actual = [i for i in p if g[i]]
    need(h in norm6 and v in p and dot(h, h) == 24 and dot(h, roots[v]) == 0 and len(deletion) == 25,
         'F1 sharp nonroot direction and25-point boundary')
    need(all(not g[i] for i in p if ov[v] >> i & 1) and len(actual) == 52
         and rank(labels[i] for i in actual) == 8, 'F1 sharp literal vanishing codeword')
    need(rank(labels[i] for i in deletion) == 7
         and all(rank([labels[i] for i in actual] + [labels[t]]) == 9 for t in deletion),
         'F1 all25 boundary correction coordinates essential')
    unit = deletion[0]
    fixed_rank = rank(labels[i] for i in deletion if i != unit)
    need(len(deletion) > 1 and fixed_rank == 7, 'F1 dimension-two independence and exact-cost lower bound')
    # U=<tau,delta_unit> has basis weights(7,1). Every vector outside the
    # unit line retains the24 fixed coordinates of rank7, so cost(U)=8.
    # This disproves the unrestricted F1 component at(7,1), not a decoder.
    return {'maximum_guaranteed_correction_support': 24, 'parabolic_threshold': 36,
            'large_proper_types': [list(key) for key in types], 'norm4_minimum_required': 30,
            'norm6_minimum_code_support': 77, 'norm6_relevant_objects': relevant6,
            'norm6_deletion_profile': [[size, count] for size, count in sorted(histogram6.items())],
            'a2_plane_minimum_code_support': 78, 'other_root_minimum_required': root_min,
            'sharp_support25_fixture': {'h_doubled': list(h), 'v_doubled': list(roots[v]),
                'tau_entries': [[list(roots[i]), tau[i]] for i in deletion],
                'tau_weight': 7, 'tau_support': 25, 'corrected_support': 52,
                'corrected_weight': 8, 'essential_coordinates': 25,
                'dimension_two_space': {'scope': 'F1 correction-space counterexample only',
                    'unit_root_doubled': list(roots[unit]), 'basis_weights': [7, 1],
                    'dimension': 2, 'exact_cost': 8, 'fixed_nonunit_support_rank': fixed_rank,
                    'union_support': 25, 'cost_at_most7_dimension_two_union_cap': 21}}}


def cycle_union(values):
    """Return rank and the union of supports of a binary cycle-space basis."""
    pivots, covered = {}, 0
    for i, value in enumerate(values):
        dependency = 1 << i
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                previous, mask = pivots[bit]
                value ^= previous
                dependency ^= mask
            else:
                pivots[bit] = (value, dependency)
                break
        if not value:
            covered |= dependency
    return len(pivots), covered


def frame_plane_checks(model):
    """Exclude non-axis private-frame directions for a(7,1) correction basis."""
    roots, labels, _, _, _ = model
    frame = []
    for sign in (1, -1):
        for j in range(4):
            vector = [0] * 8
            vector[2 * j], vector[2 * j + 1] = 2, 2 * sign
            frame.append(roots.index(tuple(vector)))
    p = [i for i in range(120) if i not in frame]
    cuts = [(normal, sum(1 << i for i in p if (normal & labels[i]).bit_count() % 2))
            for normal in range(1, 512)]
    profile, checked = Counter(), set()
    cross_checks, frame_minimum, nonroot_cases = 0, 112, 0
    need(cycle_union([1, 2, 3]) == (2, 7) and cycle_union([1, 2, 4]) == (3, 0),
         'cycle-space dependent and independent controls')
    for j in range(8):
        for k in range(8):
            if j == k:
                continue
            a, b = roots[frame[j]], roots[frame[k]]
            strata = {'frame': a, 'plus': tuple(x + y for x, y in zip(a, b)),
                      'minus': tuple(x - y for x, y in zip(a, b)),
                      'generic': tuple(x + 2 * y for x, y in zip(a, b))}
            for name, h in strata.items():
                source = sum(1 << i for i in p if dot(h, roots[i]))
                for normal, cut in cuts:
                    if (normal & labels[frame[j]]).bit_count() % 2:
                        continue
                    deletion = source & cut
                    values = []
                    while deletion:
                        bit = deletion & -deletion
                        values.append(labels[bit.bit_length() - 1])
                        deletion ^= bit
                    r, covered = cycle_union(values)
                    all_points = (1 << len(values)) - 1
                    after = r if covered == all_points else r - 1
                    key = (name, r, after)
                    profile[key] += 1
                    if key not in checked:
                        direct = [rank(values[:i] + values[i + 1:]) for i in range(len(values))]
                        need(after == min(direct), 'cycle-union minimum deletion rank')
                        need(all(direct[i] == r - (not (covered >> i & 1)) for i in range(len(values))),
                             'cycle-union pointwise coloop certificate')
                        checked.add(key)
                        cross_checks += len(values)
                    if name == 'frame':
                        frame_minimum = min(frame_minimum, len(values))
                    else:
                        need(r == 8 and covered == all_points, 'nonroot frame-plane deletion has a coloop')
                        nonroot_cases += 1
    expected = Counter({('frame', 7, 7): 14224, ('frame', 8, 8): 56,
                        ('plus', 8, 8): 14280, ('minus', 8, 8): 14280,
                        ('generic', 8, 8): 14280})
    need(profile == expected and frame_minimum == 24, 'frame-plane exhaustive profile')
    need(len(checked) == 5 and cross_checks >= 120, 'direct deletion-rank cross-check coverage')
    need(all(sum(bool(dot(root, roots[f])) for f in frame) == 4 for root in (roots[i] for i in p)),
         'aggregate four-frame incidence bound')
    need(7 * frame_minimum > 37 * 4, 'seven corrected frame members exceed correction incidences')
    return {'ordered_frame_pairs': 56, 'carrying_hyperplanes_per_pair': 255,
            'strata': 4, 'cases': sum(profile.values()), 'nonroot_cases_without_coloops': nonroot_cases,
            'profiles': [list(key) + [count] for key, count in sorted(profile.items())],
            'direct_rank_deletion_profiles_cross_checked': len(checked),
            'frame_minimum_deletions': frame_minimum, 'minimum_seven_frame_incidences': 7 * frame_minimum,
            'maximum_correction_incidences': 37 * 4}


def run_checks():
    direct, cartan = direct_model(), cartan_model()
    need(direct[0] == cartan[0] and direct[3:] == cartan[3:], 'independent root/normal inventories disagree')
    first, second = check_model(direct), check_model(cartan)
    need(first == second, 'independent geometry extension summaries disagree')
    f1_direct, f1_cartan = f1_checks(direct, False), f1_checks(cartan, True)
    need(f1_direct == f1_cartan, 'independent sharp-F1 summaries disagree')
    planes_direct, planes_cartan = frame_plane_checks(direct), frame_plane_checks(cartan)
    need(planes_direct == planes_cartan, 'independent frame-plane summaries disagree')
    return {'coordinate_models': 2, 'checks': first, 'f1': f1_direct, 'frame_planes': planes_direct}


if __name__ == '__main__':
    print(json.dumps(run_checks(), sort_keys=True, indent=2))
