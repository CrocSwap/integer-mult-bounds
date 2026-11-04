"""Counts for uniformly permuted coordinate contributions."""
from fractions import Fraction
from math import comb, factorial

from settlement import charges, subset_sums


def passing_permutations(field, u, rows):
    """Count compatible labeled orders of the proper-prefix chain."""
    m = len(u)
    if not rows:
        return factorial(m)
    if any(field.dot(row, u) != 1 for row in rows):
        raise ValueError("unnormalized guard")
    sums = subset_sums(field, charges(field, u, rows))
    ways = [1] + [0]*((1 << m) - 1)
    for mask in range(1, len(ways)):
        if mask != len(ways) - 1 and 1 in sums[mask]:
            continue
        bits = mask
        while bits:
            bit = bits & -bits
            ways[mask] += ways[mask ^ bit]
            bits ^= bit
    return ways[-1]


def flat_rows(field, b, slopes):
    rows = []
    for lam in field.vectors(len(slopes)):
        row = tuple(b)
        for a, w in zip(lam, slopes):
            row = field.axpy(row, a, w)
        rows.append(row)
    return rows


def separated_ternary_probability(values):
    plus, minus = values.count(1), values.count(2)
    n = plus + minus
    if (plus - minus) % 3 != 1:
        raise ValueError("unnormalized ternary flat")
    if plus - minus not in (1, -2):
        return Fraction(0)
    return Fraction(n, len(values)*comb(n, plus))
