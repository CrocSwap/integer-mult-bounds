#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact 17-dimensional degree-three UT4(F2) quotient.

This quotient provides necessary coefficient conditions only. It is not
faithful on F2[UT4(F2)] and does not admit a formal endpoint on its own.
Prepared for @ToikY with substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path

BASIS = ("", "a", "b", "c", "ab", "ac", "ba", "bc", "cb",
         "aba", "abc", "acb", "bab", "bac", "bcb", "cba", "cbc")
INDEX = {name: index for index, name in enumerate(BASIS)}
LETTERS = {"a": 1, "b": 2, "c": 4}
POSITIONS = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3))
Z = 32
UNIT = 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduced_word(word):
    """Canonical monomial, or None for zero in the defined quotient."""
    require(isinstance(word, str) and all(letter in LETTERS for letter in word),
            "invalid quotient monomial")
    if len(word) >= 4:
        return None
    while "ca" in word:
        word = word.replace("ca", "ac")
    if any(letter * 2 in word for letter in LETTERS):
        return None
    require(word in INDEX, "incomplete quotient basis")
    return word


@lru_cache(maxsize=1)
def basis_products():
    return tuple(tuple(0 if (name := reduced_word(left + right)) is None
                       else 1 << INDEX[name] for right in BASIS) for left in BASIS)


def algebra_mul(left, right):
    require(type(left) is int and type(right) is int
            and 0 <= left < (1 << len(BASIS)) and 0 <= right < (1 << len(BASIS)),
            "quotient coefficient vector outside the 17-bit basis")
    answer = 0
    table = basis_products()
    while left:
        bit = left & -left
        i = bit.bit_length() - 1
        terms = right
        while terms:
            other = terms & -terms
            answer ^= table[i][other.bit_length() - 1]
            terms ^= other
        left ^= bit
    return answer


def paid_group_word(word):
    image = UNIT
    for letter in word:
        require(letter in LETTERS, "invalid group generator")
        image = algebra_mul(image, UNIT | (1 << INDEX[letter]))
    return image


@lru_cache(maxsize=64)
def group_image(code):
    require(type(code) is int and 0 <= code < 64, "group code outside 0..63")
    A, B, C, D, E, F = [(code >> index) & 1 for index in range(6)]
    # Normal form a^A b^B c^C d^(D+AB) e^(E+BC) z^(F+AE).
    powers = (A, B, C, D ^ (A & B), E ^ (B & C), F ^ (A & E))
    words = ("a", "b", "c", "abab", "bcbc", "abcbabcb")
    image = UNIT
    for power, word in zip(powers, words):
        if power:
            image = algebra_mul(image, paid_group_word(word))
    return image


def literal_group_product(left_code, right_code):
    """Independent literal four-by-four multiplication for map checking."""
    require(type(left_code) is int and type(right_code) is int
            and 0 <= left_code < 64 and 0 <= right_code < 64,
            "invalid group multiplication code")
    matrices = []
    for code in (left_code, right_code):
        rows = [[int(i == j) for j in range(4)] for i in range(4)]
        for bit, (i, j) in enumerate(POSITIONS):
            rows[i][j] = (code >> bit) & 1
        matrices.append(rows)
    left, right = matrices
    product = [[sum(left[i][k] * right[k][j] for k in range(4)) & 1
                for j in range(4)] for i in range(4)]
    return sum(product[i][j] << bit for bit, (i, j) in enumerate(POSITIONS))


def matrix_product(left, right):
    rows = []
    for row in left:
        value = 0
        while row:
            bit = row & -row
            value ^= right[bit.bit_length() - 1]
            row ^= bit
        rows.append(value)
    return rows


def validate_matrix(rows, roles):
    require(isinstance(rows, (list, tuple)) and len(rows) == roles
            and all(type(row) is int and 0 <= row < (1 << roles) for row in rows),
            "invalid binary role matrix")


