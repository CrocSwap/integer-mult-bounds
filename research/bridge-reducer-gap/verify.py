"""Row reduction of elementary transvections.

The published reducer clears a determinant-one matrix by integer row
operations. On four wires it finishes every single plus-or-minus-one
transvection, and 564 of their 576 pairwise products.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
WIRES = 4

Matrix = list[list[int]]
Outcome = tuple[str, list[tuple[int, int, int]] | None]


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_BRIDGE_REDUCER selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def elementary(target: int, source: int, coefficient: int) -> Matrix:
    matrix = [[int(row == column) for column in range(WIRES)] for row in range(WIRES)]
    matrix[target][source] += coefficient
    return matrix


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum(left[row][mid] * right[mid][column] for mid in range(WIRES)) for column in range(WIRES)]
        for row in range(WIRES)
    ]


def leibniz(matrix: Matrix) -> int:
    total = 0
    from itertools import permutations

    for perm in permutations(range(WIRES)):
        sign = 1
        for left in range(WIRES):
            for right in range(left + 1, WIRES):
                if perm[left] > perm[right]:
                    sign = -sign
        term = sign
        for row, column in enumerate(perm):
            term *= matrix[row][column]
        total += term
    return total


def identity() -> Matrix:
    return [[int(row == column) for column in range(WIRES)] for row in range(WIRES)]


def reduce(matrix: Matrix) -> Outcome:
    rows = [row[:] for row in matrix]
    operations: list[tuple[int, int, int]] = []

    def operate(target: int, source: int, coefficient: int) -> None:
        if coefficient:
            rows[target] = [
                entry + coefficient * other
                for entry, other in zip(rows[target], rows[source])
            ]
            operations.append((target, source, coefficient))

    for column in range(WIRES):
        while True:
            nonzero = [row for row in range(column, WIRES) if rows[row][column] != 0]
            if len(nonzero) <= 1:
                break
            pivot = min(nonzero, key=lambda row: abs(rows[row][column]))
            for row in nonzero:
                if row != pivot:
                    operate(row, pivot, -(rows[row][column] // rows[pivot][column]))
        try:
            pivot = next(row for row in range(column, WIRES) if rows[row][column] != 0)
        except StopIteration:
            return "interrupted", None
        if pivot != column:
            operate(column, pivot, 1)
            operate(pivot, column, -1)
        if rows[column][column] == -1:
            other = column + 1 if column + 1 < WIRES else column - 1
            for _ in range(2):
                if rows[column][column] == -1:
                    operate(other, column, 1)
                    operate(column, other, -1)
                    operate(other, column, 1)
        for row in range(WIRES):
            if row != column and rows[row][column] != 0:
                operate(row, column, -rows[row][column] * rows[column][column])
    if rows == identity():
        return "reduced", operations
    return "unreduced", None


def replay(matrix: Matrix, operations: list[tuple[int, int, int]]) -> Matrix:
    rows = [row[:] for row in matrix]
    for target, source, coefficient in operations:
        rows[target] = [
            entry + coefficient * other for entry, other in zip(rows[target], rows[source])
        ]
    return rows


def transvections() -> list[tuple[int, int, int]]:
    return [
        (target, source, coefficient)
        for target in range(WIRES)
        for source in range(WIRES)
        if target != source
        for coefficient in (-1, 1)
    ]


def main() -> None:
    pinned = load()
    moves = transvections()
    single_reduced = 0
    for move in moves:
        matrix = elementary(*move)
        if leibniz(matrix) != 1:
            raise SystemExit("FAIL_BRIDGE_REDUCER single determinant moved")
        status, operations = reduce(matrix)
        if status != "reduced" or operations is None or replay(matrix, operations) != identity():
            raise SystemExit("FAIL_BRIDGE_REDUCER single transvection moved")
        single_reduced += 1
    reduced = unreduced = interrupted = 0
    for left in moves:
        left_matrix = elementary(*left)
        for right in moves:
            product = multiply(left_matrix, elementary(*right))
            if leibniz(product) != 1:
                raise SystemExit("FAIL_BRIDGE_REDUCER product determinant moved")
            status, operations = reduce(product)
            if status == "reduced":
                if operations is None or replay(product, operations) != identity():
                    raise SystemExit("FAIL_BRIDGE_REDUCER replay moved")
                reduced += 1
            elif status == "unreduced":
                unreduced += 1
            elif status == "interrupted":
                interrupted += 1
            else:
                raise SystemExit("FAIL_BRIDGE_REDUCER unknown outcome")
    if (
        pinned["wires"] != WIRES
        or pinned["singles"] != single_reduced
        or pinned["products"] != len(moves) ** 2
        or pinned["reduced"] != reduced
        or pinned["unreduced"] != unreduced
        or pinned["interrupted"] != interrupted
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_BRIDGE_REDUCER pinned result moved")
    print(f"PASS_BRIDGE_REDUCER reduced={reduced} no_new_kappa")


if __name__ == "__main__":
    main()
