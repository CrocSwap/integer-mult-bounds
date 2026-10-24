"""Check the general physical protocol with exact rectangular operators.

This check does not import package or producer code. It supplements the
operator proof and does not replace its hypotheses.
"""

from fractions import Fraction as F
from pathlib import Path
import argparse
import json


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def zero(m, n):
    return [[F(0) for _ in range(n)] for _ in range(m)]


def identity(n):
    result = zero(n, n)
    for i in range(n):
        result[i][i] = F(1)
    return result


def scale(a, c):
    return [[c * x for x in row] for row in a]


def plus(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def times(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def inverse(a):
    n = len(a)
    work = [list(map(F, row)) + eye for row, eye in zip(a, identity(n))]
    for k in range(n):
        pivot = next(j for j in range(k, n) if work[j][k])
        work[k], work[pivot] = work[pivot], work[k]
        divisor = work[k][k]
        work[k] = [x / divisor for x in work[k]]
        for j in range(n):
            if j != k:
                c = work[j][k]
                work[j] = [x - c * y for x, y in zip(work[j], work[k])]
    return [row[n:] for row in work]


def blocks(rows):
    return [sum((block[i] for block in row), []) for row in rows for i in range(len(row[0]))]


def duplicate(a):
    m, n = len(a), len(a[0])
    z = zero(m, n)
    return blocks([[a, z], [z, a]])


q0 = [[0, 2, 0], [3, 0, 0], [0, 0, 5]]
r0 = [[1, 2, 0], [0, 0, 3]]
k0 = [[3, 0], [5, 0], [0, 2]]
q, r, k = duplicate(q0), duplicate(r0), duplicate(k0)
s = times(q, q)
si = inverse(s)
a = blocks([[zero(3, 3), identity(3)], [inverse(times(q0, q0)), zero(3, 3)]])
t = times(q, a)
f_data = s
f_mode = duplicate([[6, 0], [0, 25]])
need(times(f_mode, r) == times(r, f_data), 'R productive intertwiner')
need(times(f_data, k) == times(k, f_mode), 'K productive intertwiner')
need(times(q, f_data) == times(f_data, q), 'Q productive intertwiner')
need(times(t, t) == identity(6), 'The paired T is an involution')
need(times(s, s) != identity(6), 'The example has no fourth-power identity')
g = times(r, plus(identity(6), scale(t, -1)))
h = times(plus(identity(6), t), k)
need(times(g, h) == zero(4, 4), 'The feedback product vanishes')
need(times(h, g) != zero(6, 6), 'The opposite product is not zero')
need(times(q, times(k, r)) != times(times(k, r), q), 'Q does not commute with K R')

ix, iy, iu = 0, 6, 12
def update(target, source, coefficient):
    result = identity(16)
    for i, row in enumerate(coefficient):
        for j, value in enumerate(row):
            result[target + i][source + j] += value
    return result


def core(direction):
    zdd, zdm, zmd = zero(6, 6), zero(6, 4), zero(4, 6)
    dd, mm = identity(6), identity(4)
    kr = times(k, r)
    if direction == 'forward':
        return blocks([[dd, zdd, zdm], [plus(dd, scale(kr, -1)), dd, scale(k, -1)],
                       [scale(r, -2), zmd, scale(mm, -1)]])
    return blocks([[dd, scale(plus(dd, kr), -1), scale(k, -8)], [zdd, dd, zdm],
                   [zmd, scale(r, -F(1, 4)), scale(mm, -1)]])


def diagonal(x, y, u):
    return blocks([[x, zero(6, 6), zero(6, 4)], [zero(6, 6), y, zero(6, 4)],
                   [zero(4, 6), zero(4, 6), u]])


def physical(direction, mode_frame, wrong_order=False):
    pin = diagonal(q, identity(6), identity(4))
    pout = diagonal(f_data, times(f_data, inverse(q)), mode_frame)
    raw = times(pout, times(core(direction), inverse(pin)))
    if direction == 'forward':
        sequence = [update(iu, ix, scale(times(r, a), -1)), raw,
                    update(iu, ix, r), update(iy, iu, times(a, k))]
    else:
        first = update(ix, iu, scale(times(s, times(a, k)), -8))
        second = update(iu, iy, scale(r, -F(1, 8)))
        sequence = ([second, first] if wrong_order else [first, second])
        sequence += [raw, update(iu, iy, scale(times(r, times(s, a)), F(1, 8)))]
    result = pin
    for gate in sequence:
        result = times(gate, result)
    return times(inverse(pout), result)


def expected(direction):
    result = identity(16)
    if direction == 'forward':
        result = times(update(iu, ix, scale(g, -1)),
                       times(diagonal(identity(6), identity(6), scale(identity(4), -1)), result))
        result = times(update(iy, ix, identity(6)), result)
        result = times(update(iy, iu, h), result)
    else:
        result = times(update(ix, iy, scale(identity(6), -1)), result)
        result = times(update(ix, iu, scale(h, -8)), result)
        result = times(diagonal(identity(6), identity(6), scale(identity(4), -1)), result)
        result = times(update(iu, iy, scale(g, -F(1, 8))), result)
    return result


for direction in ('forward', 'backward'):
    actual = physical(direction, f_mode)
    need(actual == expected(direction), 'Every physical input column: ' + direction)
    need(times(inverse(actual), actual) == times(actual, inverse(actual)) == identity(16),
         'Both inverse orders: ' + direction)
    wrong_f = duplicate([[6, 0], [0, 26]])
    need(physical(direction, wrong_f) != actual, 'Missing output intertwiner fails: ' + direction)
need(physical('backward', f_mode, True) != expected('backward'), 'Old-mode order is required')
report = {'status': 'PASS_INDEPENDENT_RECTANGULAR_PHYSICAL_EXAMPLE',
          'data_dimension_per_replica': 3, 'mode_dimension_per_replica': 2,
          'independent_input_columns_per_orientation': 16,
          'Q': q0, 'R': r0, 'K': k0, 'S': [[6, 0, 0], [0, 6, 0], [0, 0, 25]],
          'checks': ['Nontrivial productive intertwiners', 'Q K R differs from K R Q',
                     'Q fourth power is not identity', 'Both physical words equal the claimed formulas',
                     'Both inverse orders', 'G H is zero while H G is not zero'],
          'controls': ['Missing productive mode intertwiner', 'Reversed backward old-mode order'],
          'imports': 'Python standard library only; no package or producer code',
          'scope': 'An independent exact example supports the separately reviewed general proof'}
path = args.out
path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'])
