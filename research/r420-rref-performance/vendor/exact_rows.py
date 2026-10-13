# SPDX-License-Identifier: Apache-2.0
"""Exact rational rank and canonical RREF using primitive integer rows.

Python 3.11+, standard library only. Inputs are iterables of equally sized rows
of integers or Fraction-compatible values. Inputs are never mutated. Rank is an
int; key_of returns the canonical RREF as tuples of Fractions with zero rows
removed, matching the pinned PR364 helpers on their supported matrix inputs.

Prepared by Aman with OpenAI Codex assistance. See NOTICE.md for source credits.
"""
from fractions import Fraction
from math import gcd, lcm


def _primitive(row):
    content = gcd(*row)
    return [x // content for x in row] if content > 1 else row


def _integer_rows(matrix):
    rows = []
    for values in matrix:
        row = list(values)
        if all(isinstance(x, int) for x in row):
            rows.append(_primitive(row))
        else:
            values = [Fraction(x) for x in row]
            denominator = lcm(*(x.denominator for x in values))
            rows.append(_primitive([x.numerator * (denominator // x.denominator)
                                    for x in values]))
    if rows and any(len(row) != len(rows[0]) for row in rows):
        raise ValueError('matrix rows must have equal lengths')
    return rows


def _eliminate(matrix, reduced=False):
    rows = _integer_rows(matrix)
    if not rows:
        return rows, []
    pivots = []
    for column in range(len(rows[0])):
        rank = len(pivots)
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        base = rows[rank]
        targets = range(len(rows)) if reduced else range(rank + 1, len(rows))
        for i in targets:
            if i == rank or not rows[i][column]:
                continue
            row = rows[i]
            divisor = gcd(base[column], row[column])
            a, b = base[column] // divisor, row[column] // divisor
            rows[i] = _primitive([a*x - b*y for x, y in zip(row, base)])
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return rows, pivots


def rank_q(matrix):
    """Rank over Q; empty matrices and zero-width matrices have rank zero."""
    return len(_eliminate(matrix)[1])


def key_of(basis):
    """Canonical rational row-space key, independent of basis/row scaling."""
    rows, pivots = _eliminate(basis, reduced=True)
    return tuple(tuple(Fraction(x, row[column]) for x in row)
                 for row, column in zip(rows, pivots))
