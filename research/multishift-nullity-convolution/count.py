"""Evaluate the credited joint-nullity law by exact convolution.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from math import comb, prod


def require(ok, message):
    if not ok:
        raise ValueError(message)


def prime_power(q):
    if type(q) is not int or q < 2:
        return False
    p = 2
    while p * p <= q and q % p:
        p += 1
    if p * p > q:
        return True
    while q % p == 0:
        q //= p
    return q == 1


def joint_count(q, n, nullities):
    """Count matrices for distinct shifts; return an exact nonnegative integer."""
    require(prime_power(q), "q must be a prime power")
    require(type(n) is int and n >= 0, "n must be nonnegative")
    a = tuple(nullities)
    require(len(a) <= q, "too many distinct shifts")
    require(all(type(x) is int and x >= 0 for x in a), "invalid nullity")
    r = sum(a)
    if r > n:
        return 0
    m = n - r
    factorial = [1]
    powers = [1]
    for j in range(1, n + 1):
        powers.append(powers[-1] * q)
        factorial.append(factorial[-1] * (powers[-1] - 1))
    coefficients = [Fraction(1)] + [Fraction(0)] * m
    for x in a:
        factor = []
        power = 1
        for u in range(m + 1):
            factor.append(Fraction(1, factorial[u] * power))
            power *= powers[x]
        coefficients = [sum((coefficients[j] * factor[k - j]
                            for j in range(k + 1)), Fraction(0))
                        for k in range(m + 1)]
    exponent = n * (n - r) + comb(r, 2) - sum(comb(x, 2) for x in a)
    weight = q**exponent
    total = Fraction(0)
    for u in range(m + 1):
        total += (-1)**u * weight * coefficients[u] / factorial[m - u]
        if u < m:
            require(weight % powers[m - u] == 0, "invalid weight recurrence")
            weight //= powers[m - u]
    value = total * Fraction(factorial[n], prod(factorial[x] for x in a))
    require(value.denominator == 1 and value >= 0, "invalid exact count")
    return value.numerator
