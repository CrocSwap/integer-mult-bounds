# SPDX-License-Identifier: Apache-2.0
"""Integer-only principal-window slides after one rational initialization."""
from dataclasses import dataclass
from fractions import Fraction
from math import lcm

MAX_SOURCE = 32
MAX_WIDTH = 16
MAX_INPUT_BITS = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_div(numerator, denominator):
    require(denominator != 0, "zero exact-division pivot")
    quotient, remainder = divmod(numerator, denominator)
    require(remainder == 0, "nonintegral determinantal quotient")
    return quotient


def validate_labels(labels, size):
    labels = tuple(labels)
    require(1 <= len(labels) <= min(size, MAX_WIDTH), "window width")
    require(all(type(i) is int and 0 <= i < size for i in labels), "source label")
    require(len(set(labels)) == len(labels), "duplicate source label")
    return labels


def normalize_source(matrix):
    size = len(matrix)
    require(1 <= size <= MAX_SOURCE, "source dimension")
    require(all(len(row) == size for row in matrix), "square source")
    require(all(type(x) in (int, Fraction) for row in matrix for x in row),
            "exact rational source entries")
    rational = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    require(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                <= MAX_INPUT_BITS for row in rational for x in row), "source bit limit")
    scales = tuple(lcm(*(x.denominator for x in row)) for row in rational)
    integral = tuple(tuple(exact_div(x.numerator * scale, x.denominator) for x in row)
                     for row, scale in zip(rational, scales))
    return integral, scales


def integer_determinant(matrix):
    """Bareiss elimination with row pivoting; used only during initialization."""
    size = len(matrix)
    require(1 <= size <= MAX_WIDTH and all(len(row) == size for row in matrix),
            "determinant shape")
    work = [list(row) for row in matrix]
    previous, sign = 1, 1
    for column in range(size - 1):
        pivot_row = next((i for i in range(column, size) if work[i][column]), None)
        if pivot_row is None:
            return 0
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            sign = -sign
        pivot = work[column][column]
        for i in range(column + 1, size):
            for j in range(column + 1, size):
                work[i][j] = exact_div(pivot * work[i][j]
                                      - work[i][column] * work[column][j], previous)
            work[i][column] = 0
        previous = pivot
    return sign * work[-1][-1]


def initial_adjugate(matrix, determinant):
    """One dense rational initialization; no Fraction is retained in the cache."""
    size = len(matrix)
    work = [[Fraction(x) for x in row]
            + [Fraction(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot_row = next((i for i in range(column, size) if work[i][column]), None)
        require(pivot_row is not None, "singular initial window")
        work[column], work[pivot_row] = work[pivot_row], work[column]
        pivot = work[column][column]
        work[column] = [x / pivot for x in work[column]]
        for i in range(size):
            if i != column:
                multiplier = work[i][column]
                work[i] = [x - multiplier * y for x, y in zip(work[i], work[column])]
    adjugate = [[x * determinant for x in row[size:]] for row in work]
    require(all(x.denominator == 1 for row in adjugate for x in row),
            "integral initial adjugate")
    return tuple(tuple(x.numerator for x in row) for row in adjugate)


def delete_first(adjugate, determinant):
    size = len(adjugate)
    order = tuple(range(1, size)) + (0,)
    moved = tuple(tuple(adjugate[i][j] for j in order) for i in order)
    retained_determinant = moved[-1][-1]
    require(retained_determinant != 0, "singular retained principal window")
    retained = tuple(tuple(exact_div(retained_determinant * moved[i][j]
                                    - moved[i][-1] * moved[-1][j], determinant)
                           for j in range(size - 1)) for i in range(size - 1))
    return retained, retained_determinant


def border(retained, determinant, column, row, diagonal):
    size = len(retained)
    left = tuple(sum(retained[i][j] * column[j] for j in range(size))
                 for i in range(size))
    right = tuple(sum(row[i] * retained[i][j] for i in range(size))
                  for j in range(size))
    new_determinant = diagonal * determinant - sum(row[i] * left[i] for i in range(size))
    require(new_determinant != 0, "singular incoming principal window")
    new_adjugate = tuple(tuple(exact_div(new_determinant * retained[i][j]
                                        + left[i] * right[j], determinant)
                               for j in range(size)) + (-left[i],) for i in range(size))
    new_adjugate += (tuple(-x for x in right) + (determinant,),)
    return new_adjugate, new_determinant


@dataclass(frozen=True)
class WindowCache:
    """Construct through initialize; serialized/forged states are not an input API."""
    source: tuple[tuple[int, ...], ...]
    row_scales: tuple[int, ...]
    labels: tuple[int, ...]
    adjugate: tuple[tuple[int, ...], ...]
    determinant: int

    def slide(self, incoming):
        require(type(incoming) is int and 0 <= incoming < len(self.source),
                "incoming source label")
        require(incoming not in self.labels[1:], "incoming aliases retained label")
        retained, divisor = delete_first(self.adjugate, self.determinant)
        labels = self.labels[1:] + (incoming,)
        column = tuple(self.source[i][incoming] for i in labels[:-1])
        row = tuple(self.source[incoming][i] for i in labels[:-1])
        adjugate, determinant = border(retained, divisor, column, row,
                                      self.source[incoming][incoming])
        return WindowCache(self.source, self.row_scales, labels, adjugate, determinant)

    def numerators(self):
        """H[J,J] inverse is this integer matrix divided by determinant."""
        return tuple(tuple(x * self.row_scales[self.labels[j]] for j, x in enumerate(row))
                     for row in self.adjugate)

    def materialize(self):
        return tuple(tuple(Fraction(x, self.determinant) for x in row)
                     for row in self.numerators())


def initialize(matrix, labels):
    source, scales = normalize_source(matrix)
    labels = validate_labels(labels, len(source))
    principal = tuple(tuple(source[i][j] for j in labels) for i in labels)
    determinant = integer_determinant(principal)
    require(determinant != 0, "singular initial window")
    adjugate = initial_adjugate(principal, determinant)
    return WindowCache(source, scales, labels, adjugate, determinant)
