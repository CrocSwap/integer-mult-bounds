#!/usr/bin/env python3
"""Elementary constants in the FFT word invoice.

The checker compares the digit geometry with the stated multiples. It does
not run the word multiplier.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FFT_TIME_CONSTANTS widths=1048574 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_WIDTH = 1 << 20


def fail(message):
    raise SystemExit("FAIL_FFT_TIME_CONSTANTS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def geometry(width):
    beta = ceil_log2(width)
    digit_count = (width + beta - 1) // beta
    ell = ceil_log2(2 * digit_count)
    ring = 1 << ell
    precision = 2 * beta + ell
    return beta, ell, ring, precision


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    require(8 * 2 * (4 ** 2) == 256, "the first product moved")
    require(8 * (4 ** 3) == 512, "the second product moved")
    require(4 ** 3 == 64, "the third product moved")
    checked = 0
    for width in range(3, MAX_WIDTH + 1):
        beta, ell, ring, precision = geometry(width)
        scale = width * beta * beta
        require(ring * beta < 8 * width, "the ring ratio moved")
        require(ell + 1 <= 2 * beta, "the length ratio moved")
        require(precision <= 4 * beta, "the precision ratio moved")
        require(beta <= width, "the digit width moved")
        require(ring * (ell + 1) * precision * precision <= 256 * scale, "the first term moved")
        require(ring * precision ** 3 <= 512 * scale, "the second term moved")
        require(precision ** 3 <= 64 * scale, "the third term moved")
        checked += 1
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(checked == 1048574, "width count")
    require(receipt["widths"] == checked, "receipt widths")
    require(receipt["max_width"] == MAX_WIDTH, "receipt max")
    require(receipt["multiples"] == [256, 512, 64], "receipt multiples")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
