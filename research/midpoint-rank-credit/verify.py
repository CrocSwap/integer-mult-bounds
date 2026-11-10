#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Stronger sufficient power-moment credits. Produced by Nick Petalas."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def interval(lower, upper):
    need(type(lower) is F and type(upper) is F, "rational endpoints")
    need(0 < lower <= upper < 1, "saving interval inside (0,1)")
    need(max(lower.denominator, upper.denominator) <= 10**6, "precision limit")


def curvature(k, lower, upper):
    interval(lower, upper)
    need(type(k) is int and 1 <= k <= 64, "rank limit")
    if k == 1:
        return 4 * lower / (3 + 2 * lower)
    return lower * (1 - upper) / (k * (1 + upper * (k - 1)))


def credit(old, new, lower, upper):
    interval(lower, upper)
    need(type(old) is tuple and type(new) is tuple, "tuple profiles")
    need(3 <= len(old) == len(new) <= 65, "profile dimension")
    need(all(type(x) is int and 0 <= x <= 10**6 for x in old + new),
         "bounded nonnegative counts")
    need(old[0] == new[0] == 0, "rank zero excluded")
    delta = tuple(n - o for o, n in zip(old, new))
    caps = tuple(sum(min(r, k) * d for r, d in enumerate(delta))
                 for k in range(len(old)))
    need(caps[-1] == 0, "equal rank mass required")
    need(all(c <= 0 for c in caps), "capped-mass order required")
    value = sum((-caps[k] * curvature(k, lower, upper)
                 for k in range(1, len(old) - 1)), F(0))
    return value, caps


def log_series(x):
    """24 positive atanh terms and a geometric tail, for 1<=x<=2."""
    need(F(1) <= x <= F(2), "log reduction")
    z = (x - 1) / (x + 1)
    total = sum((2 * z ** (2 * j + 1) / (2 * j + 1)
                 for j in range(24)), F(0))
    tail = 2 * z**49 / (49 * (1 - z * z))
    return total, total + tail


def exp_negative(x):
    """Enclose exp(-x) by a positive Taylor series for exp(x/8)."""
    need(F(0) <= x <= F(5), "exp range")
    y = x / 8
    term = total = F(1)
    for j in range(1, 25):
        term *= y / j
        total += term
    first_omitted = term * y / 25
    upper = total + first_omitted / (1 - y / 26)
    return 1 / upper**8, 1 / total**8


def power_bounds(rank, saving):
    need(type(rank) is int and 1 <= rank <= 65, "oracle rank limit")
    interval(saving, saving)
    b = rank.bit_length() - 1
    l2, u2 = log_series(F(2))
    lt, ut = log_series(F(rank, 2**b))
    low_log, high_log = b * l2 + lt, b * u2 + ut
    low, _ = exp_negative(saving * high_log)
    _, high = exp_negative(saving * low_log)
    return rank * low, rank * high


def lower_bill(profile, powers):
    return sum((count * powers[r][0] for r, count in enumerate(profile)
                if r), F(0))


def upper_bill(profile, powers):
    return sum((count * powers[r][1] for r, count in enumerate(profile)
                if r), F(0))


def check_curvatures(intervals):
    checked = roots = 0
    for lower, upper in intervals:
        for a in (lower, (lower + upper) / 2, upper):
            powers = {0: (F(0), F(0))}
            powers.update({r: power_bounds(r, a) for r in range(1, 34)})
            for k in range(1, 33):
                theta_low = 2 * powers[k][0] - powers[k-1][1] - powers[k+1][1]
                need(theta_low >= curvature(k, lower, upper), "curvature bound")
                if k >= 2:
                    old = lower * (1 - upper) / ((k + 1) * (1 + upper * k))
                    need(curvature(k, lower, upper) > old, "strict improvement")
                checked += 1
            if a in (F(1, 2), F(1, 3), F(2, 3)):
                p, q = a.numerator, a.denominator
                for r in range(1, 34):
                    lo, hi = powers[r]
                    need(lo**q <= r**(q-p) <= hi**q, "independent root check")
                    roots += 1
    return checked, roots


