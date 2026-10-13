"""Exact full-rank fast path; a deficient modular rank is never returned.

Prepared for Martin Rivera with substantial OpenAI Codex assistance.
Apache-2.0. See PROOF.md for the reduction argument and NOTICE.md for credit.
"""
from fractions import Fraction

PRIME = 101


def screened_rank(matrix, fallback, stats=None):
    """Return the rational rank of a rectangular int/Fraction matrix.

    A full rank over F_101 proves the rational rank. Noninvertible
    denominators and deficient reductions go to the caller's exact routine.
    Inputs are not modified; no matrix results are cached here.
    """
    if not isinstance(matrix, (list, tuple)):
        raise TypeError("Use a list or tuple of exact rows")
    n = len(matrix)
    if n and not isinstance(matrix[0], (list, tuple)):
        raise TypeError("Use list or tuple rows")
    m = len(matrix[0]) if n else 0
    for row in matrix:
        if not isinstance(row, (list, tuple)) or len(row) != m:
            raise ValueError("Matrix must be rectangular")
        if any(type(x) not in (int, Fraction) for x in row):
            raise TypeError("Only exact int and Fraction entries are admitted")

    def record(outcome):
        if stats is not None:
            stats[outcome] += 1

    if not n or not m:
        record("empty")
        return 0
    inverses = {1: 1}
    rows = []
    for row in matrix:
        reduced = []
        for x in row:
            denominator = x.denominator % PRIME
            if not denominator:
                record("denominator_fallback")
                return fallback(matrix)
            if denominator not in inverses:
                inverses[denominator] = pow(denominator, -1, PRIME)
            reduced.append(x.numerator % PRIME * inverses[denominator] % PRIME)
        rows.append(reduced)

    rank = 0
    for col in range(m):
        pivot = next((i for i in range(rank, n) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][col], -1, PRIME)
        pivot_row = [x * inverse % PRIME for x in rows[rank]]
        for i in range(rank + 1, n):
            coefficient = rows[i][col]
            if coefficient:
                rows[i] = [(x - coefficient * y) % PRIME
                           for x, y in zip(rows[i], pivot_row)]
        rank += 1
        if rank == min(n, m):
            record("full_rank")
            return rank
    record("rank_fallback")
    return fallback(matrix)
