#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Finite lemmas for the single-odd-entry rank-nine decoder theorem.

No predecessor implementation or numerical library is imported. Rank over F3
supplies exact nonzero-minor lower bounds over Q and C; integer null vectors
supply matching upper bounds. The universal argument is in PROOF.md.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def rank3(rows, width=8):
    """Exact F3 rank, stopping once the ambient dimension is reached."""
    pivots = {}
    for row in rows:
        value = [x % 3 for x in row]
        for col in range(width):
            if not value[col]:
                continue
            if col in pivots:
                scale = value[col]
                value = [(x - scale * y) % 3 for x, y in zip(value, pivots[col])]
            else:
                inv = 1 if value[col] == 1 else 2
                pivots[col] = [(inv * x) % 3 for x in value]
                break
        if len(pivots) == width:
            return width
    return len(pivots)


def model():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((1, -1), repeat=2):
            r = [0] * 8
            r[i], r[j] = 2 * si, 2 * sj
            roots.append(tuple(r))
    roots.extend(s for s in itertools.product((1, -1), repeat=8)
                 if s.count(-1) % 2 == 0)
    lines = []
    seen = set()
    for r in roots:
        key = min(r, tuple(-x for x in r))
        if key not in seen:
            seen.add(key)
            lines.append(r)
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            r = [0] * 8
            r[i], r[i + 1] = 2, 2 * sign
            frame.append(lines.index(tuple(r)))
    ip = []
    for r in lines:
        require(dot(r, r) == 8, 'root normalization')
        require(all(dot(r, s) % 4 == 0 for s in lines), 'integral Gram matrix')
        ip.append([dot(r, s) // 4 for s in lines])
    pairing = [sum(((g + 1) % 2) << j for j, g in enumerate(row)) for row in ip]
    live = [i for i in range(120) if i not in frame]
    require(len(roots) == 240 and len(lines) == 120 and len(live) == 112,
            'E8/P112 coverage')
    require(all(ip[i][j] == (2 if i == j else 0) for i in frame for j in frame),
            'orthogonal puncture frame')
    require(rank2(pairing) == 9 and len(set(pairing)) == 120,
            'nondegenerate distinct binary labels')
    return lines, frame, live, ip, pairing


def functionals(pairing):
    """All nonzero functionals via their 120 evaluations.

    Their evaluations form the row space of the nondegenerate pairing matrix.
    Constructing the entire space avoids choosing binary label coordinates.
    """
    space = {0}
    for row in pairing:
        if row not in space:
            space |= {x ^ row for x in space}
    require(len(space) == 512, 'complete rank-nine functional space')
    return sorted(space - {0})


def mask(indices):
    return sum(1 << i for i in indices)


def pair_rank(pairing, rows, cols):
    cm = mask(cols)
    return rank2(pairing[i] & cm for i in rows)


def kernel_census(lines, frame, live, ip, pairing, hypers):
    require(len(hypers) == 511 and len(set(hypers)) == 511,
            'missing or repeated label hyperplane')
    hist = Counter()
    reduced = []
    supports_checked = 0
    for alpha in live:
        allowed = {pairing[g]: g for g in frame + [alpha]}
        found = []
        for h in hypers:
            rows = [lines[i] for i in live if i != alpha and (h >> i) & 1]
            r = rank3(rows)
            hist[r] += 1
            if h in allowed:
                g = allowed[h]
                require(r == 7 and all(dot(row, lines[g]) == 0 for row in rows),
                        'incorrect one-dimensional complex normal kernel')
                # F3 rank 7 and this exact nonzero integer null vector give
                # rank exactly 7 over Q/C and the complete complex kernel.
                found.append(g)
            else:
                require(r == 8, 'unexpected reduced-support direction')
        require(sorted(found) == sorted(frame + [alpha]), 'incomplete kernel classification')
        for g in found:
            support = [i for i in live if i != alpha and ip[g][i] != 0]
            require(rank2(pairing[i] for i in support) == 8,
                    'survivor support lost a binary dimension')
            require(all(not ((pairing[g] >> i) & 1) for i in support),
                    'survivor support has the wrong annihilator')
            supports_checked += 1
        even = [lines[i] for i in live if (pairing[alpha] >> i) & 1]
        require(rank3(even) == 8, 'even neighbors do not span the real root space')
        reduced.append({'deleted_line': alpha, 'normal_lines': sorted(found)})
    require(dict(hist) == {7: 1008, 8: 56224}, 'wrong hyperplane census totals')
    return {'hyperplanes_per_deletion': 511, 'deleted_lines': 112,
            'kernel_rank_histogram': {str(k): v for k, v in sorted(hist.items())},
            'survivor_hyperplanes': supports_checked, 'even_neighbor_spans': 112,
            'reduced_normals': reduced}


def geometry(lines, frame, live, ip, pairing):
    require(rank3(lines[i] for i in live) == 8, 'live root rank')
    for alpha in live:
        require(rank3(lines[i] for i in live if i != alpha) == 8,
                'singleton is not outside the live root code')
        require(sum(ip[alpha][g] != 0 for g in frame) == 4,
                'odd root has other than four nonzero frame coordinates')
    neighbors = [[i for i in range(120) if i != g and ip[g][i] != 0]
                 for g in range(120)]
    for g in range(120):
        require(rank2(pairing[i] for i in neighbors[g]) == 8,
                'root hyperplane rank')
    for g, h in itertools.product(range(120), repeat=2):
        require(pair_rank(pairing, neighbors[g], neighbors[h]) ==
                8 - (ip[g][h] % 2), 'root-hyperplane pairing formula')
    odd = [(a, b) for a in live for b in live if ip[a][b] % 2]
    require(len(odd) == 5824, 'odd singleton coverage')
    for a, b in odd:
        low_left = [g for g in frame if ip[g][b] % 2] + [a]
        require(len(low_left) == 5 and rank3(lines[g] for g in low_left) <= 5,
                'all-cost-seven left-normal obstruction')
        require(pair_rank(pairing, [a], [b]) == 0, 'singleton is not free')
    return {'root_hyperplane_pairings': 14400, 'odd_singletons': len(odd),
            'all_seven_left_normal_dimension_upper': 5,
            'outside_code_singletons': 112, 'frame_coordinates_per_live_root': 4}


# Exact Gaussian rationals for all-entry fixtures. Ordinary transpose only.
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))
IMAG = (Q(0), Q(1))


