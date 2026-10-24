"""Exact coordinate restrictions of Boolean algebraic normal forms.

New work produced by Nick Petalas. Apache-2.0.
An output is a sorted tuple of distinct variable-subset masks, including
mask zero for the constant one. Arithmetic is over F2.
"""

from itertools import combinations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(n, outputs):
    require(type(n) is int and 0 <= n <= 40, "variable bound")
    require(type(outputs) is tuple and 1 <= len(outputs) <= 40, "output bound")
    for terms in outputs:
        require(type(terms) is tuple and len(terms) <= 256, "term bound")
        require(all(type(t) is int and 0 <= t < 1 << n for t in terms),
                "monomial mask")
        require(terms == tuple(sorted(set(terms))), "canonical terms")


def evaluate(terms, point):
    return sum(point & term == term for term in terms) & 1


def restrict(terms, fixed, ones):
    """Substitute fixed bits, retaining cancellations over F2."""
    require(type(fixed) is int and type(ones) is int and fixed >= 0
            and ones >= 0 and ones & ~fixed == 0, "face assignment")
    zero = fixed ^ ones
    result = set()
    for term in terms:
        if term & zero == 0:
            result.symmetric_difference_update((term & ~fixed,))
    return tuple(sorted(result))


def is_affine(outputs):
    return all(term.bit_count() <= 1 for terms in outputs for term in terms)


def minimum_zero_cut(n, outputs):
    """Exact nonlinear-monomial transversal; at most 2^12 cuts."""
    validate(n, outputs)
    require(n <= 12, "cut search bound")
    edges = {t for terms in outputs for t in terms if t.bit_count() >= 2}
    for size in range(n + 1):
        for selected in combinations(range(n), size):
            cut = sum(1 << i for i in selected)
            if all(cut & edge for edge in edges):
                return cut
    raise ValueError("unreachable: fixing every variable kills each edge")


def minimum_affine_face(n, outputs):
    """Exact minimum fixing, including nonzero faces; at most 3^8 faces."""
    validate(n, outputs)
    require(n <= 8, "face search bound")
    for size in range(n + 1):
        for selected in combinations(range(n), size):
            fixed = sum(1 << i for i in selected)
            for word in range(1 << size):
                ones = sum(((word >> j) & 1) << i
                           for j, i in enumerate(selected))
                if is_affine(tuple(restrict(t, fixed, ones) for t in outputs)):
                    return fixed, ones
    raise ValueError("unreachable: a singleton face is constant")


def from_truth_table(table):
    """Boolean Mobius inversion on truth tables with at most 32 entries."""
    require(type(table) is tuple and len(table) in (1, 2, 4, 8, 16, 32),
            "truth table bound")
    require(all(type(bit) is int and bit in (0, 1) for bit in table),
            "truth table bits")
    coefficients = list(table)
    n = len(table).bit_length() - 1
    for i in range(n):
        for mask in range(1 << n):
            if mask & (1 << i):
                coefficients[mask] ^= coefficients[mask ^ (1 << i)]
    return tuple(i for i, bit in enumerate(coefficients) if bit)
