"""Bound the two powered moments from all the actual labelled port ranks."""

from collections import Counter
from fractions import Fraction
from math import isqrt

from calibration import COMPLEX_C, COMPLEX_POWER

UNIT = 1 << 112


def ceiling(a, b):
    return -(-a // b)


def power_interval(rank, exponent):
    """Return outward integer bounds in units of 2^-112 for a dyadic power."""
    k, d = exponent.numerator, exponent.denominator
    if rank <= 0 or k < 0 or d & (d - 1):
        raise ValueError("Use positive ranks and nonnegative dyadic powers")
    whole, residue = divmod(k, d)
    low = high = rank**whole * UNIT
    lo_root = hi_root = rank * UNIT
    while d > 1:
        d //= 2
        lo_root = isqrt(lo_root * UNIT)
        hi_root = 1 + isqrt(hi_root * UNIT - 1)
        if residue & d:
            low = low * lo_root // UNIT
            high = ceiling(high * hi_root, UNIT)
    return low, high


def moment(hist, exponent, upper):
    return sum(count * power_interval(rank, exponent)[upper] for rank, count in hist.items())


def certify(word, c, tilt, drop, power, slack_bits, cutoff):
    if (word.power, word.floor, word.low_cut, word.high_cut) != (power, cutoff, 12, 12):
        raise ValueError("The evaluated strictifier differs from the installed one")
    targets = Counter(p.rank for p in word.targets)
    paid = Counter(p.rank for p in word.paid)
    t = 1 - c
    lower = moment(targets, t, False)
    alpha = Fraction(moment(paid, t, True), lower)
    gamma = Fraction(moment(paid, t + tilt, True) * UNIT, lower * power_interval(12, tilt)[0])
    loss = Fraction(moment(targets, t - drop, True) * power_interval(cutoff, drop)[1], lower * UNIT)
    deficit = 1 - alpha**power - 2 * gamma**power - loss**power
    if not (tilt >= c and deficit > Fraction(1, 1 << slack_bits)):
        raise ArithmeticError("The strict local surplus cannot pay all physical fringe axes")
    return {
        "raw_productive": sum(targets.values()),
        "raw_paid": sum(paid.values()),
        "productive": dict(sorted(targets.items())),
        "paid": dict(sorted(paid.items())),
        "surplus_lower_units_1e12": int(10**12 * deficit),
    }


def both(binary, positive, profile):
    return (
        certify(
            binary,
            profile.bit_c,
            Fraction(19, 64),
            Fraction(31 if profile.power == 228 else 26, 64),
            profile.power,
            profile.floor.bit_length() - 2,
            15 if profile.power == 228 else 16,
        ),
        certify(positive, COMPLEX_C, Fraction(19, 64), Fraction(23, 64), COMPLEX_POWER, 14, 16),
    )
