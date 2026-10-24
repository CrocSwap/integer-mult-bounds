"""One-pair alternating shears.

Forward sends (X, Y) to (X, X+Y). Reverse sends (X, Y) to (X-Y, Y).
Both alternating triples equal (X, Y) to (-Y, X), which the final
exchange (X, Y) to (Y, -X) inverts.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
BOUND = 128

Matrix = tuple[tuple[int, int], tuple[int, int]]
FORWARD: Matrix = ((1, 0), (1, 1))
REVERSE: Matrix = ((1, -1), (0, 1))
EXCHANGE: Matrix = ((0, 1), (-1, 0))
TRIPLE: Matrix = ((0, -1), (1, 0))


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_ALTERNATING_SHEAR selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def apply(matrix: Matrix, point: tuple[int, int]) -> tuple[int, int]:
    x_value, y_value = point
    return (
        matrix[0][0] * x_value + matrix[0][1] * y_value,
        matrix[1][0] * x_value + matrix[1][1] * y_value,
    )


def forward(point: tuple[int, int]) -> tuple[int, int]:
    x_value, y_value = point
    return (x_value, x_value + y_value)


def reverse(point: tuple[int, int]) -> tuple[int, int]:
    x_value, y_value = point
    return (x_value - y_value, y_value)


def exchange(point: tuple[int, int]) -> tuple[int, int]:
    x_value, y_value = point
    return (y_value, -x_value)


def schedules(point: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    forward_first = forward(reverse(forward(point)))
    reverse_first = reverse(forward(reverse(point)))
    return forward_first, reverse_first


def main() -> None:
    pinned = load()
    forward_triple = multiply(FORWARD, multiply(REVERSE, FORWARD))
    reverse_triple = multiply(REVERSE, multiply(FORWARD, REVERSE))
    if forward_triple != TRIPLE or reverse_triple != TRIPLE:
        raise SystemExit("FAIL_ALTERNATING_SHEAR triple moved")
    if multiply(EXCHANGE, TRIPLE) != ((1, 0), (0, 1)):
        raise SystemExit("FAIL_ALTERNATING_SHEAR exchange is not the inverse")
    points = 0
    for x_value in range(-BOUND, BOUND + 1):
        for y_value in range(-BOUND, BOUND + 1):
            point = (x_value, y_value)
            for image in schedules(point):
                if image != (-y_value, x_value):
                    raise SystemExit(f"FAIL_ALTERNATING_SHEAR image {point}")
                if exchange(image) != point:
                    raise SystemExit(f"FAIL_ALTERNATING_SHEAR restore {point}")
            points += 1
    if (
        pinned["coordinate_bound"] != BOUND
        or pinned["points"] != points
        or pinned["schedules"] != 2
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_ALTERNATING_SHEAR pinned result moved")
    print(f"PASS_ALTERNATING_SHEAR points={points} no_new_kappa")


if __name__ == "__main__":
    main()
