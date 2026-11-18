"""Derive every scalar and native residual from the literal local tapes."""
from fractions import Fraction as F
from math import isqrt

ROLES = (236, 544, 1000)
INITIAL = {236: 265, 544: 751, 1000: 265}
OLD = [[F(0), F(1, 4), F(1), F(0)],
       [F(-2), F(0), F(0), F(1)], [F(-4), F(1), F(0), F(0)]]
NEW = [[F(0), F(1, 2), F(1, 4), F(1, 2), F(1, 2), F(1)],
       [F(-2), F(-1), F(1, 2), F(1), F(1), F(0)],
       [F(-4), F(0), F(2), F(2), F(0), F(0)]]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def ports(events, clock):
    return [{'offset': i, 'clock': clock + i, 'kind': event[0], 'role': event[1],
             'frame': event[3] if event[0] == 'MOVE' else event[-1]}
            for i, event in enumerate(events)
            if event[0] == 'MOVE' or F(event[3]).denominator != 1]


def derive(events, clock):
    sites = ports(events, clock)
    at = {row['offset']: i for i, row in enumerate(sites)}
    current = dict(INITIAL)
    rows = {role: [F(0)] * len(sites) for role in ROLES}
    for i, event in enumerate(events):
        op, role = event[:2]
        if op == 'MOVE':
            need(current[role] == event[2] and event[4] is False, 'literal native source chart')
            current[role] = event[3]
        else:
            need(op == 'ADD' and current[role] == current[event[2]] == event[-1], 'literal scalar common chart')
            q = F(event[3])
            rows[role] = [a + q * b for a, b in zip(rows[role], rows[event[2]], strict=True)]
        if i in at:
            rows[role][at[i]] += 1
    return [rows[role] for role in ROLES], sites, [current[role] for role in ROLES]


def gram(matrix):
    return [[sum(a * b for a, b in zip(row, other, strict=True)) for other in matrix] for row in matrix]


def determinant(a):
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def minors(matrix, value):
    a = [[int(i == j) * value - matrix[i][j] for j in range(3)] for i in range(3)]
    return [a[0][0], a[0][0] * a[1][1] - a[0][1] * a[1][0], determinant(a)]


def spectral_certificate(matrix):
    g = gram(matrix)
    scaled = [[16 * x for x in row] for row in g]
    need(all(x.denominator == 1 for row in scaled for x in row), 'integral scaled Gram matrix')
    scaled = [[int(x) for x in row] for row in scaled]
    trace = sum(scaled[i][i] for i in range(3))
    second = sum(scaled[i][i] * scaled[j][j] - scaled[i][j] * scaled[j][i]
                 for i in range(3) for j in range(i + 1, 3))
    polynomial = [1, -trace, second, -determinant(scaled)]
    lo, hi = F(0), F(100)
    need(all(x > 0 for x in minors(g, hi)), 'initial positive definite upper bound')
    for _ in range(80):
        mid = (lo + hi) / 2
        if all(x > 0 for x in minors(g, mid)):
            hi = mid
        else:
            lo = mid
    low, high = minors(g, lo), minors(g, hi)
    need(low[0] > 0 and low[1] > 0 and low[2] < 0 and all(x > 0 for x in high), 'strict largest-eigenvalue bracket')
    need(hi - lo < F(1, 10 ** 20), 'rational eigenvalue interval width')
    scale = 10 ** 12
    norm_lo = F(isqrt(lo.numerator * scale ** 2 // lo.denominator), scale)
    norm_hi = F(isqrt(hi.numerator * scale ** 2 // hi.denominator) + 1, scale)
    need(norm_lo ** 2 <= lo and norm_hi ** 2 > hi, 'exact square-root bracket')
    # A second calculation checks det(tI-16G) without the minor formula.
    for t in range(-2, 6):
        literal = determinant([[int(i == j) * t - scaled[i][j] for j in range(3)] for i in range(3)])
        value = 0
        for coefficient in polynomial:
            value = value * t + coefficient
        need(literal == value, 'characteristic polynomial coefficients')
    return {'matrix': [[str(x) for x in row] for row in matrix],
            'scaled_gram': scaled, 'scaled_characteristic': polynomial,
            'squared_norm_interval': [str(lo), str(hi)],
            'norm_interval': [str(norm_lo), str(norm_hi)],
            'lower_leading_minors': list(map(str, low)), 'upper_leading_minors': list(map(str, high)),
            'one_port_squared_gains': [str(sum(row[j] ** 2 for row in matrix)) for j in range(len(matrix[0]))]}
