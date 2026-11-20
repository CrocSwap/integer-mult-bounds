#!/usr/bin/env python3
"""Verify the odd residue product and adjacent-bit width extension."""

from itertools import product
import json
from pathlib import Path
from runpy import run_path


FIELD = run_path(str(Path(__file__).with_name("extension_check.py")))
primitive_powers = FIELD["list_primitive_powers"]
polynomial_product = FIELD["polynomial_product"]
reduce_polynomial = FIELD["reduce_polynomial"]


def verify(m):
    q = 1 << (m - 2)
    residue_modulus = 1 << m
    degree = m + 1
    modulus, powers = primitive_powers(degree)
    assert len(powers) == 8 * q - 1
    highest_exponent = 6 * q - 4
    table = {}
    five = [pow(5, t, residue_modulus) for t in range(q)]
    for e, field_word in enumerate(powers[:highest_exponent + 1]):
        t, s = divmod(e, 3)
        table[field_word] = ((-1)**s * five[t % q]) % residue_modulus
    assert len(table) == 6 * q - 3

    classes = {((-1)**s * value) % residue_modulus: (t, s)
               for s, (t, value) in product(range(2), enumerate(five))}
    odds = sorted(classes)
    assert odds == list(range(1, residue_modulus, 2))
    encodings = {x: powers[3 * t + s] for x, (t, s) in classes.items()}
    assert len(set(encodings.values())) == len(odds)
    assert all(x.bit_length() <= degree for x in encodings.values())
    odd_product_rows = set()
    joint_bit_rows = set()
    low_bit_rows = set()
    hits = set()
    for x in odds:
        full_row = []
        odd_pair_row = []
        # These two channels independently route the m-1 freely varying bits
        # of an odd residue, multiplying each by the hardwired polynomial 1.
        left_routed = polynomial_product(x >> 1, 1)
        for y in odds:
            raw = polynomial_product(encodings[x], encodings[y])
            decoded = reduce_polynomial(raw, modulus)
            wanted = (x * y) % residue_modulus
            tx, sx = classes[x]
            ty, sy = classes[y]
            assert decoded == powers[3 * (tx + ty) + sx + sy]
            assert table[decoded] == wanted
            hits.add(decoded)

            right_routed = polynomial_product(1, y >> 1)
            from_routes = ((2 * left_routed + 1) * (2 * right_routed + 1)) % residue_modulus
            assert from_routes == wanted
            full_row.append(wanted)
            odd_pair_row.append(wanted >> (m - 2))
        assert len(set(full_row)) > 1 and len(set(odd_pair_row)) > 1
        odd_product_rows.add(tuple(full_row))
        joint_bit_rows.add(tuple(odd_pair_row))
        low_bit_rows.add(tuple(pair >> 1 for pair in odd_pair_row))
    assert len(odd_product_rows) == len(joint_bit_rows) == 2 * q
    assert len(low_bit_rows) == q
    assert hits == set(table)
    kernel_element = (1 << (m - 1)) - 1
    assert classes[kernel_element] == (q // 2, 1)
    assert kernel_element >> (m - 2) == 1
    return {"m": m, "pairs": len(odds)**2, "joint_rows": len(joint_bit_rows),
            "full_rows": len(odd_product_rows), "one_bit_rows": len(low_bit_rows),
            "two_channel_exact_width_per_side": m,
            "mixed_channel_width_per_side": degree, "reachable_field_addresses": len(hits),
            "reduction_modulus_mask": modulus}


def main():
    cases = [verify(m) for m in range(3, 11)]
    print(json.dumps({"status": "passed", "cases": cases,
                      "pairs": sum(case["pairs"] for case in cases)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
