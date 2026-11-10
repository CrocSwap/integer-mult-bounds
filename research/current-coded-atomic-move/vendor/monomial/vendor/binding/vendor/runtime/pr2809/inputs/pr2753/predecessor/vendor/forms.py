"""Complete selected adapter preparations with binary scalar operands.

The fixed matrix and reduction indices are finite control. All coefficients
remain Word objects. Algebra follows source527 and PR2159/2160/2188/2234.
"""
from dataclasses import dataclass

from matrices import Matrices
from words import need


@dataclass
class GoodForm:
    dimension: int
    rank: int
    pivots: tuple
    rows: tuple
    columns: tuple
    cross: list

    def close(self, ring):
        ring.arena.free_many(*self.pivots)
        for _, _, value in self.rows + self.columns:
            ring.arena.free(value)
        Matrices(ring).free(self.cross)


@dataclass
class Reduction:
    kind: str
    target: int
    source: int
    scalar: object
    permutation: tuple


@dataclass
class FallbackForm:
    dimension: int
    diagonal: tuple
    permutation: tuple
    reductions: tuple
    negative_sign: bool

    def close(self, ring):
        ring.arena.free_many(*self.diagonal)
        for reduction in self.reductions:
            if reduction.scalar is not None:
                ring.arena.free(reduction.scalar)


def row_add(matrix, target, source, coefficient, ring):
    if coefficient.zero():
        return
    for j in range(len(matrix[0])):
        product = ring.multiply(coefficient, matrix[source][j])
        result = ring.add(matrix[target][j], product)
        ring.arena.free_many(matrix[target][j], product)
        matrix[target][j] = result


def column_add(matrix, target, source, coefficient, ring):
    if coefficient.zero():
        return
    for row in matrix:
        product = ring.multiply(coefficient, row[source])
        result = ring.add(row[target], product)
        ring.arena.free_many(row[target], product)
        row[target] = result


def negative_product(a, b, ring):
    value = ring.multiply(a, b)
    result = ring.negate(value)
    ring.arena.free(value)
    return result


def good_form(projector, rank, ring):
    """Keep chronological row/column scalars and the full cross block."""
    m = len(projector)
    need(1 <= rank < m <= 64, "fixed good preparation dimension")
    matrices, arena = Matrices(ring), ring.arena
    a = [[arena.copy(value) for value in reversed(row)] for row in projector]
    left, right = matrices.identity(m), matrices.identity(m)
    pivots, rows, columns = [], [], []
    for k in range(rank):
        column = m-1-k
        pivot = arena.copy(a[k][column])
        inverse = ring.inverse(pivot)
        need(inverse is not None, "complete good class")
        pivots.append(pivot)
        for i in range(k+1, m):
            coefficient = negative_product(a[i][column], inverse, ring)
            rows.append((i, k, coefficient))
            row_add(a, i, k, coefficient, ring)
            row_add(left, i, k, coefficient, ring)
        for j in range(column):
            coefficient = negative_product(a[k][j], inverse, ring)
            columns.append((column, j, coefficient))
            column_add(a, j, column, coefficient, ring)
            column_add(right, j, column, coefficient, ring)
        arena.free(inverse)
    for i in range(m):
        for j in range(m):
            need(ring.raw.compare(a[i][j], pivots[i]) == 0 if i < rank and j == m-1-i
                 else a[i][j].zero(), "complete northeast diagonal endpoint")
    matrices.free(a)
    li, ri = matrices.inverse(left), matrices.inverse(right)
    lp = matrices.multiply(left, projector)
    a0 = matrices.multiply(lp[:rank], li)
    b = matrices.multiply(ri, [row[:rank] for row in reversed(li)])
    for matrix in (a0, b):
        for row in matrix:
            for j, value in enumerate(row):
                row[j] = ring.negate(value)
                arena.free(value)
    cross = matrices.zero(m, m)
    for k, pivot in enumerate(pivots):
        inverse = ring.inverse(pivot)
        need(inverse is not None, "good pivot remains a unit")
        for i in range(m):
            value = ring.negate(b[i][k])
            if i == m-1-k:
                adjusted = ring.subtract(value, inverse)
                arena.free(value)
                value = adjusted
            arena.free(cross[i][k])
            cross[i][k] = value
        for j in range(rank, m):
            value = ring.multiply(inverse, a0[k][j])
            arena.free(cross[m-1-k][j])
            cross[m-1-k][j] = value
        arena.free(inverse)
    for matrix in (left, right, li, ri, lp, a0, b):
        matrices.free(matrix)
    return GoodForm(m, rank, tuple(pivots), tuple(rows), tuple(columns), cross)


def fallback_form(projector, ring):
    """Retain each shear's original pair and pre-operation permutation."""
    matrices, arena = Matrices(ring), ring.arena
    rows = matrices.residual(projector)
    size = len(rows)
    permutation, reductions = list(range(size)), []
    for j in range(size):
        inverse = None
        for pivot in range(j, size):
            inverse = ring.inverse(rows[pivot][j])
            if inverse is not None:
                break
        need(inverse is not None, "complete fallback unit pivot")
        if pivot != j:
            reductions.append(Reduction("swap", j, pivot, None, tuple(permutation)))
            rows[j], rows[pivot] = rows[pivot], rows[j]
            permutation[j], permutation[pivot] = permutation[pivot], permutation[j]
        for i in range(size):
            if i == j:
                continue
            coefficient = negative_product(rows[i][j], inverse, ring)
            reductions.append(Reduction("shear", i, j, coefficient, tuple(permutation)))
            row_add(rows, i, j, coefficient, ring)
        arena.free(inverse)
    diagonal = []
    determinant = arena.copy(ring.one)
    for i in range(size):
        for j in range(size):
            if i == j:
                diagonal.append(rows[i][j])
                value = ring.multiply(determinant, rows[i][j])
                arena.free(determinant)
                determinant = value
            else:
                need(rows[i][j].zero(), "complete fallback diagonal endpoint")
                arena.free(rows[i][j])
    negative_one = ring.negate(ring.one)
    positive = ring.raw.compare(determinant, ring.one) == 0
    negative = ring.raw.compare(determinant, negative_one) == 0
    need(positive or negative, "fallback terminal determinant sign")
    arena.free_many(determinant, negative_one)
    return FallbackForm(len(projector), tuple(diagonal), tuple(permutation),
                        tuple(reductions), not positive)
