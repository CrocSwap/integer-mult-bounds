"""Finite Gaussian-integer kernels and a separate canonical-chart oracle.

The C gate convention and chart definition are retained P104/native mathematics.
This implementation is new. Apache-2.0; assistance is disclosed in TASK.json.
"""
from fractions import Fraction

N = 512
ZERO = ((0, 0),) * N


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rotate(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def mapping(record):
    rows, linear, quadratic = (record[k] for k in
                               ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    need(len(rows) == len(linear) == len(quadratic) == 9, 'monomial dimensions')
    need(all(type(x) is int and 0 <= x < N for x in rows + quadratic), 'binary rows')
    need(all(type(x) is int and 0 <= x < 4 for x in linear), 'phase coefficients')
    need(type(record['offset']) is int and 0 <= record['offset'] < N, 'offset')
    need(type(record['phase']) is int and 0 <= record['phase'] < 4, 'global phase')
    result = []
    for x in range(N):
        y = record['offset'] ^ sum(((row & x).bit_count() % 2) << j
                                  for j, row in enumerate(rows))
        phase = record['phase']
        for j in range(9):
            if x >> j & 1:
                cross = quadratic[j] & x & ~((1 << (j+1))-1)
                phase += linear[j] + 2 * cross.bit_count()
        result.append((y, phase % 4))
    need(sorted(y for y, _ in result) == list(range(N)), 'monomial bijection')
    return tuple(result)


def monomial(vector, plan):
    out = list(ZERO)
    for x, (y, phase) in enumerate(plan):
        out[y] = rotate(vector[x], phase)
    return tuple(out)


def half(value, exact=True):
    if exact:
        need(value % 2 == 0, 'inexact internal halving')
    quotient, remainder = divmod(value, 2)
    return quotient + int(remainder == 1 and quotient % 2 != 0)


def stage(vector, bit, sign=1, exact=True):
    """A full C_bit stage; writes use four completed integer numerators."""
    out = list(vector)
    for x in range(N):
        if x & (1 << bit):
            continue
        y = x | (1 << bit)
        a, b = vector[x]
        c, d = vector[y]
        p, q = a-sign*b+c+sign*d, b+sign*a+d-sign*c
        r, s = a+sign*b+c-sign*d, b-sign*a+d+sign*c
        out[x] = (half(p, exact), half(q, exact))
        out[y] = (half(r, exact), half(s, exact))
    return tuple(out)


def native(vector, recipe, exact=True):
    if vector == ZERO:
        return vector
    vector = monomial(vector, mapping(recipe['right']))
    for bit in range(recipe['rank']):
        vector = stage(vector, bit, exact=exact)
    return monomial(vector, mapping(recipe['left']))


def add(left, right, coefficient):
    q = Fraction(coefficient)
    out = []
    for (a, b), (c, d) in zip(left, right, strict=True):
        need(c*q.numerator % q.denominator == d*q.numerator % q.denominator == 0,
             'inexact scalar division')
        out.append((a+c*q.numerator//q.denominator, b+d*q.numerator//q.denominator))
    return tuple(out)


def canonical_plan(frame):
    """Direct span extension, independent of native recipe permutations."""
    columns, space = [], {0}
    for candidate in tuple(frame) + tuple(1 << j for j in range(9)):
        if candidate not in space:
            columns.append(candidate)
            space |= {x ^ candidate for x in space}
    need(len(columns) == 9, 'canonical basis')
    permutation = []
    for x in range(N):
        y = 0
        for j in range(9):
            if x >> j & 1:
                y ^= columns[j]
        permutation.append(y)
    inverse = [0] * N
    for x, y in enumerate(permutation):
        inverse[y] = x
    basis = [inverse[1 << j] for j in range(9)]
    quadratic = [(1 << i) ^ sum(((a & b).bit_count() % 2) << j
                                for j, b in enumerate(basis))
                 for i, a in enumerate(basis)]
    phases = []
    for x in range(N):
        value = sum((quadratic[j] >> j) & 1 for j in range(9) if x >> j & 1)
        value += 2 * sum((quadratic[j] & x & ~((1 << (j+1))-1)).bit_count()
                         for j in range(9) if x >> j & 1)
        phases.append(value % 4)
    return permutation, inverse, phases


def chart(vector, frame, inverse=False):
    if vector == ZERO or not frame:
        return vector
    rank = len(frame)
    if rank != 9:
        p, pi, d = canonical_plan(frame)
        vector = monomial(vector, tuple((pi[x], d[x]) for x in range(N)))
    for bit in range(rank):
        vector = stage(vector, bit, sign=1 if inverse else -1)
    if rank != 9:
        vector = monomial(vector, tuple((p[x], -d[p[x]]) for x in range(N)))
    return vector
