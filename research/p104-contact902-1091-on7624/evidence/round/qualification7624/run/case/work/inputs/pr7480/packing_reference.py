# SPDX-License-Identifier: Apache-2.0
"""Retain the fixed-profile packing check from exact #7161."""

from collections import Counter
from fractions import Fraction as Q


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packing(invoice, native, g, claim):
    """Fixed T, 17 fixed native words, and fixed ambient-145 remainder mass."""
    cap = 145
    paid = Counter(invoice["P"])
    local = Counter({r: 17*count for r, count in native["paid"].items()})
    paid.subtract(local)
    require(all(n >= 0 and r <= cap for r, n in paid.items()), "Exact nonnegative paid remainder")
    mass = sum(r*n for r, n in paid.items())
    relaxed = Counter(invoice["T"])
    relaxed.subtract(local)
    relaxed[cap] -= Q(mass, cap)

    # r^(1-x) log(r) is positive. Bound each signed derivative term
    # across the entire recipe range using its monotone power factor.
    end = Q(1, 32)
    derivative = (0, 0)
    for r, count in relaxed.items():
        term = g.mul(g.power(r, end if count >= 0 else 0), g.log(r))
        derivative = g.add(derivative, g.smul(term, -count))
    require(derivative[1] < 0 and g.moment(relaxed, 0)[0] > 0 > g.moment(relaxed, end)[1],
            "Directed relaxed crossing and uniform decrease")
    lo, hi = Q(0), end
    for _ in range(36):
        mid = (lo+hi)/2
        a, b = g.moment(relaxed, mid)
        if a > 0:
            lo = mid
        elif b < 0:
            hi = mid
        else:
            raise ValueError("Ambiguous packing ceiling bisection")
    require(0 < claim < lo < hi, "Candidate within fixed-profile packing ceiling")
    return dict(ambient_cap=cap, remainder_rank_mass=mass, raw_ceiling=[str(lo), str(hi)],
                claimed_fraction=[str(claim/hi), str(claim/lo)])
