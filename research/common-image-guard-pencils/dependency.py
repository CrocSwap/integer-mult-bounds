"""Lattice formula and an alternative direct prefix count for small fields."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations

from laws import orbit_size


def subspaces(field, width):
    """Every RREF in a quotient of dimension width, once."""
    for dim in range(width + 1):
        for cols in combinations(range(width), dim):
            free = [(i, j) for i, pivot in enumerate(cols)
                    for j in range(pivot + 1, width) if j not in cols]
            for values in field.vectors(len(free)):
                rows = [[int(j == pivot) for j in range(width)] for pivot in cols]
                for (i, j), value in zip(free, values):
                    rows[i][j] = value
                yield tuple(tuple(row) for row in rows)


def minimal_forms(field, forms):
    """Independent columns of the evaluation table span its actual image S."""
    if any(row[0] != 1 for row in forms):
        raise ValueError("forms must take value one at e1")
    pivots = [next(i for i, value in enumerate(row) if value)
              for row in field.basis(forms)]
    return tuple(tuple(row[i] for i in pivots) for row in forms)


def joint(field, forms, m):
    if not forms:
        return Fraction(1)
    forms = minimal_forms(field, forms)
    r, q = len(forms[0]), field.q
    total = 0
    for basis in subspaces(field, r - 1):
        dim = len(basis) + 1
        c = r - dim
        vectors = []
        for coeff in field.vectors(dim - 1):
            y = (0,)*(r - 1)
            for scalar, row in zip(coeff, basis):
                y = field.axpy(y, scalar, row)
            vectors.extend((a, *y) for a in range(q))
        support = sum(all(field.dot(row, x) != 0 for row in forms) for x in vectors)
        weight = q**dim + (q - 1)*support
        mobius = (-1)**c * q**(c*(c - 1)//2)
        total += mobius * weight**(m - 1)
    return Fraction((q - 1)*total, orbit_size(q, r, m))


def prefix_count(field, forms, m):
    """Count correct-span pairs, retaining each prefix and quotient span.

    This path enumerates each raw coordinate/column choice. It uses no
    torus counts, rank-subtraction weights, pencil law or lattice inversion.
    """
    forms = minimal_forms(field, forms)
    r, q = len(forms[0]), field.q
    vectors = list(field.vectors(r))
    valid = {y for y in vectors if all(field.dot(row, y) != 1 for row in forms)}

    @lru_cache(None)
    def branches(prefix, span):
        next_counts = Counter()
        for col in vectors:
            enlarged = field.basis((*span, col[1:]))
            for x in range(q):
                y = field.axpy(prefix, x, col)
                if y in valid:
                    next_counts[y, enlarged] += 1
        return next_counts

    states = {((0,)*r, ()): 1}
    for _ in range(m - 1):
        updates = Counter()
        for (prefix, span), count in states.items():
            for state, ways in branches(prefix, span).items():
                updates[state] += count*ways
        states = updates
    return (q - 1)*sum(n for (_, span), n in states.items() if len(span) == r - 1)
