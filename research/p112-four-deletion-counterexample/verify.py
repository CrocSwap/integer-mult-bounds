#!/usr/bin/env python3
"""Exact, standard-library check of the four-deletion quantifier example."""

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MINOR_COLUMNS = (0, 2, 3, 4, 6)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integers(value: object, count: int, low: int, high: int) -> tuple[int, ...]:
    require(isinstance(value, list) and len(value) == count, "wrong vector length")
    require(all(type(x) is int and low <= x <= high for x in value), "invalid integer")
    return tuple(value)


def binary_rank(values: list[int] | tuple[int, ...] | set[int]) -> int:
    """Eliminate at most 112 rows of nine bits, from the highest bit down."""
    assert len(values) <= 112
    pivots = [0] * 9
    for value in values:
        assert 0 <= value < 512
        for bit in range(8, -1, -1):
            if not value & (1 << bit):
                continue
            if pivots[bit]:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return sum(value != 0 for value in pivots)


def binary_span(basis: tuple[int, ...]) -> set[int]:
    assert len(basis) <= 9
    span = {0}
    for value in basis:
        span |= {point ^ value for point in span}
    assert len(span) <= 512
    return span


def root_lines() -> set[tuple[int, ...]]:
    """Doubled E8 roots, with the first nonzero coordinate positive."""
    lines = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            vector = [0] * 8
            vector[i], vector[j] = 2, sign
            lines.add(tuple(vector))
    for tail in product((-1, 1), repeat=7):
        vector = (1,) + tail
        if sum(x < 0 for x in vector) % 2 == 0:
            lines.add(vector)
    assert len(lines) == 120
    return lines


def root_label(vector: tuple[int, ...]) -> int:
    """256 plus the parity of the Bourbaki simple-root coordinates.

    The simple roots, doubled, are (1,-1,-1,-1,-1,-1,-1,1),
    (2,2,0,...), (-2,2,0,...), (0,-2,2,0,...), and successive differences.
    The triangular equations below solve vector = sum c_i alpha_i.
    """
    assert len(vector) == 8
    coordinates = [0] * 8
    coordinates[0] = vector[7]
    coordinates[7] = (vector[6] + coordinates[0]) // 2
    for j in range(6, 2, -1):
        coordinates[j] = (vector[j - 1] + coordinates[0]) // 2 + coordinates[j + 1]
    coordinates[1] = (vector[0] + vector[1] + 2 * coordinates[3]) // 4
    coordinates[2] = (
        -vector[0] + vector[1] + 2 * coordinates[0] + 2 * coordinates[3]
    ) // 4
    return 256 + sum((value % 2) << j for j, value in enumerate(coordinates))


def dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    assert len(left) == len(right) == 8
    return sum(left[j] * right[j] for j in range(8))


