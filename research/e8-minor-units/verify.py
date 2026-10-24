"""Integer minors of the scaled E8 root model.

The published witnesses list eight root lines for each of nine characters and
one hundred forbidden pair profiles. Each minor is recomputed in the standard
coordinates scaled by two. Its determinant is a unit over the half-integers.
"""

from __future__ import annotations

import hashlib
import json
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
OMEGA = 511


def load() -> tuple[dict, dict]:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_E8_MINOR_UNITS selected kappa moved")
    pinned = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    raw = (PACKAGE / "WITNESSES.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != pinned["witness_sha256"]:
        raise SystemExit("FAIL_E8_MINOR_UNITS witness hash moved")
    return pinned, json.loads(raw)


def parity(value: int) -> int:
    return value.bit_count() % 2


def dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return sum(x * y for x, y in zip(left, right))


def leibniz(rows: list[tuple[int, ...]]) -> int:
    total = 0
    size = len(rows)
    for perm in permutations(range(size)):
        sign = 1
        for left in range(size):
            for right in range(left + 1, size):
                if perm[left] > perm[right]:
                    sign = -sign
        term = sign
        for row, column in enumerate(perm):
            term *= rows[row][column]
        total += term
    return total


def a8_model() -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    roots: list[tuple[int, ...]] = []
    labels: list[int] = []
    for i, j in combinations(range(9), 2):
        row = [0] * 9
        row[i], row[j] = 3, -3
        roots.append(tuple(row))
        labels.append(OMEGA ^ (1 << i) ^ (1 << j))
    for subset in combinations(range(9), 3):
        roots.append(tuple(2 if index in subset else -1 for index in range(9)))
        labels.append(sum(1 << index for index in subset))
    if len(roots) != 120 or len(set(roots)) != 120 or len(set(labels)) != 120:
        raise SystemExit("FAIL_E8_MINOR_UNITS root inventory moved")
    for index, row in enumerate(roots):
        if sum(row) != 0 or dot(row, row) != 18:
            raise SystemExit("FAIL_E8_MINOR_UNITS root norm moved")
        for other_index, other in enumerate(roots):
            value = dot(row, other)
            if value % 9 != 0:
                raise SystemExit("FAIL_E8_MINOR_UNITS Gram scale moved")
            if parity(labels[index] & labels[other_index]) != (1 + value // 9) % 2:
                raise SystemExit("FAIL_E8_MINOR_UNITS label pairing moved")
    return tuple(roots), tuple(labels)


def standard_roots() -> tuple[tuple[int, ...], ...]:
    rows = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            rows.append(tuple(row))
    rows += [
        row
        for row in product((-1, 1), repeat=8)
        if row[0] == 1 and sum(entry < 0 for entry in row) % 2 == 0
    ]
    if len(rows) != 120 or len(set(rows)) != 120:
        raise SystemExit("FAIL_E8_MINOR_UNITS standard inventory moved")
    return tuple(rows)


def canonical(row: tuple[int, ...]) -> tuple[int, ...]:
    return row if next(entry for entry in row if entry) > 0 else tuple(-entry for entry in row)


def oriented_roots(a8_roots: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    star = []
    for index in range(1, 8):
        row = [0] * 8
        row[0] = row[index] = 2
        star.append(tuple(row))
    star.append((1,) * 8)
    lookup = {canonical(row): index for index, row in enumerate(a8_roots)}
    oriented: list[tuple[int, ...] | None] = [None] * 120
    for root in standard_roots():
        raw = [dot(root, other) for other in star]
        if any(value % 4 for value in raw):
            raise SystemExit("FAIL_E8_MINOR_UNITS star pairing moved")
        inner = [value // 4 for value in raw]
        total = sum(inner)
        if total % 3:
            raise SystemExit("FAIL_E8_MINOR_UNITS A8 image moved")
        image = tuple(3 * value - total // 3 for value in inner) + (-total // 3,)
        if canonical(image) not in lookup:
            raise SystemExit("FAIL_E8_MINOR_UNITS missing A8 image")
        index = lookup[canonical(image)]
        sign = 1 if image == a8_roots[index] else -1
        if oriented[index] is not None:
            raise SystemExit("FAIL_E8_MINOR_UNITS binding collision")
        oriented[index] = tuple(sign * value for value in root)
    if any(row is None for row in oriented):
        raise SystemExit("FAIL_E8_MINOR_UNITS binding incomplete")
    bound = tuple(row for row in oriented if row is not None)
    for index, row in enumerate(bound):
        for other_index, other in enumerate(bound):
            if 9 * dot(row, other) != 4 * dot(a8_roots[index], a8_roots[other_index]):
                raise SystemExit("FAIL_E8_MINOR_UNITS isometry moved")
    return bound


def profiles() -> list[tuple[tuple[int, int, int, int], int, int]]:
    found = []
    for n00 in range(10):
        for n01 in range(10 - n00):
            for n10 in range(10 - n00 - n01):
                n11 = 9 - n00 - n01 - n10
                left = ((1 << (n10 + n11)) - 1) << (n00 + n01)
                right = (((1 << n01) - 1) << n00) | (((1 << n11) - 1) << (n00 + n01 + n10))
                if left and right and left != right:
                    found.append(((n00, n01, n10, n11), left, right))
    return found


def forbidden(left: int, right: int) -> bool:
    return bool(
        parity(left & right)
        or (
            parity(left) == parity(right) == 0
            and (left.bit_count() // 2) % 2 == (right.bit_count() // 2) % 2
        )
    )


def power_of_two(value: int) -> bool:
    absolute = abs(value)
    return absolute != 0 and absolute & (absolute - 1) == 0


def main() -> None:
    pinned, witnesses = load()
    a8_roots, labels = a8_model()
    rows = oriented_roots(a8_roots)
    listed = profiles()
    forbidden_profiles = {
        counts: (left, right) for counts, left, right in listed if forbidden(left, right)
    }
    singles = witnesses["single_types"]
    pairs = witnesses["forbidden_pairs"]
    if len(singles) != 9 or len(pairs) != 100 or len(listed) != 192 or len(forbidden_profiles) != 100:
        raise SystemExit("FAIL_E8_MINOR_UNITS inventory moved")
    absolutes = set()
    seen = set()
    for item in singles:
        weight = item["weight"]
        normal = item["normal"]
        if weight in seen or normal != (1 << weight) - 1:
            raise SystemExit("FAIL_E8_MINOR_UNITS single binding moved")
        seen.add(weight)
        value = leibniz([rows[index] for index in item["rows"]])
        if value != item["determinant"] or not power_of_two(value):
            raise SystemExit("FAIL_E8_MINOR_UNITS single determinant moved")
        for index in item["rows"]:
            if not parity(labels[index] & normal):
                raise SystemExit("FAIL_E8_MINOR_UNITS single support moved")
        absolutes.add(abs(value))
    seen_pairs = set()
    for item in pairs:
        counts = tuple(item["counts"])
        if counts in seen_pairs or forbidden_profiles.get(counts) != (item["a"], item["b"]):
            raise SystemExit("FAIL_E8_MINOR_UNITS pair binding moved")
        seen_pairs.add(counts)
        value = leibniz([rows[index] for index in item["rows"]])
        if value != item["determinant"] or not power_of_two(value):
            raise SystemExit("FAIL_E8_MINOR_UNITS pair determinant moved")
        for index in item["rows"]:
            if not (parity(labels[index] & item["a"]) and parity(labels[index] & item["b"])):
                raise SystemExit("FAIL_E8_MINOR_UNITS pair support moved")
        absolutes.add(abs(value))
    if seen != set(range(1, 10)) or seen_pairs != set(forbidden_profiles):
        raise SystemExit("FAIL_E8_MINOR_UNITS coverage moved")
    if (
        pinned["roots"] != 120
        or pinned["profiles"] != 192
        or pinned["forbidden_profiles"] != 100
        or pinned["minors"] != 109
        or pinned["determinant_absolutes"] != sorted(absolutes)
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_E8_MINOR_UNITS pinned result moved")
    print("PASS_E8_MINOR_UNITS minors=109 no_new_kappa")


if __name__ == "__main__":
    main()
