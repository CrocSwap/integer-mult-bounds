#!/usr/bin/env python3
"""Exact bounded-reserve contraction checks, produced by Nick Petalas.

Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import platform
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(first, second, budget, rate):
    for menu in (first, second):
        require(type(menu) is tuple and 1 <= len(menu) <= 16, "menu size/type")
        for row in menu:
            require(type(row) is tuple and len(row) == 2, "row shape")
            for entry in row:
                require(type(entry) is F and entry >= 0, "nonnegative rational row")
                require(max(entry.numerator.bit_length(),
                            entry.denominator.bit_length()) <= 64, "entry size")
    for value in (budget, rate):
        require(type(value) is F, "rational budget/rate")
        require(max(abs(value.numerator).bit_length(),
                    value.denominator.bit_length()) <= 64, "scalar size")
    require(budget >= 1 and rate >= 0, "budget/rate domain")


def bounded_weights(first, second, budget, rate):
    """Return all feasible ratios w2/w1 as a closed rational interval, or None."""
    validate(first, second, budget, rate)
    if any(a + b / budget > rate for a, b in first):
        return None
    if any(d + c / budget > rate for c, d in second):
        return None
    for (a, b), (c, d) in product(first, second):
        if (rate - a) * (rate - d) < b * c:
            return None
    low, high = 1 / budget, budget
    for c, d in second:
        if c:
            low = max(low, c / (rate - d))
    for a, b in first:
        if b:
            high = min(high, (rate - a) / b)
    require(0 < low <= high, "nonempty interval theorem")
    return low, high


def literal_ok(first, second, budget, rate, w1, w2):
    if min(w1, w2) <= 0 or max(w1, w2) > budget * min(w1, w2):
        return False
    return (all(a * w1 + b * w2 <= rate * w1 for a, b in first)
            and all(c * w1 + d * w2 <= rate * w2 for c, d in second))


def vertex_oracle(first, second, budget, rate):
    """Enumerate normalized polytope vertices; do not use pair determinants."""
    candidates = [1 / (budget + 1), budget / (budget + 1)]
    for a, b in first:
        slope = a - b - rate
        if slope:
            candidates.append(-b / slope)
    for c, d in second:
        slope = c - d + rate
        if slope:
            candidates.append((rate - d) / slope)
    for w1 in candidates:
        if literal_ok(first, second, budget, rate, w1, 1 - w1):
            return w1, 1 - w1
    return None


def compare(first, second, budget, rate):
    interval = bounded_weights(first, second, budget, rate)
    vertex = vertex_oracle(first, second, budget, rate)
    require((interval is None) == (vertex is None), "independent decision mismatch")
    if interval is not None:
        for ratio in (interval[0], sum(interval) / 2, interval[1]):
            require(literal_ok(first, second, budget, rate, F(1), ratio),
                    "invalid delivered weight")
        require(interval[0] <= vertex[1] / vertex[0] <= interval[1],
                "oracle vertex outside complete feasible interval")
    return interval is not None


def census():
    rows = tuple(product((F(0), F(1, 2), F(1)), repeat=2))
    menus = tuple((row,) for row in rows) + tuple(combinations(rows, 2))
    count = feasible = 0
    for first, second in product(menus, repeat=2):
        for budget in (F(1), F(3, 2), F(3)):
            for rate in (F(0), F(1, 2), F(1), F(3, 2), F(2)):
                feasible += compare(first, second, budget, rate)
                count += 1
    return {"cases": count, "feasible": feasible, "infeasible": count - feasible}


def phase_law():
    first = ((F(0), F(1, 2)), (F(1, 8), F(1, 4)))
    second = ((F(1, 4), F(0)), (F(1, 16), F(1, 8)))
    count = 0
    for budget in (F(1), F(5, 4), F(7, 5), F(3, 2), F(2), F(4), F(100)):
        for numerator in range(65):
            rate = F(numerator, 64)
            expected = rate >= 1 / (2 * budget) and 8 * rate * rate >= 1
            require(compare(first, second, budget, rate) == expected, "phase law")
            count += 1
    interval = bounded_weights(first, second, F(7, 5), F(5, 14))
    require(interval == (F(5, 7), F(5, 7)), "literal boundary interval")
    require(bounded_weights(first, second, F(7, 5), F(5, 14) - F(1, 10000))
            is None, "false strict improvement")
    return count


def tail_checks():
    first = ((F(0), F(1, 2)), (F(1, 8), F(1, 4)))
    second = ((F(1, 4), F(0)), (F(1, 16), F(1, 8)))
    total = (F(12, 7), F(10, 7))
    count = 0
    for budget in (F(1), F(5, 4), F(7, 5)):
        rate = 1 / (2 * budget)
        require(bounded_weights(first, second, budget, rate) is not None, "tail weight")
        current = (F(0), F(0))
        for depth in range(129):
            error = max(total[i] - current[i] for i in range(2))
            require(min(total[i] - current[i] for i in range(2)) >= 0, "prefix overshoot")
            require(error <= budget * rate ** depth * max(total), "all-depth tail")
            current = tuple(1 + max(a * current[0] + b * current[1] for a, b in menu)
                            for menu in (first, second))
            count += 1
        require(all(1 + max(a * total[0] + b * total[1] for a, b in menu) == total[i]
                    for i, menu in enumerate((first, second))), "fixed point")
    return count


def rejection_controls():
    row = ((F(0), F(1)),)
    cases = [
        ((), row, F(1), F(1)),
        (list(row), row, F(1), F(1)),
        (((F(0),),), row, F(1), F(1)),
        (((F(-1), F(0)),), row, F(1), F(1)),
        (((True, F(0)),), row, F(1), F(1)),
        (((F(2 ** 64), F(0)),), row, F(1), F(1)),
        (row, row, F(1, 2), F(1)),
        (row, row, F(1), F(-1)),
        (row, row, 1, F(1)),
        (row, row, F(1), F(1, 2 ** 64)),
        (row * 17, row, F(1), F(1)),
    ]
    for args in cases:
        try:
            bounded_weights(*args)
        except ValueError:
            continue
        raise ValueError("malformed contract accepted")
    zero, double = ((F(0), F(0)),), ((F(0), F(2)),)
    fixtures = ((double, ((F(2), F(0)),), F(4)),
                (double, zero, F(1)), (zero, ((F(2), F(0)),), F(1)))
    for first, second, budget in fixtures:
        require(vertex_oracle(first, second, budget, F(1)) is None, "false certificate")
        require(bounded_weights(first, second, budget, F(1)) is None, "missing charge")
    return len(cases) + len(fixtures)


def receipt(result):
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        require((package / name).stat().st_size <= 262144, "package source bound")
        payload = (package / name).read_bytes()
        require(len(payload) <= 262144, "package source bound")
        hashes[name] = sha256(payload).hexdigest()
    return {"schema": "bounded-adaptive-reserves/v1", "result": result,
            "sources_sha256": hashes, "python": platform.python_version()}


def main():
    require(sys.version_info[:2] == (3, 12), "requires CPython 3.12")
    result = {"census": census(), "phase_thresholds": phase_law(),
              "tail_prefixes": tail_checks(), "rejections": rejection_controls()}
    print(json.dumps(receipt(result), sort_keys=True))
    print("PASS_BOUNDED_ADAPTIVE_RESERVES")


if __name__ == "__main__":
    main()
