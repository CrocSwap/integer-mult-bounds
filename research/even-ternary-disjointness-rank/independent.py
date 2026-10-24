#!/usr/bin/env python3
"""Generate finite F_3 rank fixtures for Boolean disjointness matrices.

This standalone script constructs the matrices from subset definitions and
computes ranks by modular Gaussian elimination. Its finite outputs are
fixtures only; they do not establish a formula for general h.

Prepared for Krzysztof Wojt by a separately tasked OpenAI Codex Luna worker,
given only the matrix definition and finite dimensions, not the rank formula.
Inspected and rerun by the primary Codex agent. This is implementation
separation within AI-assisted work, not independent human review. Apache-2.0.
"""

from __future__ import annotations

import json


MODULUS = 3
K = ((1, 1), (1, 0))


def rank_mod3(matrix: list[list[int]]) -> int:
    """Return the rank over F_3 by ordinary row reduction."""
    if not matrix:
        return 0

    row_count = len(matrix)
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("rank_mod3 requires a rectangular matrix")

    work = [[entry % MODULUS for entry in row] for row in matrix]
    pivot_row = 0

    for column in range(column_count):
        selected = None
        for candidate in range(pivot_row, row_count):
            if work[candidate][column] != 0:
                selected = candidate
                break
        if selected is None:
            continue

        if selected != pivot_row:
            work[pivot_row], work[selected] = work[selected], work[pivot_row]

        pivot_value = work[pivot_row][column]
        inverse = pow(pivot_value, -1, MODULUS)
        for j in range(column, column_count):
            work[pivot_row][j] = (work[pivot_row][j] * inverse) % MODULUS

        for other in range(row_count):
            if other == pivot_row:
                continue
            factor = work[other][column]
            if factor == 0:
                continue
            for j in range(column, column_count):
                work[other][j] = (
                    work[other][j] - factor * work[pivot_row][j]
                ) % MODULUS

        pivot_row += 1
        if pivot_row == row_count:
            break

    return pivot_row


def proper_subset_matrices(h: int) -> tuple[list[int], list[list[int]], list[list[int]]]:
    """Construct A_h and B_h=I-A_h on nonempty proper subsets of [h]."""
    if h < 2:
        raise ValueError("h must be at least 2 for nonempty proper subsets")

    subsets = list(range(1, (1 << h) - 1))
    adjacency = [
        [int((left & right) == 0) for right in subsets]
        for left in subsets
    ]
    b_matrix = [
        [((1 if i == j else 0) - adjacency[i][j]) % MODULUS
         for j in range(len(subsets))]
        for i in range(len(subsets))
    ]
    return subsets, adjacency, b_matrix


def kronecker_product(
    left: tuple[tuple[int, ...], ...] | list[list[int]],
    right: tuple[tuple[int, ...], ...] | list[list[int]],
) -> list[list[int]]:
    """Form a Kronecker product with rows ordered by row-pair blocks."""
    product: list[list[int]] = []
    for left_row in left:
        for right_row in right:
            product.append([
                left_entry * right_entry
                for left_entry in left_row
                for right_entry in right_row
            ])
    return product


def full_tensor_matrix(h: int) -> list[list[int]]:
    """Construct I-K^tensor h on all subsets, reducing entries modulo 3."""
    if h < 1:
        raise ValueError("h must be positive for the tensor matrix")

    tensor: list[list[int]] = [[1]]
    for _ in range(h):
        tensor = kronecker_product(tensor, K)

    return [
        [((1 if i == j else 0) - tensor[i][j]) % MODULUS
         for j in range(len(tensor))]
        for i in range(len(tensor))
    ]


def principal_matrix_without(matrix: list[list[int]], removed: int) -> list[list[int]]:
    """Delete one indexed row and the corresponding column."""
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("principal deletion requires a square matrix")
    if removed < 0 or removed >= size:
        raise IndexError("deleted index is outside the matrix")

    kept = [index for index in range(size) if index != removed]
    return [[matrix[i][j] for j in kept] for i in kept]


def collect_results() -> dict[str, object]:
    proper_results: dict[str, dict[str, int]] = {}
    for h in (2, 4, 6, 8):
        subsets, _adjacency, b_matrix = proper_subset_matrices(h)
        proper_results[str(h)] = {
            "dimension": len(subsets),
            "rank_mod_3": rank_mod3(b_matrix),
        }

    tensor_results: dict[str, dict[str, int]] = {}
    for h in (2, 4, 6):
        full_matrix = full_tensor_matrix(h)
        full_dimension = len(full_matrix)
        tensor_results[str(h)] = {
            "dimension": full_dimension,
            "full_rank_mod_3": rank_mod3(full_matrix),
            "rank_after_deleting_empty_subset": rank_mod3(
                principal_matrix_without(full_matrix, 0)
            ),
            "rank_after_deleting_full_subset": rank_mod3(
                principal_matrix_without(full_matrix, full_dimension - 1)
            ),
        }

    return {
        "field": "F_3",
        "proper_nonempty_subset_matrix_I_minus_A": proper_results,
        "full_subset_matrix_I_minus_K_tensor_h": tensor_results,
    }


def main() -> None:
    print(json.dumps(collect_results(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