def determinant(rows: list[list[int]]) -> Fraction:
    assert len(rows) == 5 and all(len(row) == 5 for row in rows)
    matrix = [[Fraction(value) for value in row] for row in rows]
    result = Fraction(1)
    for col in range(5):
        pivot = next((i for i in range(col, 5) if matrix[i][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
            result = -result
        scale = matrix[col][col]
        result *= scale
        matrix[col] = [value / scale for value in matrix[col]]
        for i in range(col + 1, 5):
            factor = matrix[i][col]
            matrix[i] = [matrix[i][j] - factor * matrix[col][j] for j in range(5)]
    return result


def geometry(witness: dict) -> dict[int, tuple[int, ...]]:
    require(witness.get("schema") == "p112-four-deletion/v1", "wrong schema")
    raw_frame = witness.get("omitted_frame")
    require(
        isinstance(raw_frame, list) and len(raw_frame) == 8, "frame needs eight lines"
    )
    frame = [integers(row, 8, -2, 2) for row in raw_frame]
    full = root_lines()
    require(len(set(frame)) == 8 and set(frame) <= full, "invalid root frame")
    require(
        all(dot(a, b) == 0 for a, b in combinations(frame, 2)), "nonorthogonal frame"
    )
    lines = {root_label(vector): vector for vector in full - set(frame)}
    require(len(lines) == 112, "root labels collide")
    return lines


def spaces(
    witness: dict, lines: dict[int, tuple[int, ...]]
) -> tuple[set[int], list[int]]:
    collections = []
    for key in ("V1_basis", "V2_basis"):
        basis = integers(witness.get(key), 6, 1, 511)
        require(binary_rank(basis) == 6, "space must have dimension six")
        collections.append(set(lines) & binary_span(basis))
    sizes = [len(part) for part in collections]
    require(sizes == [20, 16], "unexpected Lambda sizes")
    return collections[0] | collections[1], sizes


def check_direction(row: dict, lines: dict, covered: set[int]) -> tuple[dict, set[int]]:
    require(isinstance(row, dict), "direction must be an object")
    vector = integers(row.get("vector"), 8, -2, 2)
    require(any(vector), "zero direction")
    raw_cut = row.get("remove_labels")
    require(
        isinstance(raw_cut, list) and 1 <= len(raw_cut) <= 4, "deletion budget is four"
    )
    cut = set(integers(raw_cut, len(raw_cut), 256, 511))
    require(len(cut) == len(raw_cut), "duplicate removed label")
    off = {label for label, root in lines.items() if dot(vector, root) != 0}
    residual = off - covered
    require(cut <= residual, "removed line is not in the residual")
    require(binary_rank(residual) == 8, "residual rank is not eight")
    require(binary_rank(residual - cut) == 7, "deletion does not leave rank seven")
    # Rank eight gives 255 distinct nonzero restricted binary characters.
    supports = {
        frozenset(label for label in residual if (label & char).bit_count() % 2)
        for char in range(1, 512)
    } - {frozenset()}
    require(len(supports) == 255, "incomplete restricted character space")
    small = [support for support in supports if len(support) < 12]
    require(len(small) == 1 and small[0] == cut, "cut below twelve is not unique")
    next_size = min(len(support) for support in supports if support != cut)
    return {
        "source_direction_id": row.get("source_direction_id"),
        "off_size": len(off),
        "residual_size": len(residual),
        "rank_before": 8,
        "removed_labels": sorted(cut),
        "rank_after": 7,
        "next_character_support_size": next_size,
    }, cut


def check(witness: dict) -> dict:
    require(isinstance(witness, dict), "witness must be an object")
    lines = geometry(witness)
    covered, sizes = spaces(witness, lines)
    rows = witness.get("directions")
    require(isinstance(rows, list) and len(rows) == 5, "need five directions")
    reports = []
    common_cut: set[int] = set()
    for row in rows:
        report, cut = check_direction(row, lines, covered)
        reports.append(report)
        common_cut |= cut
    vectors = [integers(row["vector"], 8, -2, 2) for row in rows]
    minor = determinant([[vector[j] for j in MINOR_COLUMNS] for vector in vectors])
    require(minor != 0, "directions are dependent")
    require(len(common_cut) == 12, "common deletion upper bound is not twelve")
    for vector in vectors:
        remaining = {
            label
            for label, root in lines.items()
            if dot(vector, root) != 0 and label not in covered | common_cut
        }
        require(binary_rank(remaining) <= 7, "common deletion upper bound fails")
    return {
        "status": "PASS_P112_FOUR_DELETION_COUNTEREXAMPLE",
        "line_count": len(lines),
        "Lambda_sizes": sizes,
        "covered_union_size": len(covered),
        "independent_direction_count": 5,
        "minor_columns_zero_based": list(MINOR_COLUMNS),
        "minor_determinant": str(minor),
        "per_direction_budget": 4,
        "minimum_common_deletions": 12,
        "common_deletion_labels": sorted(common_cut),
        "directions": reports,
    }


def check_source(path: Path, witness: dict) -> dict:
    """Optional exact-head translation check; not needed for the E8 proof."""
    raw = bounded_bytes(path, 2 * 1024 * 1024)
    pin = read_json(PACKAGE / "SOURCES.json")["predecessor"]
    require(
        hashlib.sha256(raw).hexdigest() == pin["data80_sha256"], "source hash mismatch"
    )
    rows = raw.decode("utf-8").splitlines()
    labels = list(map(int, rows[0].split()))
    roots = [tuple(map(int, row.split())) for row in rows[2:114]]
    require(len(labels) == len(roots) == 112, "source root count differs")
    lines = geometry(witness)
    canonical_labels = [root_label(root) for root in roots]
    require(set(canonical_labels) == set(lines), "source P112 differs")
    # A one-bit cyclic rotation is an invertible linear map on F2^9.
    rotated = [((label << 1) & 511) | (label >> 8) for label in canonical_labels]
    require(rotated == labels, "source label rotation differs")
    binding = witness["source_binding"]
    for key in ("V1_basis", "V2_basis"):
        source_basis = integers(binding[key], 6, 1, 511)
        require(binary_rank(source_basis) == 6, "source space dimension differs")
        canonical_span = binary_span(tuple(witness[key]))
        source_span = {((label << 1) & 511) | (label >> 8) for label in canonical_span}
        require(
            source_span == binary_span(source_basis), "source space translation differs"
        )
    for row in witness["directions"]:
        direction_id = row["source_direction_id"]
        require(type(direction_id) is int and 0 <= direction_id < 5680, "bad source id")
        fields = rows[115 + direction_id].split(":")[0].split()
        require(fields[0] == "1", "source direction is not a single vector")
        require(list(map(int, fields[1:])) == row["vector"], "source direction differs")
        indices = integers(
            row["source_remove_indices"], len(row["remove_labels"]), 0, 111
        )
        translated = {root_label(roots[i]) for i in indices}
        require(
            translated == set(row["remove_labels"]),
            "source deletion translation differs",
        )
    return {"head": pin["head"], "data80_sha256": pin["data80_sha256"]}


def bounded_bytes(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "input exceeds byte limit")
    return raw


def read_json(path: Path) -> object:
    return json.loads(bounded_bytes(path, 32768).decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness", type=Path, default=PACKAGE / "WITNESS.json")
    parser.add_argument("--source-data", type=Path)
    args = parser.parse_args()
    try:
        witness = read_json(args.witness)
        report = check(witness)
        require(
            report == read_json(PACKAGE / "RESULT.json"), "result differs from receipt"
        )
        if args.source_data is not None:
            report["source_binding"] = check_source(args.source_data, witness)
    except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
        parser.exit(1, f"verification failed: {error}\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
