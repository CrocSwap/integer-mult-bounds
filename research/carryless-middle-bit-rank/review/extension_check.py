#!/usr/bin/env python3
"""Independent finite checks of the single-channel odd-product-bit construction."""

from itertools import product
import json


def reduce_polynomial(word, modulus):
    while word.bit_length() >= modulus.bit_length():
        word ^= modulus << (word.bit_length() - modulus.bit_length())
    return word


def list_primitive_powers(width):
    size = 1 << width
    for modulus in range(size + 1, 2 * size, 2):
        power = 1
        seen = set()
        powers = []
        for _ in range(size - 1):
            if power == 0 or power in seen:
                break
            powers.append(power)
            seen.add(power)
            power = reduce_polynomial(power << 1, modulus)
        if len(powers) == size - 1 and power == 1:
            return modulus, powers
    raise AssertionError((width, "no primitive polynomial found"))


def polynomial_product(a, b):
    result = 0
    while b:
        bit = b & -b
        result ^= a << (bit.bit_length() - 1)
        b ^= bit
    return result


def check_width(m):
    width = m - 1
    period = 1 << (m - 2)
    residue_modulus = 1 << m
    field_modulus, field_powers = list_primitive_powers(width)
    residues = tuple(range(1, residue_modulus, 2))
    powers_of_five = [pow(5, e, residue_modulus) for e in range(period)]
    classes = {word: e for e, word in enumerate(powers_of_five)}
    classes.update({(-word) % residue_modulus: (e + period // 2) % period
                    for e, word in enumerate(powers_of_five)})
    assert sorted(classes) == list(residues)
    table = {field_word: (powers_of_five[e % period] >> width) & 1
             for e, field_word in enumerate(field_powers)}
    nonzero_returns = set()
    rows = set()
    for x in residues:
        row = []
        for y in residues:
            left = field_powers[classes[x]]
            right = field_powers[classes[y]]
            channel = polynomial_product(left, right)
            assert channel.bit_length() <= 2 * width - 1
            received = reduce_polynomial(channel, field_modulus)
            wanted = ((x * y) >> width) & 1
            assert received == field_powers[classes[x] + classes[y]]
            assert table[received] == wanted
            nonzero_returns.add(received)
            row.append(wanted)
        assert len(set(row)) == 2
        rows.add(tuple(row))
    assert len(rows) == period
    assert len(nonzero_returns) == 2 * period - 1
    assert len(nonzero_returns) == len(table)
    return {"m": m, "checked_pairs": len(residues)**2, "polynomial_width": width,
            "reduction_modulus_mask": field_modulus,
            "distinct_target_rows": len(rows), "constant_target_rows": 0,
            "reduced_nonzero_returns": len(nonzero_returns)}


def main():
    rows = [check_width(m) for m in range(3, 11)]
    print(json.dumps({"status": "passed", "cases": rows,
                      "checked_pairs": sum(row["checked_pairs"] for row in rows)},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
