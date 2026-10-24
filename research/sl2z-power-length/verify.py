#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md; standard library, no Git/network."""

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path


IDENTITY = (1, 0, 0, 1)
BASE = (5, 2, 2, 1)
POWER_LIMIT = 64
COEFFICIENTS = (-3, -2, -1, 1, 2, 3)
SHORT_LIMIT = 5
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (a * e + b * g, a * f + b * h,
            c * e + d * g, c * f + d * h)


def letter(family, coefficient):
    require(family in ("X", "Y"), "unknown letter family")
    require(isinstance(coefficient, (int, Fraction)), "nonrational coefficient")
    require(coefficient != 0, "zero coefficient is not a paid letter")
    if family == "X":
        return (1, coefficient, 0, 1)
    return (1, 0, coefficient, 1)


def word_matrix(word):
    require(len(word) <= 2 * POWER_LIMIT, "word exceeds finite-check bound")
    result = IDENTITY
    for family, coefficient in word:
        result = multiply(result, letter(family, coefficient))
    return result


def pell_values(last_index):
    require(1 <= last_index <= 2 * POWER_LIMIT + 1, "Pell index out of range")
    values = [0, 1]
    for index in range(2, last_index + 1):
        values.append(2 * values[index - 1] + values[index - 2])
    return values


def nearest_chain(a, b):
    require(isinstance(a, int) and isinstance(b, int), "noninteger chain input")
    require(a != 0 and b != 0, "chain starts with zero")
    require(max(abs(a).bit_length(), abs(b).bit_length()) <= 1024,
            "chain input exceeds 1024 bits")
    initial = (a, b)
    quotients, remainders = [], []
    # Each noninitial remainder at least halves the preceding divisor.
    for _ in range(abs(b).bit_length() + 2):
        floor = a // b
        quotient = floor
        if abs(a - (floor + 1) * b) < abs(a - floor * b):
            quotient += 1
        remainder = a - quotient * b
        quotients.append(quotient)
        remainders.append(remainder)
        if remainder == 0:
            return {"initial": list(initial), "quotients": quotients,
                    "remainders": remainders}
        a, b = b, remainder
    raise ValueError("least-remainder iteration bound exhausted")


def validate_chain(chain):
    a, b = chain["initial"]
    quotients, remainders = chain["quotients"], chain["remainders"]
    require(0 < len(quotients) == len(remainders) <= 1026, "bad trace lengths")
    for index, (quotient, remainder) in enumerate(zip(quotients, remainders)):
        require(b != 0, "division after a zero remainder")
        require(a == quotient * b + remainder, "division identity fails")
        require(2 * abs(remainder) <= abs(b), "not a least remainder")
        require(remainder != 0 or index == len(quotients) - 1,
                "trace continues past its first zero")
        a, b = b, remainder
    require(b == 0 and abs(a) == 1, "trace does not terminate at gcd one")


def removal_chain(word, matrix):
    a, c = matrix[0], matrix[2]
    first = word[0][0]
    remainders = []
    for index, (family, coefficient) in enumerate(word):
        expected = first if index % 2 == 0 else ("Y" if first == "X" else "X")
        require(family == expected, "word is not alternating")
        if family == "X":
            a -= coefficient * c
            remainders.append(a)
        else:
            c -= coefficient * a
            remainders.append(c)
        if a == 0 or c == 0:
            return remainders
    raise ValueError("word did not produce a zero coordinate")


def check_power(k, matrix, pell):
    expected = (pell[2 * k + 1], pell[2 * k], pell[2 * k], pell[2 * k - 1])
    require(matrix == expected, "Pell matrix identity fails")
    a, b, c, d = matrix
    require(a * d - b * c == 1, "determinant is not one")
    direct, reverse = nearest_chain(a, c), nearest_chain(c, a)
    validate_chain(direct)
    validate_chain(reverse)
    require(direct["quotients"] == [2] * (2 * k), "direct length is not 2k")
    require(reverse["quotients"] == [0] + [2] * (2 * k),
            "reverse length is not 2k+1")
    word = tuple((family, 2) for _ in range(k) for family in ("X", "Y"))
    require(word_matrix(word) == matrix, "attaining word misses full endpoint")
    require(removal_chain(word, matrix) == direct["remainders"],
            "literal inverse removals disagree with division trace")
    return {"k": k, "matrix": list(matrix), "minimum": 2 * k,
            "direct_divisions": len(direct["quotients"]),
            "reverse_divisions": len(reverse["quotients"])}


