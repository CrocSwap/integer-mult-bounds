"""Exact global sign test for the complete 36-call signed BIT invoice."""
from collections import Counter
from fractions import Fraction
from functools import cache
from math import ceil, floor, isqrt

from word import require


# Outward fixed-point enclosures. Exponents are first bracketed on a dyadic grid.
SCALE = 1 << 128
EXPONENT_BITS = 80


@cache
def roots(rank):
    low = high = rank * SCALE
    values = []
    for _ in range(EXPONENT_BITS):
        low = isqrt(low * SCALE)
        radicand = high * SCALE
        high = isqrt(radicand)
        if high * high < radicand:
            high += 1
        values.append((low, high))
    return values


def dyadic_power(rank, numerator):
    if numerator == 1 << EXPONENT_BITS:
        return rank * SCALE, rank * SCALE
    low = high = SCALE
    for j, (a, b) in enumerate(roots(rank), 1):
        if numerator & (1 << (EXPONENT_BITS - j)):
            low = low * a // SCALE
            high = (high * b + SCALE - 1) // SCALE
    return low, high


def margin(profile, exponent):
    require(0 <= exponent <= 1, "unit power domain")
    point = exponent * (1 << EXPONENT_BITS)
    left, right = floor(point), ceil(point)
    lower = upper = 0
    for rank, count in profile.items():
        lo = dyadic_power(rank, left)[0]
        hi = dyadic_power(rank, right)[1]
        lower += count * (lo if count >= 0 else hi)
        upper += count * (hi if count >= 0 else lo)
    return Fraction(lower, SCALE), Fraction(upper, SCALE)


def increasing_after_normalization(profile):
    """Verify the coefficient signs in the proof of monotonicity of M(t)/8^t."""
    remaining = Counter(profile)
    require(remaining[1] < 0 and all(remaining.pop(r, 0) <= 0 for r in range(1, 8)),
            "strictly increasing low-rank terms")
    for r in range(14, 57, 7):
        weight = remaining.pop(r + 1)
        require(weight > 0 and remaining.pop(r) == -weight, "paired high-rank terms")
    require(all(r >= 8 and n >= 0 for r, n in remaining.items()), "unpaired high-rank terms")


def whole_caller(caller, orientations):
    original = Counter(caller["targets"])
    original.subtract(caller["paid"])
    possible = Counter()
    for side in orientations:
        possible |= Counter(side["paid_omittable_with_all_helpers_zero"])
    favorable = Counter(original)
    for rank, count in possible.items():
        favorable[rank] += caller["native_invocations"] * count
    increasing_after_normalization(original)
    increasing_after_normalization(favorable)
    cutoff = margin(favorable, Fraction(3, 4))
    require(-23329 < cutoff[0] <= cutoff[1] < -23328, "optimistic high-saving sign")

    lower_eta, upper_eta = "0.0038525393934", "0.0038525393935"
    require(margin(original, 1 - Fraction(lower_eta))[0] > 0 and
            margin(original, 1 - Fraction(upper_eta))[1] < 0, "original raw crossing")
    goal = margin(original, Fraction(99, 100))
    require(Fraction("-2355.302") < goal[0] <= goal[1] < Fraction("-2355.301"),
            "strict deficit at the one-percent target")
    return {"optimal_raw_BIT_price_saving_open_interval": [lower_eta, upper_eta],
            "maximum_signed_margin_at_eta_0.01_open_interval": ["-2355.302", "-2355.301"],
            "optimistic_margin_at_t_3_over_4_open_interval": [-23329, -23328],
            "optimistic_omissions_per_call_by_rank": dict(sorted(possible.items()))}
