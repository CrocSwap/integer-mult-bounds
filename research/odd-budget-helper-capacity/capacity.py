"""Exact odd-denominator budgets for a supplied dyadic Smith chart.

Produced by Nick Petalas. Apache-2.0.
Smith normal form is classical; see PROOF.md for the scoped application.
"""

from fractions import Fraction
from math import isqrt

Matrix = tuple[tuple[Fraction, ...], ...]
MAX_DIMENSION = 6
MAX_BITS = 256
MAX_ODD = (1 << 20) - 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def matrix(rows: object) -> Matrix:
    require(isinstance(rows, (list, tuple)), "matrix must be a list or tuple")
    require(1 <= len(rows) <= MAX_DIMENSION, "matrix row capacity")
    require(all(isinstance(row, (list, tuple)) for row in rows), "matrix rows")
    width = len(rows[0])
    require(1 <= width <= MAX_DIMENSION, "matrix column capacity")
    require(all(len(row) == width for row in rows), "ragged matrix")
    values = []
    for row in rows:
        converted = []
        for value in row:
            require(type(value) in (int, Fraction), "exact rational entry required")
            value = Fraction(value)
            require(value.denominator & (value.denominator - 1) == 0,
                    "entry must be dyadic")
            require(max(abs(value.numerator).bit_length(),
                        value.denominator.bit_length()) <= MAX_BITS, "entry capacity")
            converted.append(value)
        values.append(tuple(converted))
    return tuple(values)


def identity(size: int) -> Matrix:
    require(type(size) is int and 0 <= size <= MAX_DIMENSION, "identity capacity")
    return tuple(tuple(Fraction(i == j) for j in range(size)) for i in range(size))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    require(bool(left) and bool(right), "nonempty matrix product required")
    require(len(left[0]) == len(right), "matrix product shape")
    return tuple(tuple(sum((left[i][k] * right[k][j] for k in range(len(right))),
                           Fraction(0)) for j in range(len(right[0])))
                 for i in range(len(left)))


def determinant(value: Matrix) -> Fraction:
    require(len(value) == len(value[0]), "square determinant required")
    work = [list(row) for row in value]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next((i for i in range(column, len(work)) if work[i][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[pivot], work[column] = work[column], work[pivot]
            result = -result
        leading = work[column][column]
        result *= leading
        for i in range(column + 1, len(work)):
            ratio = work[i][column] / leading
            for j in range(column + 1, len(work)):
                work[i][j] -= ratio * work[column][j]
    return result


def is_unit(value: Fraction) -> bool:
    numerator = abs(value.numerator)
    denominator = value.denominator
    return (numerator > 0 and numerator & (numerator - 1) == 0
            and denominator & (denominator - 1) == 0)


def validate_chart(k: Matrix, u: Matrix, v: Matrix, smith: tuple[int, ...]) -> None:
    for value in (k, u, v):
        require(matrix(value) == value, "invalid dyadic matrix")
    m, n = len(k), len(k[0])
    require(len(u) == m and len(u[0]) == m, "left chart shape")
    require(len(v) == n and len(v[0]) == n, "right chart shape")
    require(type(smith) is tuple and len(smith) <= min(m, n), "Smith shape")
    for i, factor in enumerate(smith):
        require(type(factor) is int and 0 < factor <= MAX_ODD and factor % 2 == 1,
                "Smith factors must be bounded positive odd integers")
        require(i == 0 or factor % smith[i - 1] == 0, "Smith divisibility")
    require(is_unit(determinant(u)) and is_unit(determinant(v)), "nonunit chart")
    expected = tuple(tuple(Fraction(smith[i] if i == j and i < len(smith) else 0)
                           for j in range(n)) for i in range(m))
    require(multiply(multiply(u, k), v) == expected, "false Smith identity")


def budget(value: int) -> None:
    require(type(value) is int and 0 < value <= MAX_ODD and value % 2 == 1,
            "budget must be a bounded positive odd integer")


def factors(value: int) -> tuple[tuple[int, int], ...]:
    budget(value)
    remaining = value
    result = []
    for prime in range(3, isqrt(value) + 1, 2):
        exponent = 0
        for _ in range(20):
            if remaining % prime:
                break
            remaining //= prime
            exponent += 1
        if exponent:
            result.append((prime, exponent))
    if remaining > 1:
        result.append((remaining, 1))
    return tuple(result)


def valuation(value: int, prime: int) -> int:
    require(type(value) is int and 0 < value < 1 << 40, "valuation input")
    require(type(prime) is int and 3 <= prime <= MAX_ODD, "valuation divisor")
    for exponent in range(41):
        if value % prime:
            return exponent
        value //= prime
    raise ValueError("valuation capacity")


def construct(k: Matrix, u: Matrix, v: Matrix, smith: tuple[int, ...],
              a: int, b: int) -> tuple[Matrix, Matrix, int, tuple[int, int] | None]:
    validate_chart(k, u, v, smith)
    budget(a)
    budget(b)
    count = sum(a * b % factor == 0 for factor in smith)
    x = tuple(tuple(Fraction(b, smith[i]) * value for value in u[i])
              for i in range(count))
    y = tuple(tuple(v[j][i] / b for i in range(count)) for j in range(len(v)))
    obstruction = None
    if count < len(smith):
        for prime, exponent in factors(smith[count]):
            if exponent > valuation(a * b, prime):
                obstruction = (prime, valuation(a * b, prime))
                break
        require(obstruction is not None, "missing prime obstruction")
    return x, y, count, obstruction


def common_denominator(smith: tuple[int, ...], count: int) -> int | None:
    require(type(count) is int and 0 <= count <= MAX_DIMENSION + 1,
            "channel count capacity")
    require(type(smith) is tuple and len(smith) <= MAX_DIMENSION, "Smith capacity")
    for i, factor in enumerate(smith):
        budget(factor)
        require(i == 0 or factor % smith[i - 1] == 0, "Smith divisibility")
    if count > len(smith):
        return None
    result = 1
    if count:
        for prime, exponent in factors(smith[count - 1]):
            result *= prime ** ((exponent + 1) // 2)
    return result
