"""Closed probabilities and exact sign comparisons. No finite-field encoding needed."""
from fractions import Fraction
from math import comb, prod


def orbit_size(q, rank, m):
    """Number of pairs (u,V) with a given image S and Vu=t."""
    if not 1 <= rank <= m:
        raise ValueError("rank outside header dimension")
    d = m - 1
    return (q**m - 1) * q**d * prod(q**d - q**i for i in range(rank - 1))


def marginal(q, m):
    a = q + (q - 1)**2
    return Fraction((q - 1) * a**(m - 1), orbit_size(q, 1, m))


def pencil(q, k, m):
    if not 0 <= k <= q or m < 2:
        raise ValueError("pencil size or header dimension")
    if k == 0:
        return Fraction(1)
    if k == 1:
        return marginal(q, m)
    a = q + (q - 1)**2
    b = q*q + (q - 1)**2 * (q + 1 - k)
    d = m - 1
    return Fraction((q - 1) * (b**d - a**d), orbit_size(q, 2, m))


def independent_triple(q, m):
    if m < 3:
        raise ValueError("three independent covectors require m >= 3")
    a = q + (q - 1)**2
    c = q**3 + (q - 1)**4
    b2 = q*q + (q - 1)**3
    b3 = q*q + (q - 1)**2 * (q - 2)
    d = m - 1
    return Fraction((q - 1) * (c**d - 3*b2**d - (q - 2)*b3**d + q*a**d),
                    orbit_size(q, 3, m))


def pattern(q, k, j, m):
    """Exact probability of one named mask with j passes among k."""
    if not 0 <= j <= k:
        raise ValueError("invalid pass count")
    return sum((-1)**i * comb(k - j, i) * pencil(q, j + i, m)
               for i in range(k - j + 1))


def binary_independent(k, m):
    """PR6701, formula (1). Independent predecessor specialization."""
    d = m - 1
    def count(j):
        if j < k - 1:
            return 0
        return 2**j * prod(2**j - 2**i for i in range(k - 1))
    return Fraction(sum(comb(d, j)*count(j) for j in range(d + 1)),
                    (2**m - 1)*count(d))


def full_flat(q, r, m):
    d = m - 1
    amount = sum(comb(d, j)*(q - 1)**(2*(d - j))*q**j *
                 prod(q**j - q**i for i in range(r - 1)) for j in range(r - 1, d + 1))
    return Fraction((q - 1)*amount, orbit_size(q, r, m))


def universal_positive_size(q):
    """First k guaranteed by the last-axis bound, not necessarily minimal."""
    a, b = q*q - q + 1, q*q
    lo, hi = 1, 2
    while q*a**hi > b**hi:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi)//2
        if q*a**mid <= b**mid:
            hi = mid
        else:
            lo = mid
    return hi


def direction(q, k, m):
    delta = pencil(q, k, m) - marginal(q, m)**k
    return (delta > 0) - (delta < 0)


def ratio_floor(q, k, m, scale=10**8):
    value = pencil(q, k, m) / marginal(q, m)**k
    return value.numerator * scale // value.denominator
