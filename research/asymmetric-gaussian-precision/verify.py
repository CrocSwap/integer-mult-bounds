#!/usr/bin/env python3
"""Exact finite corroboration of the asymmetric normalized-channel proof."""

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

type Complex = tuple[F, F]

ZERO: Complex = (F(0), F(0))
ROOTS: tuple[Complex, ...] = ((F(1), F(0)), (F(0), F(1)),
                              (F(-1), F(0)), (F(0), F(-1)))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def power(exponent: int) -> F:
    require(type(exponent) is int and 0 <= exponent <= 2048, "exponent domain")
    return F(1, 1 << exponent)


def allocation(b: int, size: int, gamma: int) -> tuple[int, int, int, int]:
    require(all(type(x) is int for x in (b, size, gamma)), "integer parameters")
    require(1 <= b <= 128 and 0 <= gamma <= 128, "finite verifier domain")
    require(1 <= size < 1 << b, "source-size guard")
    height = (size - 1).bit_length()
    accuracy = 2 * height + 2 * b + 7
    return accuracy, accuracy + 3 * gamma + 7, accuracy + 2, accuracy + 2 * gamma + 2


def error_bound(lam: F, left: F, right: F, product: F, opposite: F) -> F:
    require(0 < lam <= 1, "normalizer domain")
    require(min(left, right, product, opposite) >= 0, "nonnegative errors")
    return lam * (lam * (left + right) / 4 + left * right + product) + opposite


def add(x: Complex, y: Complex) -> Complex:
    return x[0] + y[0], x[1] + y[1]


def mul(x: Complex, y: Complex) -> Complex:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def scale(x: Complex, factor: F) -> Complex:
    return x[0] * factor, x[1] * factor


def norm1(x: Complex) -> F:
    return abs(x[0]) + abs(x[1])


