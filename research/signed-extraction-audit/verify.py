#!/usr/bin/env python3
"""Exact finite audit of the retained signed block decoder; no kappa claim."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evaluate(coefficients, base):
    value = 0
    for coefficient in reversed(coefficients):
        value = value * base + coefficient
    return value


def pack(coefficients, base):
    """Source's input scan, with a carry in {-1, 0}."""
    digits, carry = [], 0
    for coefficient in coefficients:
        carry, digit = divmod(coefficient + carry, base)
        require(carry in (-1, 0), "input carry outside {-1,0}")
        digits.append(digit)
    return digits, carry


def product_blocks(value, base, length):
    """Sign/magnitude conversion, independently of the coefficient scan."""
    require(abs(value) * 2 < base**length, "signed product width")
    magnitude, digits = abs(value), []
    for _ in range(length):
        magnitude, digit = divmod(magnitude, base)
        digits.append(digit)
    require(magnitude == 0, "magnitude overflow")
    if value < 0:
        carry = 1
        for j, digit in enumerate(digits):
            carry, digits[j] = divmod(base - 1 - digit + carry, base)
    return digits, -int(value < 0)


def extract(digits, base):
    coefficients, carries = [], [0]
    for digit in digits:
        require(0 <= digit < base, "invalid input block")
        total = digit + carries[-1]
        coefficient = total if total < base // 2 else total - base
        carry = (total - coefficient) // base
        require(-base // 2 <= coefficient < base // 2, "centered interval")
        require(carry in (0, 1), "output carry outside {0,1}")
        coefficients.append(coefficient)
        carries.append(carry)
    return coefficients, carries


def check_word(coefficients, base):
    require(all(2 * abs(c) < base for c in coefficients), "strict separation")
    value = evaluate(coefficients, base)
    digits, sign = product_blocks(value, base, len(coefficients))
    packed, input_carry = pack(coefficients, base)
    require((packed, input_carry) == (digits, sign), "input encoding")
    actual, carries = extract(digits, base)
    require(actual == list(coefficients), "coefficient oracle")
    for j in range(len(digits) + 1):
        require(evaluate(coefficients[j:], base) ==
                evaluate(digits[j:], base) + carries[j] +
                sign * base**(len(digits) - j), "residual identity")
    require(carries[-1] + sign == 0, "terminal sign extension")


def convolution(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def check_product(a, b, p):
    r, base = len(a), 1 << (4 * p)
    require(len(b) == r and r >= 2 and r & (r - 1) == 0 and r < 2**p,
            "source length domain")
    require(p >= 2 and all(abs(x) <= 2**p for x in a + b), "source input domain")
    for operand in (a, b):
        digits, sign = pack(operand, base)
        require(evaluate(digits, base) + sign * base**r == evaluate(operand, base),
                "operand packing")
    expected = convolution(a, b) + [0]
    value = evaluate(a, base) * evaluate(b, base)
    require(all(2 * abs(evaluate(v, base)) < base**r for v in (a, b)),
            "source operand width")
    require(4 * abs(value) < base**(2 * r), "source product width")
    require(value == evaluate(expected, base), "Kronecker evaluation")
    require(all(abs(x) <= r * 2**(2 * p) < base // 2 for x in expected),
            "source separation inequality")
    digits, sign = product_blocks(value, base, 2 * r)
    actual, carries = extract(digits, base)
    require(actual == expected and carries[-1] + sign == 0, "product extraction")
    check_word(expected, base)


def negative_controls():
    base = 256
    digits, sign = product_blocks(base - 1, base, 4)
    wanted = [-1, 1, 0, 0]
    no_carry = [d if d < base // 2 else d - base for d in digits]
    require(no_carry != wanted, "omitted extraction carry went undetected")
    wrong_pack = [c % base for c in wanted]
    require(evaluate(wrong_pack, base) != base - 1, "omitted packing carry")
    reversed_result, _ = extract(list(reversed(digits)), base)
    require(reversed_result != wanted, "reversed blocks went undetected")
    negative_digits, negative_sign = product_blocks(-1, base, 4)
    decoded, carries = extract(negative_digits, base)
    require(decoded == [-1, 0, 0, 0] and carries[-1] + negative_sign == 0,
            "negative sign positive control")
    require(carries[-1] + 0 != 0, "missing terminal sign went undetected")
    zero_filled, _ = extract([base - 1, 0, 0, 0], base)
    require(zero_filled != decoded, "incorrect negative high fill")
    # Both the evaluation and terminal carry pass at this forbidden positive tie.
    tie_digits, tie_sign = product_blocks(16, 32, 4)
    tie, tie_carries = extract(tie_digits, 32)
    require(tie == [-16, 1, 0, 0] and tie != [16, 0, 0, 0], "positive tie alias")
    require(evaluate(tie, 32) == 16 and tie_carries[-1] + tie_sign == 0,
            "tie must defeat recomposition and final-carry-only checks")
    return {
        "omitted_extraction_carry": no_carry,
        "omitted_packing_carry_value": evaluate(wrong_pack, base),
        "reversed_blocks": reversed_result,
        "omitted_sign_terminal_residual": carries[-1],
        "zero_filled_negative_high_blocks": zero_filled,
        "undersized_base_positive_tie": {
            "p": 2, "r": 2, "a": [4, 0], "b": [4, 0], "base": 32,
            "true_coefficients": [16, 0, 0, 0], "decoded": tie,
            "recomposition_passes": True, "terminal_carry_passes": True,
        },
    }


def audit():
    source = json.loads((HERE / "SOURCE.json").read_text())
    for path, expected in source["sha256"].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
                "source pin mismatch: " + path)
    word_counts = {}
    for base in (4, 8, 16):
        count = 0
        for length in range(1, 5):
            for word in itertools.product(range(1 - base // 2, base // 2), repeat=length):
                check_word(word, base)
                count += 1
        word_counts[str(base)] = count
    transitions = 0
    for base in (256, 4096, 65536):
        for carry in (0, 1):
            for digit in range(base):
                total = digit + carry
                coefficient = (total + base // 2) % base - base // 2
                next_carry = (total - coefficient) // base
                require(next_carry in (0, 1), "local transition carry")
                # Reach the incoming carry through a real first block.
                actual, states = extract([base - 1 if carry else 0, digit], base)
                require(actual[1] == coefficient and states[2] == next_carry,
                        "independent local transition formula")
                transitions += 1
    vectors = list(itertools.product(range(-4, 5), repeat=2))
    for a in vectors:
        for b in vectors:
            check_product(list(a), list(b), 2)
    rng = random.Random(60)
    sampled = 0
    for p in range(2, 13):
        for ell in range(1, min(p, 6)):
            r = 1 << ell
            for _ in range(4):
                a = [rng.randint(-2**p, 2**p) for _ in range(r)]
                b = [rng.randint(-2**p, 2**p) for _ in range(r)]
                check_product(a, b, p)
                sampled += 1
    return {
        "schema": 1, "base_commit": source["base_commit"], "seed": 60,
        "scope": "Finite signed block arithmetic audit; no full theorem or new kappa",
        "exhaustive_words_by_base": word_counts,
        "word_lengths": [1, 2, 3, 4],
        "local_transitions": transitions,
        "transition_bases": [256, 4096, 65536],
        "exhaustive_p2_r2_products": len(vectors)**2,
        "sampled_products": sampled,
        "sample_domain": "p=2..12; ell=1..min(p-1,5); r=2^ell; four pairs per cell; integer components in [-2^p,2^p]",
        "stopping_rule": "Complete the declared finite domains and all six negative controls",
        "negative_controls": negative_controls(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="compare against an exact JSON receipt")
    parser.add_argument("--json", action="store_true", help="print the exact receipt")
    args = parser.parse_args()
    result = audit()
    if args.check:
        require(json.loads(args.check.read_text()) == result, "receipt mismatch")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PASS_SIGNED_EXTRACTION: {sum(result['exhaustive_words_by_base'].values())} words; "
              f"{result['local_transitions']} transitions; "
              f"{result['exhaustive_p2_r2_products']} exhaustive products; "
              f"{result['sampled_products']} sampled products; "
              f"{len(result['negative_controls'])} negative controls")


if __name__ == "__main__":
    main()
