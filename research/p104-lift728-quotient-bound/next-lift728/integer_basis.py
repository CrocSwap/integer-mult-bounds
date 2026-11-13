"""Sparse rational row-span test with primitive integer elimination."""
from fractions import Fraction
from functools import reduce
from math import gcd, lcm


def primitive(row):
    divisor = reduce(gcd, row.values(), 0)
    if divisor > 1:
        return {i: x // divisor for i, x in row.items()}
    return row


def integers(row):
    denominator = lcm(*(x.denominator for x in row.values()))
    return primitive({i: x.numerator * (denominator // x.denominator) for i, x in row.items()})


def eliminate(row, pivot_row, pivot):
    a, b = pivot_row[pivot], row[pivot]
    g = gcd(a, b)
    a //= g
    b //= g
    result = {i: a * x for i, x in row.items() if i != pivot}
    for i, x in pivot_row.items():
        if i != pivot:
            c = result.get(i, 0) - b * x
            if c:
                result[i] = c
            else:
                result.pop(i, None)
    return primitive(result)


def separator(rows, target):
    # Within the unused bank, prefer the sparsest pivot row at each column.
    remaining = [integers(row) for row in rows if row]
    target = integers(target)
    pivots = []
    while remaining:
        pivot = min(min(row) for row in remaining)
        candidates = [i for i, row in enumerate(remaining) if pivot in row]
        chosen = min(candidates, key=lambda i: (len(remaining[i]), abs(remaining[i][pivot])))
        top = remaining.pop(chosen)
        if pivot in target:
            target = eliminate(target, top, pivot)
        if not target:
            return None, len(pivots) + 1
        pivots.append((pivot, top))
        remaining = [new for row in remaining
                     if (new := eliminate(row, top, pivot) if pivot in row else row)]
    probe = {min(target): Fraction(1)}
    for pivot, row in reversed(pivots):
        value = -sum(v * probe.get(i, 0) for i, v in row.items() if i != pivot) / Fraction(row[pivot])
        if value:
            probe[pivot] = value
    assert all(not sum(v * probe.get(i, 0) for i, v in row.items()) for row in rows)
    assert sum(v * probe.get(i, 0) for i, v in target.items())
    return probe, len(pivots)
