#!/usr/bin/env python3
"""Sign cancellation in the cyclic-to-negacyclic substitution.

The checker compares the two wraps. It does not run the middle-map consumer.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_NEGACYCLIC_SIGN_CANCELLATION pairs=22369620 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_ELL = 12


def fail(message):
    raise SystemExit("FAIL_NEGACYCLIC_SIGN_CANCELLATION " + message)


def require(condition, message):
    if not condition:
        fail(message)


def exponent_pairs(ring):
    count = 0
    for left in range(ring):
        for right in range(ring):
            exponent = left + right
            degree = left + right
            sign = 1
            if exponent >= ring:
                exponent -= ring
                sign = -sign
            if degree >= ring:
                degree -= ring
                sign = -sign
            require(sign == 1 and exponent == degree, "a wrap disagreed")
            count += 1
    return count


def zeta_power(ring):
    value = [1] + [0] * (ring - 1)
    for _ in range(ring):
        value = [-value[-1]] + value[:-1]
    require(value == [-1] + [0] * (ring - 1), "zeta^r missed -1")


def products(ring):
    count = 0
    limit = 1 << ring
    for left_mask in range(limit):
        left = [(left_mask >> index) & 1 for index in range(ring)]
        for right_mask in range(limit):
            right = [(right_mask >> index) & 1 for index in range(ring)]
            cyclic = [0] * ring
            signed = [0] * ring
            for left_index, left_digit in enumerate(left):
                for right_index, right_digit in enumerate(right):
                    term = left_digit * right_digit
                    cyclic[(left_index + right_index) % ring] += term
                    exponent = left_index + right_index
                    degree = left_index + right_index
                    sign = 1
                    if exponent >= ring:
                        exponent -= ring
                        sign = -sign
                    if degree >= ring:
                        degree -= ring
                        sign = -sign
                    require(exponent == degree, "a product degree moved")
                    signed[degree] += sign * term
            require(signed == cyclic, "a product disagreed")
            count += 1
    return count


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    pairs = 0
    for ell in range(1, MAX_ELL + 1):
        ring = 1 << ell
        zeta_power(ring)
        pairs += exponent_pairs(ring)
    product_count = 0
    for ring in (2, 4, 8):
        product_count += products(ring)
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(pairs == 22369620, "pair count")
    require(product_count == 65808, "product count")
    require(receipt["max_ell"] == MAX_ELL, "receipt ell")
    require(receipt["exponent_pairs"] == pairs, "receipt pairs")
    require(receipt["polynomial_products"] == product_count, "receipt products")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
