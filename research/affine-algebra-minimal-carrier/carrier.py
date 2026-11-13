"""Bounded exact affine carriers; no predecessor code or external dependencies."""

SPECS = {
    "F2": (2, (0, 1)), "F3": (3, (0, 1)),
    "F4": (2, (1, 1, 1)), "F5": (5, (0, 1)),
    "F7": (7, (0, 1)), "F8": (2, (1, 1, 0, 1)),
    "F9": (3, (1, 0, 1)),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digits(value, prime, degree):
    result = []
    for _ in range(degree):
        result.append(value % prime)
        value //= prime
    return result


def encode(coefficients, prime):
    result = 0
    for coefficient in reversed(coefficients):
        result = result * prime + coefficient % prime
    return result


def product(left, right, prime, modulus):
    degree = len(modulus) - 1
    a, b = digits(left, prime, degree), digits(right, prime, degree)
    c = [0] * (2 * degree - 1)
    for i in range(degree):
        for j in range(degree):
            c[i + j] += a[i] * b[j]
    for i in range(2 * degree - 2, degree - 1, -1):
        lead = c[i] % prime
        for j in range(degree + 1):
            c[i - degree + j] -= lead * modulus[j]
    return encode(c[:degree], prime)


class Field:
    __slots__ = ("name", "prime", "size", "add", "mul", "neg")

    def __init__(self, name, prime, size, add, mul, neg):
        self.name = name
        self.prime = prime
        self.size = size
        self.add = add
        self.mul = mul
        self.neg = neg


def field(name):
    require(name in SPECS, "unsupported finite field")
    prime, modulus = SPECS[name]
    degree = len(modulus) - 1
    size = prime ** degree
    values = [digits(x, prime, degree) for x in range(size)]
    add = tuple(tuple(encode([values[x][i] + values[y][i]
                            for i in range(degree)], prime)
                      for y in range(size)) for x in range(size))
    mul = tuple(tuple(product(x, y, prime, modulus)
                      for y in range(size)) for x in range(size))
    neg = tuple(encode([-v for v in values[x]], prime) for x in range(size))
    require(all(any(mul[x][y] == 1 for y in range(1, size))
                for x in range(1, size)), "field contains a nonunit")
    return Field(name, prime, size, add, mul, neg)


def subgroup(f, order):
    require(type(order) is int and 1 <= order < f.size
            and (f.size - 1) % order == 0, "invalid subgroup order")
    for generator in range(1, f.size):
        powers, value = [], 1
        for _ in range(order):
            powers.append(value)
            value = f.mul[value][generator]
        if value == 1 and len(set(powers)) == order:
            return tuple(powers)
    raise ValueError("subgroup generator not found")


def elements(f, h):
    return tuple((a, b) for a in h for b in range(f.size))


def compose(f, left, right):
    a, b = left
    c, d = right
    return f.mul[a][c], f.add[b][f.mul[a][d]]


def natural(f, g):
    a, b = g
    return tuple(f.add[f.mul[a][x]][b] for x in range(f.size))


def zero_matrix(size):
    return [[0] * size for _ in range(size)]


def matrices(f, h, g):
    """Return natural, augmentation, and augmented/quotient carrier matrices."""
    permutation = natural(f, g)
    q, order = f.size, len(h)
    nat, aug = zero_matrix(q), zero_matrix(q - 1)
    hybrid = zero_matrix(q + order - 1)
    for x, y in enumerate(permutation):
        nat[y][x] = 1
    for x in range(1, q):
        for y in range(1, q):
            entry = int(permutation[x] == y) - int(permutation[0] == y)
            aug[y - 1][x - 1] = entry
            hybrid[y - 1][x - 1] = entry
    for i, a in enumerate(h):
        j = h.index(f.mul[g[0]][a])
        hybrid[q - 1 + j][q - 1 + i] = 1
    return nat, aug, hybrid


def linear_combination(mats, coefficients, modulus):
    require(len(mats) == len(coefficients) and len(mats) <= 72,
            "coefficient length mismatch")
    size = len(mats[0])
    require(1 <= size <= 16, "matrix capacity exceeded")
    return [[sum(c * matrix[i][j] for c, matrix in zip(coefficients, mats))
             % modulus for j in range(size)] for i in range(size)]


def recover(f, h, matrix, modulus):
    """Invert the hybrid algebra map using affine line sums, with no H division."""
    q, order = f.size, len(h)
    require(modulus in (2, 3, 5, 7) and q % modulus != 0,
            "unsupported coefficient characteristic")
    size = q + order - 1
    require(len(matrix) == size and all(len(row) == size for row in matrix),
            "wrong carrier matrix shape")
    require(all(type(x) is int for row in matrix for x in row),
            "noninteger carrier entry")
    require(all(matrix[i][j] % modulus == 0
                for i in range(size) for j in range(size)
                if (i < q - 1) != (j < q - 1)), "mixed carrier blocks")
    sums = [matrix[q - 1 + a][q - 1] % modulus for a in range(order)]
    total, invq = sum(sums) % modulus, pow(q, -1, modulus)
    difference = [[0] + list(row[:q - 1]) for row in matrix[:q - 1]]
    difference.insert(0, [0] + [-sum(matrix[i][j] for i in range(q - 1))
                               for j in range(q - 1)])
    nat = zero_matrix(q)
    for y in range(q):
        first = (total - sum(difference[y])) * invq % modulus
        nat[y] = [(first + difference[y][x]) % modulus for x in range(q)]
    result = []
    for i, a in enumerate(h):
        for b in range(q):
            line = sum(nat[f.add[f.mul[a][x]][b]][x] for x in range(q))
            result.append((line - total + sums[i]) * invq % modulus)
    # This is a decoder for the algebra image, not for arbitrary block matrices.
    mats = [matrices(f, h, g)[2] for g in elements(f, h)]
    require(linear_combination(mats, result, modulus)
            == [[x % modulus for x in row] for row in matrix],
            "matrix is outside the carrier algebra")
    return result


def rank(vectors, modulus):
    """Finite row elimination; at most 72 vectors of length at most 256."""
    require(len(vectors) <= 72 and all(len(v) <= 256 for v in vectors),
            "rank capacity exceeded")
    pivots = {}
    for vector in vectors:
        row = [x % modulus for x in vector]
        for pivot, basis in sorted(pivots.items()):
            coefficient = row[pivot]
            if coefficient:
                row = [(x - coefficient * y) % modulus
                       for x, y in zip(row, basis)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            inverse = pow(row[pivot], -1, modulus)
            pivots[pivot] = [x * inverse % modulus for x in row]
    return len(pivots)
