"""Small exact fields, polynomials and literal pencil determinants.

The fixed corroboration domain is q in {2,3,4,5}, extension degree at most
four, field size at most 125 and matrix size at most 27. No source code from
the motivating pencil packages is imported.
"""

from itertools import product


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


class Field:
    def __init__(self, add: tuple, mul: tuple):
        q = len(add)
        require(2 <= q <= 125 and len(mul) == q, "field size")
        for table in (add, mul):
            require(all(len(row) == q for row in table), "table shape")
            require(all(0 <= a < q for row in table for a in row), "closure")
        require(all(add[0][a] == a == add[a][0] for a in range(q)), "zero")
        require(all(mul[1][a] == a == mul[a][1] for a in range(q)), "one")
        self.q, self.add, self.mul = q, add, mul
        self.neg = tuple(next(b for b in range(q) if add[a][b] == 0)
                         for a in range(q))
        self.inv = (0,) + tuple(next(b for b in range(1, q) if mul[a][b] == 1)
                                for a in range(1, q))


def base_field(q: int) -> Field:
    require(q in (2, 3, 4, 5), "unsupported base field")
    if q != 4:
        add = tuple(tuple((a + b) % q for b in range(q)) for a in range(q))
        mul = tuple(tuple((a * b) % q for b in range(q)) for a in range(q))
    else:
        add = tuple(tuple(a ^ b for b in range(q)) for a in range(q))
        rows = []
        for a in range(q):
            row = []
            for b in range(q):
                value = (a if b & 1 else 0) ^ (a << 1 if b & 2 else 0)
                row.append(value ^ 7 if value & 4 else value)
            rows.append(tuple(row))
        mul = tuple(rows)  # F2[z]/(z^2+z+1).
    return Field(add, mul)


def trim(poly: tuple) -> tuple:
    end = len(poly)
    for _ in range(len(poly) - 1):
        if poly[end - 1] != 0:
            break
        end -= 1
    return poly[:end]


def remainder(poly: tuple, divisor: tuple, field: Field) -> tuple:
    work = list(poly)
    degree = len(divisor) - 1
    for position in range(len(work) - 1, degree - 1, -1):
        factor = field.mul[work[position]][field.inv[divisor[-1]]]
        for j in range(degree + 1):
            delta = field.neg[field.mul[factor][divisor[j]]]
            index = position - degree + j
            work[index] = field.add[work[index]][delta]
    return trim(tuple(work[:degree]) or (0,))


def multiply(left: tuple, right: tuple, field: Field) -> tuple:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = field.add[out[i + j]][field.mul[a][b]]
    return trim(tuple(out))


def monics(q: int, degree: int) -> tuple:
    require(1 <= degree <= 4 and q ** degree <= 125, "polynomial domain")
    return tuple(tuple(c) + (1,) for c in product(range(q), repeat=degree))


def irreducibles(field: Field, degree: int) -> tuple:
    divisors = tuple(p for k in range(1, degree // 2 + 1)
                     for p in monics(field.q, k))
    return tuple(p for p in monics(field.q, degree)
                 if all(remainder(p, d, field) != (0,) for d in divisors))


def digits(value: int, q: int, degree: int) -> tuple:
    out = []
    for _ in range(degree):
        value, digit = divmod(value, q)
        out.append(digit)
    require(value == 0, "element encoding")
    return tuple(out)


def encode(coefficients: tuple, q: int) -> int:
    return sum(c * q ** j for j, c in enumerate(coefficients))


def extension(field: Field, modulus: tuple) -> Field:
    degree = len(modulus) - 1
    require(modulus in irreducibles(field, degree), "reducible modulus")
    if degree == 1:
        return field
    q, size = field.q, field.q ** degree
    require(size <= 125, "extension size")
    elements = tuple(digits(a, q, degree) for a in range(size))
    add, mul = [], []
    for a in elements:
        sums, products = [], []
        for b in elements:
            sums.append(encode(tuple(field.add[x][y] for x, y in zip(a, b)), q))
            reduced = remainder(multiply(a, b, field), modulus, field)
            products.append(encode(reduced, q))
        add.append(tuple(sums))
        mul.append(tuple(products))
    return Field(tuple(add), tuple(mul))


def evaluate(poly: tuple, point: int, field: Field) -> int:
    value = 0
    for coefficient in reversed(poly):
        value = field.add[field.mul[value][point]][coefficient]
    return value


def determinant(matrix: tuple, field: Field) -> int:
    n = len(matrix)
    require(1 <= n <= 27 and all(len(row) == n for row in matrix), "matrix shape")
    work, result = [list(row) for row in matrix], 1
    for j in range(n):
        pivots = tuple(i for i in range(j, n) if work[i][j])
        if not pivots:
            return 0
        pivot = pivots[0]
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            result = field.neg[result]
        result = field.mul[result][work[j][j]]
        inverse = field.inv[work[j][j]]
        for i in range(j + 1, n):
            factor = field.mul[work[i][j]][inverse]
            for k in range(j + 1, n):
                delta = field.neg[field.mul[factor][work[j][k]]]
                work[i][k] = field.add[work[i][k]][delta]
    return result


def pencil(blocks: tuple, infinity: int, field: Field) -> tuple:
    n = infinity + sum(len(p) - 1 for p in blocks)
    require(0 <= infinity <= 27 and 1 <= n <= 27, "pencil dimension")
    a, b, offset = [[0] * n for _ in range(n)], [[0] * n for _ in range(n)], 0
    for poly in blocks:
        d = len(poly) - 1
        require(d >= 1 and poly[-1] == 1, "monic block")
        for j in range(d):
            a[offset + j][offset + j] = 1
            b[offset + j][offset + d - 1] = poly[j]
        for j in range(d - 1):
            b[offset + j + 1][offset + j] = field.neg[1]
        offset += d
    for j in range(offset, n):
        b[j][j] = 1
    return tuple(map(tuple, a)), tuple(map(tuple, b))


def slice_matrix(a: tuple, b: tuple, point: int | None, field: Field) -> tuple:
    if point is None:
        return a
    return tuple(tuple(field.add[field.mul[point][x]][y] for x, y in zip(ar, br))
                 for ar, br in zip(a, b))
