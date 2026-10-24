#!/usr/bin/env python3
"""Exact block-three hook spectrum; produced by Nick Petalas, Apache-2.0."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def determinant4(rows, columns):
    """Leibniz determinant, at most 24 products of four Walsh signs."""
    require(len(rows) == len(columns) == 4, "minor shape")
    total = 0
    for order in permutations(range(4)):
        inversions = sum(order[i] > order[j]
                         for i in range(4) for j in range(i + 1, 4))
        term = (-1) ** inversions
        for i in range(4):
            term *= (-1) ** ((rows[i] & columns[order[i]]).bit_count())
        total += term
    return total


def leakage_numerator():
    """D/sqrt(32768) is the leakage matrix in normalized exterior bases."""
    subsets = tuple(combinations(range(8), 4))
    minors = tuple(tuple(determinant4(s, t) for t in subsets) for s in subsets)
    inside = tuple((x, t) for t, subset in enumerate(subsets) for x in subset)
    outside = tuple((y, s) for s, subset in enumerate(subsets)
                    for y in range(8) if y not in subset)
    require(len(inside) == len(outside) == 280, "hook partition")
    return tuple(tuple((-1) ** ((x & y).bit_count()) * minors[s][t]
                       for x, t in inside) for y, s in outside)


def scaled_gram(numerator):
    """Construct A=8 L*L with integer arithmetic, checking every division."""
    require(len(numerator) == 280, "leakage rows")
    require(all(len(row) == 280 for row in numerator), "leakage columns")
    columns = tuple(zip(*numerator))
    matrix = [[0] * 280 for _ in range(280)]
    for i in range(280):
        for j in range(i, 280):
            product = sum(x * y for x, y in zip(columns[i], columns[j]))
            require(product % 4096 == 0, "nonintegral scaled Gram entry")
            matrix[i][j] = matrix[j][i] = product // 4096
    return tuple(tuple(row) for row in matrix)


def multiply(left, right):
    """Fixed 280-square sparse product, at most 280^3 scalar updates."""
    require(len(left) == len(right) == 280, "product rows")
    require(all(len(row) == 280 for row in left + right), "product columns")
    right_sparse = tuple(tuple((j, v) for j, v in enumerate(row) if v)
                         for row in right)
    result = [[0] * 280 for _ in range(280)]
    for i, row in enumerate(left):
        for k, value in enumerate(row):
            if value:
                for j, other in right_sparse[k]:
                    result[i][j] += value * other
    return tuple(tuple(row) for row in result)


def subtract_diagonal(matrix, value):
    return tuple(tuple(x - (value if i == j else 0)
                       for j, x in enumerate(row)) for i, row in enumerate(matrix))


def trace(matrix):
    require(len(matrix) == 280, "trace rows")
    return sum(matrix[i][i] for i in range(280))


def certify(matrix):
    """Symmetry, a square-free annihilator and four moments fix the spectrum."""
    require(all(matrix[i][j] == matrix[j][i]
                for i in range(280) for j in range(280)), "Gram symmetry")
    product = matrix
    for root in (1, 5, 8):
        product = multiply(product, subtract_diagonal(matrix, root))
    require(all(value == 0 for row in product for value in row), "annihilator")
    square = multiply(matrix, matrix)
    cube = multiply(square, matrix)
    moments = (280, trace(matrix), trace(square), trace(cube))
    require(moments == (280, 1120, 6944, 46816), "spectral moments")
    multiplicities = {0: 56, 1: 48, 5: 112, 8: 64}
    for power in range(4):
        require(sum(count * root ** power for root, count in multiplicities.items())
                == moments[power], "multiplicity equation")
    # Distinct roots make these four Vandermonde equations nonsingular.
    return moments, multiplicities


def rank_error_squared(rank_budget, targets):
    require(isinstance(targets, int) and 1 <= targets <= 100, "target bound")
    require(isinstance(rank_budget, int) and 0 <= rank_budget <= 280 * targets,
            "rank bound")
    for eigenvalue, multiplicity in ((8, 64), (5, 112), (1, 48)):
        if rank_budget < multiplicity * targets:
            return Fraction(eigenvalue, 8)
        rank_budget -= multiplicity * targets
    return Fraction(0)


def controls(matrix):
    rejected = 0
    for change in (1, -1):
        mutant = [list(row) for row in matrix]
        mutant[0][0] += change
        try:
            certify(tuple(tuple(row) for row in mutant))
        except ValueError:
            rejected += 1
        else:
            raise ValueError("changed Gram diagonal accepted")
    require(rejected == 2, "mutation coverage")
    require(determinant4((0, 1, 2, 3), (0, 1, 2, 3)) == 16, "minor control")
    for targets in range(1, 21):
        explicit = ([Fraction(1)] * (64 * targets)
                    + [Fraction(5, 8)] * (112 * targets)
                    + [Fraction(1, 8)] * (48 * targets)
                    + [Fraction(0)] * (56 * targets))
        for budget in range(280 * targets + 1):
            expected = explicit[budget] if budget < len(explicit) else Fraction(0)
            require(rank_error_squared(budget, targets) == expected,
                    "ordered singular-value oracle")
    require(rank_error_squared(80 * 13, 5) == Fraction(1, 8), "13-call obstruction")
    require(rank_error_squared(80 * 14, 5) == 0, "14-call rank relaxation")
    for arguments in ((-1, 1), (281, 1), (0, 0), (0, 101)):
        try:
            rank_error_squared(*arguments)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid rank parameters accepted")
    return rejected


def main():
    numerator = leakage_numerator()
    require(Counter(value for row in numerator for value in row)
            == {-16: 2600, -8: 24944, 0: 22848, 8: 25232, 16: 2776},
            "complete numerator census")
    matrix = scaled_gram(numerator)
    moments, multiplicities = certify(matrix)
    rejected = controls(matrix)
    here = Path(__file__).resolve().parent
    files = ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: sha256((here / name).read_bytes()).hexdigest() for name in files}
    print(json.dumps({"status": "PASS_BLOCK3_HOOK_ERROR_SPECTRUM",
                      "scaled_gram_dimension": 280, "moments": moments,
                      "scaled_gram_eigenvalues": multiplicities,
                      "rejected_controls": rejected, "source_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
