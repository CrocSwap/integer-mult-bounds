"""Exact bounded linear algebra for the width-two odd-cycle normal form.

produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction

FIELDS = (0, 2, 3, 5, 101)
MAX_SIZE = 26


def check(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value, prime):
    return value % prime if prime else Fraction(value)


def inverse(value, prime):
    check(value != 0, "zero pivot")
    return pow(value, -1, prime) if prime else 1 / Fraction(value)


def matrix(data, prime):
    check(type(prime) is int and prime in FIELDS, "unsupported field")
    check(0 < len(data) <= MAX_SIZE, "row capacity")
    width = len(data[0])
    check(0 < width <= MAX_SIZE, "column capacity")
    result = []
    for row in data:
        check(len(row) == width, "ragged matrix")
        for value in row:
            check(type(value) in (int, Fraction), "nonexact coefficient")
            check(not prime or type(value) is int, "noninteger residue")
            q = Fraction(value)
            check(q.numerator.bit_length() <= 256, "numerator capacity")
            check(q.denominator.bit_length() <= 256, "denominator capacity")
        result.append(tuple(scalar(value, prime) for value in row))
    return tuple(result)


def multiply(left, right, prime):
    check(len(left[0]) == len(right), "product dimensions")
    return tuple(
        tuple(
            scalar(sum(a * b for a, b in zip(row, column, strict=True)), prime)
            for column in zip(*right, strict=True)
        )
        for row in left
    )


def rank(data, prime):
    rows = [list(row) for row in data]
    pivot = 0
    for column in range(len(rows[0])):
        chosen = next((j for j in range(pivot, len(rows)) if rows[j][column]), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        scale = inverse(rows[pivot][column], prime)
        rows[pivot] = [scalar(x * scale, prime) for x in rows[pivot]]
        for j in range(pivot + 1, len(rows)):
            coefficient = rows[j][column]
            rows[j] = [
                scalar(x - coefficient * y, prime)
                for x, y in zip(rows[j], rows[pivot], strict=True)
            ]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def inverse2(data, prime):
    (a, b), (c, d) = data
    determinant = scalar(a * d - b * c, prime)
    scale = inverse(determinant, prime)
    return tuple(
        tuple(scalar(scale * x, prime) for x in row) for row in ((d, -b), (-c, a))
    )


def block(data, i, j):
    return tuple(tuple(data[2 * i + a][2 * j + b] for b in range(2)) for a in range(2))


def diagonal(blocks):
    size = 2 * len(blocks)
    return tuple(
        tuple(
            blocks[i // 2][i % 2][j % 2] if i // 2 == j // 2 else 0 for j in range(size)
        )
        for i in range(size)
    )


def canonical(n):
    check(type(n) is int and 3 <= n <= MAX_SIZE // 2, "cycle capacity")
    rows = [[int(i == j) for j in range(2 * n)] for i in range(2 * n)]
    for i in range(n):
        a, b = 2 * i + 1, 2 * ((i + 1) % n)
        rows[a][b] = rows[b][a] = 1
    return tuple(tuple(row) for row in rows)


def validate_fit(data):
    size = len(data)
    check(size % 2 == 0 and size == len(data[0]), "square width-two fit required")
    n = size // 2
    check(n >= 5 and n % 2 == 1, "odd cycle of length at least five required")
    for i in range(n):
        for j in range(n):
            if i == j:
                check(block(data, i, j) == ((1, 0), (0, 1)), "identity block")
            elif (i - j) % n not in (1, n - 1):
                check(block(data, i, j) == ((0, 0), (0, 0)), "forbidden ordered block")
    return n


def normal_form(data, prime):
    data = matrix(data, prime)
    n = validate_fit(data)
    check(rank(data, prime) == n, "minimum-rank hypothesis")
    left_vectors = []
    for i in range(n):
        previous = (i - 1) % n
        projector = multiply(block(data, i, previous), block(data, previous, i), prime)
        columns = tuple(zip(*projector, strict=True))
        chosen = next((column for column in columns if any(column)), None)
        check(chosen is not None, "missing left edge line")
        left_vectors.append(chosen)
    bases = []
    for i in range(n):
        following = (i + 1) % n
        column = tuple((x,) for x in left_vectors[following])
        right = multiply(block(data, i, following), column, prime)
        bases.append(tuple((left_vectors[i][j], right[j][0]) for j in range(2)))
    change = diagonal(bases)
    undo = diagonal(tuple(inverse2(basis, prime) for basis in bases))
    reduced = multiply(multiply(undo, data, prime), change, prime)
    check(reduced == matrix(canonical(n), prime), "canonical similarity failed")
    return tuple(bases)
