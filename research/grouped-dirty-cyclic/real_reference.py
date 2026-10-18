"""Independent dense real-rational oracle and small matrix helpers."""
from fractions import Fraction as F


def rounded(x, bits):
    scale = 1 << bits
    value = x*scale + F(1, 2)
    return F(value.numerator // value.denominator, scale)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def power(a, n):
    out = identity(len(a))
    while n:
        if n & 1:
            out = multiply(out, a)
        a = multiply(a, a)
        n //= 2
    return out


def solve(a, b):
    n = len(a)
    a = [row.copy()+[rhs] for row, rhs in zip(a, b)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        value = a[j][j]
        a[j] = [x/value for x in a[j]]
        for i in range(n):
            if i != j:
                value = a[i][j]
                a[i] = [x-value*y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


def poly(roots):
    q = [F(1)]
    for root in roots:
        out = [F(0)]*(len(q)+1)
        for j, value in enumerate(q):
            out[j] += value
            out[j+1] -= root*value
        q = out
    return q


def exact(x, q):
    length = len(x)
    a = [[F(0)]*length for _ in x]
    for i in range(length):
        for j, value in enumerate(q):
            a[i][(i-j) % length] += value
    return solve(a, x)
