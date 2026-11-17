"""Small exact fields and an ordered-basis integer codec. Apache-2.0."""

from math import prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Polynomial coordinates for these explicitly supplied finite fields."""

    def __init__(self, q):
        specifications = {
            2: (2, (0, 1)), 3: (3, (0, 1)), 4: (2, (1, 1, 1)),
            5: (5, (0, 1)), 7: (7, (0, 1)),
            8: (2, (1, 1, 0, 1)), 9: (3, (1, 0, 1)),
        }
        require(type(q) is int and q in specifications, "unsupported field")
        self.q = q
        self.p, self.modulus = specifications[q]
        self.degree = len(self.modulus) - 1

    def digits(self, value):
        require(type(value) is int and 0 <= value < self.q, "field element")
        return tuple((value // self.p**i) % self.p for i in range(self.degree))

    def add(self, a, b):
        return sum(((x + y) % self.p) * self.p**i
                   for i, (x, y) in enumerate(zip(self.digits(a), self.digits(b))))

    def neg(self, a):
        return sum((-x % self.p) * self.p**i for i, x in enumerate(self.digits(a)))

    def mul(self, a, b):
        aa, bb = self.digits(a), self.digits(b)
        out = [0] * (2 * self.degree - 1)
        for i, x in enumerate(aa):
            for j, y in enumerate(bb):
                out[i + j] = (out[i + j] + x * y) % self.p
        for i in range(len(out) - 1, self.degree - 1, -1):
            lead = out[i]
            for j, coefficient in enumerate(self.modulus):
                out[i - self.degree + j] = (
                    out[i - self.degree + j] - lead * coefficient) % self.p
        return sum(out[i] * self.p**i for i in range(self.degree))

    def inv(self, a):
        require(type(a) is int and 0 < a < self.q, "nonzero inverse required")
        result, power, exponent = 1, a, self.q - 2
        for _ in range(exponent.bit_length()):
            if exponent & 1:
                result = self.mul(result, power)
            power = self.mul(power, power)
            exponent >>= 1
        require(self.mul(a, result) == 1, "supplied field is invalid")
        return result


def reduce_rows(field, rows, width):
    """RREF, with optional trailing right-hand-side columns."""
    require(0 <= width <= 64 and len(rows) <= 64, "matrix capacity")
    require(all(width <= len(row) <= 65 for row in rows), "matrix shape")
    work = [list(row) for row in rows]
    pivots = []
    for column in range(width):
        candidates = [i for i in range(len(pivots), len(work)) if work[i][column]]
        if not candidates:
            continue
        pivot = len(pivots)
        source = candidates[0]
        work[pivot], work[source] = work[source], work[pivot]
        inverse = field.inv(work[pivot][column])
        work[pivot] = [field.mul(inverse, x) for x in work[pivot]]
        for i in range(len(work)):
            if i != pivot:
                scale = field.neg(work[i][column])
                work[i] = [field.add(x, field.mul(scale, y))
                           for x, y in zip(work[i], work[pivot])]
        pivots.append(column)
    return work, tuple(pivots)


def rank(field, columns, n):
    rows = [[column[i] for column in columns] for i in range(n)]
    return len(reduce_rows(field, rows, len(columns))[1])


def complete(field, columns, n):
    """Extend independent columns by the earliest available standard vectors."""
    require(0 <= n <= 4 and len(columns) <= n, "basis capacity")
    require(all(len(c) == n for c in columns), "column shape")
    basis = list(columns)
    require(rank(field, basis, n) == len(basis), "dependent prefix")
    for i in range(n):
        candidate = tuple(int(i == j) for j in range(n))
        if len(basis) < n and rank(field, basis + [candidate], n) > len(basis):
            basis.append(candidate)
    require(len(basis) == n, "basis completion failed")
    return basis


def coordinates(field, basis, vector):
    n = len(basis)
    rows = [[basis[j][i] for j in range(n)] + [vector[i]] for i in range(n)]
    reduced, pivots = reduce_rows(field, rows, n)
    require(pivots == tuple(range(n)), "singular basis")
    return tuple(row[n] for row in reduced)


def base_digits(value, radix, length):
    require(type(value) is int and 0 <= value < radix**length, "digit range")
    return tuple((value // radix**i) % radix for i in range(length))


def gl_order(q, n):
    return prod(q**n - q**j for j in range(n))


def gl_unrank(field, n, index):
    require(type(n) is int and 0 <= n <= 4, "GL dimension capacity")
    require(type(index) is int and 0 <= index < gl_order(field.q, n), "GL index")
    columns = []
    for j in range(n):
        radix = field.q**n - field.q**j
        index, digit = divmod(index, radix)
        low = digit % field.q**j
        high = digit // field.q**j + 1
        coefficients = base_digits(low, field.q, j) + base_digits(high, field.q, n - j)
        basis = complete(field, columns, n)
        vector = [0] * n
        for c, coefficient in zip(basis, coefficients):
            vector = [field.add(x, field.mul(coefficient, y)) for x, y in zip(vector, c)]
        columns.append(tuple(vector))
    require(index == 0, "GL index was not exhausted")
    return tuple(columns)


def gl_rank(field, columns):
    n = len(columns)
    require(n <= 4 and all(len(c) == n for c in columns), "GL shape")
    index, place = 0, 1
    for j, vector in enumerate(columns):
        basis = complete(field, columns[:j], n)
        coefficients = coordinates(field, basis, vector)
        low = sum(x * field.q**i for i, x in enumerate(coefficients[:j]))
        high = sum(x * field.q**i for i, x in enumerate(coefficients[j:]))
        require(high != 0, "singular tangent block")
        digit = low + field.q**j * (high - 1)
        index += place * digit
        place *= field.q**n - field.q**j
    return index