def scalar(x):
    return x if isinstance(x, tuple) else (Q(x), Q(0))


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def mul(x, y):
    if x == ZERO or y == ZERO:
        return ZERO
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def inv(x):
    require(x != ZERO, 'singular factor-basis matrix')
    norm = x[0] ** 2 + x[1] ** 2
    return (x[0] / norm, -x[1] / norm)


def transpose(a):
    return [list(row) for row in zip(*a)]


def matmul(a, b):
    bt = transpose(b)
    return [[sum_gaussian(mul(x, y) for x, y in zip(row, col)) for col in bt]
            for row in a]


def sum_gaussian(values):
    out = ZERO
    for value in values:
        out = add(out, value)
    return out


def identity(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    aug = [row[:] + extra for row, extra in zip(a, identity(n))]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != ZERO), None)
        require(pivot is not None, 'singular factor-basis matrix')
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = inv(aug[col][col])
        aug[col] = [mul(x, scale) for x in aug[col]]
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                aug[r] = [add(x, neg(mul(factor, y))) for x, y in zip(aug[r], aug[col])]
    return [row[n:] for row in aug]


def fixture_factors(live, frame, ip, alpha, beta, amplitude, h):
    d = [[scalar(ip[i][g]) for g in frame] + [scalar(i == alpha)] for i in live]
    t = [[scalar(ip[i][g]) for g in frame] +
         [amplitude if i == beta else ZERO] for i in live]
    return matmul(d, h), matmul(t, transpose(inverse(h)))


