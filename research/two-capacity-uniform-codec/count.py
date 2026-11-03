"""Conditional count oracle from Ali Romman's PR6539, Theorem 1.

This is a direct implementation of the cited formula, not a new count theorem.
Apache-2.0.
"""

from math import prod

from linear import basis, intersection, mapped, require


def injections(n, k, prime):
    if not 0 <= k <= n:
        return 0
    return prod(prime**n - prime**i for i in range(k))


def gaussian(n, k, prime):
    if not 0 <= k <= n:
        return 0
    numerator = prod(prime**(n - i) - 1 for i in range(k))
    denominator = prod(prime**(k - i) - 1 for i in range(k))
    require(numerator % denominator == 0, "Nonintegral Gaussian coefficient")
    return numerator // denominator


def formula(prime, n, u, a, b, s, c, d, t, k, ell, ec, ed, ecd):
    if a > c or b > d or s > t or k > ell:
        return 0
    j, tau = a + b - s, c + d - t
    alpha, beta, common_dimension = a - j, b - j, tau - j
    require(0 <= k <= j and 0 <= j - k <= tau - ell,
            "Invalid common-quotient dimensions")
    summands = []
    for i in range(max(0, alpha - c + tau), min(alpha, common_dimension) + 1):
        summands.append(gaussian(common_dimension, i, prime)
                        * gaussian(c - tau, alpha - i, prime)
                        * prime**((common_dimension - i) * (alpha - i))
                        * injections(alpha, alpha, prime)
                        * injections(d - j - i, beta, prime) * prime**(i * beta))
    return (injections(ell, k, prime) * prime**(ell * (j - k))
            * prime**(j * (alpha + beta)) * sum(summands)
            * prime**(ecd * j + ec * alpha + ed * beta)
            * prod(prime**n - prime**i for i in range(u + s, n)))


def count(n, prime, fixed, capacities):
    """Inputs are validated by Contract; every added fixed pair is independent."""
    domain = basis(tuple(x for x, _ in fixed), n, prime)
    image = basis(tuple(y for _, y in fixed), n, prime)
    require(len(domain) == len(image) == len(fixed), "Noninjective prefix")
    (a_space, c_space), (b_space, d_space) = capacities
    source_sum = basis(a_space + b_space, n, prime)
    target_sum = basis(c_space + d_space, n, prime)
    ua = intersection(domain, a_space, n, prime)
    ub = intersection(domain, b_space, n, prime)
    u0 = intersection(domain, source_sum, n, prime)
    for source, target in ((ua, c_space), (ub, d_space), (u0, target_sum)):
        if len(basis(mapped(source, fixed, n, prime) + target, n, prime)) != len(target):
            return 0
    ec = intersection(image, c_space, n, prime)
    ed = intersection(image, d_space, n, prime)
    ecd = intersection(ec, ed, n, prime)
    z_space = basis(ec + ed, n, prime)
    k = (len(intersection(a_space, b_space, n, prime))
         + len(intersection(mapped(u0, fixed, n, prime), z_space, n, prime))
         - len(ua) - len(ub))
    return formula(prime, n, len(domain), len(a_space) - len(ua),
                   len(b_space) - len(ub), len(source_sum) - len(u0),
                   len(c_space) - len(ec), len(d_space) - len(ed),
                   len(target_sum) - len(intersection(image, target_sum, n, prime)),
                   k, len(intersection(c_space, d_space, n, prime)) - len(ecd),
                   len(ec), len(ed), len(ecd))
