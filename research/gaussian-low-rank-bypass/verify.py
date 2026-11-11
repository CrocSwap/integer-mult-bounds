"""Exact finite corroboration of the dense-bypass energy theorem.

Produced by Nick Petalas. Apache-2.0.
The universal assertion is proved in PROOF.md. This program checks bounded
Gaussian-rational matrices and writes only its generated receipt to stdout.
"""

from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import platform

type G = tuple[F, F]
type Matrix = tuple[tuple[G, ...], ...]
ZERO: G = (F(0), F(0))
ONE: G = (F(1), F(0))
MAX_DIMENSION = 64


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def add(a: G, b: G) -> G:
    return (a[0] + b[0], a[1] + b[1])


def neg(a: G) -> G:
    return (-a[0], -a[1])


def mul(a: G, b: G) -> G:
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def conjugate(a: G) -> G:
    return (a[0], -a[1])


def squared(a: G) -> F:
    return a[0] ** 2 + a[1] ** 2


def divide(a: G, b: G) -> G:
    norm = squared(b)
    require(norm != 0, "zero divisor")
    product = mul(a, conjugate(b))
    return (product[0] / norm, product[1] / norm)


def modulus_upper(a: G) -> F:
    norm = squared(a)
    numerator, denominator = isqrt(norm.numerator), isqrt(norm.denominator)
    if numerator**2 == norm.numerator and denominator**2 == norm.denominator:
        return F(numerator, denominator)
    return abs(a[0]) + abs(a[1])


def shape(a: Matrix) -> tuple[int, int]:
    require(1 <= len(a) <= MAX_DIMENSION, "row dimension")
    columns = len(a[0])
    require(1 <= columns <= MAX_DIMENSION, "column dimension")
    require(all(len(row) == columns for row in a), "ragged matrix")
    return len(a), columns


def identity(n: int) -> Matrix:
    require(1 <= n <= MAX_DIMENSION, "identity dimension")
    return tuple(tuple(ONE if i == j else ZERO for j in range(n)) for i in range(n))


def scale(a: Matrix, factor: F) -> Matrix:
    shape(a)
    return tuple(tuple((v[0] * factor, v[1] * factor) for v in row) for row in a)


def plus(a: Matrix, b: Matrix) -> Matrix:
    require(shape(a) == shape(b), "sum dimensions")
    return tuple(tuple(add(x, y) for x, y in zip(u, v)) for u, v in zip(a, b))


def adjoint(a: Matrix) -> Matrix:
    rows, columns = shape(a)
    return tuple(tuple(conjugate(a[i][j]) for i in range(rows)) for j in range(columns))


def product(a: Matrix, b: Matrix) -> Matrix:
    rows, inner = shape(a)
    other, columns = shape(b)
    require(inner == other, "product dimensions")
    sparse_rows = tuple(tuple((j, v) for j, v in enumerate(row) if v != ZERO) for row in b)
    result = []
    for i in range(rows):
        values = [ZERO] * columns
        for k in range(inner):
            if a[i][k] != ZERO:
                for j, value in sparse_rows[k]:
                    values[j] = add(values[j], mul(a[i][k], value))
        result.append(tuple(values))
    return tuple(result)


