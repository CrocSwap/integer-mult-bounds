"""Independent exact complex matrix oracle (no production imports)."""
from fractions import Fraction as F

ZERO = (F(0), F(0))


def plus(a, b): return tuple(x+y for x, y in zip(a, b))
def minus(a, b): return tuple(x-y for x, y in zip(a, b))
def times(a, b): return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]
def quotient(a, b):
    v = times(a, (b[0], -b[1])); d = b[0]**2+b[1]**2
    return v[0]/d, v[1]/d


def solve(matrix, rhs):
    n = len(rhs)
    a = [row[:]+[v] for row, v in zip(matrix, rhs)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if a[i][j] != ZERO)
        a[j], a[pivot] = a[pivot], a[j]
        divisor = a[j][j]
        a[j] = [quotient(v, divisor) for v in a[j]]
        for i in range(n):
            if i != j:
                coefficient = a[i][j]
                a[i] = [minus(v, times(coefficient, w)) for v, w in zip(a[i], a[j])]
    return [row[-1] for row in a]


def oracle(x, factors, scale):
    y = [(v[0]*scale, v[1]*scale) for v in x]
    n = len(x)
    for rho, _, phase, direction in factors:
        matrix = [[ZERO]*n for _ in range(n)]
        for i in range(n):
            matrix[i][i] = minus(matrix[i][i], rho)
            j = (i-direction) % n
            matrix[i][j] = plus(matrix[i][j], phase(i))
        y = solve(matrix, y)
    return y


def close(actual, expected, bound, label):
    if len(actual) != len(expected) or any(sum(t*t for t in minus(a, b)) > bound*bound for a, b in zip(actual, expected)):
        raise ValueError(label)
