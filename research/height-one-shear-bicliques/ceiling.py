"""Separate rational-elimination and first-row enumeration. Apache-2.0."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rank(rows: list) -> int:
    size = len(rows)
    require(size in (2, 4) and all(len(row) == size for row in rows),
            "only square matrices of order two or four are supported")
    matrix = [[Fraction(x) for x in row] for row in rows]
    pivot_row = 0
    for col in range(size):
        candidates = [r for r in range(pivot_row, size) if matrix[r][col]]
        if not candidates:
            continue
        chosen = candidates[0]
        matrix[pivot_row], matrix[chosen] = matrix[chosen], matrix[pivot_row]
        scale = matrix[pivot_row][col]
        matrix[pivot_row] = [x / scale for x in matrix[pivot_row]]
        for r in range(pivot_row + 1, size):
            factor = matrix[r][col]
            matrix[r] = [x - factor * y
                         for x, y in zip(matrix[r], matrix[pivot_row])]
        pivot_row += 1
    return pivot_row


def rank_table(matrices: tuple) -> list:
    table = [[0] * 81 for _ in range(81)]
    for i, a in enumerate(matrices):
        for j, b in enumerate(matrices):
            delta = [x - y for x, y in zip(a, b)]
            table[i][j] = rank([delta[:2], delta[2:]])
    return table


def first_row_ceiling(table: list) -> tuple:
    histogram = Counter()
    inspected = 0
    for first_rows in combinations(range(9), 3):
        for second_rows in product(range(9), repeat=3):
            a, b, c = tuple(9 * u + v for u, v in zip(first_rows, second_rows))
            inspected += 1
            if table[a][b] == table[a][c] == table[b][c] == 2:
                common = sum(table[a][j] == table[b][j] == table[c][j] == 1
                             for j in range(81))
                require(common <= 6, "seven common contacts found")
                histogram[common] += 1
    require(inspected == 61236, "first-row enumeration is incomplete")
    return dict(sorted(histogram.items())), inspected


def shear(matrix: tuple) -> list:
    a, b, c, d = matrix
    return [[1, 0, a, b], [0, 1, c, d], [0, 0, 1, 0], [0, 0, 0, 1]]


def check_attainment() -> int:
    roots = ((-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0))
    left = tuple((a, b, -a - b, a) for a, b in roots)
    right = tuple((a, b, b, -a - b) for a, b in roots)
    pairs = 0
    for side_a, side_b in product(range(2), repeat=2):
        for i, j in product(range(6), repeat=2):
            a, b = (left, right)[side_a][i], (left, right)[side_b][j]
            sa, sb = shear(a), shear(b)
            delta = [[x - y for x, y in zip(row_a, row_b)]
                     for row_a, row_b in zip(sa, sb)]
            expected = 1 if side_a != side_b else (0 if i == j else 2)
            require(rank(delta) == expected, "shear witness rank differs")
            pairs += 1
    return pairs


def rank_controls() -> int:
    controls = (
        ([[0, 0], [0, 0]], 0),
        ([[1, 2], [2, 4]], 1),
        ([[0, 1], [1, 0]], 2),
        ([[1, 1], [1, 2]], 2),
        ([[Fraction(1, 2), 1], [1, 2]], 1),
    )
    for matrix, expected in controls:
        require(rank(matrix) == expected, "elimination control failed")
    return len(controls)


def main() -> None:
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    matrices = tuple(product((-1, 0, 1), repeat=4))
    histogram, inspected = first_row_ceiling(rank_table(matrices))
    require(sum(histogram.values()) == 23488, "rank-two triple census differs")
    root = Path(__file__).resolve().parent
    print(json.dumps({
        "status": "PASS_FIRST_ROW_SHEAR_CEILING",
        "balanced_optimum": 6,
        "first_row_candidates": inspected,
        "rank_two_triples": sum(histogram.values()),
        "common_rank_one_histogram": histogram,
        "ordered_shear_pairs": check_attainment(),
        "elimination_controls": rank_controls(),
        "source_sha256": sha256((root / "ceiling.py").read_bytes()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