def transform(data: tuple[Complex, ...], lam: F, sign: int) -> tuple[Complex, ...]:
    n = len(data)
    require(n in (1, 2, 4) and sign in (-1, 1), "finite transform domain")
    output = []
    for row in range(n):
        total = ZERO
        for column in range(n):
            root = ROOTS[(sign * row * column * (4 // n)) % 4]
            total = add(total, mul(root, data[column]))
        output.append(scale(total, lam / n))
    return tuple(output)


def convolution(left: tuple[Complex, ...], right: tuple[Complex, ...]) -> tuple[Complex, ...]:
    n = len(left)
    require(n == len(right) and n in (1, 2, 4), "finite convolution domain")
    output = []
    for row in range(n):
        total = ZERO
        for column in range(n):
            total = add(total, mul(left[column], right[(row - column) % n]))
        output.append(total)
    return tuple(output)


def truncate(value: F, bits: int) -> F:
    require(type(bits) is int and 0 <= bits <= 2048, "grid domain")
    numerator = abs(value.numerator) * (1 << bits) // value.denominator
    if value < 0:
        numerator = -numerator
    return F(numerator, 1 << bits)


def budget_cases() -> int:
    count = 0
    for b in range(1, 17):
        sizes = sorted({1, (1 << b) - 1, (1 << (b - 1)) + 1} - {1 << b})
        for size in sizes:
            for gamma in (0, 1, 2, 4, 8, 31, 127):
                a, q, forward, opposite = allocation(b, size, gamma)
                eps, lam = power(a), power(gamma)
                eta_f, eta_o = lam * eps, lam**3 * eps
                delta_cap = 2 * power(q)
                bound = error_bound(lam, eta_f, eta_f, delta_cap, eta_o)
                require(bound / lam**3 < 2 * eps, "restored error budget")
                recovery = size**2 * (1 << (2 * b + 4 + 3 * gamma))
                require(bound * recovery < F(1, 4), "integer recovery margin")
                require(lam * (F(1, 4) + eps) < F(1, 2), "forward radius")
                product_radius = (lam * (F(1, 4) + eps))**2 + delta_cap
                require(product_radius < F(1, 4), "opposite input radius")
                require(lam * product_radius + eta_o < F(1, 2), "return radius")
                require(opposite - forward == 2 * gamma, "requested bit improvement")
                require(3 * power(forward + gamma) < eta_f, "forward stage sum")
                require(3 * power(opposite + gamma) < eta_o, "opposite stage sum")
                require(power(a + 3 * gamma) / eta_f == power(2 * gamma), "gain factor")
                count += 1
    return count


def one_fixture(n: int, gamma: int, seed: int, direction: int) -> None:
    b = n.bit_length()
    a, q, _, _ = allocation(b, n, gamma)
    lam, eps = power(gamma), power(a)
    left = tuple(scale(ROOTS[(seed + j) % 4], F(1 + (seed + j) % 2, 8))
                 for j in range(n))
    right = tuple(scale(ROOTS[(seed // 4 + 3 * j) % 4], F(1 + (seed + 2 * j) % 2, 8))
                  for j in range(n))
    exact_left, exact_right = transform(left, lam, -1), transform(right, lam, -1)
    actual_left = tuple(add(x, scale(ROOTS[(direction + j) % 4], lam * eps))
                        for j, x in enumerate(exact_left))
    actual_right = tuple(add(x, scale(ROOTS[(direction + 2 * j) % 4], lam * eps))
                         for j, x in enumerate(exact_right))
    product = tuple(mul(x, y) for x, y in zip(actual_left, actual_right, strict=True))
    rounded = tuple((truncate(x[0], q), truncate(x[1], q)) for x in product)
    actual = tuple(add(x, scale(ROOTS[(direction + 3 * j) % 4], lam**3 * eps))
                   for j, x in enumerate(transform(rounded, lam, 1)))
    direct = tuple(scale(x, lam**3 / n**2) for x in convolution(left, right))
    exact_product = tuple(mul(x, y) for x, y in zip(exact_left, exact_right, strict=True))
    require(transform(exact_product, lam, 1) == direct, "independent convolution identity")
    for first, second, raw, rounded_value, value, target in zip(
            actual_left, actual_right, product, rounded, actual, direct, strict=True):
        require(norm1(first) < F(1, 2) and norm1(second) < F(1, 2), "fixture forward guard")
        require(norm1(add(rounded_value, scale(raw, F(-1)))) < 2 * power(q), "inward grid error")
        require(norm1(rounded_value) < F(1, 4), "fixture opposite guard")
        require(norm1(value) < F(1, 2), "fixture return guard")
        defect = norm1(add(value, scale(target, F(-1))))
        bound = error_bound(lam, lam * eps, lam * eps, 2 * power(q), lam**3 * eps)
        require(defect <= bound, "fixture error polynomial")
        recovery = n**2 * (1 << (2 * b + 4 + 3 * gamma))
        require(defect * recovery < F(1, 4), "fixture recovery error")


def fixture_cases() -> int:
    count = 0
    for n in (1, 2, 4):
        for gamma in (0, 1, 2, 7):
            for seed in range(24):
                for direction in range(4):
                    one_fixture(n, gamma, seed, direction)
                    count += 1
    return count


def sharp_envelope_cases() -> int:
    count = 0
    for gamma in (0, 1, 3):
        lam = power(gamma)
        for left, right in ((F(1, 1024), F(1, 2048)), (F(0), F(1, 4096))):
            product, opposite = F(1, 8192), F(1, 16384)
            actual = lam * ((lam / 4 + left) * (lam / 4 + right) + product) + opposite
            ideal = lam**3 / 16
            require(actual - ideal == error_bound(lam, left, right, product, opposite),
                    "scalar equality in the abstract defect model")
            count += 1
    return count


def controls() -> int:
    count = 0
    for args in ((0, 1, 0), (1, 0, 0), (1, 2, 0), (2, 1, -1),
                 (129, 1, 0), (1, 1, 129), (True, 1, 0), (2, F(1), 0)):
        try:
            allocation(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid allocation admitted")
    a, _, _, _ = allocation(1, 1, 1)
    lam, eps = power(1), power(a)
    loose_opposite_error = lam * eps
    recovery = 1 << (2 + 4 + 3)
    require(loose_opposite_error * recovery == F(1, 2), "opposite-loosening counterexample")
    require(loose_opposite_error > lam**3 * eps, "counterexample violates retained opposite budget")
    count += 1
    ideal_channel = lam**3 / 16
    require(ideal_channel * (1 << 9) == 4, "three-normalizer recovery control")
    require(ideal_channel * (1 << 6) == F(1, 2), "omitted-normalizer control")
    count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write generated JSON outside the package")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(package), "receipt must remain outside package")
    counts = {"budget_cases": budget_cases(), "convolution_fixtures": fixture_cases(),
              "abstract_envelope_equalities": sharp_envelope_cases(), "controls": controls()}
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in files:
        with (package / name).open("rb") as handle:
            data = handle.read((1 << 20) + 1)
        require(len(data) <= 1 << 20, "package file size limit")
        hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {"status": "PASS_ASYMMETRIC_GAUSSIAN_PRECISION", "counts": counts,
               "python": sys.version.split()[0], "source_sha256": hashes,
               "claim_type": "scoped written proof with finite exact corroboration"}
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        written = args.receipt.write_text(encoded)
        require(written == len(encoded), "complete receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
