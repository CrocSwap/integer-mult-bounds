"""Exact bounded arithmetic for the split radical-square-zero fixtures."""

from itertools import product

FIELDS = (2, 3, 4, 5, 7, 8, 11)
MAX_DIMENSION = 8
MAX_MATRIX_DOMAIN = 70_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Prime fields and the fixed polynomial presentations F4 and F8."""

    def __init__(self, order):
        require(type(order) is int and order in FIELDS, "unsupported field")
        self.q = order
        self.modulus = {4: 0b111, 8: 0b1011}.get(order)

    def add(self, a, b):
        return a ^ b if self.modulus else (a + b) % self.q

    def neg(self, a):
        return a if self.modulus else -a % self.q

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def mul(self, a, b):
        if not self.modulus:
            return a * b % self.q
        result = 0
        for _ in range(self.q.bit_length() - 1):
            if b & 1:
                result ^= a
            b >>= 1
            a <<= 1
            if a & self.q:
                a ^= self.modulus
        return result

    def power(self, a, exponent):
        require(0 <= exponent <= 64, "exponent exceeds fixture bound")
        result = 1
        for _ in range(exponent):
            result = self.mul(result, a)
        return result

    def inverse(self, a):
        require(a != 0, "zero has no inverse")
        return self.power(a, self.q - 2)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def determinant(matrix, field):
    rows = [row[:] for row in matrix]
    n = len(rows)
    value = 1
    for column in range(n):
        pivot = next((j for j in range(column, n) if rows[j][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            value = field.neg(value)
        entry = rows[column][column]
        value = field.mul(value, entry)
        reciprocal = field.inverse(entry)
        for j in range(column + 1, n):
            scale = field.mul(rows[j][column], reciprocal)
            for k in range(column + 1, n):
                rows[j][k] = field.sub(rows[j][k], field.mul(scale, rows[column][k]))
    return value


def inverse(matrix, field):
    n = len(matrix)
    rows = [matrix[i][:] + identity(n)[i] for i in range(n)]
    for column in range(n):
        pivot = next((j for j in range(column, n) if rows[j][column]), None)
        require(pivot is not None, "singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = field.inverse(rows[column][column])
        rows[column] = [field.mul(scale, x) for x in rows[column]]
        for j in range(n):
            if j != column:
                scale = rows[j][column]
                rows[j] = [field.sub(x, field.mul(scale, y))
                           for x, y in zip(rows[j], rows[column])]
    return [row[n:] for row in rows]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matvec(matrix, vector, field):
    result = []
    for row in matrix:
        value = 0
        for a, b in zip(row, vector):
            value = field.add(value, field.mul(a, b))
        result.append(value)
    return result


def matmul(left, right, field):
    return transpose([matvec(left, column, field) for column in transpose(right)])


def multiply(left, right, field):
    """Multiplication in F plus J, with J squared zero and e0 the unit."""
    return [field.mul(left[0], right[0])] + [
        field.add(field.mul(left[0], right[j]), field.mul(right[0], left[j]))
        for j in range(1, len(left))]


def unit_matrix(unit, field):
    return transpose([multiply(unit, column, field) for column in identity(len(unit))])


def preserves_product(first, second, output, field):
    n = len(first)
    columns_f, columns_g = transpose(first), transpose(second)
    basis = identity(n)
    for i, j in product(range(n), repeat=2):
        left = multiply(columns_f[i], columns_g[j], field)
        if left != matvec(output, multiply(basis[i], basis[j], field), field):
            return False
    return True


def fixes_tensor(first, second, output, field):
    """Literal covariant action on every coefficient of the multiplication tensor."""
    n = len(first)
    basis = identity(n)
    for i, j in product(range(n), repeat=2):
        # The first two tensor factors act on covectors, hence these rows.
        transformed = matvec(output, multiply(first[i], second[j], field), field)
        if transformed != multiply(basis[i], basis[j], field):
            return False
    return True


def witness(triple, n, field):
    """Construct a stabilizer with the requested allowed determinant triple."""
    require(3 <= n <= MAX_DIMENSION, "radical dimension must be at least two")
    require(len(triple) == 3 and all(type(x) is int and 0 < x < field.q
                                   for x in triple), "invalid determinant triple")
    u, v, w = triple
    roots = {field.power(a, n): a for a in range(1, field.q)}
    aw, bw = field.mul(v, w), field.mul(u, w)
    require(aw in roots and bw in roots, "outside determinant image")
    a = [roots[aw]] + [(i + u) % field.q for i in range(1, n)]
    b = [roots[bw]] + [(i + v + 1) % field.q for i in range(1, n)]
    sigma = identity(n)
    sigma[1][1] = field.inverse(field.mul(field.mul(u, v), w))
    first = matmul(unit_matrix(a, field), sigma, field)
    second = matmul(unit_matrix(b, field), sigma, field)
    output = matmul(unit_matrix(multiply(a, b, field), field), sigma, field)
    return transpose(inverse(first, field)), transpose(inverse(second, field)), output


def all_matrices(n, field):
    require(field.q ** (n * n) <= MAX_MATRIX_DOMAIN, "matrix census exceeds cap")
    for entries in product(range(field.q), repeat=n * n):
        yield [list(entries[n * i:n * (i + 1)]) for i in range(n)]
