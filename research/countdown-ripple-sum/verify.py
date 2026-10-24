#!/usr/bin/env python3
"""Countdown ripple sum of the FFT counter.

The checker adds one plus the trailing-zero count at every integer. It does
not run the word multiplier.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_COUNTDOWN_RIPPLE_SUM through=16777216 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
LIMIT = 1 << 24


def fail(message):
    raise SystemExit("FAIL_COUNTDOWN_RIPPLE_SUM " + message)


def require(condition, message):
    if not condition:
        fail(message)


def trailing_zeros(number):
    return (number & -number).bit_length() - 1


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    ripple = 0
    valuation = 0
    previous_pop = 0
    for number in range(1, LIMIT + 1):
        zeros = trailing_zeros(number)
        pop = number.bit_count()
        require(pop - previous_pop == 1 - zeros, "popcount step")
        ripple += zeros + 1
        valuation += zeros
        require(ripple == 2 * number - pop, "ripple sum")
        require(valuation == number - pop, "valuation sum")
        previous_pop = pop
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["checked_through"] == LIMIT, "receipt limit")
    require(receipt["ripple_sum"] == "2N-popcount(N)", "receipt ripple")
    require(receipt["valuation_sum"] == "N-popcount(N)", "receipt valuation")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    require(ripple == 2 * LIMIT - 1, "power-of-two ripple")
    print(MARKER)


if __name__ == "__main__":
    main()
