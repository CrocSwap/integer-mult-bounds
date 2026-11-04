"""Certify the integer dimension intervals using the concavity in SIGN.md."""
from functools import lru_cache

from laws import marginal, pencil


def sign_window(q, k):
    if not 2 <= k <= q:
        raise ValueError("a pencil requires 2 <= k <= q")
    if k == 2 or q == 3:
        return dict(positive=[2, None], ties=[])

    @lru_cache(None)
    def ratio(m):
        return pencil(q, k, m)/marginal(q, m)**k

    def first_true(lo, hi, predicate):
        while lo < hi:
            mid = (lo + hi)//2
            if predicate(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo

    # Adjacent ratios decrease strictly and tend to T < 1.
    def descending(m):
        return ratio(m + 1) <= ratio(m)

    hi = 2
    while not descending(hi):
        hi *= 2
    peak = first_true(2, hi, descending)
    if ratio(peak) <= 1:
        ties = [m for m in (peak, peak + 1) if ratio(m) == 1]
        return dict(positive=[], ties=ties)
    left = first_true(2, peak, lambda m: ratio(m) > 1)
    hi = peak + 1
    while ratio(hi) > 1:
        hi *= 2
    after = first_true(peak + 1, hi, lambda m: ratio(m) <= 1)
    ties = [m for m in (left - 1, after) if m >= 2 and ratio(m) == 1]
    return dict(positive=[left, after - 1], ties=ties)
