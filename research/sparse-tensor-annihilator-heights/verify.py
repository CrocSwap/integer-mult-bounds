#!/usr/bin/env python3
"""Exact finite corroboration of the arbitrary-support valuation theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb, lcm
from pathlib import Path


Q = tuple[Fraction, Fraction]
Z = tuple[int, int]
ZERO: Q = (Fraction(0), Fraction(0))
ONE: Q = (Fraction(1), Fraction(0))
ALPHA: Q = (Fraction(3, 5), Fraction(4, 5))
PI: Z = (2, 1)
RHO: Z = (2, -1)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def add(a: Q, b: Q) -> Q:
    return a[0] + b[0], a[1] + b[1]


def neg(a: Q) -> Q:
    return -a[0], -a[1]


def mul(a: Q, b: Q) -> Q:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def div(a: Q, b: Q) -> Q:
    norm = b[0] ** 2 + b[1] ** 2
    require(norm != 0, "division by zero")
    return (a[0] * b[0] + a[1] * b[1]) / norm, (a[1] * b[0] - a[0] * b[1]) / norm


def power(a: Q, exponent: int) -> Q:
    require(type(exponent) is int and abs(exponent) <= 1024, "power bound")
    if exponent < 0:
        a = div(ONE, a)
    result = ONE
    for _ in range(abs(exponent)):
        result = mul(result, a)
    return result


def zmul(a: Z, b: Z) -> Z:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def norm(a: Z) -> int:
    return a[0] ** 2 + a[1] ** 2


def exact_div(a: Z, b: Z) -> Z:
    d = norm(b)
    require(d > 0, "integer division by zero")
    r, s = a[0] * b[0] + a[1] * b[1], a[1] * b[0] - a[0] * b[1]
    require(r % d == 0 and s % d == 0, "inexact Gaussian division")
    return r // d, s // d


def gcd_pair(a: Z, b: Z) -> Z:
    # Nearest-coordinate division halves the positive remainder norm.
    for _ in range(norm(b).bit_length() + 2):
        if b == (0, 0):
            return a
        d = norm(b)
        r, s = a[0] * b[0] + a[1] * b[1], a[1] * b[0] - a[0] * b[1]
        quotient = ((2 * r + d) // (2 * d), (2 * s + d) // (2 * d))
        product = zmul(quotient, b)
        remainder = a[0] - product[0], a[1] - product[1]
        require(2 * norm(remainder) <= d, "Euclidean descent")
        a, b = b, remainder
    raise ValueError("Euclidean step budget exhausted")


def content(coefficients: tuple[Z, ...]) -> Z:
    require(1 <= len(coefficients) <= 10, "content size")
    result = (0, 0)
    for value in coefficients:
        result = gcd_pair(result, value)
    return result


def primitive(values: tuple[Q, ...]) -> tuple[Z, ...]:
    require(3 <= len(values) <= 10, "primitive size")
    denominator = 1
    for a, b in values:
        denominator = lcm(denominator, a.denominator, b.denominator)
    cleared = tuple((a * denominator, b * denominator) for a, b in values)
    require(all(a.denominator == b.denominator == 1 for a, b in cleared), "denominator clearing")
    integral = tuple((a.numerator, b.numerator) for a, b in cleared)
    divisor = content(integral)
    require(divisor != (0, 0), "zero relation")
    reduced = tuple(exact_div(value, divisor) for value in integral)
    units = ((1, 0), (0, 1), (-1, 0), (0, -1))
    return max(tuple(zmul(value, unit) for value in reduced) for unit in units)


def support(exponents: tuple[int, ...]) -> tuple[int, ...]:
    require(type(exponents) is tuple and 3 <= len(exponents) <= 10, "support size")
    require(all(type(m) is int and abs(m) <= 128 for m in exponents), "integer exponent")
    require(all(a < b for a, b in zip(exponents, exponents[1:])), "increasing support")
    require(exponents[-1] - exponents[0] <= 64, "support span")
    return exponents


def nodes(exponents: tuple[int, ...]) -> tuple[Q, ...]:
    return tuple(power(ALPHA, m) for m in support(exponents))


def cofactors(points: tuple[Q, ...]) -> tuple[Q, ...]:
    require(3 <= len(points) <= 10, "cofactor size")
    result = []
    for omit in range(len(points)):
        value = ONE
        for a, b in combinations(range(len(points)), 2):
            if a != omit and b != omit:
                value = mul(value, add(points[b], neg(points[a])))
        result.append(neg(value) if omit % 2 else value)
    return tuple(result)


def independent_kernel(points: tuple[Q, ...]) -> tuple[Q, ...]:
    """Solve the literal n by n system with the last coefficient fixed to 1."""
    require(3 <= len(points) <= 10, "kernel size")
    n = len(points) - 1
    matrix = [[power(x, k) for x in points[:-1]] + [neg(power(points[-1], k))]
              for k in range(n)]
    for column in range(n):
        pivot = next((r for r in range(column, n) if matrix[r][column] != ZERO), None)
        require(pivot is not None, "singular Vandermonde")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [div(value, scale) for value in matrix[column]]
        for row in range(n):
            if row != column:
                scale = matrix[row][column]
                matrix[row] = [add(a, neg(mul(scale, b)))
                               for a, b in zip(matrix[row], matrix[column])]
    return tuple(matrix[row][-1] for row in range(n)) + (ONE,)


def valuation(value: Z, prime: Z) -> int:
    require(value != (0, 0) and prime in (PI, RHO), "valuation domain")
    bound = norm(value).bit_length() + 1
    for exponent in range(bound):
        r = value[0] * prime[0] + value[1] * prime[1]
        s = value[1] * prime[0] - value[0] * prime[1]
        if r % 5 or s % 5:
            return exponent
        value = r // 5, s // 5
    raise ValueError("valuation step budget exhausted")


def profile(exponents: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    support(exponents)
    n = len(exponents) - 1
    gaps = tuple(b - a for a, b in zip(exponents, exponents[1:]))
    return tuple((sum((n - 1 - s) * gaps[s] for s in range(j, n)),
                  sum(s * gaps[s] for s in range(j))) for j in range(n + 1))


def evaluate(coefficients: tuple[Z, ...], points: tuple[Q, ...], k: int) -> Q:
    require(len(coefficients) == len(points) <= 10 and 0 <= k <= 9, "evaluation shape")
    total = ZERO
    for coefficient, point in zip(coefficients, points):
        scalar = Fraction(coefficient[0]), Fraction(coefficient[1])
        total = add(total, mul(scalar, power(point, k)))
    return total


def validate(exponents: tuple[int, ...], coefficients: tuple[Z, ...]) -> int:
    support(exponents)
    require(len(coefficients) == len(exponents), "coefficient shape")
    require(all(type(a) is int and type(b) is int for a, b in coefficients), "integral coefficient")
    require(all(c != (0, 0) for c in coefficients), "zero coefficient")
    require(norm(content(coefficients)) == 1, "nonprimitive relation")
    expected = profile(exponents)
    points = nodes(exponents)
    for k in range(len(exponents) - 1):
        require(evaluate(coefficients, points, k) == ZERO, "nonzero root residual")
    for coefficient, (a, b) in zip(coefficients, expected):
        require((valuation(coefficient, PI), valuation(coefficient, RHO)) == (a, b),
                "wrong gap valuation")
        require(norm(coefficient) >= 5 ** (a + b), "coefficient norm floor")
    n = len(exponents) - 1
    gaps = tuple(b - a for a, b in zip(exponents, exponents[1:]))
    mass = sum(a + b for a, b in expected)
    weighted = sum((n - 1 + 2 * s * (n - 1 - s)) * gap for s, gap in enumerate(gaps))
    require(mass == weighted, "gap mass identity")
    require((mass == 2 * comb(n + 1, 3)) == all(gap == 1 for gap in gaps), "mass equality locus")
    require(mass >= 2 * comb(n + 1, 3), "mass floor")
    require(max(norm(c) for c in coefficients) >= 5 ** comb(n, 2), "maximum height floor")
    return mass


def fixtures() -> tuple[tuple[int, ...], ...]:
    small = tuple((0,) + tail for n in range(2, 6) for tail in combinations(range(1, 9), n))
    larger = []
    for n in range(6, 10):
        larger.extend((tuple(2 * j for j in range(n + 1)),
                       tuple(j + j // 2 for j in range(n + 1)),
                       tuple(j + j * (j - 1) // 4 for j in range(n + 1)),
                       tuple(sum(1 + s % 3 for s in range(j)) for j in range(n + 1))))
    translated = tuple(tuple(m + shift for m in e) for e in small[:10] for shift in (-7, 11))
    return small + tuple(larger) + translated


def controls() -> int:
    invalid = ((), (0, 1), (0, 0, 1), (0, 2, 1), (0, 1, 65),
               (0, True, 2), (0, Fraction(1), 2), (-129, -128, -127))
    count = 0
    for exponents in invalid:
        try:
            support(exponents)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid support accepted")
    exponents = (0, 1, 3, 7)
    coefficients = primitive(cofactors(nodes(exponents)))
    a, b = coefficients[0]
    changed = ((a + 1, b),) + coefficients[1:]
    mutants = (changed, coefficients[:-1], tuple(zmul(c, PI) for c in coefficients),
               ((0, 0),) + coefficients[1:], tuple((a, -b) for a, b in coefficients))
    for mutant in mutants:
        try:
            validate(exponents, mutant)
        except ValueError:
            count += 1
        else:
            raise ValueError("bad coefficient vector accepted")
    return count


def main() -> None:
    cases = fixtures()
    coefficients_checked = roots_checked = tensor_entries = nonconsecutive = 0
    digest = sha256()
    for exponents in cases:
        points = nodes(exponents)
        coefficients = primitive(cofactors(points))
        require(coefficients == primitive(independent_kernel(points)), "independent kernel disagreement")
        mass = validate(exponents, coefficients)
        n = len(exponents) - 1
        if n <= 5:
            for address in range(1 << (n - 1)):
                require(evaluate(coefficients, points, address.bit_count()) == ZERO, "tensor entry")
                tensor_entries += 1
        nonconsecutive += any(b - a > 1 for a, b in zip(exponents, exponents[1:]))
        coefficients_checked += len(coefficients)
        roots_checked += n
        digest.update(json.dumps([exponents, coefficients, mass], separators=(",", ":")).encode())
    sample_exponents = (0, 1, 3, 4)
    sample = primitive(cofactors(nodes(sample_exponents)))
    sample_mass = validate(sample_exponents, sample)
    package = Path(__file__).resolve().parent
    filenames = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in filenames}
    print(json.dumps({"status": "PASS_SPARSE_TENSOR_ANNIHILATOR_HEIGHTS", "fixtures": len(cases),
                      "coefficient_occurrences": coefficients_checked, "root_residuals": roots_checked,
                      "literal_tensor_diagonal_entries": tensor_entries,
                      "nonconsecutive_supports": nonconsecutive, "rejected_controls": controls(),
                      "case_digest": digest.hexdigest(),
                      "sample": {"exponents": sample_exponents, "coefficients": sample,
                                 "valuations": profile(sample_exponents), "mass": sample_mass},
                      "sha256": hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
