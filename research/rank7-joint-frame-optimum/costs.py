# SPDX-License-Identifier: Apache-2.0
"""Exact tariff comparisons uniform on 0 < b <= 1/100."""

from fractions import Fraction
from functools import lru_cache

from spaces import require

MAX_B = Fraction(1, 100)


@lru_cache(maxsize=9)
def log_interval(integer):
    """atanh series with its positive geometric tail, 96 terms."""
    require(type(integer) is int and 1 <= integer <= 9, "logarithm argument")
    z = Fraction(integer - 1, integer + 1)
    lower = 2 * sum((z ** (2 * k + 1) / (2 * k + 1) for k in range(96)),
                    Fraction(0))
    tail = 2 * z ** 193 / (193 * (1 - z * z))
    return lower, lower + tail


def signed_sum(delta, power, negate=False):
    lower = Fraction(0)
    for r in range(1, 10):
        coefficient = (-1 if negate else 1) * r * delta[r]
        lo, hi = log_interval(r)
        lower += coefficient * (lo ** power if coefficient >= 0 else hi ** power)
    return lower


@lru_cache(maxsize=1024)
def certificate(delta):
    """Prove sum delta[r]*H_r(b) strictly positive, or return None."""
    require(len(delta) == 10 and all(type(n) is int and abs(n) <= 15000 for n in delta),
            "bounded integral tariff difference")
    require(sum(r * delta[r] for r in range(10)) == 0, "equal telescoping rank mass")
    if not any(delta[1:]):
        return ("equal", 0)
    concavity = tuple(-sum((r - k) * delta[r] for r in range(k + 1, 10))
                      for k in range(1, 9))
    if min(concavity) >= 0 and max(concavity) > 0:
        return ("concavity", concavity)
    first = signed_sum(delta, 1, negate=True)
    second = signed_sum(delta, 2)
    third = sum((r * delta[r] * log_interval(r)[1] ** 3
                 for r in range(1, 10) if delta[r] > 0), Fraction(0))
    lower = first - MAX_B * max(0, -second) / 2 - MAX_B ** 2 * third / 6
    if lower > 0:
        return ("taylor", lower)
    return None


def compare(a, b):
    """Return -1, 0, +1 only after a uniform exact proof of the comparison."""
    delta = tuple(x - y for x, y in zip(a, b, strict=True))
    proof = certificate(delta)
    if proof is not None:
        return 0 if proof[0] == "equal" else 1
    require(certificate(tuple(-x for x in delta)) is not None,
            "unresolved tariff comparison, no numerical fallback")
    return -1