def check_profiles(intervals):
    profiles = tuple((0,) + x for x in product(range(3), repeat=4))
    comparisons = pairs = 0
    for lower, upper in intervals:
        oracles = tuple({r: power_bounds(r, a) for r in range(1, 5)}
                        for a in (lower, (lower + upper) / 2, upper))
        for old in profiles:
            for new in profiles:
                if old == new:
                    continue
                delta = tuple(n-o for o, n in zip(old, new))
                caps = tuple(sum(min(r, k)*d for r, d in enumerate(delta))
                             for k in range(5))
                if caps[-1] or any(c > 0 for c in caps):
                    continue
                value, _ = credit(old, new, lower, upper)
                for powers in oracles:
                    need(lower_bill(old, powers) - upper_bill(new, powers) >= value,
                         "complete profile credit")
                    comparisons += 1
                pairs += 1
    return pairs, comparisons


def check_exchange():
    lower, upper = F(17, 10000), F(18, 10000)
    value, caps = credit((0, 0, 2, 0), (0, 1, 0, 1), lower, upper)
    need(caps == (0, 0, -1, 0), "exchange capped profile")
    need(value == F(84847, 100180000), "exact new credit")
    count = value.denominator // value.numerator + 1
    need(count == 1181 and (count - 1)*value <= 1 < count*value,
         "least sufficient count for this bound")
    old_value = lower*(1-upper)/(3*(1+2*upper))
    old_count = old_value.denominator // old_value.numerator + 1
    need(old_count == 1775 and count*old_value < 1, "strict certificate gain")
    return {"credit": str(value), "exchanges": count,
            "rank_two_children_required": 2*count,
            "funded_rank_one_charge": 1,
            "uniform_raw_slack_lower": str(count*value-1),
            "preceding_bound_exchanges": old_count,
            "fewer_exchanges": old_count-count}


def check_controls():
    lo, hi = F(17, 10000), F(18, 10000)
    old, new = (0, 0, 2, 0), (0, 1, 0, 1)
    fixtures = (
        (new, old, lo, hi), (old, (0, 1, 0, 0), lo, hi),
        ((1, 0, 2, 0), new, lo, hi), ((0, -1, 2, 0), new, lo, hi),
        ((0, True, 2, 0), new, lo, hi), (old, new, F(0), hi),
        (old, new, hi, lo), (old, new, lo, F(1)),
        (list(old), new, lo, hi), (old, new, F(1, 1000001), hi),
        ((0,)*66, (0,)*66, lo, hi), ((0, 1000001, 0), (0, 1000001, 0), lo, hi),
    )
    for args in fixtures:
        rejected = False
        try:
            credit(*args)
        except ValueError:
            rejected = True
        need(rejected, "invalid credit accepted")
    powers = {r: power_bounds(r, F(1, 2)) for r in (1, 2, 3)}
    theta_high = 2*powers[2][1] - powers[1][0] - powers[3][0]
    need(theta_high < F(1, 4), "favorable-endpoint false bound not rejected")
    need(credit(old, old, lo, hi)[0] == 0, "zero gain control")
    need(power_bounds(1, lo) == (F(1), F(1)), "rank-one exactness")
    return len(fixtures) + 3


def main():
    intervals = ((F(17, 10000), F(18, 10000)),
                 (F(1, 8), F(1, 4)), (F(1, 3), F(2, 3)))
    curvature_cases, root_cases = check_curvatures(intervals)
    pairs, comparisons = check_profiles(intervals)
    result = {"status": "PASS_MIDPOINT_RANK_CREDIT",
              "claim_type": "scoped proof with exact finite corroboration",
              "curvature_cases": curvature_cases,
              "independent_root_cases": root_cases,
              "profile_interval_pairs": pairs,
              "profile_point_comparisons": comparisons,
              "controls": check_controls(), "exchange": check_exchange()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (package / name).open("rb") as handle:
            raw = handle.read(131073)
        need(len(raw) <= 131072, "package file limit")
        hashes[name] = sha256(raw).hexdigest()
    result["package_sha256"] = hashes
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
