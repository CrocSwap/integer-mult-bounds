"""Separately written exact-rational evaluator of the source Newton equations.

This module imports no primary evaluator, schedules, or normalization helpers.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F


def round_down(z, precision):
    scaled = z * 2 ** precision
    return F(scaled.numerator // scaled.denominator, 2 ** precision)


def inverse(c, target):
    if not isinstance(c, F) or not 1 <= c < 2 or target < 1:
        raise ValueError("invalid rational reciprocal input")
    x = F(5, 8)
    records = []
    # Direct capped powers of two, independent of the primary schedule helper.
    goals = [1] + [min(2 ** k, target) for k in range(1, (target - 1).bit_length() + 1)]
    for index, m in enumerate(goals):
        t = 6 if index == 0 else m + 5
        c_prefix = round_down(c, t)
        product = round_down(c_prefix * x, t)
        x = round_down(x * (2 - product), t)
        records.append((m, t, int(c_prefix * 2 ** t),
                        int(product * 2 ** t), int(x * 2 ** t)))
    return x, tuple(records)


def root(c, target):
    if not isinstance(c, F) or not 1 <= c < 4 or target < 1:
        raise ValueError("invalid rational root input")
    x = F(3, 2)
    records = []
    goals = [1] + [min(2 ** k, target) for k in range(1, (target - 1).bit_length() + 1)]
    for index, m in enumerate(goals):
        t = 6 if index == 0 else m + 5
        d, j = x, 0
        while d >= 2:
            d /= 2
            j += 1
        while d < 1:
            d *= 2
            j -= 1
        z, inner = inverse(d, t)
        v = z / (F(2) ** j)
        c_prefix = round_down(c, t)
        quotient = round_down(c_prefix * v, t)
        x = round_down((x + quotient) / 2, t)
        zb = inner[-1][1]
        records.append((m, t, int(c_prefix * 2 ** t), j,
                        int(z * 2 ** zb), zb, int(quotient * 2 ** t),
                        int(x * 2 ** t), inner))
    return x, tuple(records)
