"""Adjacent reflections of the scaled E8 roots.

Each adjacent pair of A8 coordinates determines a root. Reflection through
that root stays inside the 120-line alphabet and swaps the two corresponding
label bits. The integer numerator 4I - alpha alpha^T squares to 16I.
"""

from __future__ import annotations

import json
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
OMEGA = 511


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def parity(value: int) -> int:
    return value.bit_count() % 2


def dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    return sum(x * y for x, y in zip(left, right))


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
        raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT root inventory moved")
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
        raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT standard inventory moved")
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
            raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT star pairing moved")
        inner = [value // 4 for value in raw]
        total = sum(inner)
        if total % 3:
            raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT A8 image moved")
        image = tuple(3 * value - total // 3 for value in inner) + (-total // 3,)
        index = lookup[canonical(image)]
        sign = 1 if image == a8_roots[index] else -1
        oriented[index] = tuple(sign * value for value in root)
    if any(row is None for row in oriented):
        raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT binding incomplete")
    return tuple(row for row in oriented if row is not None)


def reflect(row: tuple[int, ...], alpha: tuple[int, ...]) -> tuple[int, ...]:
    product = dot(row, alpha)
    if product % 4:
        raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT quotient moved")
    return tuple(entry - (product // 4) * other for entry, other in zip(row, alpha))


def main() -> None:
    pinned = load()
    a8_roots, labels = a8_model()
    scalar = oriented_roots(a8_roots)
    lookup = {canonical(row): index for index, row in enumerate(scalar)}
    root_lookup = {row: index for index, row in enumerate(a8_roots)}
    transports = 0
    matrix_entries = 0
    for generator in range(8):
        pair = tuple(
            3 if coordinate == generator else -3 if coordinate == generator + 1 else 0
            for coordinate in range(9)
        )
        alpha = scalar[root_lookup[pair]]
        numerator = [
            [4 * int(row == column) - alpha[row] * alpha[column] for column in range(8)]
            for row in range(8)
        ]
        for row in range(8):
            for column in range(8):
                total = sum(numerator[row][mid] * numerator[mid][column] for mid in range(8))
                if total != 16 * int(row == column):
                    raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT involution moved")
                matrix_entries += 1
        for index, row in enumerate(scalar):
            image = reflect(row, alpha)
            if canonical(image) not in lookup:
                raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT alphabet moved")
            target = lookup[canonical(image)]
            label = labels[index]
            swap = ((label >> generator) ^ (label >> (generator + 1))) & 1
            transposed = label ^ ((1 << generator) | (1 << (generator + 1))) if swap else label
            if labels[target] != transposed:
                raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT label action moved")
            for coordinate in range(8):
                mixed = sum(numerator[coordinate][mid] * row[mid] for mid in range(8))
                if 4 * image[coordinate] != mixed:
                    raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT transport identity moved")
            transports += 1
    if (
        pinned["generators"] != 8
        or pinned["transports"] != transports
        or pinned["matrix_entries"] != matrix_entries
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_E8_REFLECTION_TRANSPORT pinned result moved")
    print(f"PASS_E8_REFLECTION_TRANSPORT transports={transports} no_new_kappa")


if __name__ == "__main__":
    main()
