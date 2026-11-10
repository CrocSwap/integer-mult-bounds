"""Exact common reserves for the retained two-type row menu."""

from fractions import Fraction
from hashlib import sha256
import json

Row = tuple[Fraction, Fraction]
Menu = tuple[tuple[Row, ...], tuple[Row, ...]]
Vector = tuple[Fraction, Fraction]
SOURCE_SHA256 = "8819bb327b318bed314cc6cd12781e4ad148a18a4cf77fa749167bc7b1c3c3b4"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_menu(data: bytes) -> Menu:
    """Authenticate the exact source bytes before parsing their four rows."""
    require(sha256(data).hexdigest() == SOURCE_SHA256, "source hash mismatch")
    raw = json.loads(data)
    require(raw["schema"] == "adaptive-row-bill/v1", "unexpected schema")
    groups = raw["rows"]
    require(len(groups) == 2, "expected two types")
    parsed = []
    for group in groups:
        require(len(group) == 2, "expected two rows per type")
        rows = []
        for row in group:
            require(len(row) == 2, "expected two coefficients")
            a, b = (Fraction(value) for value in row)
            require(a >= 0 and b >= 0, "negative row")
            rows.append((a, b))
        parsed.append(tuple(rows))
    return parsed[0], parsed[1]


def common_ratio(menu: Menu, weight: Vector) -> Fraction:
    require(len(weight) == 2 and min(weight) > 0, "positive two-type weight required")
    return max(
        (row[0] * weight[0] + row[1] * weight[1]) / weight[i]
        for i in range(2)
        for row in menu[i]
    )


def check_certificate(menu: Menu, weight: Vector, ratio: Fraction) -> None:
    require(0 <= ratio < 1, "ratio must be in [0,1)")
    require(common_ratio(menu, weight) <= ratio, "row exceeds claimed ratio")


def next_prefix(menu: Menu, value: Vector) -> Vector:
    require(len(value) == 2 and min(value) >= 0, "nonnegative prefix required")
    values = tuple(
        1 + max(row[0] * value[0] + row[1] * value[1] for row in group)
        for group in menu
    )
    return values[0], values[1]


def first_cutoff(ratio: Fraction, prefactor: Fraction, bits: int) -> int:
    require(0 < ratio < 1 and prefactor >= 1, "invalid tail bound")
    require(type(bits) is int and 1 <= bits <= 128, "bits outside 1..128")
    threshold = Fraction(1, 2**bits)
    tail = prefactor
    for depth in range(1025):
        if tail <= threshold:
            return depth
        tail *= ratio
    raise ValueError("cutoff exceeds the explicit 1024-depth limit")
