"""Finite checks of the last-axis sufficient condition and full-flat formula."""
from fractions import Fraction

from dependency import joint
from finite import Field
from laws import full_flat, marginal, pencil, universal_positive_size


def flat_examples():
    matched = 0
    for q in (2, 3, 4, 5):
        f = Field(q)
        for r in range(2, 4):
            forms = [(1, *x) for x in f.vectors(r - 1)]
            for m in range(r, r + 4):
                value = full_flat(q, r, m)
                if value != joint(f, forms, m):
                    raise ValueError("complete flat vs lattice")
                if r == 2 and value != pencil(q, q, m):
                    raise ValueError("complete line vs pencil")
                if m == r and value != Fraction(q - 1, q**m - 1):
                    raise ValueError("last-axis equality at full rank")
                matched += 1
    bounds = []
    for q in (2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 29, 31):
        k = universal_positive_size(q)
        t = Fraction(q*q - q + 1, q*q)
        if not q*t**k <= 1 < q*t**(k - 1) or k > q*q:
            raise ValueError("universal sufficient size boundary")
        for m in (2, 3, 5, 10):
            if Fraction(q - 1, q**m - 1) <= marginal(q, m)**k:
                raise ValueError("last-axis strict inequality")
        bounds.append(dict(q=q, first_size_certified_by_last_axis=k))
    return dict(full_flat_checks=matched, sufficient_sizes=bounds)
