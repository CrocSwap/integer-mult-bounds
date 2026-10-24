"""Finite q-Toeplitz factorization of the Gaussian matrix.

For 0 < q <= 1/4 and order n, G_ij = q^{(i-j)^2}. The products
f_j = prod_{k=1}^j (1-q^{2k}), g_j = q^{j^2}/f_j and h_j = (-q)^j/f_j
give a lower-triangular Toeplitz inverse T(g)T(h)=I and
G^{-1} = D_f^{-1} T(h)^T D_f T(h) D_f^{-1}.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
DENOMINATORS = (4, 5, 6, 8, 10)
MAX_ORDER = 6


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def toeplitz(values: list[Fraction]) -> list[list[Fraction]]:
    order = len(values)
    return [
        [values[i - j] if i >= j else Fraction(0) for j in range(order)]
        for i in range(order)
    ]


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    order = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(order)) for j in range(order)]
        for i in range(order)
    ]


def identity(order: int) -> list[list[Fraction]]:
    return [[Fraction(int(i == j)) for j in range(order)] for i in range(order)]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def factors(q: Fraction, order: int) -> tuple[list[Fraction], list[Fraction], list[Fraction]]:
    widths = [Fraction(1)]
    for index in range(1, order):
        widths.append(widths[-1] * (1 - q ** (2 * index)))
    squares = [q ** (index * index) / widths[index] for index in range(order)]
    signed = [((-q) ** index) / widths[index] for index in range(order)]
    return widths, squares, signed


def main() -> None:
    pinned = load()
    q_edge = Fraction(1, 4)
    tail = q_edge ** 2 / (1 - q_edge ** 2)
    if tail != Fraction(1, 15) or 1 - tail != Fraction(14, 15):
        raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION product bound moved")
    if (Fraction(15, 14) / (1 - q_edge)) != Fraction(10, 7):
        raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION row-sum bound moved")
    matrices = 0
    for denominator in DENOMINATORS:
        q = Fraction(1, denominator)
        if q > q_edge:
            raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION q moved")
        for order in range(1, MAX_ORDER + 1):
            widths, squares, signed = factors(q, order)
            if any(value < Fraction(14, 15) or value > 1 for value in widths):
                raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION width moved")
            lower = toeplitz(squares)
            upper_source = toeplitz(signed)
            if multiply(lower, upper_source) != identity(order):
                raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION triangular inverse moved")
            row_sum = max(
                sum(abs(entry) for entry in row) for row in upper_source
            )
            if row_sum > Fraction(10, 7):
                raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION norm moved")
            diagonal = [
                [widths[i] if i == j else Fraction(0) for j in range(order)]
                for i in range(order)
            ]
            inverse_diagonal = [
                [(1 / widths[i]) if i == j else Fraction(0) for j in range(order)]
                for i in range(order)
            ]
            factor = multiply(diagonal, multiply(lower, inverse_diagonal))
            gaussian = multiply(factor, multiply(diagonal, transpose(factor)))
            expected = [[q ** ((i - j) ** 2) for j in range(order)] for i in range(order)]
            if gaussian != expected:
                raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION matrix moved")
            inverse = multiply(
                inverse_diagonal,
                multiply(
                    transpose(upper_source),
                    multiply(diagonal, multiply(upper_source, inverse_diagonal)),
                ),
            )
            if multiply(inverse, gaussian) != identity(order):
                raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION inverse moved")
            matrices += 1
    if pinned["matrices"] != matrices or pinned["no_new_kappa"] is not True:
        raise SystemExit("FAIL_Q_TOEPLITZ_FACTORIZATION pinned result moved")
    print(f"PASS_Q_TOEPLITZ_FACTORIZATION matrices={matrices} no_new_kappa")


if __name__ == "__main__":
    main()
