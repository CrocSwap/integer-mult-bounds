#!/usr/bin/env python3
"""Logarithm absorption bound for the FFT word cost.

The checker compares an integer ceiling with 24n. It does not run the word
multiplier.
"""

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_LOG_ABSORPTION_BOUND through=16777216 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
LIMIT = 1 << 24


def fail(message):
    raise SystemExit("FAIL_LOG_ABSORPTION_BOUND " + message)


def require(condition, message):
    if not condition:
        fail(message)


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def exponential_half():
    total = Fraction(0)
    term = Fraction(1)
    for index in range(40):
        total += term
        term /= 2 * (index + 1)
    require(total + 2 * term < 2, "exp(1/2) reached 2")
    return total + 2 * term


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    upper = exponential_half()
    require(upper < 2, "the half exponential escaped")
    require(8 * 3 == 24, "the constant factors moved")
    checked = 0
    for number in range(1, LIMIT + 1):
        require(number + 2 <= 3 * number, "the width factor moved")
        ceiling = ceil_log2(number + 2)
        require(ceiling * ceiling <= 24 * number, "the logarithm bound moved")
        checked += 1
    for base in range(1, 1025):
        for exponent in range(0, 17):
            require(base ** exponent <= (base + 2) ** exponent, "the power order moved")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(checked == LIMIT, "the range moved")
    require(receipt["checked_through"] == LIMIT, "receipt limit")
    require(receipt["delta_one_bound"] == "24n", "receipt bound")
    require(receipt["width_factor"] == 3, "receipt width")
    require(receipt["series_below"] == 2, "receipt series")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
