#!/usr/bin/env python3
"""Exact premises and fixtures; the quantified proof is in README.md.

Hanson Sun / bbMisk, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {'research/p112-single-lift/geometry.py',
          'research/complex-frame-pair-decoders/PROOF.md'}
STRATA = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))
EXPECTED_U = (27, 28, 31, 32, 69, 70, 73, 74, 77, 78, 81, 82,
              85, 86, 89, 90, 93, 94, 97, 98, 103, 104, 107, 108)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_sources(sources):
    rows = [r for r in sources['files'] if r['usage'] == 'input']
    require(len(rows) == len(INPUTS) and {r['path'] for r in rows} == INPUTS,
            'complete input inventory')
    for row in rows:
        require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
                == row['sha256'], 'source digest: ' + row['path'])


def rank(rows):
    pivots = {}
    for v in rows:
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return len(pivots)


def cost(pairing, left, right):
    mask = sum(1 << j for j in right)
    return rank(pairing[i] & mask for i in left)


def model():
    spec = importlib.util.spec_from_file_location(
        'pinned_p112_geometry', ROOT / 'research/p112-single-lift/geometry.py')
    geometry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geometry)
    data = geometry.build()
    geometry.check_geometry(data)
    order = sorted(range(112), key=lambda i: max(tuple(data['roots'][i]),
                              tuple(-v for v in data['roots'][i])))
    roots, x, labels, duals = [], [], [], []
    for i in order:
        r = data['roots'][i]
        canonical = max(tuple(r), tuple(-v for v in r))
        sign = 1 if tuple(r) == canonical else -1
        roots.append(list(canonical))
        x.append([sign * v for v in data['X'][i]])
        labels.append(data['labels'][i])
        duals.append(data['duals'][i])
    pairing = [sum(((d & label).bit_count() % 2) << j
                   for j, label in enumerate(labels)) for d in duals]
    require(rank(pairing) == 9, 'ambient pairing rank')
    return roots, x, pairing


def finite_premises(roots, x, pairing):
    u_set = [i for i, row in enumerate(x) if row[0] and not (pairing[i] & 1)]
    require(tuple(u_set) == EXPECTED_U, 'canonical PR1375 boundary')
    neighbors = [j for j in range(112)
                 if all(not (pairing[i] >> j & 1) for i in u_set)]
    require(neighbors == [0], 'common odd neighbor')
    supports = [[i for i, row in enumerate(x) if a * row[0] + b * row[1]]
                for a, b in STRATA]
    columns = [[i for i in s if i != 0] for s in supports]
    surviving = [[i for i in s if i not in u_set] for s in supports]
    original = [[cost(pairing, s, c) for c in columns] for s in supports]
    full = [[cost(pairing, s, c) for c in columns] for s in surviving]
    pure = [cost(pairing, u_set, c) for c in columns]
    proper = [{'restored_index': k,
               'ranks': [[cost(pairing, [i for i in s if i not in u_set or i == k], c)
                          for c in columns] for s in supports]}
              for k in u_set]
    require(min(v for row in original for v in row) == 8, 'original floor eight')
    require(min(v for row in full for v in row) == 7, 'full-deletion floor seven')
    require(pure == [7] * 5, 'pure-correction floor seven')
    require(min(v for p in proper for row in p['ranks'] for v in row) == 8,
            'every maximal proper deletion restores floor eight')
    coordinate_costs = [cost(pairing, [i for i in range(112) if x[i][k]],
                            [i for i in range(112) if x[i][k]]) for k in range(8)]
    require(coordinate_costs == [8] * 8, 'coordinate COPY baseline')
    before = rank(pairing[i] for i in supports[0])
    after = rank(pairing[i] for i in surviving[0])
    require((before, after) == (8, 7), 'genuine boundary span loss')
    counts = Counter(v for p in proper for row in p['ranks'] for v in row)
    return {
        'root_order': 'lexicographic positive-first doubled E8 roots',
        'roots': roots, 'coordinate_pair': [0, 1], 'singleton': 0,
        'boundary': u_set, 'common_odd_neighbors': neighbors,
        'stratum_coefficients': [list(s) for s in STRATA],
        'supports': supports, 'right_survivors': columns,
        'original_ranks': original, 'full_deletion_ranks': full,
        'pure_correction_ranks': pure, 'proper_deletions': proper,
        'coordinate_costs': coordinate_costs,
        'boundary_spans': {'before': before, 'after': after},
        'summary': {'pairing_checks': 655, 'original_min': 8,
                    'full_deletion_min': 7, 'pure_correction_min': 7,
                    'proper_deletion_checks': 600,
                    'proper_rank_counts': {str(k): v for k, v in sorted(counts.items())}},
    }


# Gaussian rationals, with ordinary transpose and no floating point.
def q(x=0, y=0):
    return (F(x), F(y))


def add(z, w):
    return (z[0] + w[0], z[1] + w[1])


def neg(z):
    return (-z[0], -z[1])


def mul(z, w):
    return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])


def inv(z):
    d = z[0] ** 2 + z[1] ** 2
    require(d != 0, 'nonzero scalar inverse')
    return (z[0] / d, -z[1] / d)


def total(values):
    value = q()
    for v in values:
        value = add(value, v)
    return value


def inverse(matrix):
    n = len(matrix)
    a = [row[:] + [q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j] != q()), None)
        require(p is not None, 'invertible factor change')
        a[j], a[p] = a[p], a[j]
        scale = inv(a[j][j])
        a[j] = [mul(v, scale) for v in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [add(v, neg(mul(scale, w))) for v, w in zip(a[i], a[j])]
    return [row[n:] for row in a]


def factors(x, u, lam, matrix, wrong_transpose=False):
    mi = inverse(matrix)
    left = [[q(row[0]), q(row[1]), u[i]] for i, row in enumerate(x)]
    right = [[q(row[0]), q(row[1]), lam if i == 0 else q()]
             for i, row in enumerate(x)]
    d = [[total(mul(row[k], matrix[k][j]) for k in range(3)) for j in range(3)]
         for row in left]
    t = [[total(mul(row[k], mi[k][j] if wrong_transpose else mi[j][k])
                for k in range(3)) for j in range(3)] for row in right]
    return d, t


def validate_factors(x, u, lam, d, t, conjugate=False):
    for i in range(112):
        for j in range(112):
            actual = total(mul(d[i][k], (t[j][k][0], -t[j][k][1])
                               if conjugate else t[j][k]) for k in range(3))
            expected = q(x[i][0] * x[j][0] + x[i][1] * x[j][1])
            if j == 0:
                expected = add(expected, mul(u[i], lam))
            require(actual == expected, 'three-term matrix identity')


def factor_costs(pairing, d, t):
    return [cost(pairing, [i for i in range(112) if d[i][k] != q()],
                 [j for j in range(112) if t[j][k] != q()]) for k in range(3)]


def rejected(call, text):
    try:
        call()
    except ValueError as e:
        require(text in str(e), 'unexpected failure: ' + str(e))
        return
    raise ValueError('negative control accepted: ' + text)


def fixtures_and_controls(x, pairing, finite, sources):
    one, zero, imag = q(1), q(), q(0, 1)
    identity = [[q(i == j) for j in range(3)] for i in range(3)]
    cancellation = [[one, zero, zero], [zero, one, zero], [q(-1), zero, one]]
    dense = [[one, one, one], [zero, one, imag], [one, zero, one]]
    shear = [[one, q(1, 1), zero], [zero, one, q(0, -1)], [zero, zero, one]]
    full = [q(row[0]) if i in EXPECTED_U else zero for i, row in enumerate(x)]
    varied = [zero] * 112
    for n, i in enumerate(EXPECTED_U):
        varied[i] = (one, imag, q(1, 1), q(2, -1))[(n + 39) % 4]
    proper = varied[:]
    proper[EXPECTED_U[39 % 24]] = zero
    singleton = [zero] * 112
    singleton[EXPECTED_U[39 % 24]] = q(1, 1)
    cases = [('zero correction', [zero] * 112, one, identity),
             ('attaining full boundary', full, one, identity),
             ('cancellation moves the bill', full, one, cancellation),
             ('arbitrary full-support phases', varied, imag, dense),
             ('maximal proper support', proper, q(2, -1), dense),
             ('singleton within boundary', singleton, imag, dense),
             ('zero singleton amplitude', full, zero, dense),
             ('complex triangular dual factors', varied, imag, shear),
             ('zero u with dense mixing', [zero] * 112, imag, dense)]
    fixtures = []
    for name, u, lam, m in cases:
        d, t = factors(x, u, lam, m)
        validate_factors(x, u, lam, d, t)
        ranks = factor_costs(pairing, d, t)
        require(sum(r >= 8 for r in ranks) >= 2 or min(ranks) >= 7,
                'proved rank-profile disjunction')
        fixtures.append({'name': name, 'correction_support_size': sum(v != zero for v in u),
                         'three_costs': ranks, 'whole_cost': 48 + sum(ranks),
                         'matrix_entries_checked': 112 * 112})
    require(fixtures[1]['three_costs'] == [8, 8, 0], 'sharp attainment')
    require(fixtures[2]['three_costs'] == [7, 8, 7], 'cost of coupled cancellation')
    controls = []
    broken = deepcopy(sources)
    next(r for r in broken['files'] if r['usage'] == 'input')['sha256'] = '0' * 64
    rejected(lambda: check_sources(broken), 'source digest')
    controls.append('source digest mutation')
    broken = deepcopy(sources)
    broken['files'] = [r for r in broken['files'] if r['path'] != sorted(INPUTS)[0]]
    rejected(lambda: check_sources(broken), 'complete input inventory')
    controls.append('missing proof-relevant source')
    rejected(lambda: require(finite['boundary_spans']['after'] == 8,
                             'false 24-row span preservation'), 'false 24-row span preservation')
    controls.append('false extension of predecessor span premise')
    bad_neighbor = next(j for j in range(112)
                        if any(pairing[i] >> j & 1 for i in EXPECTED_U))
    rejected(lambda: require(all(not (pairing[i] >> bad_neighbor & 1) for i in EXPECTED_U),
                             'free rectangle'), 'free rectangle')
    controls.append('nonfree singleton column')
    d, t = factors(x, varied, imag, dense, wrong_transpose=True)
    rejected(lambda: validate_factors(x, varied, imag, d, t), 'matrix identity')
    controls.append('inverse used without transpose')
    d, t = factors(x, varied, imag, dense)
    rejected(lambda: validate_factors(x, varied, imag, d, t, conjugate=True), 'matrix identity')
    controls.append('conjugate instead of ordinary transpose')
    d, t = factors(x, full, one, cancellation)
    for row in d:
        row[2] = zero
    rejected(lambda: validate_factors(x, full, one, d, t), 'matrix identity')
    controls.append('omitted compensation term behind apparent 15-cost pair')
    rejected(lambda: inverse([[one] * 3 for _ in range(3)]), 'invertible factor change')
    controls.append('singular factor change')
    return fixtures, controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='explicitly write a newly computed receipt')
    parser.add_argument('--check', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    check_sources(sources)
    roots, x, pairing = model()
    finite = finite_premises(roots, x, pairing)
    fixtures, controls = fixtures_and_controls(x, pairing, finite, sources)
    actual = {'schema_version': 1,
              'scope': 'fixed PR1375 24-row boundary, arbitrary complex amplitudes and GL(3,C)',
              'finite_premises': finite, 'fixtures': fixtures, 'controls': controls}
    changed = deepcopy(actual)
    changed['finite_premises']['proper_deletions'][0]['ranks'][0][0] -= 1
    rejected(lambda: require(changed == actual, 'complete receipt equality'), 'complete receipt equality')
    actual['controls'].append('corrupted finite-premise receipt')
    if args.write:
        args.write.write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(args.check.read_text()) == actual, 'complete receipt equality')
    print('PASS_P112_BOUNDARY24_S39 pairings=655 proper_deletions=24 fixtures=9 '
          'entries=112896 controls=9 copy_floor=64')


if __name__ == '__main__':
    main()
