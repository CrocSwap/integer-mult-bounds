#!/usr/bin/env python3
"""Exact optimization of two stated compiler inequalities. Apache-2.0."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def floor(value):
    return value.numerator // value.denominator


def ceil(value):
    return -floor(-value)


def parameters(c, uniform, v, h):
    need(isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 4096,
         "tensor power must be an integer in [1,4096]")
    for value in (c, uniform, h):
        need(isinstance(value, F), "parameters must be exact fractions")
        need(max(value.numerator.bit_length(), value.denominator.bit_length()) <= 256,
             "parameter exceeds the executable 256-bit input bound")
    need(0 < uniform < c < 1 and 0 < h <= 1, "invalid exponent domain")
    gap = c - uniform
    a = v * (8 * h - 3)
    debt = 1 + 8 * v * c
    e = gap * a + debt
    need(e > 8 * v * gap * h, "feasible pole must exceed the base range")
    return gap, a, debt, e


def original_gaps(c, uniform, v, h, h0, h1, x):
    """Evaluate the original inequalities, without the reduced objective."""
    gap = c - uniform
    induction = h0 * h * x - ((5 + 8 * h) * v * x + 1 + 8 * v * (c - x))
    final = h1 * (gap - x) - h0 * (c - x)
    return (h0 >= 8 * v and 0 < x < gap, induction, final)


def optimum(c, uniform, v, h):
    gap, a, debt, e = parameters(c, uniform, v, h)
    d = gap * h
    square = debt * uniform * e / c
    left = floor(e / d) + 1
    right = ceil((e + square + 1) / d) + 1
    first = left
    # The right endpoint exceeds (e+sqrt(square))/d. Binary search the
    # derivative's sign, with a budget from the initial interval.
    for _ in range((right - left).bit_length() + 1):
        if left == right:
            break
        middle = (left + right) // 2
        derivative = c * (d * middle - e) ** 2 - debt * uniform * e
        if derivative >= 0:
            right = middle
        else:
            left = middle + 1
    need(left == right, "derivative search exhausted its proved bound")
    candidates = (left,) if left == first else (left - 1, left)
    rows = []
    for h0 in candidates:
        x = debt / (h * h0 - a)
        threshold = h0 * (c - x) / (gap - x)
        h1 = floor(threshold) + 1
        domain, induction, final = original_gaps(c, uniform, v, h, h0, h1, x)
        need(domain and induction == 0 and final > 0, "invalid optimum witness")
        rows.append((h1, h0, x, threshold))
    h1, h0, x, threshold = min(rows)
    return {"H0": h0, "H1": h1, "x": x, "threshold": threshold,
            "candidates": tuple(row[1] for row in rows)}


def literal_feasible(c, uniform, v, h, h0, h1):
    """An independent interval oracle for a proposed integer pair."""
    if h0 < 8 * v or h1 <= h0:
        return False
    slope = h0 * h - (5 + 8 * h) * v + 8 * v
    if slope <= 0:
        return False
    lower = (1 + 8 * v * c) / slope
    upper = (h1 * (c - uniform) - h0 * c) / (h1 - h0)
    return 0 < lower < c - uniform and lower < upper


def exhaustive_small():
    cases = pairs = 0
    for v in (1, 2):
        for h in (F(1, 2), F(1)):
            for c in (F(1, 4), F(1, 2), F(3, 4)):
                for ratio in (F(1, 4), F(1, 2), F(3, 4)):
                    uniform = c * ratio
                    result = optimum(c, uniform, v, h)
                    best = result["H1"]
                    # Every improving pair has H0 < H1 <= best. Enumerate
                    # every possible H0 and the entire separator interval.
                    need(best < 10000, "small oracle capacity")
                    for h0 in range(8 * v, best):
                        need(not literal_feasible(c, uniform, v, h, h0, best - 1),
                             "literal oracle found a smaller integer H1")
                        pairs += 1
                    need(literal_feasible(c, uniform, v, h, result["H0"], best),
                         "literal oracle rejected the optimum")
                    cases += 1
    return {"parameter_cases": cases, "integer_H0_candidates": pairs}


def controls():
    rejected = 0
    for args in ((F(1, 2), F(1, 2), 1, F(1, 2)),
                 (F(1, 2), F(0), 1, F(1, 2)),
                 (F(1, 2), F(1, 4), 0, F(1, 2)),
                 (F(1, 2), F(1, 4), 1, F(0)),
                 (F(1, 2), F(1, 4), 4097, F(1, 2)),
                 (F(1, 2), F(1, 2**257), 1, F(1, 2))):
        try:
            optimum(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    c, uniform, v, h = F(1, 2), F(1, 4), 1, F(1, 2)
    result = optimum(c, uniform, v, h)
    h0, x = result["H0"], result["x"]
    need(not literal_feasible(c, uniform, v, h, h0, result["H1"] - 1),
         "one-below result accepted")
    need(original_gaps(c, uniform, v, h, h0, result["H1"], x / 2)[1] < 0,
         "underfunded induction accepted")
    # This integer H1 puts the final inequality exactly at equality.
    need(original_gaps(c, uniform, v, h, 43, 1806, F(10, 41))[2] == 0,
         "closed final boundary control")
    need(not literal_feasible(c, uniform, v, h, 43, 1806),
         "non-strict final boundary accepted")
    return {"invalid_inputs_rejected": rejected, "scientific_controls": 3}


def fixture(c, uniform):
    v, h = 1024, F(1, 64)
    result = optimum(c, uniform, v, h)
    x = (c - uniform) / 2
    h0 = ceil(((5 + 8 * h) * v * x + 1 + 8 * v * (c - x)) / (h * x))
    h1 = floor(h0 * (c - x) / (c - uniform - x)) + 1
    need(result["H1"] < h1, "no strict improvement over midpoint")
    return {"tested_saving": c, "uniform_saving": uniform,
            "midpoint_H0": h0, "midpoint_H1": h1,
            "optimum": result, "H1_reduction": h1 - result["H1"]}


def main():
    result = {
        "status": "PASS_INTEGER_COMPILER_SEPARATOR",
        "claim_type": "scoped proof with finite exact corroboration",
        "merged_BIT_fixture": fixture(F(".00346"), F(".003459")),
        "PR4814_parameter_fixture": fixture(F(".00347545806"), F(".00347545805")),
        "exhaustive": exhaustive_small(),
        "controls": controls(),
        "package_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest()
                           for name in ("verify.py", "PROOF.md", "SOURCES.json",
                                        "TASK.json", "VERIFY.json", "README.md")},
    }
    print(json.dumps(result, default=str, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
