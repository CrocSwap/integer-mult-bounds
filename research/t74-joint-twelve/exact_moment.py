# SPDX-License-Identifier: Apache-2.0
# Tekalign with substantial OpenAI Codex assistance.
from fractions import Fraction as F
DIMENSION=73
def require(condition, message):
    if not condition:
        raise ValueError(message)


def log_reduced(x):
    """Forty atanh terms with their positive geometric tail."""
    require(1 <= x <= 2, 'log reduction range')
    t = (x - 1) / (x + 1)
    lower = sum((2 * t ** (2 * j + 1) / (2 * j + 1)
                 for j in range(40)), F(0))
    tail = 2 * t ** 81 / (81 * (1 - t * t))
    return lower, lower + tail


def log_bounds(x):
    require(x >= 1, 'positive logarithm range')
    power = 0
    while x >= 2:
        x /= 2
        power += 1
    a, b = log_reduced(x)
    c, d = log_reduced(F(2))
    return a + power * c, b + power * d


def exp_bounds(x):
    """Taylor terms 0..15; later term ratios are bounded by x/17."""
    require(0 <= x < F(1, 100), 'exponential argument range')
    term, lower = F(1), F(1)
    for n in range(1, 16):
        term = term * x / n
        lower += term
    tail = term * x / 16 / (1 - x / 17)
    return lower, lower + tail


def moment_bounds(profile, exponent):
    lower = upper = F(0)
    for rank, count in sorted(profile.items()):
        log_lo, log_hi = log_bounds(F(DIMENSION, rank))
        exp_lo, _ = exp_bounds(exponent * log_lo)
        _, exp_hi = exp_bounds(exponent * log_hi)
        weight = F(count * rank, DIMENSION)
        lower += weight * exp_lo
        upper += weight * exp_hi
    return lower, upper
