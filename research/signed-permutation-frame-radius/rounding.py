"""Exact bounded implementation of the conjugated nearest-integer rounder.

Produced by Nick Petalas. Apache-2.0.
The written theorem has no dimension or magnitude limits; this executable does.
"""

from fractions import Fraction


MAX_DIMENSION = 8
MAX_BITS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(value):
    """Validate an integer frame and return its exact integer inverse."""
    require(isinstance(value, tuple), "frame must be a tuple")
    dimension = len(value)
    require(1 <= dimension <= MAX_DIMENSION, "unsupported dimension")
    require(all(isinstance(row, tuple) and len(row) == dimension
                for row in value), "frame must be square")
    require(all(type(entry) is int and entry.bit_length() <= 16
                for row in value for entry in row), "invalid frame entry")
    rows = [[Fraction(entry) for entry in row] +
            [Fraction(i == j) for j in range(dimension)]
            for i, row in enumerate(value)]
    for column in range(dimension):
        pivot = next((i for i in range(column, dimension)
                      if rows[i][column]), None)
        require(pivot is not None, "singular frame")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [entry / divisor for entry in rows[column]]
        for i in range(dimension):
            if i != column:
                factor = rows[i][column]
                rows[i] = [a - factor * b
                           for a, b in zip(rows[i], rows[column])]
    inverse = tuple(tuple(row[dimension:]) for row in rows)
    require(all(entry.denominator == 1 for row in inverse for entry in row),
            "frame must be unimodular")
    return tuple(tuple(int(entry) for entry in row) for row in inverse)


def apply(frame, point):
    return tuple(sum(a * b for a, b in zip(row, point)) for row in frame)


def nearest(value):
    """Nearest integer, with half ties away from zero; in particular odd."""
    magnitude = abs(value)
    result = (2 * magnitude.numerator + magnitude.denominator) // (
        2 * magnitude.denominator)
    return result if value >= 0 else -result


def round_point(frame, inverse, point):
    """Trusted frame/inverse from matrix(); validate external rational data."""
    require(isinstance(point, tuple) and len(point) == len(frame),
            "point dimension mismatch")
    require(all(type(entry) in (int, Fraction) for entry in point),
            "point must be exact rational")
    exact = tuple(Fraction(entry) for entry in point)
    require(all(max(entry.numerator.bit_length(), entry.denominator.bit_length())
                <= MAX_BITS for entry in exact), "point magnitude limit")
    coordinates = apply(inverse, exact)
    result = apply(frame, tuple(nearest(entry) for entry in coordinates))
    require(all(type(entry) is int for entry in result), "noninteger result")
    return result


def radius(frame, denominator):
    require(type(denominator) is int and 1 <= denominator <= 2**16,
            "invalid grid denominator")
    return Fraction(denominator // 2, denominator) * max(
        sum(abs(entry) for entry in row) for row in frame)


def extremizer(frame, denominator):
    """One grid point whose stabilizer forces the claimed radius."""
    require(type(denominator) is int and 1 <= denominator <= 2**16,
            "invalid grid denominator")
    row = max(frame, key=lambda entries: sum(abs(entry) for entry in entries))
    signs = tuple(1 if entry >= 0 else -1 for entry in row)
    coordinate = Fraction(denominator // 2, denominator)
    return apply(frame, tuple(coordinate * sign for sign in signs)), signs
