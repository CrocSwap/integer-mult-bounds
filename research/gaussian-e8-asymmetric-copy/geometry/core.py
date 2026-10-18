"""Exact Gaussian E8 geometry, using only the Python standard library.

Roots use doubled standard E8 coordinates. A Gaussian scalar is an integer
pair (real, imaginary). Row elimination stays integral by cross multiplication.
No floating point, external project imports, or precomputed geometry is used.
"""
from functools import lru_cache
from itertools import combinations, product
from math import gcd


ZERO = (0, 0)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def conj(a):
    return (a[0], -a[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def hermitian(a, b):
    value = ZERO
    for x, y in zip(a, b):
        value = add(value, mul(conj(x), y))
    return value


def primitive(row):
    """Canonical rational scaling: first entry real positive, then integer gcd."""
    pivot = next((x for x in row if x != ZERO), None)
    if pivot is None:
        return tuple(row)
    values = tuple(mul(x, conj(pivot)) for x in row)
    divisor = 0
    for real, imag in values:
        divisor = gcd(divisor, abs(real))
        divisor = gcd(divisor, abs(imag))
    return tuple((real // divisor, imag // divisor) for real, imag in values)


def cancel(row, basis, column):
    return primitive(tuple(sub(mul(basis[column], x), mul(row[column], y))
                           for x, y in zip(row, basis)))


def rowspace(rows):
    """Canonical reduced rowspace basis over Q(i), with integer-pair entries."""
    basis = []
    pivots = []
    for input_row in rows:
        row = tuple(input_row)
        for pivot, previous in zip(pivots, basis):
            if row[pivot] != ZERO:
                row = cancel(row, previous, pivot)
        if not any(x != ZERO for x in row):
            continue
        row = primitive(row)
        pivot = next(i for i, x in enumerate(row) if x != ZERO)
        position = next((i for i, p in enumerate(pivots) if p > pivot), len(pivots))
        basis.insert(position, row)
        pivots.insert(position, pivot)
    for i in range(len(basis) - 1, -1, -1):
        for j in range(i):
            if basis[j][pivots[i]] != ZERO:
                basis[j] = cancel(basis[j], basis[i], pivots[i])
    return tuple(basis)


def gaussian_rank(matrix):
    return len(rowspace(matrix))


def orthogonal_complement(basis, dimension=4):
    """Canonical basis of the Hermitian orthogonal complement over Q(i)."""
    equations = rowspace(tuple(conj(value) for value in row) for row in basis)
    pivots = [next(i for i, value in enumerate(row) if value != ZERO) for row in equations]
    scale = 1
    for row, pivot in zip(equations, pivots):
        assert row[pivot][1] == 0 and row[pivot][0] > 0
        scale *= row[pivot][0]
    result = []
    for free in range(dimension):
        if free in pivots:
            continue
        row = [ZERO] * dimension
        row[free] = (scale, 0)
        for equation, pivot in zip(equations, pivots):
            factor = scale // equation[pivot][0]
            row[pivot] = (-factor * equation[free][0], -factor * equation[free][1])
        result.append(primitive(row))
    return rowspace(result)


def in_span(vector, basis):
    row = tuple(vector)
    for previous in basis:
        pivot = next(i for i, x in enumerate(previous) if x != ZERO)
        if row[pivot] != ZERO:
            row = cancel(row, previous, pivot)
    return not any(x != ZERO for x in row)


def complex_structure(root):
    return tuple(value for i in range(0, 8, 2) for value in (-root[i + 1], root[i]))


def e8_roots():
    roots = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            root = [0] * 8
            root[i], root[j] = a, b
            roots.append(tuple(root))
    for root in product((-1, 1), repeat=8):
        if sum(value == -1 for value in root) % 2 == 0:
            roots.append(root)
    return tuple(sorted(roots))


def gaussian_lines():
    roots = e8_roots()
    root_set = set(roots)
    assert len(root_set) == 240
    assert all(sum(x * x for x in root) == 8 for root in roots)
    representatives = set()
    for root in roots:
        rotated = complex_structure(root)
        assert rotated in root_set
        orbit = (root, rotated, tuple(-x for x in root), tuple(-x for x in rotated))
        assert len(set(orbit)) == 4
        representatives.add(min(orbit))
    assert len(representatives) == 60
    return tuple(sorted(representatives))


class Geometry:
    def __init__(self):
        self.lines = gaussian_lines()
        self.vectors = tuple(tuple((root[i], root[i + 1]) for i in range(0, 8, 2))
                             for root in self.lines)
        self.gram = tuple(tuple(hermitian(a, b) for b in self.vectors) for a in self.vectors)

    @lru_cache(maxsize=None)
    def _basis(self, support):
        return rowspace(self.vectors[i] for i in support)

    def basis(self, support):
        return self._basis(tuple(sorted(set(support))))

    def rank(self, support):
        return len(self.basis(support))

    def closure(self, support):
        basis = self.basis(support)
        return tuple(i for i, vector in enumerate(self.vectors) if in_span(vector, basis))

    def pairing_rank(self, readers, sources):
        reader_basis = self.basis(readers)
        source_basis = self.basis(sources)
        return gaussian_rank(tuple(tuple(hermitian(a, b) for b in source_basis)
                                   for a in reader_basis))

    def flats(self, maxrank=3):
        """Enumerate all root-generated flats up to maxrank by successive extensions."""
        previous = {(): ()}
        result = {0: ((),)}
        for rank in range(1, maxrank + 1):
            spaces = {}
            for basis, support in previous.items():
                support_set = set(support)
                for i, vector in enumerate(self.vectors):
                    if i in support_set:
                        continue
                    extended = rowspace(basis + (vector,))
                    if len(extended) != rank:
                        continue
                    spaces[extended] = None
            for basis in spaces:
                spaces[basis] = tuple(i for i, vector in enumerate(self.vectors)
                                      if in_span(vector, basis))
            result[rank] = tuple(sorted(spaces.values()))
            previous = spaces
        return result
