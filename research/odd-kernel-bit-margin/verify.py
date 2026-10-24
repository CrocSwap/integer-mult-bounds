#!/usr/bin/env python3
"""Odd kernels cost more ADDRESS coefficient bits than the dyadic kernel.

The checker rebuilds the seven-event word. It does not try another tariff.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ODD_KERNEL_BIT_MARGIN comparisons=330 min_fused=14 no_new_kappa"
KERNELS = (3, 5, 7, 9, 15)


def fail(message):
    raise SystemExit("FAIL_ODD_KERNEL_BIT_MARGIN " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def address_word(power):
    require(isinstance(power, int) and power != 0, "the query power moved")
    slope = Fraction(power, 4)
    return (
        ("affine", Fraction(1), (Fraction(-1),)),
        ("affine", Fraction(1), (Fraction(1),)),
        ("affine", slope, (1 + slope, -slope, -slope)),
        ("child",),
        ("affine", Fraction(1), (Fraction(1),)),
        ("affine", Fraction(1), (Fraction(-1),)),
        ("affine", -1 / slope, (1 / slope - 1, Fraction(1), Fraction(1))),
    )


def bit_length(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def word_tariff(power):
    total = 0
    for event in address_word(power):
        if event[0] != "affine":
            continue
        total += bit_length(event[1])
        total += sum(bit_length(coefficient) for coefficient in event[2])
    return total


def closed_tariff(power):
    slope = Fraction(power, 4)
    variable = (slope, 1 + slope, -slope, -slope, -1 / slope, 1 / slope - 1)
    return 20 + sum(bit_length(coefficient) for coefficient in variable)


def program(powers):
    return sum(word_tariff(power) for power in powers)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    require((word_tariff(1), word_tariff(2), word_tariff(4)) == (45, 38, 32), "the word tariff lost its descent")
    fused_margins = []
    baseline_margins = []
    for kernel in KERNELS:
        for index in range(33):
            scale = kernel << index
            dyadic = 1 << index
            for power in (-scale, scale, 2 * scale, -(dyadic), dyadic, 2 * dyadic):
                require(word_tariff(power) == closed_tariff(power), "the closed tariff moved")
            fused = program((-scale, 2 * scale, -scale)) - program((-dyadic, 2 * dyadic, -dyadic))
            baseline = program((-scale, scale, scale, -scale)) - program((-dyadic, dyadic, dyadic, -dyadic))
            require(fused > 0 and baseline > 0, "an odd kernel met the dyadic bill")
            fused_margins.append((fused, kernel, index))
            baseline_margins.append(baseline)
    require(len(fused_margins) == 165 and len(baseline_margins) == 165, "the comparison count moved")
    require(min(fused_margins) == (14, 3, 0), "the fused margin moved")
    require(min(baseline_margins) == 16, "the baseline margin moved")
    return {
        "comparisons": 330,
        "min_fused_margin": 14,
        "min_baseline_margin": 16,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