def rank(a: Matrix) -> int:
    rows, columns = shape(a)
    work = [list(row) for row in a]
    pivot_row = 0
    for column in range(columns):
        candidates = [i for i in range(pivot_row, rows) if work[i][column] != ZERO]
        if not candidates:
            continue
        selected = candidates[0]
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [divide(v, divisor) for v in work[pivot_row]]
        for i in range(rows):
            coefficient = work[i][column]
            if i != pivot_row and coefficient != ZERO:
                work[i] = [add(x, neg(mul(coefficient, y))) for x, y in zip(work[i], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def gaussian_entry(width: int, row: int, column: int) -> G:
    require(1 <= width <= 6 and 0 <= row < 2**width and 0 <= column < 2**width, "Gaussian address")
    value = ONE
    for bit in range(width):
        sign = -1 if ((row ^ column) >> bit) & 1 else 1
        value = mul(value, (F(1, 2), F(sign, 2)))
    return value


def gaussian(width: int) -> Matrix:
    require(1 <= width <= 6, "Gaussian width")
    n = 2**width
    return tuple(tuple(gaussian_entry(width, i, j) for j in range(n)) for i in range(n))


def validate_unitary(a: Matrix) -> None:
    rows, columns = shape(a)
    require(rows == columns, "unitary dimensions")
    check(product(adjoint(a), a) == identity(rows), "unitary identity")


def validate_child(k: Matrix) -> None:
    validate_unitary(k)
    n = len(k)
    check(all(squared(value) == F(1, n) for row in k for value in row), "flat child")


def target(width: int, copies: int) -> Matrix:
    require(1 <= width <= 3 and 1 <= copies <= 3, "target parameters")
    n = 2**width
    d = copies * n
    return tuple(tuple(gaussian_entry(width, i % n, j % n) if i // n == j // n else ZERO
                       for j in range(d)) for i in range(d))


def frobenius_squared(a: Matrix) -> F:
    shape(a)
    return sum((squared(value) for row in a for value in row), F(0))


def adapter_bounds(a: Matrix, b: Matrix) -> tuple[F, F]:
    rows, columns = shape(a)
    shape(b)
    column_bound = max(sum((modulus_upper(a[i][j]) for i in range(rows)), F(0)) for j in range(columns))
    row_bound = max(sum((modulus_upper(v) for v in row), F(0)) for row in b)
    return column_bound, row_bound


def check_case(t: Matrix, k: Matrix, a: Matrix, b: Matrix, h: Matrix,
               eta: F, claimed_rank: int | None = None) -> tuple[int, F, F]:
    """K and T are immutable matrices validated by the fixture boundary.

    Error fixtures have E=eta*T, whose operator norm is exactly eta.
    The theorem itself permits every E with operator norm at most eta.
    """
    require(F(0) <= eta < F(1), "error domain")
    d, columns = shape(t)
    require(d == columns and shape(h) == (d, d), "endpoint dimensions")
    child_path = product(b, product(k, a))
    check(plus(plus(child_path, h), scale(t, eta)) == t, "endpoint equation")
    h_rank = rank(h)
    if claimed_rank is not None:
        check(h_rank == claimed_rank, "bypass rank")
    column_bound, row_bound = adapter_bounds(a, b)
    energy = frobenius_squared(child_path)
    upper = F(d * d, len(k)) * (column_bound * row_bound) ** 2
    lower = (d - h_rank) * (1 - eta) ** 2
    check(lower <= energy <= upper, "energy sandwich")
    return h_rank, energy, upper


def sharp_witness(t: Matrix, k: Matrix, eta: F) -> tuple[Matrix, Matrix, Matrix]:
    d, n = len(t), len(k)
    require(d <= n, "witness capacity")
    a = tuple(tuple((F(1 - eta, d), F(0)) if i == 0 else ZERO for _ in range(d)) for i in range(n))
    b = tuple(tuple(conjugate(k[i][0]) for i in range(n)) for _ in range(d))
    projection = tuple(tuple((F(1, d), F(0)) for _ in range(d)) for _ in range(d))
    h = scale(plus(t, scale(projection, F(-1))), 1 - eta)
    return a, b, h


def seeded_adapter(rows: int, columns: int, seed: int) -> Matrix:
    require(1 <= rows <= 16 and 1 <= columns <= 16 and 0 <= seed < 100, "adapter seed")
    return tuple(tuple((F(((i * 7 + j * 3 + seed) % 5) - 2, 4),
                        F(((i * 3 + j * 11 + seed * 2) % 3) - 1, 4))
                       for j in range(columns)) for i in range(rows))


def finite_checks() -> dict[str, int]:
    children = {width: gaussian(width) for width in (1, 2, 4, 6)}
    for k in children.values():
        validate_child(k)
    counts = {"flat_unitaries": len(children), "sharp_witnesses": 0,
              "general_adapters": 0, "full_child_controls": 0}
    for width, recursive_rank in ((1, 2), (1, 4), (2, 2), (2, 3), (3, 2)):
        k = children[width * recursive_rank]
        for copies in range(1, min(3, len(k) // 2**width) + 1):
            t = target(width, copies)
            validate_unitary(t)
            for eta in (F(0), F(1, 2)):
                a, b, h = sharp_witness(t, k, eta)
                h_rank, energy, upper = check_case(t, k, a, b, h, eta, len(t) - 1)
                check(energy == upper == (1 - eta) ** 2, "sharp constant")
                check(h_rank == len(t) - 1, "sharp rank")
                counts["sharp_witnesses"] += 1
    for width in (1, 2):
        k, t = children[2], target(width, 1)
        validate_unitary(t)
        for seed in range(24):
            a = seeded_adapter(len(k), len(t), seed)
            b = seeded_adapter(len(t), len(k), seed + 24)
            h = plus(t, scale(product(b, product(k, a)), F(-1)))
            check_case(t, k, a, b, h, F(0))
            counts["general_adapters"] += 1
    for width in (1, 2):
        k = children[width]
        check_case(k, k, identity(len(k)), identity(len(k)), scale(k, F(0)), F(0), 0)
        counts["full_child_controls"] += 1
    return counts


def rejection_checks() -> int:
    t, k = target(1, 2), gaussian(2)
    validate_unitary(t)
    validate_child(k)
    a, b, h = sharp_witness(t, k, F(0))
    cases = ((t, k, a, b, h, F(0), 2),
             (t, k, a, b, scale(h, F(0)), F(0), None),
             (t, k, a, b, scale(h, F(-1)), F(0), None),
             (t, k, a, b, h, F(1, 2), None),
             (t, k, a, b, h, F(1), None),
             (t, k, a, b, h, F(-1), None),
             (t, scale(k, F(-1)), a, b, h, F(0), None),
             (t, k, scale(a, F(2)), b, h, F(0), None),
             (t, k, a, scale(b, F(0)), h, F(0), None),
             (t, k, a[:-1], b, h, F(0), None),
             (t, k, a, b, h[:-1], F(0), None))
    rejected = 0
    for case in cases:
        try:
            check_case(*case)
        except (AssertionError, ValueError):
            rejected += 1
    check(rejected == len(cases), "rejection controls")
    for malformed in (scale(k, F(2)), k[:-1], identity(len(k))):
        try:
            validate_child(malformed)
        except (AssertionError, ValueError):
            rejected += 1
        else:
            raise AssertionError("invalid child accepted")
    return rejected


def main() -> None:
    counts = finite_checks()
    counts["rejection_controls"] = rejection_checks()
    package = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_GAUSSIAN_LOW_RANK_BYPASS", "python": platform.python_version(),
                      "counts": counts, "sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
