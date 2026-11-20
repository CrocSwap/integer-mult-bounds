# SPDX-License-Identifier: Apache-2.0
"""Shared hash, echelon and directed price routines for the independent replay."""

from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from math import isqrt
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
Q = Fraction


def digest(data):
    return sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load(relative):
    data = (HERE / relative).read_bytes()
    return json.loads(gzip.decompress(data) if relative.endswith(".gz") else data)


def authenticate():
    locks = load("SOURCE-LOCK.json")
    for item in locks:
        data = (HERE / item["file"]).read_bytes()
        assert digest(data) == item["sha256"], item["file"]
        if "git_blob" in item:
            git_object = f"blob {len(data)}\0".encode() + data
            assert sha1(git_object).hexdigest() == item["git_blob"], item["file"]
    return len(locks)


def parts(bits):
    """Enumerate the nonzero positions of a binary row."""
    while bits:
        low = bits & -bits
        yield low.bit_length() - 1
        bits ^= low


def sparse_axpy(dest, source, scale):
    for axis, coefficient in source.items():
        val = dest.get(axis, 0) + coefficient * scale
        if val:
            dest[axis] = val
        else:
            dest.pop(axis, None)


def row_rank(rows):
    """Exact sparse elimination with an incremental basis."""
    basis = {}
    for source in rows:
        row = dict(source)
        while row:
            pivot = min(row)
            weight = row[pivot]
            if pivot not in basis:
                basis[pivot] = (weight, row)
                break
            denominator, old = basis[pivot]
            sparse_axpy(row, old, -weight / denominator)
    return len(basis)


def histogram(data):
    return Counter({int(rank): count for rank, count in data.items()})


def scaled(counts, n):
    return Counter({rank: n * count for rank, count in counts.items()})


def margin(paid, targets, point):
    """Enclose sum (target_g - paid_g) g^(1-k) on a directed dyadic grid."""
    precision = 224
    unit = 1 << precision
    exponent = 1 - Q(point)
    raw = exponent * unit
    bottom = raw.numerator // raw.denominator
    top = -(-raw.numerator // raw.denominator)
    assert 0 < bottom <= top < unit

    def bound(grade, exponent_bits, upward):
        def round_ratio(value):
            return -(-value // unit) if upward else value // unit

        def root(value):
            value *= unit
            r = isqrt(value)
            return r + (upward and r * r < value)

        result = unit
        repeated_root = grade * unit
        for bit in range(precision - 1, -1, -1):
            repeated_root = root(repeated_root)
            if exponent_bits & (1 << bit):
                result = round_ratio(result * repeated_root)
        return result

    lo = hi = 0
    for grade in sorted(paid.keys() | targets.keys()):
        count = targets[grade] - paid[grade]
        if count:
            low = bound(grade, bottom, False)
            high = bound(grade, top, True)
            endpoints = (low, high) if count > 0 else (high, low)
            lo += count * endpoints[0]
            hi += count * endpoints[1]
    return Q(lo, unit), Q(hi, unit)


def enclose(interval, digits=45):
    grid = 10 ** digits
    lo, hi = [value * grid for value in interval]
    lower = lo.numerator // lo.denominator
    upper = -(-hi.numerator // hi.denominator)

    def show(number):
        whole, fraction = divmod(abs(number), grid)
        return f"{'-' if number < 0 else ''}{whole}.{fraction:0{digits}d}"

    return [show(lower), show(upper)]


def matches_interval(expected, actual):
    """The recomputed interval must lie within the predecessor enclosure."""
    return Q(expected[0]) <= actual[0] <= actual[1] <= Q(expected[1])
