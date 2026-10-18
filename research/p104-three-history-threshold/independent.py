# SPDX-License-Identifier: Apache-2.0
"""Positive-binomial moment enclosures, with no logarithms or ceiling imports."""

from fractions import Fraction as Q
from functools import lru_cache

SCALE = 1 << 128


def require(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(maxsize=16)
def child(rank, saving):
    """Bound (rank/73)^(1-saving) by (1-z)^(-saving)'s positive series."""
    require(type(rank) is int and 1 <= rank <= 73, 'independent rank')
    require(isinstance(saving, Q) and 0 <= saving <= Q(1, 100), 'independent saving')
    require(max(saving.numerator.bit_length(), saving.denominator.bit_length()) <= 128,
            'independent rational bit bound')
    x, z = Q(rank, 73), Q(73 - rank, 73)
    if not saving or not z:
        return x, x
    low = high = total_low = total_high = SCALE
    for k in range(4096):
        ratio = z * (saving + k) / (k + 1)
        low = low * ratio.numerator // ratio.denominator
        high = -((-high * ratio.numerator) // ratio.denominator)
        # This is the first omitted term. All later ratios are at most z.
        tail = Q(high, SCALE) / (1 - z)
        if tail < Q(1, 1 << 64):
            return x * Q(total_low, SCALE), x * (Q(total_high, SCALE) + tail)
        total_low += low
        total_high += high
    raise ValueError('independent series exhausted its 4096-term bound')


def moment(cheap, units, merged, saving):
    """Rebuild this alphabet's invoice directly, independently of the primary code."""
    counts = (cheap, units, merged)
    require(all(type(n) is int and n >= 0 for n in counts) and sum(counts) <= 482,
            'independent helper counts')
    entries = [(1, 1074), (2, 58), (3, 86), (4, 104), (5, 48),
               (6, 24), (7, 8), (8, 8), (1, 2 * cheap), (7, cheap),
               (1, 9 * units + 7 * merged), (2, merged),
               (51, Q(4344 - 9 * sum(counts), 51))]
    low = high = Q(0)
    for rank, count in entries:
        a, b = child(rank, saving)
        low += count * a
        high += count * b
    return low * Q(9, 832), high * Q(9, 832)
