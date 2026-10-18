"""Fixed-dimensional preparations whose entries are binary word tapes.

Matrix positions and row permutations range over the fixed 64/128-dimensional
control alphabet. Runtime entries never become Python integers. The algebra
adapts the retained source527/PR2160/2159/2234 normal forms.
"""
from words import need


class Matrices:
    def __init__(self, ring):
        self.ring, self.arena = ring, ring.arena

    def zero(self, rows, columns):
        need(0 < rows <= 128 and 0 < columns <= 256, "fixed matrix dimensions")
        return [[self.arena.zero() for _ in range(columns)] for _ in range(rows)]

    def free(self, matrix):
        for row in matrix:
            for value in row:
                self.arena.free(value)

    def copy(self, matrix):
        return [[self.arena.copy(value) for value in row] for row in matrix]

    def identity(self, size):
        out = self.zero(size, size)
        for i in range(size):
            self.arena.free(out[i][i])
            out[i][i] = self.arena.copy(self.ring.one)
        return out

    def constants(self, matrix):
        """Compile a fixed rational source matrix; inverses use the word machine."""
        palette = {}
        for row in matrix:
            for constant in row:
                if constant in palette:
                    continue
                numerator = self.ring.literal(constant.numerator)
                denominator = self.ring.literal(constant.denominator)
                inv = self.ring.inverse(denominator)
                need(inv is not None, "source denominator is a unit")
                palette[constant] = self.ring.multiply(numerator, inv)
                self.arena.free_many(numerator, denominator, inv)
        out = [[self.arena.copy(palette[constant]) for constant in row] for row in matrix]
        for value in palette.values():
            self.arena.free(value)
        return out

    def multiply(self, a, b):
        rows, inner, columns = len(a), len(b), len(b[0])
        need(all(len(row) == inner for row in a) and all(len(row) == columns for row in b),
             "matrix product shape")
        out = self.zero(rows, columns)
        for i in range(rows):
            for k in range(inner):
                if a[i][k].zero():
                    continue
                for j in range(columns):
                    if b[k][j].zero():
                        continue
                    product = self.ring.multiply(a[i][k], b[k][j])
                    total = self.ring.add(out[i][j], product)
                    self.arena.free_many(out[i][j], product)
                    out[i][j] = total
        return out

    def inverse(self, matrix):
        size = len(matrix)
        need(size <= 128 and all(len(row) == size for row in matrix), "fixed square matrix")
        identity = self.identity(size)
        rows = [[self.arena.copy(value) for value in row] + unit
                for row, unit in zip(matrix, identity)]
        for j in range(size):
            pinv = None
            for pivot in range(j, size):
                pinv = self.ring.inverse(rows[pivot][j])
                if pinv is not None:
                    break
            need(pinv is not None, "matrix unit pivot")
            rows[j], rows[pivot] = rows[pivot], rows[j]
            for k in range(2*size):
                value = self.ring.multiply(pinv, rows[j][k])
                self.arena.free(rows[j][k])
                rows[j][k] = value
            self.arena.free(pinv)
            for i in range(size):
                if i == j or rows[i][j].zero():
                    continue
                coefficient = self.arena.copy(rows[i][j])
                for k in range(2*size):
                    product = self.ring.multiply(coefficient, rows[j][k])
                    value = self.ring.subtract(rows[i][k], product)
                    self.arena.free_many(rows[i][k], product)
                    rows[i][k] = value
                self.arena.free(coefficient)
        for i in range(size):
            for j in range(size):
                need(self.ring.raw.compare(rows[i][j], self.ring.one) == 0 if i == j else rows[i][j].zero(),
                     "binary matrix inverse endpoint")
                self.arena.free(rows[i][j])
        return [row[size:] for row in rows]

    def projector(self, header, rank):
        need(0 < rank < len(header), "proper projector rank")
        inv = self.inverse(header)
        out = self.multiply([row[:rank] for row in header], inv[:rank])
        self.free(inv)
        return out

    def good_pivots(self, projector, rank):
        rows = self.copy(projector)
        size, pivots = len(rows), []
        for k in range(rank):
            inv = self.ring.inverse(rows[k][k])
            need(inv is not None, "binary nongeneric good class")
            pivots.append(self.arena.copy(rows[k][k]))
            for i in range(k+1, size):
                if rows[i][k].zero():
                    continue
                coefficient = self.ring.multiply(rows[i][k], inv)
                for j in range(size):
                    product = self.ring.multiply(coefficient, rows[k][j])
                    value = self.ring.subtract(rows[i][j], product)
                    self.arena.free_many(rows[i][j], product)
                    rows[i][j] = value
                self.arena.free(coefficient)
            self.arena.free(inv)
        # Rank-r split projectors with these pivots have zero residual block.
        for i in range(rank, size):
            for j in range(rank, size):
                need(rows[i][j].zero(), "binary full-ring Schur block")
        self.free(rows)
        return pivots

    def residual(self, p):
        size = len(p)
        need(size <= 64, "selected residual dimension")
        out = self.zero(2*size, 2*size)
        for i in range(size):
            for j in range(size):
                if i == j:
                    complement = self.ring.subtract(self.ring.one, p[i][j])
                else:
                    complement = self.ring.negate(p[i][j])
                for row, column, value in (
                    (i, j, complement),
                    (2*size-1-i, 2*size-1-j, self.arena.copy(complement)),
                    (i, 2*size-1-j, self.arena.copy(p[i][j])),
                    (2*size-1-i, j, self.arena.copy(p[i][j])),
                ):
                    self.arena.free(out[row][column])
                    out[row][column] = value
        return out

    def fallback(self, projector):
        rows = self.residual(projector)
        size = len(rows)
        permutation = list(range(size))  # Fixed finite row-label control.
        for j in range(size):
            inv = None
            for pivot in range(j, size):
                inv = self.ring.inverse(rows[pivot][j])
                if inv is not None:
                    break
            need(inv is not None, "binary fallback unit pivot")
            rows[j], rows[pivot] = rows[pivot], rows[j]
            permutation[j], permutation[pivot] = permutation[pivot], permutation[j]
            for i in range(size):
                if i == j or rows[i][j].zero():
                    continue
                coefficient = self.ring.multiply(rows[i][j], inv)
                for k in range(size):
                    product = self.ring.multiply(coefficient, rows[j][k])
                    value = self.ring.subtract(rows[i][k], product)
                    self.arena.free_many(rows[i][k], product)
                    rows[i][k] = value
                self.arena.free(coefficient)
            self.arena.free(inv)
        diagonal = []
        for i in range(size):
            for j in range(size):
                if i == j:
                    diagonal.append(rows[i][j])
                else:
                    need(rows[i][j].zero(), "binary fallback diagonal endpoint")
                    self.arena.free(rows[i][j])
        return diagonal, tuple(permutation)

    def raw_header(self, low, high, q):
        """Compile-time low class plus encoded runtime high digits."""
        qword = self.ring.literal(q)
        constants = {constant for row in low for constant in row}
        palette = {constant: self.ring.literal(constant) for constant in constants}
        out = []
        for lo, hi in zip(low, high):
            row = []
            for constant, digit in zip(lo, hi):
                term = self.ring.multiply(qword, digit)
                row.append(self.ring.add(term, palette[constant]))
                self.arena.free(term)
            out.append(row)
        self.arena.free(qword)
        for value in palette.values():
            self.arena.free(value)
        return out

    def prepare(self, low, high, q, fixed_preparation, rank):
        raw = self.raw_header(low, high, q)
        basis_chart = self.constants(fixed_preparation)
        header = self.multiply(raw, basis_chart)
        self.free(raw)
        self.free(basis_chart)
        p = self.projector(header, rank)
        self.free(header)
        return p
