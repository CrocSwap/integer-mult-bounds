#!/usr/bin/env python3
"""Rebuild the boundary directly from Euclidean roots and set-based F2 rows.

Imports neither verify.py nor predecessor code. Hanson Sun / bbMisk, with
substantial OpenAI Codex assistance. Apache-2.0. Same author, not human review.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def binary_rank(rows):
    # Sets of column indices, smallest pivot, symmetric difference.
    basis = {}
    for original in rows:
        row = set(original)
        while row:
            pivot = min(row)
            if pivot not in basis:
                basis[pivot] = row
                break
            row.symmetric_difference_update(basis[pivot])
    return len(basis)


def rational_basis(matrix):
    echelon = {}
    indices = []
    for i, original in enumerate(matrix):
        row = list(map(Fraction, original))
        for p, old in sorted(echelon.items()):
            scale = row[p]
            row = [v - scale * w for v, w in zip(row, old)]
        p = next((j for j, v in enumerate(row) if v), None)
        if p is not None:
            echelon[p] = [v / row[p] for v in row]
            indices.append(i)
    return indices


def determinant(matrix):
    a = [list(map(Fraction, row)) for row in matrix]
    result = Fraction(1)
    for k in range(len(a)):
        p = next((j for j in range(k, len(a)) if a[j][k]), None)
        if p is None:
            return Fraction(0)
        if p != k:
            a[k], a[p] = a[p], a[k]
            result = -result
        scale = a[k][k]
        result *= scale
        for j in range(k + 1, len(a)):
            weight = a[j][k] / scale
            a[j] = [v - weight * w for v, w in zip(a[j], a[k])]
    return result


def build():
    lines = set()
    for i, j in combinations(range(8), 2):
        for si, sj in product((-2, 2), repeat=2):
            r = [0] * 8
            r[i], r[j] = si, sj
            lines.add(max(tuple(r), tuple(-v for v in r)))
    for r in product((-1, 1), repeat=8):
        if sum(v < 0 for v in r) % 2 == 0:
            lines.add(max(r, tuple(-v for v in r)))
    check(len(lines) == 120, 'E8 line count')
    frame = []
    for k in range(0, 8, 2):
        for sign in (1, -1):
            r = [0] * 8
            r[k], r[k + 1] = 2, 2 * sign
            frame.append(tuple(r))
    roots = sorted(lines.difference(frame))
    dot = lambda r, s: sum(a * b for a, b in zip(r, s))
    check(len(roots) == 112, 'punctured line count')
    check(all(dot(r, s) % 4 == 0 for r in roots for s in roots), 'integral Gram')
    x = [[dot(r, f) // 4 for f in frame] for r in roots]
    gram = [[dot(r, s) // 4 for s in roots] for r in roots]
    b = [{j for j, v in enumerate(row) if (v + 1) % 2} for row in gram]
    check(binary_rank(b) == 9, 'affine pairing rank nine')
    check(all(sum(a * c for a, c in zip(x[i], x[j])) == 2 * gram[i][j]
              for i in range(112) for j in range(112)), 'all 12544 coordinate identities')
    return roots, x, b, gram


def reconstruct(roots, x, b):
    rho = lambda s, t: binary_rank(b[i].intersection(t) for i in s)
    coeffs = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2)]
    support = [[i for i, r in enumerate(x) if a * r[0] + c * r[1]] for a, c in coeffs]
    columns = [[j for j in s if j != 0] for s in support]
    u = sorted(i for i in support[0] if 0 not in b[i])
    check(len(u) == 24, '24-row boundary')
    common = [j for j in range(112) if all(j not in b[i] for i in u)]
    check(common == [0], 'unique odd neighbor')
    original = [[rho(s, t) for t in columns] for s in support]
    surviving = [[i for i in s if i not in u] for s in support]
    full = [[rho(s, t) for t in columns] for s in surviving]
    pure = [rho(u, t) for t in columns]
    proper = []
    for kept in u:
        erased = set(u).difference({kept})
        matrix = [[rho(set(s).difference(erased), t) for t in columns] for s in support]
        check(min(v for row in matrix for v in row) == 8, 'proper deletion minimum')
        proper.append({'restored_index': kept, 'ranks': matrix})
    check(min(v for row in original for v in row) == 8, 'original minimum')
    check(min(v for row in full for v in row) == 7 and pure == [7] * 5, 'full boundary minimum')
    counts = Counter(v for item in proper for row in item['ranks'] for v in row)
    coordinates = [rho([i for i in range(112) if x[i][k]],
                       [i for i in range(112) if x[i][k]]) for k in range(8)]
    check(coordinates == [8] * 8, 'baseline eight-by-eight')
    return {
        'root_order': 'lexicographic positive-first doubled E8 roots',
        'roots': [list(r) for r in roots], 'coordinate_pair': [0, 1], 'singleton': 0,
        'boundary': u, 'common_odd_neighbors': common,
        'stratum_coefficients': [list(c) for c in coeffs],
        'supports': support, 'right_survivors': columns,
        'original_ranks': original, 'full_deletion_ranks': full,
        'pure_correction_ranks': pure, 'proper_deletions': proper,
        'coordinate_costs': coordinates,
        'boundary_spans': {'before': binary_rank(b[i] for i in support[0]),
                          'after': binary_rank(b[i] for i in surviving[0])},
        'summary': {'pairing_checks': 655, 'original_min': 8,
                    'full_deletion_min': 7, 'pure_correction_min': 7,
                    'proper_deletion_checks': 600,
                    'proper_rank_counts': {str(k): v for k, v in sorted(counts.items())}},
    }


def expect_rejection(call, message):
    try:
        call()
    except ValueError as e:
        check(message in str(e), 'unexpected negative-control failure')
        return
    raise ValueError('negative control accepted: ' + message)


def extra_checks(x, b, gram, finite):
    u_set = set(finite['boundary'])
    u = [row[0] if i in u_set else 0 for i, row in enumerate(x)]
    left = [row + [u[i]] for i, row in enumerate(x)]
    right = [row + [int(i == 0)] for i, row in enumerate(x)]
    minors = []
    for side, matrix in [('left', left), ('right', right)]:
        indices = rational_basis(matrix)
        check(len(indices) == 9, 'rank-nine completion factors')
        det = determinant([matrix[i] for i in indices])
        check(det != 0, 'rank-nine witness minor')
        minors.append({'side': side, 'rows': indices, 'determinant': str(det)})
    # Integer recheck of the cancellation fixture, including constrained entries.
    d = [[r[0] - u[i], r[1], u[i]] for i, r in enumerate(x)]
    t = [[r[0], r[1], r[0] + int(i == 0)] for i, r in enumerate(x)]
    check(all(sum(a * c for a, c in zip(d[i], t[j])) ==
              x[i][0] * x[j][0] + x[i][1] * x[j][1] + u[i] * int(j == 0)
              for i in range(112) for j in range(112)), 'integer cancellation identity')
    costs = [binary_rank(b[i].intersection(j for j in range(112) if t[j][k])
                        for i in range(112) if d[i][k]) for k in range(3)]
    check(costs == [7, 8, 7], 'coupled cancellation bill')
    bad_entry = next((i, j) for i in range(112) for j in range(112)
                     if j in b[i] and u[i] * t[j][2])
    controls = []
    wrong = [{j for j, v in enumerate(row) if v % 2} for row in gram]
    expect_rejection(lambda: check(binary_rank(wrong) == 9, 'affine label offset'), 'affine label offset')
    controls.append('omitted affine one in pairing')
    expect_rejection(lambda: check(finite['boundary_spans']['after'] == 8, 'false span preservation'),
                     'false span preservation')
    controls.append('span-loss premise treated as preserved')
    changed = deepcopy(finite)
    changed['proper_deletions'][0]['ranks'][0][0] -= 1
    expect_rejection(lambda: check(changed == finite, 'full finite receipt'), 'full finite receipt')
    controls.append('corrupted restoration rank')
    changed = deepcopy(finite)
    changed['proper_deletions'].pop()
    expect_rejection(lambda: check(changed == finite, 'full finite receipt'), 'full finite receipt')
    controls.append('incomplete proper-subset coverage')
    i, j = bad_entry
    expect_rejection(lambda: check(u[i] * t[j][2] == 0, 'omitted required term'), 'omitted required term')
    controls.append('omitted compensation fails a constrained entry')
    bad = next(j for j in range(112) if any(j in b[i] for i in u_set))
    expect_rejection(lambda: check(all(bad not in b[i] for i in u_set), 'free support'), 'free support')
    controls.append('wrong singleton breaks free support')
    return {'schema_version': 1, 'geometry': 'direct doubled E8 roots and Gram parity; set elimination',
            'pairing_checks': 655, 'all_pairs_identity_entries': 12544,
            'cancellation_identity_entries': 12544, 'cancellation_costs': costs,
            'omission_counterexample': {'row': i, 'column': j, 'missing_value': u[i] * t[j][2]},
            'rank_nine_completion_minors': minors, 'controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    parser.add_argument('--check', type=Path, default=HERE / 'INDEPENDENT.json')
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    roots, x, b, gram = build()
    finite = reconstruct(roots, x, b)
    check(finite == json.loads(args.certificate.read_text())['finite_premises'], 'full finite receipt')
    actual = extra_checks(x, b, gram, finite)
    if args.write:
        args.write.write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    else:
        check(actual == json.loads(args.check.read_text()), 'independent receipt equality')
    print('PASS_P112_BOUNDARY24_INDEPENDENT pairings=655 identities=25088 '
          'rank9_minors=2 controls=6 copy_floor=64')


if __name__ == '__main__':
    main()
