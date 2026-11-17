"""Bounded exact arithmetic. Produced by Nick Petalas. Apache-2.0."""

MAX_DIM = 12


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Small polynomial-basis fields, with canonical integer elements."""

    def __init__(self, p, modulus):
        choices = {2: ((0, 1), (1, 1, 1), (1, 1, 0, 1)),
                   3: ((0, 1), (1, 0, 1)), 5: ((0, 1), (2, 0, 1))}
        require(type(p) is int and p in choices, 'unsupported characteristic')
        require(isinstance(modulus, (list, tuple)) and 2 <= len(modulus) <= 4 and
                all(type(a) is int and 0 <= a < p for a in modulus), 'modulus format')
        require(tuple(modulus) in choices[p], 'unsupported field modulus')
        self.p, self.modulus = p, tuple(modulus)
        self.degree = len(modulus) - 1
        self.q = p ** self.degree
        self.digits = tuple(tuple((x // p**i) % p for i in range(self.degree))
                            for x in range(self.q))
        self.plus = tuple(tuple(self.encode((a+b) % p for a, b in zip(x, y))
                                for y in self.digits) for x in self.digits)
        self.times = tuple(tuple(self.polynomial_product(x, y) for y in self.digits)
                           for x in self.digits)
        self.negative = tuple(self.encode((-a) % p for a in x) for x in self.digits)
        inverses = [0]
        for a in range(1, self.q):
            candidates = [b for b in range(1, self.q) if self.times[a][b] == 1]
            require(len(candidates) == 1, 'modulus is not a field')
            inverses.append(candidates[0])
        self.reciprocal = tuple(inverses)

    def encode(self, digits):
        return sum(a * self.p**i for i, a in enumerate(digits))

    def polynomial_product(self, x, y):
        d, p = self.degree, self.p
        work = [0] * (2*d-1)
        for i in range(d):
            for j in range(d):
                work[i+j] = (work[i+j] + x[i]*y[j]) % p
        for k in range(2*d-2, d-1, -1):
            coefficient = work[k]
            for j in range(d):
                work[k-d+j] = (work[k-d+j] - coefficient*self.modulus[j]) % p
        return self.encode(work[:d])

    def add(self, a, b):
        return self.plus[a][b]

    def mul(self, a, b):
        return self.times[a][b]

    def neg(self, a):
        return self.negative[a]


def check_matrix(matrix, n, field):
    require(type(n) is int and 1 <= n <= MAX_DIM, 'matrix dimension')
    require(isinstance(matrix, (list, tuple)) and len(matrix) == n and
            all(isinstance(row, (list, tuple)) and len(row) == n for row in matrix), 'matrix shape')
    require(all(type(a) is int and 0 <= a < field.q for row in matrix for a in row),
            'canonical matrix entries')


def check_tensor(table, field):
    require(isinstance(table, (list, tuple)), 'tensor container')
    n = len(table)
    require(1 <= n <= MAX_DIM, 'tensor dimension')
    for matrix in table:
        check_matrix(matrix, n, field)
    return n


def identity(n):
    require(type(n) is int and 1 <= n <= MAX_DIM, 'identity dimension')
    return [[int(i == j) for j in range(n)] for i in range(n)]


def sum_field(values, field):
    result = 0
    for value in values:
        result = field.add(result, value)
    return result


def matvec(matrix, vector, field):
    return [sum_field((field.mul(a, b) for a, b in zip(row, vector)), field)
            for row in matrix]


def matmul(left, right, field):
    return [list(row) for row in zip(*(matvec(left, column, field)
                                     for column in zip(*right)))]


def solve_unique(rows, variables, field):
    require(1 <= variables <= MAX_DIM and 1 <= len(rows) <= MAX_DIM**2,
            'linear system bounds')
    require(all(len(row) == variables+1 for row in rows), 'linear system shape')
    work, pivot_row = [list(row) for row in rows], 0
    for column in range(variables):
        candidates = [i for i in range(pivot_row, len(work)) if work[i][column]]
        require(candidates, 'linear system not unique')
        selected = candidates[0]
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        scale = field.reciprocal[work[pivot_row][column]]
        work[pivot_row] = [field.mul(scale, a) for a in work[pivot_row]]
        for i in range(len(work)):
            if i != pivot_row:
                coefficient = work[i][column]
                work[i] = [field.add(a, field.neg(field.mul(coefficient, b)))
                           for a, b in zip(work[i], work[pivot_row])]
        pivot_row += 1
    require(all(not any(row[:variables]) and row[-1] == 0
                for row in work[variables:]), 'inconsistent linear system')
    return [work[i][-1] for i in range(variables)]


def inverse(matrix, field):
    n = len(matrix)
    check_matrix(matrix, n, field)
    columns = []
    for column in range(n):
        rows = [list(row) + [int(i == column)] for i, row in enumerate(matrix)]
        columns.append(solve_unique(rows, n, field))
    return [list(row) for row in zip(*columns)]


def evaluate(table, x, y, field):
    n = len(table)
    result = [0] * n
    for i in range(n):
        for j in range(n):
            coefficient = field.mul(x[i], y[j])
            if coefficient:
                for k in range(n):
                    result[k] = field.add(result[k], field.mul(coefficient, table[i][j][k]))
    return result


def isotope(table, left, right, output, field):
    """Return output * table(left*x, right*y), with column-map conventions."""
    n = check_tensor(table, field)
    for matrix in (left, right, output):
        check_matrix(matrix, n, field)
    return [[matvec(output, evaluate(table, x, y, field), field)
             for y in zip(*right)] for x in zip(*left)]


def find_unit(table, field):
    n = check_tensor(table, field)
    rows = [[table[i][j][k] for i in range(n)] + [int(j == k)]
            for j in range(n) for k in range(n)]
    return solve_unique(rows, n, field)


def check_algebra(table, field):
    n = check_tensor(table, field)
    unit, basis = find_unit(table, field), identity(n)
    for i in range(n):
        require(evaluate(table, unit, basis[i], field) == basis[i] and
                evaluate(table, basis[i], unit, field) == basis[i], 'two-sided unit')
        for j in range(n):
            require(table[i][j] == table[j][i], 'commutative algebra')
            for k in range(n):
                require(evaluate(table, table[i][j], basis[k], field) ==
                        evaluate(table, basis[i], table[j][k], field), 'associative algebra')
    return unit


def unpack(vector, field):
    require(all(type(a) is int and 0 <= a < field.q for a in vector), 'K vector')
    return [digit for a in vector for digit in field.digits[a]]


def pack(vector, field):
    require(len(vector) % field.degree == 0 and
            all(type(a) is int and 0 <= a < field.p for a in vector), 'F vector')
    return [field.encode(vector[i:i+field.degree])
            for i in range(0, len(vector), field.degree)]


def restrict_matrix(matrix, field):
    n, d = len(matrix), field.degree
    check_matrix(matrix, n, field)
    require(n*d <= MAX_DIM, 'restricted dimension')
    columns = []
    for i in range(n):
        for a in range(d):
            vector = [0] * n
            vector[i] = field.p**a
            columns.append(unpack(matvec(matrix, vector, field), field))
    return [list(row) for row in zip(*columns)]


def restrict_tensor(table, field):
    n, d = check_tensor(table, field), field.degree
    require(n*d <= MAX_DIM, 'restricted dimension')
    result = [[[0] * (n*d) for _ in range(n*d)] for _ in range(n*d)]
    for i in range(n):
        for j in range(n):
            for a in range(d):
                for b in range(d):
                    coefficient = field.mul(field.p**a, field.p**b)
                    result[i*d+a][j*d+b] = unpack(
                        [field.mul(coefficient, c) for c in table[i][j]], field)
    return result
