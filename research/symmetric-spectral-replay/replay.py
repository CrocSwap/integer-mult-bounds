#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Retained primary verifier: Ali Romman, PR5624, Apache-2.0.
# Symmetric adjacency-power evaluation: Nick Petalas.
# See README.md for the exact source adapter and equivalence proof.
"""Check the finite alternating-plane decoder and its support certificate."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() & 1


def basis(values):
    pivots = {}
    for x in values:
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return tuple(pivots.values())


def copy_tariff(source, reader):
    left, right = basis(source), basis(reader)
    return len(basis(sum(dot(x, y) << j for j, y in enumerate(right)) for x in left))


def modular_rank(matrix, prime):
    a = [[x % prime for x in row] for row in matrix]
    r = 0
    for j in range(len(a[0]) if a else 0):
        k = next((k for k in range(r, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[r], a[k] = a[k], a[r]
        scale = pow(a[r][j], -1, prime)
        a[r] = [(x * scale) % prime for x in a[r]]
        for k in range(r + 1, len(a)):
            scale = a[k][j]
            if scale:
                a[k] = [(x - scale * y) % prime for x, y in zip(a[k], a[r])]
        r += 1
    return r


def solve(matrix, rhs):
    a = [[Fraction(x) for x in row] + [Fraction(y)] for row, y in zip(matrix, rhs)]
    for j in range(len(a)):
        k = next(i for i in range(j, len(a)) if a[i][j])
        a[j], a[k] = a[k], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for k in range(len(a)):
            if k != j:
                scale = a[k][j]
                a[k] = [x - scale * y for x, y in zip(a[k], a[j])]
    return [row[-1] for row in a]


def convolution(left, right):
    out = {}
    for x, (a, b) in left.items():
        for y, (c, d) in right.items():
            u, v = out.get(x ^ y, (0, 0))
            out[x ^ y] = (u + a * c - b * d, v + a * d + b * c)
    return {x: v for x, v in out.items() if v != (0, 0)}


def native_checks(plane):
    a, b, c = plane
    product = {0: (1, 0)}
    for v in plane:
        product = convolution(product, {0: (1, 1), v: (1, -1)})
    need(product == {0: (-4, 0), a: (4, 0), b: (4, 0), c: (4, 0)}, 'native phase')
    q = {0: (-1, 0), a: (1, 0), b: (1, 0), c: (1, 0)}
    need(convolution(q, q) == {0: (4, 0)}, 'native square')
    rows = tuple((b if a >> j & 1 else 0) ^ (a if b >> j & 1 else 0) for j in range(7))
    need(len(basis(rows)) == 2, 'native rank two')
    need(len(basis(row ^ (1 << j) for j, row in enumerate(rows))) == 5, 'complement rank five')


def rejected(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError('corruption was accepted')


def symmetric_step(neighbors, power):
    n = len(neighbors)
    result = [[0] * n for _ in range(n)]
    for i, row in enumerate(neighbors):
        for j in range(i, n):
            value = sum(power[k][j] for k in row)
            result[i][j] = value
            result[j][i] = value
    return result


def compute():
    points = tuple(x for x in range(1, 128) if x.bit_count() % 2 == 0)
    need(len(points) == 63 and len(basis(points)) == 6, 'even space')
    need(copy_tariff(points, points) == 6, 'nondegenerate even space')
    all_planes = sorted({tuple(sorted((a, b, a ^ b))) for a in points for b in points if a != b})
    planes = tuple(e for e in all_planes if dot(e[0], e[1]))
    need(len(all_planes) == 651 and len(planes) == 336, 'plane census')
    for e in planes:
        native_checks(e)
    neighbors = [tuple(j for j, f in enumerate(planes) if all(not dot(a, b) for a in e[:2] for b in f[:2])) for e in planes]
    need(all(len(row) == 20 and i not in row for i, row in enumerate(neighbors)), 'graph degree')
    need(all(i in neighbors[j] for i, row in enumerate(neighbors) for j in row), 'graph symmetry')

    # N is the numerator of the spectral projector for eigenvalue 2.
    n = len(planes)
    power = [[int(i == j) for j in range(n)] for i in range(n)]
    numerator = [[0] * n for _ in range(n)]
    annihilator = [[0] * n for _ in range(n)]
    nc = (5120, 1024, -144, -16, 1, 0)
    ac = (-10240, 3072, 1312, -112, -18, 1)
    traces = []
    for degree in range(6):
        traces.append(sum(power[i][i] for i in range(n)))
        for i in range(n):
            for j, value in enumerate(power[i]):
                numerator[i][j] += nc[degree] * value
                annihilator[i][j] += ac[degree] * value
        if degree < 5:
            power = symmetric_step(neighbors, power)
    need(not any(any(row) for row in annihilator), 'annihilator identity')
    roots = (-8, -4, 2, 8, 20)
    multiplicities = solve([[x ** k for x in roots] for k in range(5)], traces[:5])
    need(multiplicities == [27, 105, 168, 35, 1], 'exact spectrum')
    need(sum(numerator[i][i] for i in range(n)) == 6480 * 168, 'projector trace')

    prime = 65537
    need(all(prime % d for d in range(2, isqrt(prime) + 1)), 'prime modulus')
    census = []
    first = None
    for e in all_planes:
        vectors = tuple(v for v in points if not dot(v, e[0]) and not dot(v, e[1]))
        need(len(vectors) == 15 and len(basis(vectors)) == 4, 'four-space dimension')
        ids = tuple(i for i, f in enumerate(planes) if all(v in vectors for v in f))
        minor = [[numerator[i][j] for j in ids] for i in ids]
        r = modular_rank(minor, prime)
        need(r == len(ids), 'four-space principal minor')
        census.append([list(e), len(ids), r])
        if first is None:
            first = minor
    counts = Counter((s, r) for _, s, r in census)
    need(counts == {(16, 16): 315, (20, 20): 336}, 'support census')

    # The 336-column factorization of K is a positive tariff control.
    tariffs = []
    for i, e in enumerate(planes):
        source = [v for j in (i, *neighbors[i]) for v in planes[j]]
        tariffs.append(copy_tariff(source, e))
    need(tariffs == [2] * n, 'column factorization tariff')
    e = planes[0]
    bad_q = {0: (1, 0), **{v: (1, 0) for v in e}}
    rejected(lambda: need(convolution(bad_q, bad_q) == {0: (4, 0)}, 'wrong constant sign'))
    bad_minor = [row[:] for row in first]
    bad_minor[0] = [0] * len(bad_minor)
    rejected(lambda: need(modular_rank(bad_minor, prime) == len(bad_minor), 'singular minor'))
    rejected(lambda: need(all(x == 0 for x in numerator[0]), 'coordinate vector outside image'))
    rejected(lambda: need(n - max(multiplicities) == 167, 'false fitting rank'))
    return {
        'status': 'PASS_ALTERNATING_PLANE_SPECTRAL_COPY',
        'scope': 'I-A/2 with exactly 168 scalar factors over characteristic zero',
        'ambient_dimension': 7, 'active_dimension': 6,
        'ports': n, 'degree': 20, 'native_rank_counts': {'2': n},
        'complement_rank_counts': {'5': n},
        'traces_A_power_0_through_5': traces,
        'spectrum': [[x, int(m)] for x, m in zip(roots, multiplicities)],
        'annihilator_coefficients_low_first': list(ac),
        'projector_numerator_coefficients_low_first': list(nc[:5]),
        'projector_denominator': 6480, 'minor_prime': prime,
        'four_space_minor_ranks': [[s, r, count] for (s, r), count in sorted(counts.items())],
        'four_space_census_sha256': hashlib.sha256(json.dumps(census, separators=(',', ':')).encode()).hexdigest(),
        'minimum_uniform_fitting_rank': 168, 'minimum_rank_coefficient': '-1/2',
        'minimum_factor_support_dimension': 5, 'minimum_factor_tariff': 4,
        'copy_floor_for_168_terms': 672, 'two_coordinate_allowance': 672,
        'column_control_terms': n, 'column_control_copy_mass': sum(tariffs),
        'rejection_controls': 4, 'new_kappa': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = compute()
    expected = json.loads((Path(__file__).resolve().parent / 'RESULT.json').read_text())
    need(result == expected, 'receipt differs')
    if args.output:
        with args.output.open('x') as output:
            json.dump(result, output, indent=2)
            output.write('\n')
    print(result['status'])


if __name__ == '__main__':
    main()
