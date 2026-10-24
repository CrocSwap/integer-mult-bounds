#!/usr/bin/env python3
"""Exact finite corroboration of rational-threshold rank exchanges."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    need(1 <= len(left) <= 15 and 1 <= len(right) <= 15, "polynomial capacity")
    need(len(left) + len(right) <= 16, "product degree capacity")
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def stencil(q, s):
    need(type(q) is int and type(s) is int, "integer threshold parameters")
    need(2 <= q <= 12 and 1 <= s < q, "finite checker threshold domain")
    last = [-2**s] + [0] * (q - 1) + [1]
    return multiply(multiply((-1, 1), (-2, 1)), last)


def profiles(coefficients):
    need(1 <= len(coefficients) <= 15, "profile degree capacity")
    need(all(type(c) is int for c in coefficients), "integer profile counts")
    added = {2**j: c for j, c in enumerate(coefficients) if c > 0}
    removed = {2**j: -c for j, c in enumerate(coefficients) if c < 0}
    return removed, added


def evaluate(coefficients, x):
    result = Q(0)
    for c in reversed(coefficients):
        result = result * x + c
    return result


def root_interval(p):
    """Enclose x=2**p using only integer powers, at 80 binary places."""
    need(isinstance(p, Q) and 0 < p < 1, "interior rational power")
    need(p.denominator <= 12, "finite root denominator")
    scale = 2**80
    lo, hi = scale, 2 * scale
    target = 2**p.numerator * scale**p.denominator
    for _ in range(81):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        if mid**p.denominator <= target:
            lo = mid
        else:
            hi = mid
    need(hi - lo == 1, "root bisection exhaustion")
    need(lo**p.denominator <= target < hi**p.denominator, "root bracket")
    return Q(lo, scale), Q(hi, scale)


def direct_difference_interval(removed, added, bounds):
    lo, hi = bounds
    lower, upper = Q(0), Q(0)
    for rank, count in added.items():
        j = rank.bit_length() - 1
        lower += count * lo**j
        upper += count * hi**j
    for rank, count in removed.items():
        j = rank.bit_length() - 1
        lower -= count * hi**j
        upper -= count * lo**j
    return lower, upper


def threshold_remainder(coefficients, q, s):
    """Reduce the literal profile modulo x**q-2**s at the claimed crossing."""
    remainder = list(coefficients)
    for j in range(len(remainder) - 1, q - 1, -1):
        remainder[j - q] += remainder[j] * 2**s
        remainder[j] = 0
    return tuple(remainder[:q])


def check_sign(removed, added, p, q, s, bounds):
    lo, hi = direct_difference_interval(removed, added, bounds)
    need(hi < 0 if q * p > s else lo > 0, "direct raw moment sign")


def family_checks():
    powers = sorted({Q(m, n) for n in range(2, 11) for m in range(1, n)})
    brackets = {p: root_interval(p) for p in powers}
    counters = dict(families=0, polynomial_points=0, power_comparisons=0, crossings=0)
    for q in range(2, 13):
        for s in range(1, q):
            coefficients = stencil(q, s)
            old, new = profiles(coefficients)
            need(sum(old.values()) == sum(new.values()), "child count conservation")
            need(sum(r*c for r, c in old.items()) ==
                 sum(r*c for r, c in new.items()), "rank mass conservation")
            need(not any(threshold_remainder(coefficients, q, s)), "exact crossing")
            for x in (Q(5, 4), Q(3, 2), Q(7, 4), Q(1997, 1000)):
                actual = evaluate(coefficients, x)
                expected = (x - 1) * (x - 2) * (x**q - 2**s)
                need(actual == expected, "literal profile factorization")
                counters["polynomial_points"] += 1
            for p in powers:
                if q * p == s:
                    counters["crossings"] += 1
                    continue
                check_sign(old, new, p, q, s, brackets[p])
                counters["power_comparisons"] += 1
            counters["families"] += 1
    return counters


def overhead_checks():
    old, new = profiles(stencil(2, 1))
    need(old == {1: 4, 8: 3} and new == {2: 6, 16: 1}, "first exchange")
    lower, upper = Q(399, 200), Q(499, 250)
    need(399**10000 < 2**9969 * 200**10000, "lower endpoint power")
    need(2**997 * 250**1000 < 499**1000, "upper endpoint power")
    credit = (lower - 1) * (2 - upper) * (lower**2 - 2)
    need(credit == Q(15760999, 2000000000), "uniform credit")
    need(126 * credit < 1 < 127 * credit, "sufficient paid-copy cut")
    old_paid, new_paid = {1: 508, 8: 381}, {1: 1, 2: 762, 16: 127}
    need(sum(old_paid.values()) == 889 and sum(new_paid.values()) == 890,
         "fully charged count")
    need(sum(r*c for r, c in old_paid.items()) == 3556, "old paid mass")
    need(sum(r*c for r, c in new_paid.items()) == 3557, "new paid mass")
    need(127 * credit - 1 == Q(1646873, 2000000000), "strict paid margin")
    for x in (lower, (lower + upper) / 2, upper):
        raw = 1 + 762*x + 127*x**4 - 508 - 381*x**3
        need(raw < 0, "complete paid profile at rational bracket points")
    return dict(credit=str(credit), copies=127, strict_margin=str(127*credit - 1),
                old_paid=old_paid, new_paid=new_paid, rational_paid_points=3)


def expect_rejection(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def controls():
    for args in ((1, 0), (2, 0), (2, 2), (13, 1), (True, 1), (3, Q(1))):
        expect_rejection(stencil, *args)
    old, new = profiles(stencil(2, 1))
    expect_rejection(check_sign, old, {2: 6}, Q(1, 4), 2, 1, root_interval(Q(1, 4)))
    expect_rejection(check_sign, new, old, Q(3, 4), 2, 1, root_interval(Q(3, 4)))
    need(evaluate(stencil(2, 1), Q(5, 4)) > 0, "all-exponent extension fails")
    need(evaluate(stencil(2, 1), Q(3, 2)) < 0, "orientation control")
    need(Q(126) * Q(15760999, 2000000000) < 1, "126 not certified by this credit")
    need(not (2**997 * 2000**1000 < 3991**1000), "too-small upper bracket")
    return 12


def main():
    result = dict(status="PASS_RATIONAL_THRESHOLD_RANK_EXCHANGE",
                  finite=family_checks(), overhead=overhead_checks(), controls=controls())
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        need(path.stat().st_size <= 1024 * 1024, "package read capacity")
        data = path.read_bytes()
        need(len(data) <= 1024 * 1024, "package file capacity")
        hashes[name] = sha256(data).hexdigest()
    result["source_sha256"] = hashes
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
