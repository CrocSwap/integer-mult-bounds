"""Independent exact continuous-box certificate for 24 physical pair orders.

No author imports and no floating-point arithmetic. Positive Bernstein
coefficients certify the whole five-dimensional box, not sampled points.
"""
from fractions import Fraction as Q
from itertools import permutations, product
from math import comb
import json


def add(a, b, sign=1):
    c = dict(a)
    for e, v in b.items():
        c[e] = c.get(e, 0) + sign * v
        if not c[e]:
            del c[e]
    return c


def mul(a, b):
    c = {}
    for e, v in a.items():
        for f, w in b.items():
            g = tuple(x + y for x, y in zip(e, f))
            c[g] = c.get(g, 0) + v * w
    return {e: v for e, v in c.items() if v}


def sign(p):
    return (-1) ** sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))


def entry(i, j):
    a, b = divmod(i, 2)
    c, d = divmod(j, 2)
    return {(int(a < c), int(a > c), int(b < d), int(b > d)): 1}


def determinant(order):
    matrix = [[entry(order[i], order[j]) for j in range(4)] for i in range(4)]
    displacement = [[add(matrix[i][j], matrix[i - 1][j - 1], -1)
                     if i and j else matrix[i][j] for j in range(4)] for i in range(4)]
    out = {}
    for p in permutations(range(4)):
        term = {(0, 0, 0, 0): sign(p)}
        for i in range(4):
            term = mul(term, displacement[i][p[i]])
        out = add(out, term)
    return out


def box_power(poly, bounds):
    out = {}
    for exponents, coefficient in poly.items():
        term = {(0,) * len(bounds): Q(coefficient)}
        for j, (power, (lo, hi)) in enumerate(zip(exponents, bounds)):
            factor = {}
            for k in range(power + 1):
                e = [0] * len(bounds)
                e[j] = k
                factor[tuple(e)] = comb(power, k) * lo ** (power - k) * (hi - lo) ** k
            term = mul(term, factor)
        out = add(out, term)
    return out


def bernstein_range(poly):
    degrees = tuple(max(e[j] for e in poly) for j in range(5))
    coefficients = []
    for k in product(*(range(d + 1) for d in degrees)):
        b = Q(0)
        for e, a in poly.items():
            if all(i <= j for i, j in zip(e, k)):
                factor = Q(1)
                for i, j, d in zip(e, k, degrees):
                    factor *= Q(comb(j, i), comb(d, i))
                b += a * factor
        coefficients.append(b)
    return min(coefficients), max(coefficients), len(coefficients)


def check():
    # Physical variables u,x are large; v=w*V,y=w*Y with common w>0.
    bounds = [(Q(1023, 1024), Q(1)), (Q(1), Q(2)),
              (Q(1023, 1024), Q(1)), (Q(1), Q(2)), (Q(0), Q(1, 2048))]
    rows = []
    for order in permutations(range(4)):
        raw = determinant(order)
        k = min(e[1] + e[3] for e in raw)
        poly = {(*e, e[1] + e[3] - k): v for e, v in raw.items()}
        orientation = sum(v for e, v in poly.items() if e[4] == 0)
        if orientation not in (-1, 1):
            raise ValueError('Unexpected limiting sign')
        poly = {e: orientation * v for e, v in poly.items()}
        lo, hi, count = bernstein_range(box_power(poly, bounds))
        if lo < Q(1, 4):
            raise ValueError(('Continuous box fails', order, k, str(lo)))
        rows.append({'order': order, 'w_power': k, 'orientation': orientation,
                     'bernstein_min': str(lo), 'bernstein_max': str(hi), 'coefficients': count})
    # Controls: signs, normalization and physical phase orientation matter.
    gray = determinant((0, 1, 3, 2))
    at_equal_half = sum(Q(v) * Q(1, 2) ** sum(e) for e, v in gray.items())
    if at_equal_half != 0:
        raise ValueError('Equal symmetric Gray counterexample failed')
    bad = {e: -v for e, v in box_power({(0, 0, 0, 0, 0): 1}, bounds).items()}
    if bernstein_range(bad)[0] >= Q(1, 4):
        raise ValueError('Sign corruption undetected')
    # The same continuous box does not tensorize to full rank in g=3.
    # H_ij=w^popcount(i & ~j), with all U_i=1 and V_i=w.
    order3 = (0, 1, 2, 4, 3, 6, 7, 5)
    columns = []
    for j in (2, 5):
        column = []
        for i in range(8):
            value = {((order3[i] & ~order3[j] & 7).bit_count(),): 1}
            if i:
                previous = {((order3[i-1] & ~order3[j-1] & 7).bit_count(),): 1}
                value = add(value, previous, -1)
            column.append(value)
        columns.append(column)
    expected = [{(0,): 1}, {(0,): -1, (1,): 1}] + [{} for _ in range(6)]
    if columns[0] != expected or columns[1] != expected:
        raise ValueError('Three-axis exact column coincidence failed')
    return {'status': 'PASS_EXACT_CONTINUOUS_BOX', 'orders': len(rows),
            'meaning': 'All24 determinants have absolute value at least w^k/4, k in{0,1,2}; hence at least w^2/4 for0<w<=1/2048. Bernstein positivity certifies the entire rational box.',
            'bounds': [[str(a), str(b)] for a, b in bounds], 'rows': rows,
            'negative_controls': ['equal symmetric Gray rank failure outside box', 'orientation-sign corruption',
                                  'three-axis exact repeated columns inside the continuous box'],
            'three_axis_boundary': {'order': order3, 'equal_columns_zero_based': [2, 5],
                                    'common_column': ['1', 'w-1'] + ['0'] * 6,
                                    'scope': 'The continuous-box full-rank lemma fails in g3. This is not an actual distinct-prime source counterexample.'}}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2, sort_keys=True))