def all_powers():
    pell = pell_values(2 * POWER_LIMIT + 1)
    matrix, records = IDENTITY, []
    for k in range(1, POWER_LIMIT + 1):
        matrix = multiply(matrix, BASE)
        records.append(check_power(k, matrix, pell))
    return records


def short_word_census():
    alphabet = tuple((family, coefficient) for family in ("X", "Y")
                     for coefficient in COEFFICIENTS)
    matrices = tuple(letter(*entry) for entry in alphabet)
    target = multiply(multiply(BASE, BASE), BASE)
    counts, hits = [], []
    for length in range(SHORT_LIMIT + 1):
        count = 0
        for indices in product(range(len(alphabet)), repeat=length):
            matrix = IDENTITY
            for index in indices:
                matrix = multiply(matrix, matrices[index])
            count += 1
            if matrix == target:
                hits.append(list(indices))
        require(count == len(alphabet) ** length, "incomplete word layer")
        counts.append(count)
    require(not hits, "bounded short word reaches B cubed")
    return {"coefficients": list(COEFFICIENTS), "length_limit": SHORT_LIMIT,
            "words_by_length": counts, "words": sum(counts), "hits": hits}


def expect_rejection(case, value):
    try:
        if case == "chain":
            validate_chain(value)
        elif case == "power":
            check_power(3, value, pell_values(7))
        elif case == "letter":
            letter(*value)
        elif case == "integer":
            require(all(isinstance(t, int) for _, t in value),
                    "rational word is outside the integer alphabet")
        else:
            raise RuntimeError("unknown rejection control")
    except ValueError:
        return 1
    raise ValueError("damaged control was accepted: " + case)


def controls():
    target = multiply(multiply(BASE, BASE), BASE)
    chain = nearest_chain(target[0], target[2])
    bad_quotient = json.loads(json.dumps(chain))
    bad_quotient["quotients"][0] += 1
    bad_remainder = json.loads(json.dumps(chain))
    bad_remainder["remainders"][-1] = 1
    count = expect_rejection("chain", bad_quotient)
    count += expect_rejection("chain", bad_remainder)
    count += expect_rejection("power", (target[0] + 1,) + target[1:])
    count += expect_rejection("letter", ("Z", 2))
    count += expect_rejection("letter", ("X", 0))
    rational = (("X", Fraction(12, 5)), ("Y", 70), ("X", Fraction(2, 5)))
    require(word_matrix(rational) == target, "rational boundary word fails")
    count += expect_rejection("integer", rational)
    word = tuple((family, 2) for _ in range(3) for family in ("X", "Y"))
    for omitted in range(len(word)):
        require(word_matrix(word[:omitted] + word[omitted + 1:]) != target,
                "omitted call retained the endpoint")
        count += 1
    require(tuple(entry % 2 for entry in target) == IDENTITY,
            "mod-two quotient control changed")
    require(sum(abs(t) for _, t in word) == 12, "unit-price boundary changed")
    return {"rejections": count, "rational_three_letter_endpoint": list(target),
            "mod_two_endpoint": list(IDENTITY), "unit_expansion_letters": 12}


def source_hashes():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    return {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in names}


def make_result():
    powers = all_powers()
    census = short_word_census()
    checked_controls = controls()
    return {"schema_version": 1, "claim_type": "scoped-proof",
            "theorem": "lambda(B^k)=2k for all integers k>=1",
            "finite_powers": powers, "bounded_word_census": census,
            "controls": checked_controls, "source_sha256": source_hashes()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", type=Path, help="write a fresh generated result")
    mode.add_argument("--certificate", type=Path, help="compare another result")
    args = parser.parse_args()
    result = make_result()
    if args.write:
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with args.write.open("x", encoding="utf-8") as output:
            require(output.write(payload) == len(payload), "short certificate write")
    else:
        path = args.certificate or PACKAGE / "RESULT.json"
        require(path.stat().st_size <= 1_000_000, "certificate exceeds 1 MB")
        recorded = json.loads(path.read_text(encoding="utf-8"))
        require(recorded == result, "certificate differs from exact regeneration")
    print("PASS_SL2Z_POWER_LENGTH powers=64 minimum=2k "
          f"short_words={result['bounded_word_census']['words']} "
          f"hits=0 rejection_controls={result['controls']['rejections']} "
          "classical_division_chain_theorem=cited no_new_kappa")


if __name__ == "__main__":
    main()
