"""Small exact matrix operations for the fixed conditioning certificate.

Produced by Nick Petalas. Apache-2.0.
"""
from fractions import Fraction as F
from itertools import combinations


def need(condition, message):
    if not condition:
        raise ValueError(message)


def shape(a):
    n = len(a)
    need(1 <= n <= 4, "matrix dimension must be 1..4")
    need(all(len(row) == n for row in a), "square matrix required")
    need(all(type(x) in (int, F) for row in a for x in row), "exact entries required")
    need(all(abs(x.numerator).bit_length() <= 8192 and x.denominator.bit_length() <= 8192
             for row in a for x in map(F, row)), "matrix entry capacity")
    return n


def identity(n):
    need(type(n) is int and 1 <= n <= 4, "identity dimension")
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def transpose(a):
    n = shape(a)
    return tuple(tuple(a[j][i] for j in range(n)) for i in range(n))


def multiply(a, b):
    n = shape(a)
    need(shape(b) == n, "matrix dimensions differ")
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(n)), F(0))
                       for j in range(n)) for i in range(n))


def add(a, b):
    n = shape(a)
    need(shape(b) == n, "matrix dimensions differ")
    return tuple(tuple(a[i][j] + b[i][j] for j in range(n)) for i in range(n))


def scale(a, scalar):
    n = shape(a)
    scalar = F(scalar)
    return tuple(tuple(scalar * a[i][j] for j in range(n)) for i in range(n))


def determinant(a):
    n = shape(a)
    work = [list(map(F, row)) for row in a]
    result = F(1)
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            work[pivot], work[col] = work[col], work[pivot]
            result = -result
        value = work[col][col]
        result *= value
        for row in range(col + 1, n):
            factor = work[row][col] / value
            for k in range(col + 1, n):
                work[row][k] -= factor * work[col][k]
    return result


def inverse(a):
    n = shape(a)
    unit = identity(n)
    work = [list(map(F, a[i])) + list(unit[i]) for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i][col]), None)
        need(pivot is not None, "singular matrix")
        work[pivot], work[col] = work[col], work[pivot]
        value = work[col][col]
        work[col] = [x / value for x in work[col]]
        for row in range(n):
            if row != col:
                factor = work[row][col]
                work[row] = [x - factor * y for x, y in zip(work[row], work[col])]
    answer = tuple(tuple(row[n:]) for row in work)
    need(multiply(a, answer) == unit and multiply(answer, a) == unit, "inverse residual")
    return answer


def psd(a):
    n = shape(a)
    if transpose(a) != a:
        return False
    for size in range(1, n + 1):
        for indices in combinations(range(n), size):
            minor = tuple(tuple(a[i][j] for j in indices) for i in indices)
            if determinant(minor) < 0:
                return False
    return True


def norm_at_most(a, bound):
    n = shape(a)
    bound = F(bound)
    need(bound >= 0, "negative norm bound")
    return psd(add(scale(identity(n), bound * bound),
                   scale(multiply(transpose(a), a), -1)))


def validate_error(d, bound):
    n = shape(d)
    need(F(bound) >= 0, "negative error budget")
    zero = scale(identity(n), 0)
    need(multiply(d, d) == zero, "error must be square-zero")
    need(norm_at_most(d, bound), "error exceeds Euclidean budget")


def shear_error(n, d, lower=False, rank_two=False):
    need(type(n) is int and 2 <= n <= 4, "shear dimension must be 2..4")
    need(type(lower) is bool and type(rank_two) is bool, "shear flags")
    need(not rank_two or n == 4, "rank-two shear needs dimension four")
    d = F(d)
    need(d >= 0, "negative shear size")
    matrix = [[F(0) for _ in range(n)] for _ in range(n)]
    matrix[1 if lower else 0][0 if lower else 1] = d
    if rank_two:
        matrix[3 if lower else 2][2 if lower else 3] = d / 2
    return tuple(tuple(row) for row in matrix)


def orthogonal(n, mode):
    need(type(mode) is int and 0 <= mode < 4, "orthogonal mode")
    matrix = [list(row) for row in identity(n)]
    if n >= 2:
        a, b = ((F(3, 5), F(4, 5)) if mode % 2 == 0
                else (F(5, 13), F(12, 13)))
        i, j = (0, n - 1) if mode < 2 else (0, 1)
        matrix[i][i], matrix[i][j] = a, -b
        matrix[j][i], matrix[j][j] = b, a
    result = tuple(tuple(row) for row in matrix)
    need(multiply(transpose(result), result) == identity(n), "orthogonal residual")
    return result
