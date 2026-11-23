"""Directed upper price for the installed interior Gaussian suffixes.

This is a price proof only.  It does not change the installed calendar,
word, ownership, rounding, terminal loss, exterior service, or tape clock.
"""

from fractions import Fraction as Q
from math import gcd


def upper_numerator(recipe, lower, intervals):
    """Bound the integral of every occupied paid-to-target edge.

    All edges are summed using their actual weighted paid counts and actual
    installed shares.  The final upward quantization is one-sided.
    """
    c = recipe.trial
    t = 1 - c
    assert 0 < t < 1 and lower > 8 and lower % 2 == 0
    assert len(recipe.cells) == 51
    grid = 1 << 96
    total = 0
    average_better = 0
    for (raw_r, raw_k), share in recipe.cells.items():
        r, k = Q(raw_r), Q(raw_k)
        assert share > 0 and 5 * r <= 4 * k
        assert (2 * r).denominator == (2 * k).denominator == 1
        assert recipe.paid.histogram[raw_r] > 0
        assert recipe.targets.histogram[raw_k] > 0
        # Since e,d are even, every routed suffix is at most this value.
        pointwise = 10 * k - 8 * r - gcd(int(2 * r), int(2 * k))
        # Integrate the two sawtooth terms against y^(-1-t), y>=lower.
        averaged = 9 * (k - r) + t * r * r / (2 * k * lower)
        assert pointwise > 0 and averaged > 0
        average_better += averaged < pointwise
        bound = min(pointwise, averaged)
        # The fraction of the y density induced from x is (r/k)^t.
        ratio_upper = Q(intervals(raw_r, t)[1], intervals(raw_k, t)[0])
        assert 0 < ratio_upper < 1
        term = recipe.paid.histogram[raw_r] * share * ratio_upper * bound
        total += -(-(term * grid).numerator // (term * grid).denominator)
    assert average_better == len(recipe.cells)
    return Q(total, grid)
