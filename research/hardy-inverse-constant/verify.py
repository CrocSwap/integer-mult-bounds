#!/usr/bin/env python3
"""Check the rational Hardy constant and derived norm budgets exactly."""

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LIMIT = 2 * 1024 * 1024
RADICES = (3, 4, 5, 7, 8, 9, 11, 16, 25, 27, 32, 49, 64, 71)
CONSTANT = F(22, 7)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    result = [F(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return tuple(result)


def integral(polynomial):
    return sum((F(c, i + 1) for i, c in enumerate(polynomial)), F(0))


def check_certificate(quotient, remainder):
    # x^4(1-x)^4 = (1+x^2)Q(x) - 4.
    numerator = (0, 0, 0, 0, 1, -4, 6, -4, 1)
    product = list(multiply((1, 0, 1), quotient))
    product[0] += remainder
    require(tuple(product) == numerator, "polynomial division certificate")
    require(remainder == -4, "arctangent coefficient must give pi")
    require(integral(quotient) == CONSTANT, "rational integral must be 22/7")
    return {
        "quotient": list(quotient),
        "remainder": remainder,
        "integral_quotient": str(integral(quotient)),
        "integral_positive_numerator": str(integral(numerator)),
    }


def envelope(n, m, delta, constant=CONSTANT):
    require(type(n) is int and type(m) is int, "degrees must be exact integers")
    require(0 <= m <= n <= 128, "finite calibration degree domain")
    require(delta > 0 and constant > 0, "positive gap and coefficient constant")
    return (1 + constant * m) * (1 + constant * n) / delta


def ceil_log2(value):
    require(value > 0, "logarithm argument must be positive")
    numerator, denominator = value.numerator, value.denominator
    exponent = numerator.bit_length() - denominator.bit_length()
    below = (numerator <= denominator << exponent) if exponent >= 0 else (
        numerator << -exponent <= denominator)
    return exponent if below else exponent + 1


def prime_power(r):
    for p in range(2, r + 1):
        if r % p == 0:
            power, exponent = p, 1
            for _ in range(r.bit_length()):
                if power >= r:
                    break
                power *= p
                exponent += 1
            require(power == r, "radix must be a prime power")
            return p, exponent
    raise ValueError("radix must exceed one")


def budget_rows():
    rows = []
    for r in RADICES:
        p, exponent = prime_power(r)
        n, degree, height = r - 1, r - r // p, 2 ** r - 1
        gap_inverse = 2 * r * n * height ** (n * degree - 1)
        old = F(gap_inverse * (1 + 4 * n) ** 2)
        new = gap_inverse * (1 + CONSTANT * n) ** 2
        require(new < old, "strict rational-envelope improvement")
        old_bits, new_bits = ceil_log2(old), ceil_log2(new)
        require(new_bits <= old_bits, "ceiling monotonicity")
        rows.append({"radix": r, "prime": p, "prime_exponent": exponent,
                     "old_bound_bits": old_bits, "new_bound_bits": new_bits,
                     "saved_bound_bits": old_bits - new_bits})
    return rows


def rejection_controls():
    bad_arguments = ((-1, 0, F(1)), (1, 2, F(1)), (1, 0, F(0)),
                     (1, 0, F(-1)), (True, 0, F(1)))
    rejected = 0
    for args in bad_arguments:
        try:
            envelope(*args)
        except ValueError:
            rejected += 1
    for quotient, remainder in (((4, 0, -4, 0, 5, -4, 2), -4),
                                ((4, 0, -4, 0, 5, -4, 1), 4)):
        try:
            check_certificate(quotient, remainder)
        except ValueError:
            rejected += 1
    require(rejected == 7, "all seven malformed controls must be rejected")
    return rejected


def finite_checks():
    count = 0
    for n in range(129):
        for m in range(n + 1):
            old, new = envelope(n, m, F(1), F(4)), envelope(n, m, F(1))
            difference = F(6, 7) * (n + m) + F(300, 49) * n * m
            require(old - new == difference, "symbolic improvement coefficients")
            require((old > new) == (n > 0), "constant-polynomial boundary")
            count += 1
    log_checks = 0
    for numerator in range(1, 65):
        for denominator in range(1, 65):
            value = F(numerator, denominator)
            e = ceil_log2(value)
            require(F(2) ** (e - 1) < value <= F(2) ** e,
                    "exact binary ceiling bracket")
            log_checks += 1
    return {"degree_pairs": count, "logarithm_brackets": log_checks,
            "rejected_controls": rejection_controls()}


def read_bounded(path):
    require(path.is_file() and not path.is_symlink(), "regular source file required")
    require(path.stat().st_size <= LIMIT, "source exceeds two MiB")
    return path.read_bytes()


def digest(path):
    return hashlib.sha256(read_bounded(path)).hexdigest()


def source_receipt():
    manifest = json.loads(read_bounded(PACKAGE / "SOURCES.json"))
    live = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(live) == 1, "exactly one inherited proof input")
    row = live[0]
    require(row["path"] == "research/rational-circle-bound/PROOF.md", "proof path")
    actual = digest(ROOT / row["path"])
    require(actual == row["sha256"], "inherited proof source hash")
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
             "verify.py")
    return {"input": {row["path"]: actual},
            "package": {name: digest(PACKAGE / name) for name in names}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="create a new external receipt")
    args = parser.parse_args()
    certificate = check_certificate((4, 0, -4, 0, 5, -4, 1), -4)
    require(F(22, 7) < 4, "rational constant improves four")
    require(CONSTANT ** 2 / 16 == F(121, 196), "quadratic coefficient ratio")
    receipt = {"status": "PASS_HARDY_INVERSE_CONSTANT", "claim_type": "scoped proof",
               "constant_upper_bound": str(CONSTANT), "certificate": certificate,
               "finite_checks": finite_checks(), "budgets": budget_rows(),
               "sha256": source_receipt()}
    rendered = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.emit is not None:
        output = args.emit.resolve()
        require(not output.is_relative_to(ROOT), "receipt must be outside checkout")
        with output.open("x", encoding="utf-8") as handle:
            written = handle.write(rendered)
            require(written == len(rendered), "complete receipt write")
    print(rendered, end="")


if __name__ == "__main__":
    main()
