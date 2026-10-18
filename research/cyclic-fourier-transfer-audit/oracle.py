#!/usr/bin/env python3
"""Independent finite-dimensional oracle for the cyclic Fourier transfer audit.

Only the Python standard library is used.  No predecessor/producer code or
certificate is imported.  Gaussian rational Gauss--Jordan inversion is checked
against a separate factor/geometric-series construction, and against both
matrix identities.  Square-root *intervals*, never floating-point decisions,
certify every reported norm inequality.

Convention: Z_L e_j = e_(j+1 mod L), and coefficients are in ascending order.
For P(z)=c prod(z-r), the reverse triangle inequality on |z|=1 proves the
circle separation delta=|c| prod(abs(1-|r|)).  All fixture root/scale moduli are
rational and are checked exactly.  M=sum(j*|a_j|) is bounded from above by
rational square-root intervals, so |P'(z)|<=M throughout the unit circle.

For T=tau Z_L^w and m=L/gcd(L,w), T^m=tau^m I.  Thus each factor inverse is
  (T-r I)^-1 = sum(r^(m-1-k) T^k, k=0..m-1)/(tau^m-r^m).
The implementation below builds this inverse by circular convolution, without
using either the dense matrix builder or the dense elimination algorithm.

The finite samples are regression evidence, not a proof of the universal
Fourier estimate.  The mathematical argument is provided separately.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from math import gcd, isqrt
import json
import random


@dataclass(frozen=True)
class GQ:
    """A Gaussian rational with exact arithmetic."""

    re: F = F(0)
    im: F = F(0)

    def __add__(self, other: GQ) -> GQ:
        return GQ(self.re + other.re, self.im + other.im)

    def __neg__(self) -> GQ:
        return GQ(-self.re, -self.im)

    def __sub__(self, other: GQ) -> GQ:
        return self + (-other)

    def __mul__(self, other: GQ) -> GQ:
        return GQ(self.re * other.re - self.im * other.im,
                  self.re * other.im + self.im * other.re)

    def __truediv__(self, other: GQ) -> GQ:
        square = other.norm_square()
        if not square:
            raise ZeroDivisionError("zero Gaussian rational")
        return GQ((self.re * other.re + self.im * other.im) / square,
                  (self.im * other.re - self.re * other.im) / square)

    def __pow__(self, exponent: int) -> GQ:
        if exponent < 0:
            return (ONE / self) ** (-exponent)
        result, base = ONE, self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent //= 2
        return result

    def norm_square(self) -> F:
        return self.re * self.re + self.im * self.im

    def conjugate(self) -> GQ:
        return GQ(self.re, -self.im)


ZERO, ONE = GQ(), GQ(F(1))
Matrix = list[list[GQ]]
SQRT_GRID = 10**12


def sqrt_interval(value: F) -> tuple[F, F]:
    """Return rational lower/upper square-root bounds, exact when possible."""
    if value < 0:
        raise ValueError("negative square root")
    numerator, denominator = value.numerator, value.denominator
    nr, dr = isqrt(numerator), isqrt(denominator)
    if nr * nr == numerator and dr * dr == denominator:
        return F(nr, dr), F(nr, dr)
    floor = isqrt(numerator * SQRT_GRID**2 // denominator)
    lo, hi = F(floor, SQRT_GRID), F(floor + 1, SQRT_GRID)
    if not lo * lo <= value <= hi * hi:
        raise AssertionError("invalid rational square-root enclosure")
    return lo, hi


def rational_modulus(value: GQ) -> F:
    lo, hi = sqrt_interval(value.norm_square())
    if lo != hi:
        raise ValueError("fixture requires an exactly rational modulus")
    return lo


def identity(size: int) -> Matrix:
    return [[ONE if row == col else ZERO for col in range(size)]
            for row in range(size)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    result = [[ZERO for _ in range(size)] for _ in range(size)]
    # Sparse skipping is useful for the direct polynomial matrices.
    for row in range(size):
        for middle in range(size):
            a = left[row][middle]
            if a == ZERO:
                continue
            for col in range(size):
                b = right[middle][col]
                if b != ZERO:
                    result[row][col] = result[row][col] + a * b
    return result


def dense_polynomial(coefficients: tuple[GQ, ...], size: int,
                     stride: int, tau: GQ) -> Matrix:
    """Horner evaluation on an explicit dense permutation matrix."""
    shift = [[ZERO for _ in range(size)] for _ in range(size)]
    for col in range(size):
        shift[(col + stride) % size][col] = tau
    matrix = [[ZERO for _ in range(size)] for _ in range(size)]
    for coefficient in reversed(coefficients):
        matrix = multiply(matrix, shift)
        for index in range(size):
            matrix[index][index] = matrix[index][index] + coefficient
    return matrix


def dense_inverse(matrix: Matrix) -> Matrix:
    """Exact Gauss--Jordan with pivoting, independently of cyclic structure."""
    size = len(matrix)
    eye = identity(size)
    rows = [list(row) + eye[index] for index, row in enumerate(matrix)]
    for col in range(size):
        pivot = next((row for row in range(col, size)
                      if rows[row][col] != ZERO), None)
        if pivot is None:
            raise ValueError("singular matrix")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        denominator = rows[col][col]
        rows[col] = [value / denominator for value in rows[col]]
        for row in range(size):
            if row == col or rows[row][col] == ZERO:
                continue
            factor = rows[row][col]
            rows[row] = [value - factor * pivot_value
                         for value, pivot_value in zip(rows[row], rows[col])]
    if [row[:size] for row in rows] != eye:
        raise AssertionError("elimination failed to produce identity")
    return [row[size:] for row in rows]


@dataclass(frozen=True)
class Fixture:
    name: str
    scale: GQ
    roots: tuple[GQ, ...]

    def coefficients(self) -> tuple[GQ, ...]:
        coefficients = [self.scale]
        for root in self.roots:
            product = [ZERO] * (len(coefficients) + 1)
            for index, value in enumerate(coefficients):
                product[index] = product[index] - root * value
                product[index + 1] = product[index + 1] + value
            coefficients = product
        return tuple(coefficients)

    def circle_parameters(self) -> tuple[F, F]:
        delta = rational_modulus(self.scale)
        for root in self.roots:
            delta *= abs(F(1) - rational_modulus(root))
        if delta <= 0:
            raise ValueError("positive circle separation is required")
        derivative = sum((index * sqrt_interval(value.norm_square())[1]
                          for index, value in enumerate(self.coefficients())), F(0))
        return delta, derivative


def geometric_inverse(fixture: Fixture, size: int,
                      stride: int, tau: GQ) -> Matrix:
    """Independent inverse assembled from circular convolution of factors."""
    period = size // gcd(size, stride)
    kernel = [ONE / fixture.scale] + [ZERO] * (size - 1)
    for root in fixture.roots:
        denominator = tau**period - root**period
        factor = [ZERO] * size
        for power in range(period):
            index = (power * stride) % size
            factor[index] = (factor[index]
                             + root**(period - 1 - power) * tau**power / denominator)
        product = [ZERO] * size
        for left, value in enumerate(kernel):
            if value == ZERO:
                continue
            for right, other in enumerate(factor):
                if other != ZERO:
                    index = (left + right) % size
                    product[index] = product[index] + value * other
        kernel = product
    return [[kernel[(row - col) % size] for col in range(size)]
            for row in range(size)]


def row_norm_interval(row: list[GQ]) -> tuple[F, F]:
    bounds = [sqrt_interval(value.norm_square()) for value in row]
    return (sum((lo for lo, _ in bounds), F(0)),
            sum((hi for _, hi in bounds), F(0)))


def fixtures() -> tuple[Fixture, ...]:
    return (
        Fixture("constant_complex", GQ(F(9, 10), F(6, 5)), ()),
        Fixture("inner_real", ONE, (GQ(F(1, 3)),)),
        Fixture("outer_imaginary", ONE, (GQ(F(0), F(2)),)),
        Fixture("mixed_real", ONE, (GQ(F(-1, 2)), GQ(F(2)))),
        Fixture("mixed_complex", GQ(F(3, 5), F(4, 5)),
                (GQ(F(3, 10), F(2, 5)), GQ(F(6, 5), F(8, 5)))),
        Fixture("cubic_zero_constant", GQ(F(2)),
                (ZERO, GQ(F(1, 3)), GQ(F(0), F(2)))),
    )


def require_unit_tau(tau: GQ) -> None:
    if tau.norm_square() != 1:
        raise ValueError("the transfer theorem requires |tau| = 1")


def require(condition: bool, message: str) -> None:
    # Deliberately not Python assert: checks remain active under python -O.
    if not condition:
        raise AssertionError(message)


def negative_controls() -> dict[str, object]:
    fixture = Fixture("controls", ONE, (GQ(F(1, 3), F(0)),))
    coefficients = fixture.coefficients()
    matrix = dense_polynomial(coefficients, 5, 1, ONE)
    wrong_direction = geometric_inverse(fixture, 5, -1, ONE)
    require(multiply(matrix, wrong_direction) != identity(5),
            "wrong shift direction was not detected")

    complex_fixture = fixtures()[4]
    tau = GQ(F(3, 5), F(4, 5))
    matrix = dense_polynomial(complex_fixture.coefficients(), 5, 1, tau)
    wrong_tau = geometric_inverse(complex_fixture, 5, 1, tau.conjugate())
    require(multiply(matrix, wrong_tau) != identity(5),
            "wrong tau conjugation was not detected")
    conjugated = Fixture("conjugated", complex_fixture.scale.conjugate(),
                         tuple(root.conjugate() for root in complex_fixture.roots))
    wrong_coefficients = geometric_inverse(conjugated, 5, 1, tau)
    require(multiply(matrix, wrong_coefficients) != identity(5),
            "wrong coefficient conjugation was not detected")
    reversed_coefficients = tuple(reversed(complex_fixture.coefficients()))
    wrong_order = dense_inverse(dense_polynomial(reversed_coefficients, 5, 1, tau))
    require(multiply(matrix, wrong_order) != identity(5),
            "wrong coefficient order was not detected")

    singular = Fixture("unit_circle_root", ONE, (ONE,))
    try:
        singular.circle_parameters()
    except ValueError:
        pass
    else:
        raise AssertionError("unit-circle root was admitted")
    try:
        dense_inverse(dense_polynomial(singular.coefficients(), 4, 1, ONE))
    except ValueError:
        pass
    else:
        raise AssertionError("singular matrix was inverted")

    # P(z)=z-1/2 has delta=1/2 and M=1 on the circle.  However at the
    # nonunit scalar tau=51/100, L=1 its inverse norm is exactly 100,
    # exceeding sqrt(380/7) and the inherited bound 10.
    nonunit = GQ(F(51, 100))
    try:
        require_unit_tau(nonunit)
    except ValueError:
        pass
    else:
        raise AssertionError("nonunit scalar was admitted")
    nonunit_fixture = Fixture("nonunit_counterexample", ONE, (GQ(F(1, 2)),))
    inverse = dense_inverse(dense_polynomial(nonunit_fixture.coefficients(), 1, 0, nonunit))
    lo, hi = row_norm_interval(inverse[0])
    delta, derivative = nonunit_fixture.circle_parameters()
    square_bound = 1 / delta**2 + F(44, 7) * derivative / delta**3
    inherited = 1 / delta + 2 * derivative / delta**2
    require(lo == hi == 100 and lo**2 > square_bound and lo > inherited,
            "nonunit scalar did not refute both transferred estimates")

    return {
        "wrong_shift_direction": "rejected by exact product identity",
        "wrong_tau_conjugation": "rejected by exact product identity",
        "wrong_coefficient_conjugation": "rejected by exact product identity",
        "reversed_coefficient_order": "rejected by exact product identity",
        "unit_circle_root": "rejected: delta=0; dense matrix singular",
        "nonunit_tau": {
            "polynomial": "z - 1/2", "L": 1, "w": 0, "tau": "51/100",
            "inverse_norm": "100", "new_squared_bound": str(square_bound),
            "inherited_bound": str(inherited),
            "result": "hypothesis rejected; omitting it falsifies both bounds",
        },
    }


def run() -> dict[str, object]:
    """Execute deterministic exact tests and return a JSON-serializable summary."""
    collection = fixtures()
    gauges = (ONE, -ONE, GQ(F(0), F(1)), GQ(F(3, 5), F(4, 5)))
    strides = (-2, 0, 3)
    cases = [(index, size, stride, tau)
             for index in range(len(collection))
             for size in range(1, 10) for stride in strides for tau in gauges]
    # The random seed changes only traversal; the complete sample set is fixed.
    random.Random(60).shuffle(cases)
    summaries: list[dict[str, object]] = []
    parameters = []
    for fixture in collection:
        delta, derivative = fixture.circle_parameters()
        parameters.append((delta, derivative))
        summaries.append({
            "name": fixture.name, "degree": len(fixture.roots),
            "circle_delta": str(delta), "derivative_M_upper": str(derivative),
            "new_squared_bound": str(1 / delta**2 + F(44, 7) * derivative / delta**3),
            "inherited_bound": str(1 / delta + 2 * derivative / delta**2),
            "samples": 0,
        })
    noncoprime, zero_stride, negative_stride = 0, 0, 0
    for index, size, stride, tau in cases:
        require_unit_tau(tau)
        fixture = collection[index]
        matrix = dense_polynomial(fixture.coefficients(), size, stride, tau)
        inverse = dense_inverse(matrix)
        independent = geometric_inverse(fixture, size, stride, tau)
        require(inverse == independent,
                f"dense/geometric disagreement: {fixture.name}, {size}, {stride}, {tau}")
        eye = identity(size)
        require(multiply(matrix, inverse) == eye and multiply(inverse, matrix) == eye,
                "exact two-sided inverse identity failed")
        delta, derivative = parameters[index]
        square_bound = 1 / delta**2 + F(44, 7) * derivative / delta**3
        inherited = 1 / delta + 2 * derivative / delta**2
        norms = [row_norm_interval(row) for row in inverse]
        require(len(set(norms)) == 1, "cyclic inverse has nonuniform row norms")
        for _, hi in norms:
            require(hi**2 <= square_bound, "new norm estimate was not certified")
            require(hi <= inherited, "inherited norm estimate was not certified")
        summaries[index]["samples"] += 1
        noncoprime += int(stride != 0 and gcd(size, stride) > 1)
        zero_stride += int(stride == 0)
        negative_stride += int(stride < 0)

    return {
        "schema": "cyclic-fourier-transfer-finite-oracle-v1",
        "arithmetic": "Gaussian rational; exact dense Gauss-Jordan; rational sqrt intervals",
        "seed": 60, "seed_role": "case ordering only",
        "L": list(range(1, 10)), "strides": list(strides),
        "tau": ["1", "-1", "i", "3/5 + 4/5 i"],
        "sample_count": len(cases), "negative_stride_samples": negative_stride,
        "zero_stride_samples": zero_stride, "nonzero_noncoprime_samples": noncoprime,
        "checks": ["dense inverse equals independent geometric inverse",
                   "exact left and right inverse identities",
                   "uniform cyclic row l1 norms",
                   "row_l1_upper^2 <= delta^-2 + (44/7) M delta^-3",
                   "row_l1_upper <= delta^-1 + 2 M delta^-2"],
        "fixtures": summaries, "negative_controls": negative_controls(),
        "scope": "finite regression evidence; universal bound requires the separate proof",
        "status": "PASS",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
