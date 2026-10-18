#!/usr/bin/env python3
"""Independent finite-premise method: all maximal two-anchor erasures.

No primary or predecessor imports. Euclidean roots and set elimination replace
the primary's lattice coordinates, packed-bit character census and cut proof.
Same AI-assisted author; this is not independent human review. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNIVERSE = frozenset(range(112))


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def canonical(r):
    return max(tuple(r), tuple(-x for x in r))


def dimension(rows):
    # Sparse Gaussian elimination with smallest-column pivots and symmetric
    # differences; no integer bit-packing or calls to the primary rank engine.
    echelon = {}
    for raw in rows:
        row = set(raw)
        while row:
            leading = min(row)
            if leading in echelon:
                row.symmetric_difference_update(echelon[leading])
            else:
                echelon[leading] = row
                break
    return len(echelon)


def geometry():
    roots = {canonical(signs) for signs in product((-1, 1), repeat=8)
             if product_sign(signs) == 1}
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[a], r[b] = 2, 2 * sign
            roots.add(canonical(r))
    check(len(roots) == 120, 'complete 120 E8 root lines')
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            r = [0] * 8
            r[i], r[i + 1] = 2, 2 * sign
            frame.append(tuple(r))
    roots = sorted(roots - set(frame))
    check(len(roots) == 112, 'P112 puncture')
    x = [[dot(r, f) // 4 for f in frame] for r in roots]
    matrix = [{j for j, s in enumerate(roots) if (1 + dot(r, s) // 4) % 2}
              for r in roots]
    for i in range(112):
        for j in range(112):
            check(dot(roots[i], roots[j]) % 4 == 0, 'integral root Gram')
            check(dot(x[i], x[j]) == dot(roots[i], roots[j]) // 2,
                  'coordinate/root identity')
            check((j in matrix[i]) == (i in matrix[j]), 'pairing symmetry')
    check(dimension(matrix) == 9, 'ambient binary rank')
    return roots, x, matrix


def product_sign(values):
    result = 1
    for value in values:
        result *= value
    return result


def supports(x):
    return [{i for i, row in enumerate(x) if a * row[2] + b * row[4]}
            for a, b in ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2))]


def direct_erasures(matrix, ss):
    original = [dimension(matrix[i] for i in s) for s in ss]
    check(original == [8, 8, 9, 9, 9], 'five original spans')
    stream, histogram = bytearray(), Counter()
    for beta, gamma in combinations(range(112), 2):
        deleted = UNIVERSE - matrix[beta] - matrix[gamma]
        histogram[len(deleted)] += 1
        for wanted, s in zip(original, ss):
            actual = dimension(matrix[i] for i in sorted(s - deleted))
            check(actual == wanted, 'two-anchor span preservation')
            stream.append(actual)
    check(sum(histogram.values()) == 6216 and len(stream) == 31080,
          'complete unordered-anchor domain')
    return {'anchor_pairs': 6216, 'span_checks': len(stream),
            'original_spans': original,
            'maximal_rectangle_row_sizes': {str(k): v for k, v in sorted(histogram.items())},
            'rank_stream_sha256': hashlib.sha256(stream).hexdigest()}


def verify_orbit(x, matrix, maps):
    check(len(maps) == 28 and {tuple(m['pair']) for m in maps}
          == set(combinations(range(8), 2)), 'all 28 coordinate pairs')
    lookup = {canonical(r): i for i, r in enumerate(x)}
    for m in maps:
        p = m['permutation']
        check(sorted(p) == list(range(8)), 'coordinate permutation')
        check(sorted([p[2], p[4]]) == m['pair'], 'selected pair image')
        rows = []
        for i, r in enumerate(x):
            moved = [0] * 8
            for k, coordinate in enumerate(p):
                moved[coordinate] = r[k]
            j = lookup.get(canonical(moved))
            check(j is not None, 'preserved live root set')
            sign = 1 if moved == x[j] else -1
            check(j == m['row_map'][i] and sign == m['signs'][i], 'recorded signed root map')
            rows.append(j)
        check(len(set(rows)) == 112, 'root bijection')
        for i in range(112):
            check({rows[j] for j in matrix[i]} == matrix[rows[i]], 'transported pairing row')
    return 28 * 112 * 112


def term_cost(matrix, a, b):
    right = {j for j, value in enumerate(b) if value}
    return dimension(matrix[i] & right for i, value in enumerate(a) if value)


def integer_fixture(x, matrix):
    v = [int(j in (42, 43)) for j in range(112)]
    u_set = UNIVERSE - matrix[42] - matrix[43]
    u = [x[i][2] if i in u_set else 0 for i in range(112)]
    a, b = [row[2] for row in x], [row[4] for row in x]
    # Literal algebra, without a matrix inverse or the primary fixture builder.
    left = [[a[i] - u[i], b[i], u[i]] for i in range(112)]
    right = [[a[i], b[i], a[i] + v[i]] for i in range(112)]
    entries = 0
    for i in range(112):
        for j in range(112):
            check(dot(left[i], right[j]) == a[i] * a[j] + b[i] * b[j] + u[i] * v[j],
                  'literal compensated identity')
            entries += 1
    costs = [term_cost(matrix, [r[k] for r in left], [r[k] for r in right])
             for k in range(3)]
    omission = next((i, j) for i in range(112) for j in matrix[i]
                    if u[i] * (a[j] + v[j]) != 0)
    i, j = omission
    error = -u[i] * (a[j] + v[j])
    check(error != 0, 'omission changes constrained entry')
    return {'identity_entries': entries, 'replacement_ranks': costs,
            'whole_copy_cost': 48 + sum(costs),
            'omission_entry': [i, j], 'omission_error': error}


def rejects(fn, reason):
    try:
        fn()
    except ValueError as exc:
        check(reason in str(exc), 'wrong rejection: ' + str(exc))
        return reason
    raise ValueError('negative control accepted: ' + reason)


def run():
    roots, x, matrix = geometry()
    primary = json.loads((HERE / 'CERTIFICATE.json').read_text())
    packed = [sum(1 << j for j in row) for row in matrix]
    obj = {'roots': roots, 'X': x, 'B': packed}
    actual_hash = hashlib.sha256(json.dumps(obj, sort_keys=True,
                                separators=(',', ':')).encode()).hexdigest()
    check(actual_hash == primary['geometry_sha256'], 'geometry agreement')
    ss = supports(x)
    baseline = [[dimension(matrix[i] & t for i in s) for t in ss] for s in ss]
    check(baseline == primary['character_census']['baseline_pairings'], 'baseline agreement')
    check(min(map(min, baseline)) == 8, 'baseline cost eight')
    erasures = direct_erasures(matrix, ss)
    orbit_entries = verify_orbit(x, matrix, primary['coordinate_orbit'])
    fixture = integer_fixture(x, matrix)
    controls = []
    controls.append(rejects(lambda: verify_orbit(x, matrix, primary['coordinate_orbit'][:-1]),
                            '28 coordinate'))
    bad = deepcopy(primary['coordinate_orbit'])
    bad[0]['row_map'][0], bad[0]['row_map'][1] = bad[0]['row_map'][1], bad[0]['row_map'][0]
    controls.append(rejects(lambda: verify_orbit(x, matrix, bad), 'signed root map'))
    deleted = ss[0] - matrix[42]
    after = dimension(matrix[i] for i in ss[0] - deleted)
    check(after == 7, 'single-anchor rank drop')
    controls.append(rejects(lambda: check(after == 8, 'single-anchor span claim'), 'single-anchor'))
    controls.append(rejects(lambda: check(fixture['omission_error'] == 0, 'omitted compensation'),
                            'omitted compensation'))
    controls.append(rejects(lambda: check(dimension([matrix[0] & {0}]) == 0,
                                         'diagonal rectangle is free'), 'diagonal rectangle'))
    bad_baseline = deepcopy(baseline)
    bad_baseline[0][0] -= 1
    controls.append(rejects(lambda: check(bad_baseline == baseline, 'changed rank receipt'),
                            'changed rank receipt'))
    return {'status': 'PASS_P112_MULTILINE_INDEPENDENT_S42',
            'geometry_sha256': actual_hash, 'geometry_entries': 12544,
            'baseline_pairings': baseline, 'direct_erasures': erasures,
            'orbit_pairing_entries': orbit_entries, 'integer_fixture': fixture,
            'negative_controls': controls,
            'scope': 'Independent two-anchor finite-premise check; quantified theorem is in README.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', type=Path)
    ap.add_argument('--check', type=Path, default=HERE / 'INDEPENDENT.json')
    args = ap.parse_args()
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        check(result == json.loads(args.check.read_text()), 'complete independent receipt mismatch')
    print(result['status'], 'anchor_pairs=6216 span_checks=31080',
          'orbit_pairs=28 integer_entries=12544 controls=6')


if __name__ == '__main__':
    main()
