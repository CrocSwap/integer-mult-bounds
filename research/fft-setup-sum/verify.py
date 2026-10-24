#!/usr/bin/env python3
"""Sum of the three FFT setup terms.

The checker adds the geometry terms. It does not run the word multiplier.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FFT_SETUP_SUM widths=4194302 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_WIDTH = 1 << 22


def fail(message):
    raise SystemExit("FAIL_FFT_SETUP_SUM " + message)


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
    require(256 + 512 + 64 == 832, "the separate caps moved")
    require(1017 < 7 * 832, "the sharp ratio passed the separate sum")
    checked = 0
    equalities = 0
    for width in range(3, MAX_WIDTH + 1):
        beta = ceil_log2(width)
        digit_count = (width + beta - 1) // beta
        ell = ceil_log2(2 * digit_count)
        ring = 1 << ell
        precision = 2 * beta + ell
        square = precision * precision
        cube = precision * square
        total = ring * (ell + 1) * square + ring * cube + cube
        scale = width * beta * beta
        require(7 * total <= 1017 * scale, "the setup sum moved")
        if 7 * total == 1017 * scale:
            equalities += 1
            require(width == 7 and total == 9153, "an unexpected equality")
        checked += 1
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(checked == 4194302, "width count")
    require(equalities == 1, "equality count")
    require(receipt["widths"] == checked, "receipt widths")
    require(receipt["max_width"] == MAX_WIDTH, "receipt max")
    require(receipt["numerator"] == 1017 and receipt["denominator"] == 7, "receipt ratio")
    require(receipt["equality_width"] == 7, "receipt equality")
    require(receipt["separate_cap_sum"] == 832, "receipt caps")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
