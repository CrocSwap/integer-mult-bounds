#!/usr/bin/env python3
"""Independent square-root interval checks for the proper-terminal sign criterion.

Finite corroboration at t=1/2, not a proof for arbitrary exponents. Uses no
predecessor or primary-checker code. apoursh, with OpenAI Codex assistance.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations_with_replacement
import json
from math import isqrt

SCALE = 1 << 100


def require(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=None)
def root_bounds(value):
    """Outward rational bounds on sqrt(value), using integer arithmetic only."""
    value = Q(value)
    require(value >= 0, "negative radicand")
    floor = isqrt(value.numerator * SCALE * SCALE // value.denominator)
    low = Q(floor, SCALE)
    high = low if low * low == value else Q(floor + 1, SCALE)
    require(low * low <= value <= high * high, "invalid root enclosure")
    return low, high


def interval_product(left, right):
    values = [a * b for a in left for b in right]
    return min(values), max(values)


def subtract(left, right):
    return left[0] - right[1], left[1] - right[0]


def radical_terms(a, b, x):
    require(a <= x <= b, "query outside path")
    terms = Counter()
    for coefficient, value in ((1, x-a), (1, b-x), (-1, b-a)):
        terms[Q(value)] += coefficient
    return terms


def evaluate(terms):
    low = high = Q(0)
    for radicand, coefficient in terms.items():
        if not coefficient or not radicand:
            continue
        lo, hi = root_bounds(radicand)
        if coefficient >= 0:
            low += coefficient * lo
            high += coefficient * hi
        else:
            low += coefficient * hi
            high += coefficient * lo
    return low, high


def h(a, b, x):
    return evaluate(radical_terms(Q(a), Q(b), Q(x)))


def bill_terms(T, paths, x, weights=None):
    terms = radical_terms(Q(0), Q(T), Q(x))
    if weights is None:
        weights = [1] * len(paths)
    require(len(weights) == len(paths), "weight count")
    for (a, b), weight in zip(paths, weights):
        for radicand, coefficient in radical_terms(Q(a), Q(b), Q(x)).items():
            terms[radicand] -= weight * coefficient
    return terms


def g(T, paths, x, weights=None):
    return evaluate(bill_terms(T, paths, x, weights))


def sign(bounds):
    low, high = bounds
    if high < 0:
        return -1
    if low > 0:
        return 1
    if low == high == 0:
        return 0
    raise ValueError("interval insufficient to certify sign")


def check_ratio_grid():
    comparisons = strict = identical = 0
    for T in range(2, 9):
        for a in range(T):
            for b in range(T, T + 5):
                points = [Q(a) + Q((T-a)*j, 8) for j in range(1, 8)]
                for x, y in zip(points, points[1:]):
                    # R(y)-R(x) has this numerator; denominators are positive.
                    hx, hy = h(0, T, x), h(0, T, y)
                    require(sign(hx) == sign(hy) == 1, "nonpositive baseline")
                    if a == 0 and b == T:
                        require(h(a, b, x) == hx and h(a, b, y) == hy,
                                "identity ratio")
                        identical += 1
                    else:
                        determinant = subtract(interval_product(h(a, b, y), hx),
                                               interval_product(h(a, b, x), hy))
                        require(sign(determinant) == 1, "ratio not strictly increasing")
                        strict += 1
                    comparisons += 1
    return dict(ratio_comparisons=comparisons,
                strict_ratios=strict, identical_ratios=identical)


def check_bills():
    bills = normalized_pairs = endpoint_premises = interior_checks = 0
    constant_normalized = positive_left_endpoints = zero_bills = 0
    for T in range(2, 7):
        alphabet = [(a, b) for a in range(T) for b in range(T, T+3)]
        for m in range(1, 4):
            for paths in combinations_with_replacement(alphabet, m):
                A = max(a for a, _ in paths)
                left_sign = sign(g(T, paths, A))
                require(sign(g(T, paths, T)) <= 0, "positive terminal bill")
                points = [Q(A) + Q((T-A)*j, 6) for j in range(1, 6)]
                values = [g(T, paths, x) for x in points]
                all_original = all(pair == (0, T) for pair in paths)
                exceptional_zero = m == 1 and all_original
                if left_sign <= 0:
                    endpoint_premises += 1
                    for value in values:
                        require(sign(value) == (0 if exceptional_zero else -1),
                                "endpoint sign criterion")
                        interior_checks += 1
                    zero_bills += int(exceptional_zero)
                else:
                    positive_left_endpoints += 1
                for x, y, gx, gy in zip(points, points[1:], values, values[1:]):
                    if all_original:
                        # Exact cancellation: G/H = 1-m throughout the interval.
                        remainder = bill_terms(T, paths, x)
                        for radicand, coefficient in radical_terms(Q(0),Q(T),x).items():
                            remainder[radicand] -= (1-m) * coefficient
                        require(not any(remainder.values()), "constant normalized bill")
                        constant_normalized += 1
                    else:
                        difference = subtract(interval_product(gy, h(0,T,x)),
                                              interval_product(gx, h(0,T,y)))
                        require(sign(difference) == -1,
                                "normalized bill not strictly decreasing")
                    normalized_pairs += 1
                bills += 1
    return dict(bills=bills, normalized_pairs=normalized_pairs,
                constant_normalized_pairs=constant_normalized,
                nonpositive_left_endpoint_bills=endpoint_premises,
                positive_left_endpoint_bills=positive_left_endpoints,
                certified_interior_signs=interior_checks,
                exceptional_zero_bills=zero_bills)


def check_predecessor_witness():
    paths = ((3,25), (17,26), (0,25), (6,25))
    left, inside, right = (g(24, paths, x) for x in (17,Q(3819,160),24))
    require(sign(subtract(inside,left)) == 1, "predecessor left maximum gap")
    require(sign(subtract(inside,right)) == 1, "predecessor right maximum gap")
    require(sign(inside) == sign(left) == sign(right) == -1,
            "predecessor sign control")
    return dict(predecessor_witness_checks=3)


def check_failure_controls():
    # Dropping b>=T makes the unit-weight endpoint implication false.
    require(sign(g(4, ((0,3),), 0)) == 0, "short-path left endpoint")
    require(sign(g(4, ((0,3),), 1)) == 1, "short-path interior counterexample")
    # With a negative coefficient, the original path cancels the target and
    # the remaining positive H_(1,8) gives a positive interior after a zero start.
    paths = ((0,4),(1,8))
    require(sign(g(4, paths, 1, (1,-1))) == 0, "signed-weight left endpoint")
    require(sign(g(4, paths, 2, (1,-1))) == 1, "signed-weight counterexample")
    # Even a positive fractional weight invalidates the raw endpoint test at 0.
    fractional = ((0,3),)
    require(sign(g(2, fractional, 0, (Q(1,2),))) == 0, "fractional left endpoint")
    require(sign(g(2, fractional, 2, (Q(1,2),))) == -1, "fractional terminal")
    require(sign(g(2, fractional, 1, (Q(1,2),))) == 1, "fractional counterexample")
    # The exponent range is load bearing: at t=1 the normalizer vanishes;
    # at t=2 it is negative, so the positive-denominator comparison is invalid.
    require(1 + 3 - 4 == 0, "linear exponent control")
    require(1**2 + 3**2 - 4**2 < 0, "convex exponent control")
    # Flip the proposed monotonic direction on a strict valid fixture.
    numerator = subtract(interval_product(h(1,5,3),h(0,4,2)),
                         interval_product(h(1,5,2),h(0,4,3)))
    require(sign(numerator) == 1, "reversed-inequality control")
    return dict(failure_controls=6)


def main():
    results = {}
    for check in (check_ratio_grid, check_bills, check_predecessor_witness,
                  check_failure_controls):
        results.update(check())
    print("PASS_INDEPENDENT_SIGN_CRITERION " + json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
