"""Exact reference model for restoring signed unit row additions.

Produced by Nick Petalas. Apache-2.0.
"""

from __future__ import annotations

MAX_ROWS = 8
MAX_GATES = 256
Gate = tuple[int, int, int]
Matrix = tuple[tuple[int, ...], ...]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fibonacci(index: int) -> int:
    need(type(index) is int and 0 <= index <= MAX_GATES + 2, "Fibonacci index")
    previous, current = 0, 1
    for _ in range(index):
        previous, current = current, previous + current
    return previous


def validate(n: int, word: tuple[Gate, ...]) -> None:
    need(type(n) is int and 1 <= n <= MAX_ROWS, "row count")
    need(type(word) is tuple and len(word) <= MAX_GATES, "word capacity")
    for gate in word:
        need(type(gate) is tuple and len(gate) == 3, "gate shape")
        need(all(type(value) is int for value in gate), "integer gate")
        target, source, sign = gate
        need(0 <= target < n and 0 <= source < n, "row index")
        need(target != source and sign in (-1, 1), "signed unit ADD")


def identity(n: int) -> Matrix:
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def apply(matrix: Matrix, gate: Gate) -> Matrix:
    target, source, sign = gate
    rows = list(matrix)
    rows[target] = tuple(a + sign * b for a, b in zip(rows[target], rows[source]))
    return tuple(rows)


def measures(matrix: Matrix) -> tuple[int, int]:
    entry = max(abs(value) for row in matrix for value in row)
    norm = max(sum(abs(value) for value in row) for row in matrix)
    return entry, norm


def trace(n: int, word: tuple[Gate, ...]) -> tuple[Matrix, tuple[tuple[int, int], ...]]:
    validate(n, word)
    matrix = identity(n)
    heights = [measures(matrix)]
    for gate in word:
        matrix = apply(matrix, gate)
        heights.append(measures(matrix))
    return matrix, tuple(heights)


def check_loop(n: int, word: tuple[Gate, ...], budget: int) -> tuple[int, int]:
    need(type(budget) is int and len(word) <= budget <= MAX_GATES, "gate budget")
    endpoint, heights = trace(n, word)
    need(endpoint == identity(n), "full arbitrary-input endpoint is not identity")
    length = len(word)
    for cut, (entry, norm) in enumerate(heights):
        radius = min(cut, length - cut)
        need(entry <= fibonacci(radius + 1), "coefficient envelope")
        need(norm <= fibonacci(radius + 2), "row-norm envelope")
    peak = tuple(max(pair[j] for pair in heights) for j in range(2))
    need(peak[0] <= fibonacci(budget // 2 + 1), "budget coefficient")
    need(peak[1] <= fibonacci(budget // 2 + 2), "budget row norm")
    return peak


def attaining_word(steps: int) -> tuple[Gate, ...]:
    need(type(steps) is int and 0 <= steps <= MAX_GATES // 2, "attainer capacity")
    outward = tuple((step % 2, 1 - step % 2, 1) for step in range(steps))
    return outward + tuple((i, j, -sign) for i, j, sign in reversed(outward))
