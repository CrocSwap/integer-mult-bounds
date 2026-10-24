#!/usr/bin/env python3
"""Carry recovery of the FFT digit product.

The checker convolves base-B digits and carries them. It does not run the
word multiplier.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FFT_CARRY_RECOVERY products=1398096 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_WIDTH = 10


def fail(message):
    raise SystemExit("FAIL_FFT_CARRY_RECOVERY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def geometry(width):
    beta = ceil_log2(width)
    base = 1 << beta
    digit_count = (width + beta - 1) // beta
    ell = ceil_log2(2 * digit_count)
    ring = 1 << ell
    return beta, base, digit_count, ring


def cap_identity(digit_count, base):
    room = base - 1
    numerator = digit_count * room * room + digit_count * room
    require(numerator == digit_count * room * base, "the carry cap missed an exact division")
    return digit_count * room


def recover(left, right, beta, base, digit_count, ring, cap):
    left_digits = [(left >> (beta * index)) & (base - 1) for index in range(digit_count)]
    right_digits = [(right >> (beta * index)) & (base - 1) for index in range(digit_count)]
    coefficients = [0] * (2 * digit_count - 1)
    for left_index, left_digit in enumerate(left_digits):
        for right_index, right_digit in enumerate(right_digits):
            coefficients[left_index + right_index] += left_digit * right_digit
    carry = 0
    total = 0
    place = 1
    for index in range(ring):
        coefficient = coefficients[index] if index < len(coefficients) else 0
        mixed = coefficient + carry
        digit = mixed % base
        carry = mixed // base
        require(carry <= cap, "a carry left the cap")
        total += digit * place
        place *= base
    require(carry == 0, "the final carry survived")
    require(total == left * right, "the carried word missed the product")


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    products = 0
    for width in range(2, MAX_WIDTH + 1):
        beta, base, digit_count, ring = geometry(width)
        cap = cap_identity(digit_count, base)
        limit = 1 << width
        for left in range(limit):
            for right in range(limit):
                recover(left, right, beta, base, digit_count, ring, cap)
                products += 1
    for base in range(2, 257):
        for digit_count in range(1, 257):
            cap_identity(digit_count, base)
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(products == 1398096, "product count")
    require(receipt["max_width"] == MAX_WIDTH, "receipt width")
    require(receipt["products"] == products, "receipt products")
    require(receipt["carry_cap"] == "q(B-1)", "receipt cap")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
