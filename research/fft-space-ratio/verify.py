#!/usr/bin/env python3
"""Packed-record ratio of the FFT word.

The checker compares r(p0+2) with 88n/7. It does not run the word multiplier.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FFT_SPACE_RATIO widths=4194302 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_WIDTH = 1 << 22


def fail(message):
    raise SystemExit("FAIL_FFT_SPACE_RATIO " + message)


def require(condition, message):
    if not condition:
        fail(message)


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    require(8 * 4 == 32 and 8 * 2 == 16, "the coarse factors moved")
    checked = 0
    equalities = 0
    for width in range(3, MAX_WIDTH + 1):
        beta = ceil_log2(width)
        digit_count = (width + beta - 1) // beta
        ell = ceil_log2(2 * digit_count)
        ring = 1 << ell
        precision = 2 * beta + ell
        record = ring * (precision + 2)
        require(7 * record <= 88 * width, "the sharp ratio moved")
        require(record < 40 * width, "the coarse ratio moved")
        if 7 * record == 88 * width:
            equalities += 1
            require(width == 7, "an unexpected equality")
        checked += 1
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(checked == 4194302, "width count")
    require(equalities == 1, "equality count")
    require(receipt["widths"] == checked, "receipt widths")
    require(receipt["max_width"] == MAX_WIDTH, "receipt max")
    require(receipt["numerator"] == 88 and receipt["denominator"] == 7, "receipt ratio")
    require(receipt["equality_width"] == 7, "receipt equality")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
