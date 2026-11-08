"""Small exact helpers for the source-bound precision certificate."""
from fractions import Fraction
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high, message):
    require(type(value) is int and low <= value <= high, message)
    return value


def rational(value):
    require(type(value) in (str, int), 'literal exact scalar')
    answer = Fraction(value)
    require(answer and answer.denominator & (answer.denominator-1) == 0,
            'nonzero Gaussian-dyadic exterior scalar')
    return answer


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def row_record(row):
    return [[key, str(value)] for key, value in sorted(row.items())]


def mass(row):
    return sum(map(abs, row.values()), Fraction(0))


def debt(row):
    out = 0
    for value in row.values():
        denominator = Fraction(value).denominator
        require(denominator & (denominator-1) == 0, 'dyadic row coefficient')
        out = max(out, denominator.bit_length()-1)
    return out


def span(vectors):
    require(type(vectors) is list and len(vectors) <= 9, 'nine-axis source frame')
    reached = {0}
    for value in vectors:
        integer(value, 1, 511, 'binary source frame vector')
        require(value not in reached, 'independent source frame')
        reached |= {x ^ value for x in tuple(reached)}
    return frozenset(reached)


def same_typed(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(same_typed(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same_typed(a, b) for a, b in zip(left, right))
    return left == right
