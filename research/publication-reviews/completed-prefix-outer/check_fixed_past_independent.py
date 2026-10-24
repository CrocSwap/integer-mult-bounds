"""Check the finite algebra used in the conditional fixed-past proof."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


ZERO = (F(0), F(0))
ONE = (F(1), F(0))
I = (F(0), F(1))
PROOF = "frozen/lanes/temporal-reuse/FIXED-PAST-OUTER-CLOSURE.md"
PROOF_PIN = "30bc7581255af6cd571a410f5e4c76b51eaa2f4956f9343a0ab133fa0d1e52ff"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def scale(a, matrix):
    return [[mul(a, x) for x in row] for row in matrix]


def identity(n):
    return [[ONE if j == k else ZERO for k in range(n)] for j in range(n)]


def product(a, b):
    return [[sum_gaussian(mul(x, y) for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def sum_gaussian(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def power(a, exponent):
    result = identity(len(a))
    for _ in range(exponent):
        result = product(a, result)
    return result


def tensor(a, b):
    return [[mul(aij, bkl) for aij in ar for bkl in br]
            for ar in a for br in b]


def tensor_power(a, exponent):
    result = [[ONE]]
    for _ in range(exponent):
        result = tensor(result, a)
    return result


def norm_square(value):
    return value[0] ** 2 + value[1] ** 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(sha256((args.package / PROOF).read_bytes()).hexdigest() == PROOF_PIN,
         "The fixed-past proof pin differs")
    h0 = scale((F(1, 2), F(0)), [[ONE, ONE], [ONE, (-F(1), F(0))]])
    s = [[ONE, ZERO], [ZERO, I]]
    c = [[(F(1, 2), F(1, 2)), (F(1, 2), -F(1, 2))],
         [(F(1, 2), -F(1, 2)), (F(1, 2), F(1, 2))]]
    h = product(s, product(c, s))
    need(h == scale((F(1), F(1)), h0), "The conversion identity differs")
    need(power(h, 2) == scale(I, identity(2)), "The square identity differs")
    need(power(h, 8) == identity(2), "The period identity differs")
    tensor_cases = 0
    for width in range(6):
        hp = tensor_power(h, width)
        for exponent in range(-9, 10):
            actual = power(hp, exponent % 8)
            need(actual == tensor_power(power(h, exponent % 8), width),
                 "The tensor power identity differs")
            for row in actual:
                values = [norm_square(x) for x in row if x != ZERO]
                if exponent % 2:
                    need(len(values) == 2 ** width and set(values) == {F(1, 2 ** width)},
                         "The odd-power row entries differ")
                    need(len(values) ** 2 * values[0] == 2 ** width,
                         "The squared row sum differs")
                else:
                    need(values == [F(1)], "The even-power row differs")
            tensor_cases += 1
    propagation_cases = 0
    for width in range(1, 4):
        hp = tensor_power(h, width)
        for count in range(1, 5):
            active = [product(s if index % 2 else identity(2), h0)
                      for index in range(count)]
            rounds = [tensor(hp, a) for a in active]
            decoder = tensor(power(hp, (-count) % 8), identity(2))
            for injected in range(1, count + 1):
                suffix = identity(2 ** (width + 1))
                active_suffix = identity(2)
                for index in range(injected, count):
                    suffix = product(rounds[index], suffix)
                    active_suffix = product(active[index], active_suffix)
                expected = tensor(power(hp, (-injected) % 8), active_suffix)
                need(product(decoder, suffix) == expected,
                     "The decoded error propagator differs")
                propagation_cases += 1
    controls = {
        "normalizing_the_past_to_H0_breaks_h_squared_iI":
            power(h0, 2) != scale(I, identity(2)),
        "a_current_bit_code_does_not_commute_with_its_twiddle":
            product(h, s) != product(s, h),
        "omitting_the_decoder_changes_the_error_propagator":
            h != power(h, 7),
        "an_odd_past_power_is_not_an_infinity_norm_contraction":
            len(h[0]) ** 2 * norm_square(h[0][0]) > 1,
    }
    need(all(controls.values()), "A negative control failed")
    receipt = {
        "status": "PASS_FIXED_PAST_INDEPENDENT_BOUNDED_CHECK",
        "proof_sha256": PROOF_PIN,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "arithmetic": "Exact rational pairs for Gaussian numbers; standard library only",
        "tensor_widths": [0, 1, 2, 3, 4, 5],
        "power_range": [-9, 9],
        "tensor_power_cases": tensor_cases,
        "decoded_error_propagator_cases": propagation_cases,
        "negative_controls": controls,
        "native_supplier_verified": False,
        "recursive_invoice_verified": False,
        "scope": "Finite exact checks of the identities in the written conditional proof. The general bound uses the written tensor and commutation arguments.",
    }
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