def word_coefficients(word, roles):
    """Evaluate arbitrary admitted paid words; return all named coefficients.

    A word entry is (label,x,y), with nonzero binary vector bit encodings.
    Matrix rows use the same bit convention as the primary checker.
    """
    require(type(roles) is int and roles >= 1, "positive integer role count required")
    result = {"": [1 << i for i in range(roles)]}
    for label, x, y in word:
        require(label in LETTERS and type(x) is int and type(y) is int
                and 0 < x < (1 << roles) and 0 < y < (1 << roles),
                "invalid rank-one paid factor")
        coupling = [y if (x >> i) & 1 else 0 for i in range(roles)]
        updated = {name: rows[:] for name, rows in result.items()}
        for name, rows in result.items():
            next_name = reduced_word(name + label)
            if next_name is None:
                continue
            increment = matrix_product(rows, coupling)
            updated[next_name] = [a ^ b for a, b in zip(
                updated.get(next_name, [0] * roles), increment)]
        result = {name: rows for name, rows in updated.items() if any(rows)}
    return {name: result.get(name, [0] * roles) for name in BASIS}


mixed_coefficients = word_coefficients


def image_coefficients(formal, roles):
    """Evaluate a full formal group-algebra operator in the quotient."""
    require(type(roles) is int and roles >= 1 and isinstance(formal, dict),
            "invalid formal quotient input")
    result = {name: [0] * roles for name in BASIS}
    for code, rows in formal.items():
        validate_matrix(rows, roles)
        image = group_image(code)
        while image:
            bit = image & -image
            name = BASIS[bit.bit_length() - 1]
            result[name] = [a ^ b for a, b in zip(result[name], rows)]
            image ^= bit
    return result


def self_checks():
    names = {reduced_word("".join(word)) for length in range(4)
             for word in itertools.product(LETTERS, repeat=length)} - {None}
    require(names == set(BASIS) and len(BASIS) == 17, "quotient basis coverage")
    units = [1 << index for index in range(len(BASIS))]
    require(all(algebra_mul(UNIT, value) == algebra_mul(value, UNIT) == value
                for value in units), "quotient unit")
    associative = 0
    for left, middle, right in itertools.product(units, repeat=3):
        require(algebra_mul(algebra_mul(left, middle), right)
                == algebra_mul(left, algebra_mul(middle, right)), "quotient associativity")
        associative += 1
    images = [group_image(code) for code in range(64)]
    require(len(set(images)) == 64, "group images collide")
    products = []
    for left, right in itertools.product(range(64), repeat=2):
        code = literal_group_product(left, right)
        require(algebra_mul(images[left], images[right]) == images[code],
                "normal-form map is not a group homomorphism")
        products.append(code)
    central = [BASIS[index] for index in range(len(BASIS)) if (images[Z] >> index) & 1]
    require(central == ["", "abc", "acb", "bac", "cba"], "central cubic coefficients")
    require(algebra_mul(images[Z] ^ UNIT, images[LETTERS["a"]] ^ UNIT) == 0,
            "common formal kernel must be invisible in quotient")
    # Compare direct coefficient expansion with the full-group-image route.
    # Literal fixture: two central targets on two distinct coordinate projectors.
    fixture = [(label, 1 << role, 1 << role) for role in range(2)
               for label in "abcbabcb"]
    expected = {0: [0, 0], Z: [1, 2]}
    require(word_coefficients(fixture, 2) == image_coefficients(expected, 2),
            "central word coefficients do not match its formal target image")
    encoded = json.dumps([list(BASIS), images, products], separators=(",", ":")).encode()
    return {"schema_version": 1, "basis": list(BASIS), "dimension": 17,
            "basis_associativity_products": associative, "group_products": len(products),
            "distinct_group_images": len(set(images)), "central_image": central,
            "group_map_sha256": hashlib.sha256(encoded).hexdigest(),
            "common_kernel_zero": True,
            "scope": "Necessary cubic coefficients; full group-algebra endpoint admission remains separate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="compare every self-check receipt field")
    parser.add_argument("--write", type=Path, help="write a fresh receipt; refuse occupied paths")
    args = parser.parse_args()
    result = self_checks()
    if args.check:
        require(json.loads(args.check.read_text()) == result, "quotient receipt differs")
    if args.write:
        with args.write.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print("PASS_UT4_CUBIC_QUOTIENT dimension=17 products=4096 associative=4913")


if __name__ == "__main__":
    main()
