"""Exact common-chart rank-one shears with one borrowed source hub.

Produced by Nick Petalas. Apache-2.0.
Classical integer row reduction and restored-field conjugation are credited
in README.md. This module does not import predecessor implementations.
"""

from fractions import Fraction
from math import gcd

MAX_ROLES = 8
MAX_BITS = 64
MAX_DENOMINATOR = 1 << 16
MAX_GATES = 16384


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dyadic(value):
    return value.denominator & (value.denominator - 1) == 0


def validate(matrix):
    need(1 <= len(matrix) <= MAX_ROLES, "bounded nonempty target list")
    width = len(matrix[0])
    need(1 <= width <= MAX_ROLES, "bounded nonempty source list")
    need(all(len(row) == width for row in matrix), "rectangular matrix")
    result = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    for row in result:
        for value in row:
            need(dyadic(value), "dyadic matrix required")
            need(abs(value.numerator).bit_length() <= MAX_BITS, "numerator cap")
            need(value.denominator <= MAX_DENOMINATOR, "denominator cap")
    return result


def factor(matrix):
    """Return M=a*b, with a dyadic and b primitive integral, or zero."""
    row = next((row for row in matrix if any(row)), None)
    if row is None:
        return None
    denominator = max(x.denominator for x in row)
    integers = tuple(int(x * denominator) for x in row)
    divisor = gcd(*integers)
    b = tuple(x // divisor for x in integers)
    pivot = next(i for i, x in enumerate(b) if x)
    if b[pivot] < 0:
        b = tuple(-x for x in b)
    a = tuple(row[pivot] / b[pivot] for row in matrix)
    need(all(x == a[i] * b[j] for i, row in enumerate(matrix)
             for j, x in enumerate(row)), "rank at most one required")
    need(all(dyadic(x) for x in a), "primitive factor must be dyadic")
    need(gcd(*b) == 1, "primitive source row")
    return a, b


def reduction(b):
    """Return elementary matrices E_l such that b E_1 ... E_L=e_0."""
    row = list(b)
    gates = []
    step_cap = 4 * MAX_BITS + 8
    for j in range(1, len(row)):
        for _ in range(step_cap):
            if row[j] == 0:
                break
            quotient = abs(row[0]) // abs(row[j])
            if (row[0] < 0) != (row[j] < 0):
                quotient = -quotient
            if quotient:
                gates.append((j, 0, -quotient))
                row[0] -= quotient * row[j]
            gates.extend(((0, j, -1), (j, 0, 1), (0, j, -1)))
            row[0], row[j] = row[j], -row[0]
        need(row[j] == 0, "Euclidean iteration cap")
    if row[0] == -1:
        need(len(row) >= 2, "one-source factor is positive")
        rotation = ((0, 1, -1), (1, 0, 1), (0, 1, -1))
        gates.extend(rotation + rotation)
        row[0] = 1
    need(row == [1] + [0] * (len(row) - 1), "unit row after reduction")
    need(len(gates) <= MAX_GATES // 2 - MAX_ROLES, "source gate cap")
    return tuple(gates)


def compile_shear(raw):
    matrix = validate(raw)
    factors = factor(matrix)
    if factors is None:
        return (), (), ()
    a, b = factors
    reduced = reduction(b)
    prepare = tuple((i, j, Fraction(-q)) for i, j, q in reduced)
    readout = tuple((len(b) + j, 0, q) for j, q in enumerate(a) if q)
    restore = tuple((i, j, -q) for i, j, q in reversed(prepare))
    need(len(prepare + readout + restore) <= MAX_GATES, "complete gate cap")
    return prepare, readout, restore


def allowance(coefficient):
    """Retained scalar ADD allowance; zero instructions are never emitted."""
    q = Fraction(coefficient)
    need(q != 0 and dyadic(q), "nonzero dyadic ADD")
    n, d = abs(q.numerator), q.denominator
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)
