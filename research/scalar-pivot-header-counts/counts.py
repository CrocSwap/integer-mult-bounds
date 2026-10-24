"""Exact sharp-header counts without enumerating compressed matrices.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The field order q is a supplied prime power.
"""
from fractions import Fraction
from math import prod
from itertools import product


def need(ok, message):
    if not ok:
        raise ValueError(message)


def injection(q, n, k):
    if k < 0 or n < k:
        return 0
    return prod(q**n - q**i for i in range(k))


def gl(q, n):
    return injection(q, n, n)


def gaussian(q, n, k):
    if k < 0 or k > n:
        return 0
    value, rem = divmod(injection(q, n, k), gl(q, k))
    need(rem == 0, 'integer Gaussian coefficient')
    return value


def joint_nullities(q, d, shifts=2):
    need(type(q) is int and q >= shifts and type(d) is int and d >= 0 and
         shifts in (2, 3), 'field order, dimension and distinct shifts')
    g = [[gaussian(q, n, k) for k in range(n + 1)] for n in range(d + 1)]
    count = {}
    # This is the retained incidence inversion from Discussion 5261.
    for a in product(range(d, -1, -1), repeat=shifts):
        if sum(a) > d:
            continue
        used = 0
        incidence = q**(d*(d-sum(a)))
        for size in a:
            incidence *= g[d-used][size] * q**(used*size)
            used += size
        larger = sum(prod(g[e[i]][a[i]] for i in range(shifts)) * value
                     for e, value in count.items()
                     if all(e[i] >= a[i] for i in range(shifts)))
        count[a] = incidence - larger
        need(count[a] >= 0, 'nonnegative exact stratum')
    need(sum(count.values()) == q**(d*d), 'all matrices counted')
    return count


def unrestricted(q, r, d, rho):
    return sum(gaussian(q, d-rho, k-rho) * injection(q, r, k) * q**(d*(r-k))
               for k in range(rho, min(d, r) + 1))


def full_rank(q, r, d, rho):
    if r < d:
        return 0
    return injection(q, r, d) * q**(rho*(r-d)) * injection(q, r-d, d-rho)


def fixed_product(q, d, profile, ranks):
    arbitrary = [unrestricted(q, r, d, rho) for r, rho in zip(profile, ranks)]
    full = [full_rank(q, r, d, rho) for r, rho in zip(profile[1:], ranks[1:])]
    return prod(arbitrary), arbitrary[0] * prod(full)


def headers(q, d, profile, pivot_class='identity'):
    need(type(d) is int and d >= 1 and len(profile) == 4 and
         all(type(r) is int and r >= 0 for r in profile), 'header dimensions')
    n = sum(profile)
    need(n >= d, 'pivot fits ambient space')
    # The caller supplies the equality class of (0, lambda, 2lambda-1).
    need(pivot_class in ('identity', 'half', 'generic'), 'pivot class')
    need(pivot_class != 'half' or q % 2 == 1, 'half needs odd characteristic')
    need(pivot_class != 'generic' or q >= 4, 'generic class must exist')
    shifts = 3 if pivot_class == 'generic' else 2
    zero_sector = {'identity': 1, 'half': 0, 'generic': 2}[pivot_class]
    sharp = common = 0
    for nullities, multiplicity in joint_nullities(q, d, shifts).items():
        ranks = (d-nullities[zero_sector], d-nullities[1],
                 d-nullities[1], d-nullities[0])
        all_splits, good_splits = fixed_product(q, d, profile, ranks)
        common += multiplicity * all_splits
        sharp += multiplicity * good_splits
    completion = gl(q, n-d)
    total = gl(q, n)
    return dict(sharp=sharp*completion, common=common*completion, total=total,
                sharp_probability=Fraction(sharp*completion, total),
                conditional_probability=Fraction(sharp, common) if common else None)
