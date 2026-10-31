#!/usr/bin/env python3
"""Sharp squared tensor-phase envelope over exact rational budgets.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No floating-point or trigonometric decisions are used.
"""
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def budget(value):
    require(type(value) in (int, Fraction), "budget must be an exact rational")
    result = Fraction(value)
    require(0 <= result <= 4, "squared budget must be in [0,4]")
    return result


def high_branch(square_budget, cube_budget):
    """Decide 3 asin(sqrt(s)/2)+2 asin(sqrt(t)/2) >= pi exactly."""
    s, t = budget(square_budget), budget(cube_budget)
    if s >= 3:
        return True
    h = (1 - s) ** 2 * (4 - s)
    if s <= 1:
        return t >= 2 and h <= (t - 2) ** 2
    return t >= 2 or h >= (t - 2) ** 2


def increasing_root(poly, value, lower, upper, bits):
    require(type(bits) is int and 8 <= bits <= 256, "bits must be 8..256")
    lo, hi = Fraction(lower), Fraction(upper)
    require(poly(lo) <= value <= poly(hi), "root is not bracketed")
    if poly(lo) == value:
        return lo, lo
    if poly(hi) == value:
        return hi, hi
    for _ in range(bits + 2):
        mid = (lo + hi) / 2
        image = poly(mid)
        if image == value:
            return mid, mid
        if image < value:
            lo = mid
        else:
            hi = mid
    return lo, hi


def squared_envelope(square_budget, cube_budget, bits=80):
    """Return branch and a rational enclosure of the optimal ||A-B||^2."""
    s, t = budget(square_budget), budget(cube_budget)
    require(type(bits) is int and 8 <= bits <= 256, "bits must be 8..256")
    if high_branch(s, t):
        lo, hi = increasing_root(lambda x: x * (x - 3) ** 2, t, 3, 4, bits)
        return "high", lo, hi
    qlo, qhi = increasing_root(lambda x: x * (4 - x), s, 0, 2, bits)
    clo, chi = increasing_root(lambda x: x * (3 - x) ** 2, t, 0, 1, bits)
    return "low", min(qlo, clo), min(qhi, chi)


def angular_envelope(a, b):
    """Return optimal theta/pi for exact rational a/pi,b/pi in [0,1/2]."""
    require(type(a) in (int, Fraction) and type(b) in (int, Fraction),
            "angular budgets must be exact rationals")
    a, b = Fraction(a), Fraction(b)
    require(0 <= a <= Fraction(1, 2) and 0 <= b <= Fraction(1, 2),
            "angular budgets must be in [0,1/2]")
    if 3 * a + 2 * b >= 1:
        return "high", Fraction(2, 3) + 2 * b / 3
    return "low", min(a, 2 * b / 3)
