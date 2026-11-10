"""Exact sparse multiplication for the pinned square rational matrices."""

from fractions import Fraction


def multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    """Return every entry, omitting only products with an exact zero operand."""
    order = len(left)
    if not 1 <= order <= 6 or len(right) != order:
        raise ValueError("matrix order must be in 1..6")
    if any(len(row) != order for row in left + right):
        raise ValueError("square matrices of equal order required")
    result = [[Fraction(0)] * order for _ in range(order)]
    for i, row in enumerate(left):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(right[k]):
                    if other:
                        result[i][j] += value * other
    return result
