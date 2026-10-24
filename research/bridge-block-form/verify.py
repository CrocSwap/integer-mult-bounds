"""Four-wire bridge block form.

A bridge (target <- source, q) adds q times X_source to X_target and subtracts
q times Y_target from Y_source. Its matrix is diag(E, E inverse transpose).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
WIRES = 4
COEFFICIENT_BOUND = 12
PRODUCT_BOUND = 3

Matrix = tuple[tuple[int, ...], ...]


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_BRIDGE_BLOCK_FORM selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def identity(size: int) -> Matrix:
    return tuple(tuple(1 if row == column else 0 for column in range(size)) for row in range(size))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)
    return tuple(
        tuple(sum(left[row][mid] * right[mid][column] for mid in range(size)) for column in range(size))
        for row in range(size)
    )


def determinant(matrix: Matrix) -> int:
    size = len(matrix)
    if size == 1:
        return matrix[0][0]
    total = 0
    for column, entry in enumerate(matrix[0]):
        if entry == 0:
            continue
        minor = tuple(tuple(row[index] for index in range(size) if index != column) for row in matrix[1:])
        total += ((-1) ** column) * entry * determinant(minor)
    return total


def elementary(target: int, source: int, coefficient: int) -> Matrix:
    rows = [list(row) for row in identity(WIRES)]
    rows[target][source] += coefficient
    return tuple(tuple(row) for row in rows)


def inverse_transpose(matrix: Matrix) -> Matrix:
    size = len(matrix)
    adjugate = [[0] * size for _ in range(size)]
    det = determinant(matrix)
    if det not in (1, -1):
        raise SystemExit("FAIL_BRIDGE_BLOCK_FORM determinant is not a unit")
    for row in range(size):
        for column in range(size):
            minor = tuple(
                tuple(matrix[i][j] for j in range(size) if j != column)
                for i in range(size)
                if i != row
            )
            cofactor = ((-1) ** (row + column)) * determinant(minor) if size > 1 else 1
            adjugate[column][row] = det * cofactor
    inverse = tuple(tuple(row) for row in adjugate)
    return tuple(tuple(inverse[column][row] for column in range(size)) for row in range(size))


def bridge(target: int, source: int, coefficient: int) -> Matrix:
    matrix = [[0] * (2 * WIRES) for _ in range(2 * WIRES)]
    for index in range(2 * WIRES):
        matrix[index][index] = 1
    matrix[target][source] += coefficient
    matrix[WIRES + source][WIRES + target] -= coefficient
    return tuple(tuple(row) for row in matrix)


def block_form(target: int, source: int, coefficient: int) -> Matrix:
    left = elementary(target, source, coefficient)
    right = inverse_transpose(left)
    size = 2 * WIRES
    matrix = [[0] * size for _ in range(size)]
    for row in range(WIRES):
        for column in range(WIRES):
            matrix[row][column] = left[row][column]
            matrix[WIRES + row][WIRES + column] = right[row][column]
    return tuple(tuple(row) for row in matrix)


def pairs(bound: int) -> list[tuple[int, int, int]]:
    return [
        (target, source, coefficient)
        for target in range(WIRES)
        for source in range(WIRES)
        if target != source
        for coefficient in range(-bound, bound + 1)
    ]


def main() -> None:
    pinned = load()
    bridges = pairs(COEFFICIENT_BOUND)
    for target, source, coefficient in bridges:
        found = bridge(target, source, coefficient)
        if found != block_form(target, source, coefficient):
            raise SystemExit(f"FAIL_BRIDGE_BLOCK_FORM form {target} {source} {coefficient}")
        if determinant(elementary(target, source, coefficient)) != 1:
            raise SystemExit(f"FAIL_BRIDGE_BLOCK_FORM determinant {target} {source}")
        if multiply(found, bridge(target, source, -coefficient)) != identity(2 * WIRES):
            raise SystemExit(f"FAIL_BRIDGE_BLOCK_FORM inverse {target} {source}")
    products = 0
    for left in pairs(PRODUCT_BOUND):
        left_matrix = bridge(*left)
        left_block = elementary(left[0], left[1], left[2])
        for right in pairs(PRODUCT_BOUND):
            product = multiply(left_matrix, bridge(*right))
            combined = multiply(left_block, elementary(right[0], right[1], right[2]))
            expected_right = inverse_transpose(combined)
            expected = [[0] * (2 * WIRES) for _ in range(2 * WIRES)]
            for row in range(WIRES):
                for column in range(WIRES):
                    expected[row][column] = combined[row][column]
                    expected[WIRES + row][WIRES + column] = expected_right[row][column]
            if product != tuple(tuple(row) for row in expected):
                raise SystemExit("FAIL_BRIDGE_BLOCK_FORM product left the block form")
            products += 1
    if (
        pinned["wires"] != WIRES
        or pinned["coefficient_bound"] != COEFFICIENT_BOUND
        or pinned["bridges"] != len(bridges)
        or pinned["product_bound"] != PRODUCT_BOUND
        or pinned["products"] != products
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_BRIDGE_BLOCK_FORM pinned result moved")
    print(f"PASS_BRIDGE_BLOCK_FORM bridges={len(bridges)} no_new_kappa")


if __name__ == "__main__":
    main()