def validate_fixture(d, t, live, ip, pairing, alpha, beta, amplitude):
    require(alpha in live and beta in live and ip[alpha][beta] % 2 == 1,
            'completion is outside the odd-entry scope')
    require(amplitude != ZERO, 'completion amplitude must be nonzero')
    require(len(d) == len(t) == 112 and all(len(row) == 9 for row in d + t),
            'nine-term factor dimensions')
    actual = matmul(d, transpose(t))
    for ri, i in enumerate(live):
        for cj, j in enumerate(live):
            expected = scalar(2 * ip[i][j])
            if i == alpha and j == beta:
                expected = add(expected, amplitude)
            require(actual[ri][cj] == expected, 'incorrect single-entry completion')
    costs = [pair_rank(pairing, [live[i] for i in range(112) if d[i][k] != ZERO],
                       [live[j] for j in range(112) if t[j][k] != ZERO]) for k in range(9)]
    require(sum(costs) >= 64, 'fixture contradicts copy floor')
    return costs


def fixtures(live, frame, ip, pairing):
    alpha, beta = next((a, b) for a in live for b in live if ip[a][b] % 2)
    cases = [('attaining', ONE, identity(9)), ('imaginary-completion', IMAG, identity(9))]
    h = identity(9)
    h[8][0] = ONE
    cases.append(('pure-singleton-side', IMAG, h))
    h = identity(9)
    for j in range(8):
        h[j][0] = scalar(ip[alpha][frame[j]])
    shear = identity(9)
    shear[8][0] = scalar(-4)
    h = matmul(h, shear)
    cases.append(('attaining-with-seven-and-one', IMAG, h))
    h = identity(9)
    for k in range(9):
        shear = identity(9)
        shear[k][(k + 1) % 9] = IMAG if k % 2 else scalar(Q(1, 2))
        h = matmul(h, shear)
    cases.append(('all-nine-columns-mixed', IMAG, h))
    out = []
    for name, amplitude, h in cases:
        d, t = fixture_factors(live, frame, ip, alpha, beta, amplitude, h)
        costs = validate_fixture(d, t, live, ip, pairing, alpha, beta, amplitude)
        if name in ('attaining', 'imaginary-completion'):
            require(costs == [8] * 8 + [0], 'sharp cost-64 attainment')
        if name == 'attaining-with-seven-and-one':
            require(costs == [7] + [8] * 7 + [1], 'coupled cost-seven compensation')
        out.append({'name': name, 'alpha': alpha, 'beta': beta,
                    'amplitude': [str(x) for x in amplitude],
                    'term_costs': costs, 'copy_cost': sum(costs), 'matrix_entries': 12544})
    return out


def check_sources():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    count = 0
    for item in source['files']:
        if item['usage'] == 'input':
            require(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'],
                    'source input drift: ' + item['path'])
            count += 1
    require(count == 1, 'source input coverage')


def build():
    check_sources()
    lines, frame, live, ip, pairing = model()
    return {'schema_version': 1, 'status': 'PASS_P112_SINGLETON_RANK9_LEMMAS',
            'claim': 'PROOF.md: every nine-term factorization of a nonzero single-odd-entry completion costs at least 64',
            'kernel_census': kernel_census(lines, frame, live, ip, pairing, functionals(pairing)),
            'geometry': geometry(lines, frame, live, ip, pairing),
            'fixtures': fixtures(live, frame, ip, pairing),
            'scope': 'Finite E8/P112 lemmas plus a written universal complex proof; no physical supplier or new kappa'}


def check_receipt(actual, recorded):
    require(actual == recorded, 'certificate differs from the complete replay')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate the package-local certificate')
    args = parser.parse_args()
    actual = build()
    if args.write:
        (HERE / 'CERTIFICATE.json').write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    else:
        check_receipt(actual, json.loads((HERE / 'CERTIFICATE.json').read_text()))
    print('PASS_P112_SINGLETON_RANK9_LEMMAS hyperplanes=57232 kernels=1008 '
          'odd_entries=5824 pairings=14400 fixtures=5 sharp_copy_floor=64')


if __name__ == '__main__':
    try:
        main()
    except (Invalid, OSError, KeyError, json.JSONDecodeError) as error:
        print('FAIL_P112_SINGLETON_RANK9:', error, file=sys.stderr)
        sys.exit(1)
