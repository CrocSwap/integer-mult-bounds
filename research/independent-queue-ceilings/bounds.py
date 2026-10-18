# SPDX-License-Identifier: Apache-2.0
"""Directed integer-root enclosures; no logarithms, exponentials or floats.

Written for this audit by Hanson Sun with OpenAI Codex assistance. The method
has precedents in PR706/PR1577; no code from either implementation is imported.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import isqrt


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    return -(-n // d)


def sqrt_up(n):
    r = isqrt(n)
    return r + (r * r != n)


@lru_cache(maxsize=None)
def root_ladder(n, d, exponent_bits, precision):
    """Enclose (n/d)^(1/2^j), j=1..exponent_bits, scaled by 2^precision."""
    require(type(n) is int and type(d) is int and n >= d > 0,
            'root base must be a rational >= 1')
    require(type(exponent_bits) is int and type(precision) is int
            and 1 <= exponent_bits <= 1024 and 1 <= precision <= 2048,
            'unsupported root precision')
    scale = 1 << precision
    lo, hi = n * scale // d, ceil_div(n * scale, d)
    ladder = []
    for _ in range(exponent_bits):
        lo, hi = isqrt(lo * scale), sqrt_up(hi * scale)
        ladder.append((lo, hi))
    return tuple(ladder)


def rational_power(n, d, a, exponent_bits=96, precision=192):
    """Return rational lo <= (n/d)^a <= hi for n/d >= 1 and 0 <= a <= 1.

    The exponent is bracketed by adjacent dyadics. Each selected binary digit
    multiplies an independently outward-rounded member of the root ladder.
    All intermediate products are rounded outwards before the next product.
    """
    require(type(a) in (int, Q) and Q(0) <= a <= Q(1), 'exponent outside [0,1]')
    a = Q(a)
    roots = root_ladder(n, d, exponent_bits, precision)
    scale, denominator = 1 << precision, 1 << exponent_bits
    low_k = a.numerator * denominator // a.denominator
    high_k = ceil_div(a.numerator * denominator, a.denominator)

    def dyadic(k, upper):
        if k == denominator:
            return ceil_div(n * scale, d) if upper else n * scale // d
        value = scale
        for j, pair in enumerate(roots, 1):
            if k & (1 << (exponent_bits - j)):
                product = value * pair[upper]
                value = ceil_div(product, scale) if upper else product // scale
        return value

    return Q(dyadic(low_k, False), scale), Q(dyadic(high_k, True), scale)


def child_cost(rank, width, a, exponent_bits=96, precision=192):
    require(type(rank) is int and type(width) is int and 0 < rank < width,
            'child rank must lie strictly between zero and width')
    lo, hi = rational_power(width, rank, a, exponent_bits, precision)
    return Q(rank, width) * lo, Q(rank, width) * hi


def relaxation(local, a, *, width=73, families=896, stages=9, centre=64,
               cap=51, exponent_bits=96, precision=192):
    """Fully charged local profile plus optimistically concentrated idle mass.

    This is only the PR1240 coverage-law relaxation. Physical supplier costs
    and other interfaces are not inferred from this numerical calculation.
    """
    require(type(width) is int and type(cap) is int and 0 < cap < width
            and 2 * cap * cap < width * width, 'invalid halving-guard cap')
    require(type(families) is int and families > 0
            and type(stages) is int and stages > 0, 'invalid family normalization')
    require(type(centre) in (int, Q) and centre >= 0, 'invalid centre charge')
    require(type(local) is dict and bool(local), 'empty local profile')
    for rank, count in local.items():
        require(type(rank) is int and 0 < rank < width
                and type(count) in (int, Q) and count >= 0, 'invalid local child')
    w = Q(families, stages)
    local_mass = sum(rank * count for rank, count in local.items())
    idle_mass = (width - 1) * w + centre - local_mass
    require(idle_mass >= 0, 'local mass exceeds coverage budget')
    lo = hi = Q(0)
    for rank, count in sorted(local.items()):
        lower, upper = child_cost(rank, width, a, exponent_bits, precision)
        lo += count * lower
        hi += count * upper
    lower, upper = child_cost(cap, width, a, exponent_bits, precision)
    lo += idle_mass / cap * lower
    hi += idle_mass / cap * upper
    return lo / w, hi / w


def side(interval):
    lo, hi = interval
    require(lo <= hi, 'reversed interval')
    if hi < 1:
        return 'below'
    if lo > 1:
        return 'above'
    raise ValueError('interval does not separate one')
