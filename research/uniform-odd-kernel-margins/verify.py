#!/usr/bin/env python3
"""Exact finite corroboration of the uniform odd-kernel tariff theorem.

Produced by Nick Petalas. Apache-2.0.
The all-parameter result rests on PROOF.md, not this finite enumeration.
"""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(q, j):
    require(type(q) is int and 0 < q < 2**2048 and q % 2 == 1,
            "q must be a positive odd integer below 2^2048")
    require(type(j) is int and 0 <= j <= 1024,
            "j must be an integer in 0..1024")


def coefficient_charge(value):
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def literal_word(k):
    require(type(k) is int and k != 0 and abs(k).bit_length() <= 4096,
            "k must be a nonzero integer of at most 4096 bits")
    a = Fraction(k, 4)
    coefficients = (a, 1 + a, -a, -a, -1 / a, 1 / a - 1)
    return 20 + sum(coefficient_charge(c) for c in coefficients)


def formula_word(q, j):
    parameters(q, j)
    b = q.bit_length()
    if j == 0:
        return 35 + 5*b + (q+4).bit_length() + abs(q-4).bit_length()
    if j == 1:
        return 30 + 5*b + (q+2).bit_length() + abs(q-2).bit_length()
    if j == 2:
        return 25 + 5*b + (q+1).bit_length() + (q-1).bit_length()
    if q == 1:
        return 7*j + 17
    return 7*j + 7*b + 11


def word_floor(j):
    return (4, 6, 8)[min(j, 2)]


def fused_floor(j):
    return (14, 20, 24)[min(j, 2)]


def baseline_floor(j):
    return (16, 24, 32)[min(j, 2)]


def check_pair(q, j):
    parameters(q, j)
    require(j < 1024, "paired check needs one following exponent")
    actual = literal_word(q << j)
    predicted = formula_word(q, j)
    require(actual == predicted, f"word formula at q={q}, j={j}")
    require(literal_word(-(q << j)) == actual, "sign symmetry")
    require(literal_word(q << (j+1)) == formula_word(q, j+1),
            "next-exponent formula")
    delta = actual - literal_word(1 << j)
    next_delta = formula_word(q, j+1) - formula_word(1, j+1)
    values = (delta, 2*delta + next_delta, 4*delta)
    floors = (word_floor(j), fused_floor(j), baseline_floor(j))
    for value, floor in zip(values, floors, strict=True):
        require(value >= floor, "uniform lower margin")
        require((value == floor) == (q == 3), "unique minimizer")
    return values


def dense_cases():
    count = 0
    minima = [None, None, None]
    for q in range(3, 1024, 2):
        for j in range(40):
            values = check_pair(q, j)
            for i in range(3):
                minima[i] = values[i] if minima[i] is None else min(minima[i], values[i])
            count += 1
    require(minima == [4, 14, 16], "global sharp finite witnesses")
    return {"pairs": count, "minimum_word_fused_baseline": minima}


def boundary_cases():
    count = 0
    for b in (2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
        kernels = sorted({q for q in (2**b-5, 2**b-3, 2**b-1,
                                     2**b+1, 2**b+3, 2**b+5)
                          if q >= 3 and q % 2 == 1})
        for q in kernels:
            for j in (0, 1, 2, 3, 4, 33, 64, 127, 511, 1023):
                check_pair(q, j)
                count += 1
    for j in range(1024):
        require(literal_word(1 << j) == formula_word(1, j), "dyadic boundary")
        check_pair(3, j)
    return {"power_boundary_pairs": count, "sharp_kernel_exponents": 1024,
            "dyadic_exponents": 1024}


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("accepted invalid input: " + label)


def controls():
    bad = ((0, 0), (-3, 0), (2, 0), (True, 0), (3.0, 0),
           (3, -1), (3, 1025), (3, True), (3, 0.5), (2**2048+1, 0))
    labels = [reject(lambda q=q, j=j: formula_word(q, j), f"parameters-{i}")
              for i, (q, j) in enumerate(bad)]
    for i, k in enumerate((0, True, Fraction(3, 2), 2**4096)):
        labels.append(reject(lambda k=k: literal_word(k), f"word-{i}"))
    require(coefficient_charge(Fraction(0)) == 1, "zero coefficient costs one")
    require(literal_word(4) - 1 != formula_word(1, 2), "reject omitted zero coefficient")
    require(literal_word(3) - literal_word(1) == 4, "j=0 sharpness")
    require(literal_word(6) - literal_word(2) == 6, "j=1 sharpness")
    require(literal_word(12) - literal_word(4) == 8, "j=2 sharpness")
    require(formula_word(3, 3) - formula_word(1, 3) == 8, "j>=3 sharpness")
    labels.extend(("omit-zero-coefficient", "raise-j0-word-floor",
                   "raise-j1-word-floor", "raise-j2-word-floor",
                   "raise-large-j-word-floor"))
    delta = literal_word(3) - literal_word(1)
    next_delta = literal_word(6) - literal_word(2)
    require(2*delta + next_delta < 15, "reject fused floor 15")
    require(4*delta < 17, "reject baseline floor 17")
    labels.extend(("raise-global-fused-floor", "raise-global-baseline-floor"))
    return labels


def receipt(results):
    here = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = here / name
        require(path.stat().st_size <= 1024*1024, "package file exceeds 1 MiB")
        data = path.read_bytes()
        hashes[name] = sha256(data).hexdigest()
    return {"status": "PASS_UNIFORM_ODD_KERNEL_MARGINS",
            "claim_type": "scoped proof with finite corroboration",
            "python": sys.version, "results": results, "sha256": hashes}


def main():
    results = {"dense": dense_cases(), "boundaries": boundary_cases(),
               "controls": controls()}
    print(json.dumps(receipt(results), sort_keys=True))
    print("PASS_UNIFORM_ODD_KERNEL_MARGINS")


if __name__ == "__main__":
    main()
