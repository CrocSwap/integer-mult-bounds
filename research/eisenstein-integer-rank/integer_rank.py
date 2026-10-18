"""Exact Q(omega)-rank by integer rows, omega^2+omega+1=0.

Prepared by ywz65 with OpenAI Codex assistance. Apache-2.0.
Primitive-row elimination is standard, not a new rank theorem.
"""
from fractions import Fraction
from math import gcd, lcm


def need(ok, message):
    if not ok:
        raise ValueError(message)


def primitive(row):
    content = gcd(*(value for pair in row for value in pair))
    return [(a//content, b//content) for a, b in row] if content > 1 else row


def rank(matrix):
    """Rank of a rectangular rational-pair matrix; never modifies or caches it.

    Each entry (a,b) denotes a+b*omega. Integers and Fraction components are
    accepted; floats, booleans and ragged matrices are rejected.
    """
    if not matrix:
        return 0
    width = len(matrix[0])
    rows = []
    for row in matrix:
        need(len(row) == width, 'ragged K matrix')
        need(all(isinstance(pair, (tuple, list)) and len(pair) == 2 for pair in row),
             'K entry must be a rational pair')
        need(all(type(value) in (int, Fraction) for pair in row for value in pair),
             'K components must be exact rational numbers')
        den = lcm(*(value.denominator for pair in row for value in pair))
        rows.append(primitive([(a.numerator*(den//a.denominator),
                                b.numerator*(den//b.denominator)) for a, b in row]))
    pivot = 0
    for col in range(width):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col] != (0, 0)), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        a, b = rows[pivot][col]
        for i in range(pivot+1, len(rows)):
            c, d = rows[i][col]
            if not (c or d):
                continue
            # (a+b*w)*row_i - (c+d*w)*pivot_row, w^2=-w-1.
            out = [(0, 0)]*(col+1)
            for (x, y), (u, v) in zip(rows[i][col+1:], rows[pivot][col+1:]):
                out.append((a*x-b*y-c*u+d*v, a*y+b*x-b*y-c*v-d*u+d*v))
            rows[i] = primitive(out)
        pivot += 1
        if pivot == len(rows):
            break
    return pivot
