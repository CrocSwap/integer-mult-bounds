#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the whole-helper dual and the strict saved-arm moment increments."""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import intervals as I

WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPACITIES = {8: 672, 16: 448, 32: 448, 48: 448}
BONUS = {8: 2, 16: 4, 32: 8, 48: -13}
BASE_WIDTHS = (56, 32, 30, 122, 240)
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
ROOT = (Q("0.001676905273619680861300"), Q("0.001676905273619680861301"))
ATTAINING_BINS = (
    (8, (0, 0, 0, 1, 0), 24864, 0),
    (16, (0, 0, 0, 2, 0), 3306, 0),
    (16, (0, 0, 1, 0, 1), 9394, 0),
    (16, (2, 0, 0, 1, 0), 3876, 0),
    (32, (0, 0, 2, 0, 2), 298, 0),
    (32, (0, 1, 0, 0, 3), 10656, 0),
    (32, (1, 0, 0, 0, 3), 5622, 1),
    (48, (0, 0, 0, 0, 0), 11302, 48),
    (48, (1, 0, 0, 1, 4), 5274, 0),
)


def patterns(capacity, position=0):
    if position == len(WIDTHS):
        yield (), capacity, 0
        return
    width, price = WIDTHS[position], PRICES[position]
    for count in range(capacity // width + 1):
        for tail, residual, value in patterns(capacity - count * width, position + 1):
            yield (count,) + tail, residual, value + count * price


def price_table():
    table, count = {}, 0
    for capacity in CAPACITIES:
        for _, residual, value in patterns(capacity):
            value += BONUS[capacity]
            table[residual] = max(table.get(residual, value), value)
            count += 1
    # This recurrence has no pattern-count vectors.
    fills = [None] * 49
    fills[0] = 0
    for filled in range(1, 49):
        values = [fills[filled - w] + p for w, p in zip(WIDTHS, PRICES)
                  if filled >= w and fills[filled - w] is not None]
        if values:
            fills[filled] = max(values)
    other = {}
    for capacity in CAPACITIES:
        for filled in range(capacity + 1):
            if fills[filled] is not None:
                residual = capacity - filled
                value = BONUS[capacity] + fills[filled]
                other[residual] = max(other.get(residual, value), value)
    assert table == other
    assert count == 1163 and (table[0], table[1], table[48]) == (0, 19, -13)
    return table, count


def interval_sum(coefficients, endpoint_range=ROOT):
    lower = upper = Q(0)
    for rank, coefficient in coefficients.items():
        lo = I.child_cost(rank, 73, endpoint_range[0])[0]
        hi = I.child_cost(rank, 73, endpoint_range[1])[1]
        lower += coefficient * (lo if coefficient >= 0 else hi)
        upper += coefficient * (hi if coefficient >= 0 else lo)
    return lower, upper


def majorizes(left, right):
    left, right = sorted(left, reverse=True), sorted(right, reverse=True)
    assert len(left) == len(right) and sum(left) == sum(right)
    a = b = 0
    for x, y in zip(left, right):
        a += x
        b += y
        assert a >= b
    assert left != right


def complete_bound(even=0, odd=0):
    # Counts are per call. Fractional values give the all-call average.
    total = Q(even) + Q(odd)
    profile = {r: Q(9 * n) for r, n in LOCAL.items()}
    profile[1] -= 18 * even
    profile[2] += 18 * even + 9 * odd
    n1 = Q(5622, 37) + Q(198, 37) * total
    n48 = Q(11302, 37) - Q(18, 37) * total
    profile[1] += n1
    profile[48] = n48
    assert sum(r * n for r, n in profile.items()) == 73 * 896 - 320
    return profile


def verify():
    if not __debug__:
        raise RuntimeError("verification requires assertions; do not use -O")
    table, count = price_table()
    mass = sum(c * n for c, n in CAPACITIES.items()) - 9 * sum(w * n for w, n in zip(WIDTHS, BASE_WIDTHS))
    price = sum(BONUS[c] * n for c, n in CAPACITIES.items()) + 9 * sum(p * n for p, n in zip(PRICES, BASE_WIDTHS))
    assert (mass, price, 48 * price + 13 * mass) == (14814, -1084, 140550)
    # One switched call replaces one width 7 with one width 9.
    assert 48 * (PRICES[4] - PRICES[2]) - 13 * 2 == 550
    assert Q(550, 925) == Q(22, 37)
    assert (2 + Q(22, 37)) / 48 == Q(2, 37)
    margins = []
    for rank, value in table.items():
        if rank in (0, 1, 48):
            continue
        v = 48 * value + 13 * rank
        coefficients = {rank: Q(48), 48: -rank + Q(v, 925), 1: -Q(48 * v, 925)}
        lo, _ = interval_sum(coefficients)
        assert lo > 0, (rank, lo)
        margins.append(lo)
    assert interval_sum({1: Q(48), 48: Q(-1)})[0] > 0
    majorizes([48] + [1] * 26 + [0] * 10, [2] * 37)
    majorizes([48, 48] + [0] * 57, [2] * 37 + [1] * 22)
    profile = complete_bound()
    below = interval_sum(profile, (ROOT[0], ROOT[0]))
    above = interval_sum(profile, (ROOT[1], ROOT[1]))
    assert below[1] < 896 < above[0]
    for capacity, stock in CAPACITIES.items():
        assert sum(n for c, _, n, _ in ATTAINING_BINS if c == capacity) == 37 * stock
    for i, stock in enumerate(BASE_WIDTHS):
        assert sum(p[i] * n for _, p, n, _ in ATTAINING_BINS) == 37 * 9 * stock
    for capacity, pattern, _, residual in ATTAINING_BINS:
        assert sum(w * n for w, n in zip(WIDTHS, pattern)) + residual == capacity
    assert {r: sum(n for _, _, n, s in ATTAINING_BINS if s == r)
            for r in (1, 48)} == {1: 5622, 48: 11302}
    # Free removal of two rank-1 residuals contradicts the necessary dual.
    false_n1 = Q(5622, 37) - 2
    assert 925 * false_n1 < 140550 + 550
    return {"status": "PASS_ALL_REPLICA_SAVED_ARM_OBSTRUCTION", "patterns": count,
            "root_bracket": list(map(str, ROOT)), "minimum_support_margin": str(min(margins)),
            "residual_increment_per_switch": {"1": "22/37", "48": "-2/37"},
            "even_total_increment": {"1": "-52/37", "2": "2", "48": "-2/37"},
            "odd_total_increment": {"1": "22/37", "2": "1", "48": "-2/37"}}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
