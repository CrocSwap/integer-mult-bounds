#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# New fixed-puncture investigation: ChatGPT for Andrey Mas, 2026-10-14.
# Root/pairing conventions and the 69-cost baseline are credited in ATTRIBUTION.md.
"""Exact stdlib replay of the fixed 26-puncture completion minimum 62.

No network, third-party packages, floating point, symbolic algebra package,
positivity assumption, or assertions. See proof.md for the universal proof.
All arrays representing normal matrices are ROWS; paired normals are COLUMNS.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from math import gcd
from pathlib import Path

P = [0, 23, 24, 25, 26, 34, 35, 36, 37, 48, 60, 61, 62, 63, 66, 67,
     72, 73, 76, 77, 78, 79, 82, 83, 88, 89]
FIXED_A = [Q(x, 2) for x in (1, -1, -1, -1, 1, 1, -1, 1)]
FIXED_B = list(map(Q, (0, 0, 0, 0, 0, 0, -2, 2)))
ELIGIBLE_B = [23, 25, 30, 34, 36, 61, 63, 66, 73, 77, 79, 82, 89]
SIX_PAIRS = [(23, 34), (25, 36), (61, 77), (63, 79), (66, 82), (73, 89)]
OPTIMAL_ROOTS = [23, 25, 30, 61, 63, 66, 73]
SCHEMA = 'fixed-paired26-completion-v1'

PRIOR_A = [
    ['1/2', 1, 0, 0, 0, 0, 0, 0],
    ['-1/2', 0, 1, 0, 0, 0, 0, 0],
    ['-1/2', 0, 0, 1, 0, 0, 0, 0],
    ['-1/2', 0, 0, 0, 1, 0, 0, 0],
    ['1/2', 0, 0, 0, 0, 1, 0, 0],
    ['1/2', 0, 0, 0, 0, 0, 1, 0],
    ['-1/2', 0, 0, 0, 0, 0, 0, 1],
    ['1/2', 0, 0, 0, 0, 0, 0, 1],
]
PRIOR_B = [
    [0, 2, 0, 0, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 0, 0, 0], [0, 0, 0, 0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 0], [0, 0, 0, 0, 0, 0, 2, 0],
    [-2, 1, -1, -1, -1, 1, 1, 1], [2, -1, 1, 1, 1, -1, -1, 1],
]
BRANCH_A = [
    ['1/2', 0, 1, 0, 0, 0, 0, 0],
    ['-1/2', 1, 0, 1, 0, 0, 0, 0],
    ['-1/2', -1, 0, 1, 0, 0, 0, 0],
    ['-1/2', 0, 0, 0, 1, 0, 0, 0],
    ['1/2', 0, 0, 0, 0, 1, 0, 0],
    ['1/2', 0, 0, 0, 0, 0, 1, 0],
    ['-1/2', 0, 0, 0, 0, 0, 0, 1],
    ['1/2', 0, 0, 0, 0, 0, 0, 1],
]


class VerificationError(RuntimeError):
    """A mathematical premise, witness, or certificate check failed."""


def need(condition, message):
    if not condition:
        raise VerificationError(message)


def rational_matrix(rows):
    return [[Q(x) for x in row] for row in rows]


def encode_matrix(rows):
    return [[str(x) for x in row] for row in rows]


def dot(a, b):
    need(len(a) == len(b), 'dot-product shape mismatch')
    return sum(x * y for x, y in zip(a, b))


def tr(a):
    need(bool(a) and len({len(r) for r in a}) == 1, 'transpose shape mismatch')
    return list(map(list, zip(*a)))


def mm(a, b):
    need(bool(a) and bool(b) and all(len(r) == len(b) for r in a),
         'matrix product shape mismatch')
    return [[dot(row, col) for col in tr(b)] for row in a]


def matrix_add(a, b, sign=1):
    need(len(a) == len(b) and all(len(x) == len(y) for x, y in zip(a, b)),
         'matrix addition shape mismatch')
    return [[x + sign * y for x, y in zip(u, v)] for u, v in zip(a, b)]


def scale(a, s):
    return [[s * x for x in row] for row in a]


def inverse(a):
    """Rational Gauss-Jordan inversion, with explicit singularity errors."""
    n = len(a)
    need(n > 0 and all(len(r) == n for r in a), 'inverse needs square matrix')
    m = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
         for i, row in enumerate(a)]
    for k in range(n):
        p = next((i for i in range(k, n) if m[i][k]), None)
        need(p is not None, 'singular normal matrix')
        m[k], m[p] = m[p], m[k]
        pivot = m[k][k]
        m[k] = [x / pivot for x in m[k]]
        for i in range(n):
            if i != k and m[i][k]:
                f = m[i][k]
                m[i] = [x - f * y for x, y in zip(m[i], m[k])]
    return [r[n:] for r in m]


def det_int(a):
    """Independent integer Bareiss determinant; every division is checked."""
    n = len(a)
    need(all(len(r) == n and all(type(x) is int for x in r) for r in a),
         'integer determinant input')
    if n == 0:
        return 1
    m = [r[:] for r in a]
    sign, previous = 1, 1
    for k in range(n - 1):
        p = next((i for i in range(k, n) if m[i][k]), None)
        if p is None:
            return 0
        if p != k:
            m[k], m[p] = m[p], m[k]
            sign = -sign
        pivot = m[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                value, remainder = divmod(m[i][j] * pivot - m[i][k] * m[k][j],
                                          previous)
                need(remainder == 0, 'non-exact Bareiss division')
                m[i][j] = value
            m[i][k] = 0
        previous = pivot
    return sign * m[-1][-1]


def primitive(v):
    g = gcd(*v)
    if g == 0:
        return list(v)
    if next(x for x in v if x) < 0:
        g = -g
    return [x // g for x in v]


def select_rows(rows, ids, ncols=8):
    """Fraction-free streaming row selection, distinct from determinant check."""
    pivots, selected = {}, []
    for ident, row in zip(ids, rows):
        v = list(row)
        for p, w in sorted(pivots.items()):
            if v[p]:
                s, t = w[p], v[p]
                v = primitive([s * x - t * y for x, y in zip(v, w)])
        p = next((i for i, x in enumerate(v) if x), None)
        if p is not None:
            pivots[p] = primitive(v)
            selected.append(ident)
        if len(pivots) == ncols:
            break
    return selected, sorted(pivots)


def bit_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def dense_binary_rank(rows, ncols):
    """Literal dense F2 elimination, independently cross-checking bit ranks."""
    m = [list(r) for r in rows]
    need(all(len(r) == ncols and all(x in (0, 1) for x in r) for r in m),
         'dense binary input')
    k = 0
    for j in range(ncols):
        p = next((i for i in range(k, len(m)) if m[i][j]), None)
        if p is None:
            continue
        m[k], m[p] = m[p], m[k]
        for i in range(k + 1, len(m)):
            if m[i][j]:
                m[i] = [x ^ y for x, y in zip(m[i], m[k])]
        k += 1
    return k


def binary_inverse(rows, n):
    m = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        p = next((i for i in range(j, n) if (m[i] >> j) & 1), None)
        need(p is not None, 'singular binary coordinate form')
        m[j], m[p] = m[p], m[j]
        for i in range(n):
            if i != j and ((m[i] >> j) & 1):
                m[i] ^= m[j]
    need(all((m[i] & ((1 << n) - 1)) == 1 << i for i in range(n)),
         'binary inverse reduction failure')
    return [r >> n for r in m]


def root_lines():
    roots = set()
    for i, j in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = signs
            v = tuple(v)
            roots.add(max(v, tuple(-x for x in v)))
    for v in product((-1, 1), repeat=8):
        if sum(x < 0 for x in v) % 2 == 0:
            roots.add(max(v, tuple(-x for x in v)))
    return sorted(roots)


def check_pairing_formula(roots, pairing):
    need(len(pairing) == 120, 'pairing shape')
    for i, u in enumerate(roots):
        expected = 0
        for j, v in enumerate(roots):
            q, rem = divmod(dot(u, v), 4)
            need(rem == 0, 'root dot product not divisible by four')
            expected |= ((q + 1) & 1) << j
        need(pairing[i] == expected, 'wrong pairing: unit label is mandatory')


def geometry():
    roots = root_lines()
    need(len(roots) == 120 and all(dot(v, v) == 8 for v in roots), 'root generation')
    need(P == sorted(set(P)) and len(P) == 26, 'fixed puncture')
    live = [i for i in range(120) if i not in P]
    pairing = [sum((((dot(u, v) // 4) + 1) & 1) << j
                   for j, v in enumerate(roots)) for u in roots]
    check_pairing_formula(roots, pairing)
    need(bit_rank(pairing) == 9, 'ambient pairing rank')
    need(dense_binary_rank([[(r >> j) & 1 for j in range(120)]
                            for r in pairing], 120) == 9, 'dense ambient rank')
    basis = []
    for i in range(120):
        if bit_rank([pairing[j] for j in basis + [i]]) > len(basis):
            basis.append(i)
        if len(basis) == 9:
            break
    need(basis == [0, 1, 2, 3, 6, 12, 20, 30, 42], 'pairing-row label basis')
    labels = [sum(((row >> b) & 1) << j for j, b in enumerate(basis))
              for row in pairing]
    h = [labels[i] for i in basis]
    hi = binary_inverse(h, 9)
    need(bit_rank(labels) == 9, 'label span')
    # Check the nondegenerate label form on every full-root ordered pair.
    for i, li in enumerate(labels):
        transformed = 0
        for k in range(9):
            if (li >> k) & 1:
                transformed ^= hi[k]
        for j, lj in enumerate(labels):
            need(((transformed & lj).bit_count() & 1) == ((pairing[i] >> j) & 1),
                 'label-coordinate pairing reconstruction')
    rows, cols = select_rows([roots[i] for i in live], live)
    need(len(rows) == 8, 'live rational root rank')
    minor = det_int([[roots[i][j] for j in cols] for i in rows])
    need(minor != 0, 'live root rank witness')
    live_mask = sum(1 << i for i in live)
    need(bit_rank([pairing[i] & live_mask for i in live]) == 9, 'live pairing rank')
    g = {'roots': roots, 'live': live, 'pairing': pairing, 'labels': labels,
         'R': [[Q(x, 2) for x in roots[i]] for i in live]}
    report = {'punctures': P, 'live_indices': live, 'root_count': 120,
              'root_sha256': hashlib.sha256(json.dumps(roots, separators=(',', ':')).encode()).hexdigest(),
              'ambient_pairing_rank': 9, 'live_pairing_rank': 9,
              'label_basis_pairing_rows': basis, 'labels': labels,
              'coordinate_form_inverse_rows': hi, 'pairing_reconstruction_entries': 14400,
              'live_root_rank': 8, 'live_root_minor_rows': rows,
              'live_root_minor_columns': cols, 'live_doubled_root_minor_determinant': minor}
    return g, report


def support(g, normal):
    return [i for i in g['live'] if dot(g['roots'][i], normal) != 0]


def label_dimension(g, indices):
    return bit_rank(g['labels'][i] for i in indices)


def rectangle_rank(g, s, t):
    mask = sum(1 << j for j in t)
    rank = bit_rank(g['pairing'][i] & mask for i in s)
    dense = [[(g['pairing'][i] >> j) & 1 for j in t] for i in s]
    need(rank == dense_binary_rank(dense, len(t)), 'rectangular rank disagreement')
    return rank


def kernel_inventory(g):
    roots, live, labels = g['roots'], g['live'], g['labels']
    records, groups = [], {}
    for lam in range(1, 512):
        violations = [i for i in live if (labels[i] & lam).bit_count() & 1]
        rows, cols = select_rows([roots[i] for i in violations], violations)
        rank = len(rows)
        need(rank in (7, 8), 'unexpected annihilator-matrix rank')
        minor = det_int([[roots[i][j] for j in cols] for i in rows])
        need(minor != 0, 'invalid annihilator rank lower witness')
        root = None
        if rank == 7:
            candidates = [j for j, v in enumerate(roots)
                          if all(dot(roots[i], v) == 0 for i in violations)]
            need(len(candidates) == 1, 'rank-seven kernel is not one certified root line')
            root = candidates[0]
            # Nonzero kernel + nonzero 7-minor proves EXACT rank seven over Q and C.
            need(any(roots[root]), 'zero kernel witness')
            groups.setdefault(root, []).append(lam)
        records.append({'lambda': lam, 'violation_count': len(violations), 'rank': rank,
                        'minor_root_rows': rows, 'minor_columns': cols,
                        'minor_determinant': minor, 'kernel_root_index': root})
    need(Counter(x['rank'] for x in records) == Counter({8: 482, 7: 29}), 'inventory totals')
    need(sorted(groups) == sorted(P + [30]), 'complete reduced-direction set')
    reduced = []
    for index in sorted(groups):
        s = support(g, roots[index])
        dimension = label_dimension(g, s)
        annihilators = [lam for lam in range(1, 512)
                       if all(((labels[i] & lam).bit_count() & 1) == 0 for i in s)]
        need(annihilators == groups[index], 'kernel/support annihilator mismatch')
        need(dimension == (7 if index == 0 else 8), 'reduced support dimension')
        reduced.append({'root_index': index, 'dimension': dimension,
                        'support': s, 'annihilator_functionals': annihilators})
    eligible_a = [i for i in sorted(groups) if dot(roots[i], FIXED_B) == 0]
    eligible_b = [i for i in sorted(groups) if dot(roots[i], FIXED_A) == 0]
    need(eligible_a == [30] and eligible_b == ELIGIBLE_B, 'fixed-pair perpendicular inventory')
    c_dots = [dot(roots[30], roots[i]) for i in eligible_b]
    need(all(c_dots), 'a reduced residual B direction is perpendicular to r30')
    costs_c = [rectangle_rank(g, support(g, roots[30]), support(g, roots[i]))
               for i in eligible_b]
    need(costs_c == [7 if i == 30 else 8 for i in eligible_b], 'r30 pair charges')
    return {'matrices': records, 'rank_histogram': {'7': 29, '8': 482},
            'reduced_directions': reduced, 'eligible_residual_A_roots': eligible_a,
            'eligible_residual_B_roots': eligible_b,
            'doubled_root30_dot_eligible_B': c_dots, 'root30_pair_costs': costs_c}


def check_all_pairs(g, d, t):
    need(len(d) == len(t) == 94 and all(len(row) == 8 for row in d + t),
         'decoder must have exactly 94 rows and eight terms')
    zero_rhs = 0
    for i in range(94):
        for j in range(94):
            rhs = 2 * dot(g['R'][i], g['R'][j])
            need(dot(d[i], t[j]) == rhs, 'all-pairs identity fails at live positions %d,%d' % (i, j))
            zero_rhs += rhs == 0
    return {'ordered_entries_checked': 8836, 'zero_rhs_entries_checked': zero_rhs}


def term_reports(g, d, t, di=None, ti=None):
    if di is None:
        di = [[Q(0)] * 8 for _ in range(94)]
    if ti is None:
        ti = [[Q(0)] * 8 for _ in range(94)]
    terms = []
    for k in range(8):
        s = [index for p, index in enumerate(g['live']) if d[p][k] != 0 or di[p][k] != 0]
        u = [index for p, index in enumerate(g['live']) if t[p][k] != 0 or ti[p][k] != 0]
        terms.append({'term': k, 'D_support': s, 'T_support': u,
                      'support_sizes': [len(s), len(u)],
                      'label_dimensions': [label_dimension(g, s), label_dimension(g, u)],
                      'copy_cost': rectangle_rank(g, s, u)})
    return terms


def check_claimed_bill(report, costs, total):
    need(costs == [t['copy_cost'] for t in report['terms']], 'understated or altered separate term costs')
    need(total == sum(costs) == report['total_copy_cost'], 'incorrect complete bill')


def verify_decoder(g, a, b, expected_costs=None):
    need(len(a) == len(b) == 8 and all(len(row) == 8 for row in a + b), 'normal matrix dimensions')
    need(tr(a)[0] == FIXED_A and tr(b)[0] == FIXED_B, 'designated first pair must be exact, not merely proportional')
    two_i = [[Q(2 * (i == j)) for j in range(8)] for i in range(8)]
    need(mm(a, tr(b)) == two_i, 'A B^T is not 2I')
    need(mm(tr(a), b) == two_i, 'A^T B is not 2I')
    d, t = mm(g['R'], a), mm(g['R'], b)
    identity = check_all_pairs(g, d, t)
    terms = term_reports(g, d, t)
    result = {'A_rows': encode_matrix(a), 'B_rows': encode_matrix(b),
              'identity': identity, 'terms': terms,
              'total_copy_cost': sum(x['copy_cost'] for x in terms)}
    if expected_costs is not None:
        check_claimed_bill(result, expected_costs, sum(expected_costs))
    return result


def optimal_classification(g):
    """Both a structural six-pair description and every 7-subset determinant."""
    roots = g['roots']
    for x, y in SIX_PAIRS:
        need(tuple(u + v for u, v in zip(roots[x], roots[30])) == roots[y], 'six-pair addition')
    canonical_columns = [[int(2 * x) for x in FIXED_B], roots[30]] + [roots[x] for x, _ in SIX_PAIRS]
    canonical_det = det_int(tr(canonical_columns))
    need(canonical_det != 0, 'seven-dimensional configuration basis')
    structural = set()
    for singles in product(*SIX_PAIRS):
        structural.add(tuple(sorted((30,) + singles)))
    for doubled in range(6):
        other_pairs = [pair for j, pair in enumerate(SIX_PAIRS) if j != doubled]
        for singles in product(*other_pairs):
            structural.add(tuple(sorted(SIX_PAIRS[doubled] + singles)))
    direct, histogram = [], Counter()
    for indices in combinations(ELIGIBLE_B, 7):
        columns = [[int(2 * x) for x in FIXED_B]] + [roots[i] for i in indices]
        determinant = det_int(tr(columns))
        histogram[str(determinant)] += 1
        if determinant:
            direct.append(indices)
    need(len(direct) == 256 and set(direct) == structural, 'optimal basis census')
    need(sum(histogram.values()) == 1716, '7-subset census coverage')
    return {'six_pairs': [list(p) for p in SIX_PAIRS],
            'doubled_canonical_basis_determinant': canonical_det,
            'subset_count': 1716, 'independent_count': 256,
            'containing_root30': sum(30 in s for s in direct),
            'not_containing_root30': sum(30 not in s for s in direct),
            'determinant_histogram': dict(sorted(histogram.items())),
            'optimal_unordered_B_root_sets': [list(s) for s in direct]}


def complex_control(g, a, b):
    """Exact Q(i) shear via rational real/imaginary matrices, no complex floats."""
    ai, bi = [[Q(0)] * 8 for _ in range(8)], [[Q(0)] * 8 for _ in range(8)]
    for row in range(8):
        ai[row][1] = a[row][2]
        bi[row][2] = -b[row][1]
    d, di = mm(g['R'], a), mm(g['R'], ai)
    t, ti = mm(g['R'], b), mm(g['R'], bi)
    hermitian_failure = None
    zero_rhs = 0
    for i in range(94):
        for j in range(94):
            rhs = 2 * dot(g['R'][i], g['R'][j])
            real = dot(d[i], t[j]) - dot(di[i], ti[j])
            imag = dot(d[i], ti[j]) + dot(di[i], t[j])
            need(real == rhs and imag == 0, 'complex ordinary-transpose identity')
            zero_rhs += rhs == 0
            hr = dot(d[i], t[j]) + dot(di[i], ti[j])
            hi = dot(di[i], t[j]) - dot(d[i], ti[j])
            if hermitian_failure is None and (hr != rhs or hi != 0):
                hermitian_failure = {'live_positions': [i, j],
                                     'root_indices': [g['live'][i], g['live'][j]],
                                     'computed_real': str(hr), 'computed_imag': str(hi),
                                     'required_real': str(rhs)}
    ar_col, ai_col = tr(a)[1], tr(ai)[1]
    need(any(ar_col) and any(ai_col), 'nonzero complex control column')
    need(dot(ar_col, ar_col) - dot(ai_col, ai_col) == 0 and dot(ar_col, ai_col) == 0,
         'complex control is not isotropic')
    need(hermitian_failure is not None, 'conjugate-transpose control failed to distinguish conventions')
    need(tr(ai)[0] == [0] * 8 and tr(bi)[0] == [0] * 8, 'complex control moved first pair')
    terms = term_reports(g, d, t, di, ti)
    costs = [x['copy_cost'] for x in terms]
    need(costs == [6, 8, 9, 8, 8, 8, 8, 8], 'complex shear bill')
    # Independently realifying the two changed columns can preserve every
    # actual support while destroying their dual compatibility.
    bad_a = bad_b = None
    chosen_t = chosen_s = None
    for candidate in range(1, 20):
        aa = copy.deepcopy(a)
        for row in range(8):
            aa[row][1] += candidate * a[row][2]
        if support(g, tr(aa)[1]) == terms[1]['D_support']:
            chosen_t, bad_a = candidate, aa
            break
    need(bad_a is not None, 'realification control A parameter')
    for candidate in range(1, 20):
        if candidate == chosen_t:
            continue
        bb = copy.deepcopy(b)
        for row in range(8):
            bb[row][2] -= candidate * b[row][1]
        if support(g, tr(bb)[2]) == terms[2]['T_support']:
            chosen_s, bad_b = candidate, bb
            break
    need(bad_b is not None, 'realification control B parameter')
    for k in range(8):
        need(support(g, tr(bad_a)[k]) == terms[k]['D_support'] and
             support(g, tr(bad_b)[k]) == terms[k]['T_support'],
             'realification did not preserve an actual support')
    expect_rejection('support-preserving independent realification',
                     lambda: verify_decoder(g, bad_a, bad_b))
    return {'construction': 'A[:,1] += i*A[:,2]; B[:,2] -= i*B[:,1], using pre-shear columns',
            'A_real_rows': encode_matrix(a), 'A_imag_rows': encode_matrix(ai),
            'B_real_rows': encode_matrix(b), 'B_imag_rows': encode_matrix(bi),
            'isotropic_A_column': 1, 'isotropic_ordinary_square': ['0', '0'],
            'ordered_complex_entries_checked': 8836, 'zero_rhs_entries_checked': zero_rhs,
            'terms': terms, 'total_copy_cost': sum(costs),
            'hermitian_failure': hermitian_failure,
            'support_preserving_but_incompatible_realification': {
                'A_parameter': chosen_t, 'B_parameter': chosen_s,
                'all_sixteen_supports_preserved': True, 'dual_identity_rejected': True}}


def expect_rejection(name, call):
    try:
        call()
    except VerificationError:
        return name
    raise VerificationError('negative control incorrectly accepted: ' + name)


def first_difference(a, b, path='$'):
    if type(a) is not type(b):
        return path + ' (type)'
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return path + ' (keys)'
        for k in a:
            d = first_difference(a[k], b[k], path + '.' + k)
            if d:
                return d
    elif isinstance(a, list):
        if len(a) != len(b):
            return path + ' (length)'
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_difference(x, y, path + '[' + str(i) + ']')
            if d:
                return d
    elif a != b:
        return path
    return None


def compare_certificate(received, computed):
    need(isinstance(received, dict), 'certificate must be an object')
    need(received.get('schema') == SCHEMA, 'certificate schema')
    records = received.get('inventory', {}).get('matrices', [])
    need([r.get('lambda') for r in records] == list(range(1, 512)),
         'certificate must contain every nonzero functional exactly once, in order')
    mismatch = first_difference(received, computed)
    need(mismatch is None, 'certificate mismatch at ' + str(mismatch))


def negative_controls(g, a, b, optimal, core):
    names = []
    wrong_b = copy.deepcopy(b)
    for row in range(8):
        wrong_b[row][1] /= 2
    names.append(expect_rejection('wrong residual dual scale', lambda: verify_decoder(g, a, wrong_b)))
    names.append(expect_rejection('inverse instead of inverse transpose',
                                  lambda: verify_decoder(g, a, scale(inverse(a), 2))))
    singular_a = copy.deepcopy(a)
    for row in range(8):
        singular_a[row][2] = singular_a[row][1]
    names.append(expect_rejection('singular residual normal basis',
                                  lambda: verify_decoder(g, singular_a, b)))
    gauge_a, gauge_b = copy.deepcopy(a), copy.deepcopy(b)
    for row in range(8):
        gauge_a[row][0] *= 2
        gauge_b[row][0] /= 2
    names.append(expect_rejection('untracked gauge change of designated first pair',
                                  lambda: verify_decoder(g, gauge_a, gauge_b)))
    names.append(expect_rejection('undercharged separate invoice',
                                  lambda: check_claimed_bill(optimal, [6, 7, 8, 8, 8, 8, 8, 8], 61)))
    forged_terms = copy.deepcopy(optimal['terms'])
    forged_terms[1]['D_support'].pop()
    names.append(expect_rejection('deleted ACTUAL nonzero support entry',
                                  lambda: need(forged_terms == optimal['terms'], 'false actual support')))
    d, t = mm(g['R'], a), mm(g['R'], b)
    bad_d = copy.deepcopy(d)
    bad_d[0][1] += 1
    names.append(expect_rejection('altered decoder fails full ordered-entry identity',
                                  lambda: check_all_pairs(g, bad_d, t)))
    names.append(expect_rejection('ninth zero term violates exactly-eight contract',
                                  lambda: check_all_pairs(g, [r + [Q(0)] for r in d],
                                                         [r + [Q(0)] for r in t])))
    no_unit = [r ^ ((1 << 120) - 1) for r in g['pairing']]
    need(bit_rank(no_unit) == 8, 'no-unit control expected rank eight')
    names.append(expect_rejection('omitted unit label',
                                  lambda: check_pairing_formula(g['roots'], no_unit)))
    # The same full recursive comparison used for external certificates.
    bad = copy.deepcopy(core)
    bad['inventory']['matrices'] = [r for r in bad['inventory']['matrices'] if r['lambda'] != 286]
    names.append(expect_rejection('omitted functional 286', lambda: compare_certificate(bad, core)))
    bad = copy.deepcopy(core)
    bad['inventory']['matrices'][285]['rank'] = 8
    names.append(expect_rejection('false rank-eight claim at functional 286',
                                  lambda: compare_certificate(bad, core)))
    bad = copy.deepcopy(core)
    bad['inventory']['matrices'][285]['kernel_root_index'] = 0
    names.append(expect_rejection('wrong kernel direction at functional 286',
                                  lambda: compare_certificate(bad, core)))
    bad = copy.deepcopy(core)
    bad['inventory']['matrices'][0]['minor_determinant'] += 1
    names.append(expect_rejection('forged exact minor determinant', lambda: compare_certificate(bad, core)))
    bad = copy.deepcopy(core)
    bad['geometry']['punctures'][0] = 1
    names.append(expect_rejection('changed fixed puncture', lambda: compare_certificate(bad, core)))
    return {'rejected': names, 'count': len(names),
            'additional_complex_controls': ['conjugate transpose disagrees',
                                            'independent support-preserving realification loses duality'],
            'wrong_no_unit_pairing_rank': 8}


def compute_certificate():
    g, geo = geometry()
    # Reproduce the predecessor FIRST, before any new decoder or conclusion.
    pa, pb = rational_matrix(PRIOR_A), rational_matrix(PRIOR_B)
    prior = verify_decoder(g, pa, pb, [6, 9, 9, 9, 9, 9, 9, 9])
    inventory = kernel_inventory(g)
    b = tr([FIXED_B] + [[Q(x, 2) for x in g['roots'][i]] for i in OPTIMAL_ROOTS])
    a = scale(tr(inverse(b)), 2)
    optimal = verify_decoder(g, a, b, [6, 8, 8, 8, 8, 8, 8, 8])
    ba = rational_matrix(BRANCH_A)
    bb = scale(tr(inverse(ba)), 2)
    branch = verify_decoder(g, ba, bb, [6, 7, 9, 9, 9, 9, 9, 9])
    need(tr(ba)[1] == [Q(x, 2) for x in g['roots'][30]] == tr(bb)[1], '67-branch paired root')
    classification = optimal_classification(g)
    complex_example = complex_control(g, a, b)
    core = {'schema': SCHEMA, 'geometry': geo, 'prior_69': prior, 'inventory': inventory,
            'minimum': 62, 'lower_bound_branches': {'no_reduced_residual_A': 62,
                                                   'a_reduced_residual_A_exists': 67},
            'optimal_62': optimal, 'sharp_reduced_A_branch_67': branch,
            'optimal_classification': classification, 'complex_isotropic_control': complex_example}
    controls = negative_controls(g, a, b, optimal, core)
    core['negative_controls'] = controls
    return core


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path,
                        default=Path(__file__).resolve().with_name('certificate.json'))
    parser.add_argument('--write-certificate', action='store_true',
                        help='deliberately regenerate the specified certificate')
    args = parser.parse_args(argv)
    try:
        computed = compute_certificate()
        if args.write_certificate:
            args.certificate.write_text(json.dumps(computed, indent=2, sort_keys=True) + '\n', encoding='utf-8')
            print('WROTE_CERTIFICATE ' + str(args.certificate))
        else:
            received = json.loads(args.certificate.read_text(encoding='utf-8'))
            compare_certificate(received, computed)
        print('PASS_FIXED_PAIRED26_MINIMUM_62')
        print('prior=69 optimal=62 reduced_A_branch=67; all 8836 entries checked for each')
        print('inventory: 511/511 functionals; rank8=482 rank7=29; 27 complex kernel lines')
        print('optimal classes: 256/1716 seven-subsets; 64 with r30, 192 without')
        print('Q(i) isotropic example: cost63; 8836 complex entries; ordinary transpose only')
        print('negative controls: 14 rejected, plus 2 complex convention/compatibility controls')
        return 0
    except (VerificationError, OSError, ValueError, TypeError, KeyError) as exc:
        print('FAIL_FIXED_PAIRED26: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
