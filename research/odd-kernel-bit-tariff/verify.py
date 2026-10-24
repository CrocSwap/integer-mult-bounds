#!/usr/bin/env python3
"""Coefficient-bit tariff of the odd-kernel address word.

The checker prices the named seven-event word. It does not extend j past 32.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ODD_KERNEL_BIT_TARIFF rows=165 margin=14 no_new_kappa"
KERNELS = (1, 3, 5, 7, 9, 15)
ODD = (3, 5, 7, 9, 15)
J_MAX = 32


def fail(message):
    raise SystemExit("FAIL_ODD_KERNEL_BIT_TARIFF " + message)


def require(condition, message):
    if not condition:
        fail(message)


def bits(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def coefficients(power):
    slope = Fraction(power, 4)
    events = (
        (Fraction(1), (Fraction(-1),)),
        (Fraction(1), (Fraction(1),)),
        (slope, (1 + slope, -slope, -slope)),
        (Fraction(1), (Fraction(1),)),
        (Fraction(1), (Fraction(-1),)),
        (-1 / slope, (1 / slope - 1, Fraction(1), Fraction(1))),
    )
    values = []
    for diagonal, controls in events:
        values.append(diagonal)
        values.extend(controls)
    return values


def word_cost(power):
    return sum(bits(value) for value in coefficients(power))


def fused(index, kernel):
    step = kernel * (1 << index)
    return word_cost(-step) + word_cost(2 * step) + word_cost(-step)


def baseline(index, kernel):
    step = kernel * (1 << index)
    return word_cost(-step) + word_cost(step) + word_cost(step) + word_cost(-step)


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require(word_cost(4) == 32 and word_cost(2) == 38 and word_cost(1) == 45, "the dyadic samples moved")
    require(word_cost(4) < word_cost(2) < word_cost(1), "the word cost became monotone")
    fused_hits = baseline_hits = 0
    smallest = None
    place = None
    for index in range(J_MAX + 1):
        dyadic_fused = fused(index, 1)
        dyadic_base = baseline(index, 1)
        for kernel in KERNELS:
            step = kernel * (1 << index)
            require(word_cost(step) == word_cost(-step), "a sign changed the word cost")
            require(fused(index, kernel) == 2 * word_cost(step) + word_cost(2 * step), "the fused sum moved")
            require(baseline(index, kernel) == 4 * word_cost(step), "the baseline sum moved")
            require(baseline(index, kernel) > fused(index, kernel), "fusion did not save bits")
            if kernel == 1:
                continue
            margin = fused(index, kernel) - dyadic_fused
            require(margin > 0 and baseline(index, kernel) > dyadic_base, "an odd kernel did not exceed the dyadic bill")
            fused_hits += 1
            baseline_hits += 1
            if smallest is None or margin < smallest:
                smallest = margin
                place = [kernel, index]
    require(fused_hits == baseline_hits == 5 * 33 == 165, "the comparison count moved")
    require(smallest == 14 and place == [3, 0], "the smallest fused margin moved")
    require({kernel: fused(2, kernel) for kernel in KERNELS} == {1: 102, 3: 126, 5: 145, 7: 147, 9: 166, 15: 168}, "the j=2 samples moved")
    return {
        "odd_rows": 165,
        "fused_exceeds": 165,
        "baseline_exceeds": 165,
        "minimum_fused_margin": 14,
        "minimum_at_kernel": 3,
        "minimum_at_j": 0,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
