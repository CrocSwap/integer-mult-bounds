"""Fixed-q compilation of lexicographic GL codes, independent of input width."""
from math import prod
from words import need


class Constraints:
    def __init__(self, rows, q):
        self.rows, self.q = rows, q
        self.basis, self.inconsistent = [], False

    def next(self, column):
        coefficients = [row[column] for row in self.rows]
        rhs = 0
        for pivot, row, value in self.basis:
            factor = coefficients[pivot]
            coefficients = [(a-factor*b) % self.q for a, b in zip(coefficients, row)]
            rhs = (rhs+factor*value) % self.q
        pivot = next((i for i, x in enumerate(coefficients) if x), None)
        return coefficients, rhs, pivot

    def excluded(self, reduced, value):
        if self.inconsistent:
            return 0
        _row, rhs, pivot = reduced
        if pivot is not None:
            return self.q**(len(self.rows)-len(self.basis)-1)
        return self.q**(len(self.rows)-len(self.basis)) if value == rhs else 0

    def choose(self, reduced, value):
        if self.inconsistent:
            return
        row, rhs, pivot = reduced
        if pivot is None:
            self.inconsistent = value != rhs
            return
        inverse = pow(row[pivot], -1, self.q)
        normalized = tuple(x*inverse % self.q for x in row)
        self.basis.append((pivot, normalized, (value-rhs)*inverse % self.q))
        self.basis.sort(key=lambda item: item[0])


class LowCodes:
    def __init__(self, q, dimension, requests=1):
        need(q >= 3 and all(q % p for p in range(2, q)) and
             1 <= dimension <= 64 and requests > 0, "fixed prime and source vocabulary")
        self.q, self.dimension, self.requests = q, dimension, requests
        self.radices = tuple(q**dimension-q**k for k in range(dimension))
        self.size = prod(self.radices)
        self.limit = 2*requests*self.size
        self.bits = max(1, (self.limit-1).bit_length())

    def vector_rank(self, rows, vector):
        constraints, rank = Constraints(rows, self.q), 0
        for column, value in enumerate(vector):
            reduced = constraints.next(column)
            total = self.q**(self.dimension-column-1)
            for smaller in range(value):
                rank += total-constraints.excluded(reduced, smaller)
            constraints.choose(reduced, value)
        need(constraints.inconsistent, "independent low row")
        return rank

    def vector_unrank(self, rows, rank):
        constraints, vector = Constraints(rows, self.q), []
        for column in range(self.dimension):
            reduced = constraints.next(column)
            total = self.q**(self.dimension-column-1)
            for value in range(self.q):
                count = total-constraints.excluded(reduced, value)
                if rank < count:
                    vector.append(value)
                    constraints.choose(reduced, value)
                    break
                rank -= count
            else:
                raise ValueError("low-row rank range")
        need(rank == 0 and constraints.inconsistent, "complete independent low row")
        return tuple(vector)

    def rank(self, matrix):
        need(len(matrix) == self.dimension and
             all(len(row) == self.dimension and all(isinstance(x, int) and 0 <= x < self.q
                                                     for x in row) for row in matrix),
             "fixed low matrix shape and residues")
        rank, previous = 0, []
        for row, radix in zip(matrix, self.radices):
            rank = rank*radix+self.vector_rank(previous, row)
            previous.append(tuple(row))
        return rank

    def unrank(self, rank):
        need(isinstance(rank, int) and 0 <= rank < self.size, "GL low ordinal")
        digits = []
        for radix in reversed(self.radices):
            rank, digit = divmod(rank, radix)
            digits.append(digit)
        rows = []
        for digit in reversed(digits):
            rows.append(self.vector_unrank(rows, digit))
        return tuple(rows)

    def encode(self, request, common, matrix):
        need(0 <= request < self.requests and common in (False, True), "fixed request/view tag")
        return (2*request+int(common))*self.size+self.rank(matrix)

    def decode(self, code):
        need(isinstance(code, int) and 0 <= code < self.limit, "complete compiled source code")
        tag, ordinal = divmod(code, self.size)
        return tag//2, bool(tag & 1), self.unrank(ordinal)
