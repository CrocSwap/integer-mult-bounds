"""Exact reverse demands for the literal Newton-W neighbor additions.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from math import comb

ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def add(x, y):
    return (x[0]+y[0], x[1]+y[1])


def scale(x, q):
    return (x[0]*q, x[1]*q)


def mul(x, y):
    return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])


def power(x, n):
    value = ONE
    for _ in range(n):
        value = mul(value, x)
    return value


def v2(x):
    if x <= 0:
        raise ValueError('Use a positive integer')
    return (x & -x).bit_length()-1


def valuation(x):
    norm = x[0]*x[0]+x[1]*x[1]
    if not norm:
        return None
    return v2(norm.numerator)-v2(norm.denominator)


def validate(n, a, degree, digits):
    if (any(type(x) is not int for x in (n, a, degree, digits))
            or not 1 <= n <= 128 or not 1 <= degree <= n
            or not 0 <= a <= n-degree or not 0 <= digits <= 10000):
        raise ValueError('Invalid n, interval, degree or precision')


def radial_w(values, n):
    out = []
    for j in range(n+1):
        value = scale(values[j], n)
        if j:
            value = add(value, scale(values[j-1], -j))
        if j < n:
            value = add(value, scale(values[j+1], -(n-j)))
        out.append(scale(value, Q(1, 2)))
    return out


def kernels(n, a, degree):
    validate(n, a, degree, 0)
    state = [ZERO]*(n+1)
    answer = {}
    for h in range(degree, 0, -1):
        if h < degree:
            w = radial_w(state, n)
            state = [scale(add(w[j], scale(state[j], -a-h)), Q(1, h+1))
                     for j in range(n+1)]
        coefficient = mul(power((Q(0), Q(1)), a), power((Q(-1), Q(1)), h))
        state[0] = add(state[0], coefficient)
        answer[h] = [scale(x, Q(1, 2*h)) for x in state]
    return answer


def plan(n, a, degree, digits):
    validate(n, a, degree, digits)
    demands = []
    for h in range(1, degree+1):
        debt, witness_degree = max((k-2*h+2+2*v2(h*comb(k, h)), k)
                                  for k in range(h, degree+1))
        q = max(0, digits+debt)
        shell = digits+degree-2*h+2+2*v2(h*comb(degree, h))
        demands.append({'stage': h, 'digits': q, 'minimum_valuation': -debt,
                        'witness_distance': witness_degree-h,
                        'shell_floor': max(0, shell)})
    return {'n': n, 'a': a, 'degree': degree, 'output_digits': digits,
            'demands': demands,
            'neighbor_adds': degree*n*(1 << n),
            'minimum_neighbor_precision_mass': n*(1 << n)*sum(x['digits'] for x in demands),
            'shell_mass_floor': n*(1 << n)*sum(x['shell_floor'] for x in demands)}
