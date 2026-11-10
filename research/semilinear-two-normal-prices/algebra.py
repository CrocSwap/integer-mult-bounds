"""Exact finite corroboration for the weighted two-normal theorem.

Produced by Nick Petalas. Apache-2.0.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mul(a, b, degree, polynomial):
    result = 0
    for _ in range(degree):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << degree):
            a ^= polynomial
    return result


def inverse(value, degree, polynomial):
    require(0 < value < 1 << degree, "nonzero field element required")
    result = 1
    for _ in range((1 << degree) - 2):
        result = mul(result, value, degree, polynomial)
    return result


def identity(size):
    return tuple(tuple(int(i == j) for j in range(size)) for i in range(size))


def multiply(left, right, degree, polynomial):
    size = len(left)
    rows = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                rows[i][j] ^= mul(left[i][k], right[k][j], degree, polynomial)
    return tuple(tuple(row) for row in rows)


def projectors(size):
    result = []
    for u in range(1, 1 << size):
        for v in range(1, 1 << size):
            if (u & v).bit_count() % 2:
                result.append(tuple(tuple(((u >> i) & 1) * ((v >> j) & 1)
                                          for j in range(size)) for i in range(size)))
    return tuple(result)


def validate_projector(projector):
    size = len(projector)
    require(1 <= size <= 3, "finite checker supports one to three roles")
    require(all(len(row) == size for row in projector), "square projector required")
    require(all(value in (0, 1) for row in projector for value in row), "binary projector required")
    require(projector in projectors(size), "rank-one idempotent required")


def gate(projector, scalar, degree, polynomial):
    validate_projector(projector)
    require(2 <= scalar < 1 << degree, "nonidentity invertible scalar required")
    size = len(projector)
    return tuple(tuple(int(i == j) ^ mul(scalar ^ 1, projector[i][j], degree, polynomial)
                       for j in range(size)) for i in range(size))


def quotient_census(degree, polynomial, size):
    factors = [(p, scalar, gate(p, scalar, degree, polynomial))
               for p in projectors(size) for scalar in range(2, 1 << degree)]
    inverse_gates = {gate(p, inverse(scalar, degree, polynomial), degree, polynomial): (p, scalar)
                     for p, scalar, _ in factors}
    require(len(inverse_gates) == len(factors), "injective gate parameterization")
    closures = 0
    for p, scalar, first in factors:
        for q, other, second in factors:
            third = inverse_gates.get(multiply(second, first, degree, polynomial))
            if third is not None:
                r, last = third
                require(p == q == r, "three-call quotient loop has a common projector")
                require(mul(mul(scalar, other, degree, polynomial), last, degree, polynomial) == 1,
                        "scalar product is one")
                closures += 1
    expected = len(projectors(size)) * ((1 << degree) - 2) * ((1 << degree) - 3)
    require(closures == expected, "complete quotient-loop count")
    return {"degree": degree, "roles": size, "pairs": len(factors) ** 2, "loops": closures}


def group_table():
    labels = tuple((a, j) for a in range(1, 8) for j in range(3))
    lookup = {label: index for index, label in enumerate(labels)}
    table = []
    for a, j in labels:
        row = []
        for b, k in labels:
            twisted = b
            for _ in range(j):
                twisted = mul(twisted, twisted, 3, 11)
            row.append(lookup[(mul(a, twisted, 3, 11), (j + k) % 3)])
        table.append(tuple(row))
    return labels, tuple(table)


def coefficients(value):
    require(0 <= value < 1 << 21, "group algebra coefficient range")
    result = []
    for _ in range(21):
        if not value:
            break
        lowest = value & -value
        result.append(lowest.bit_length() - 1)
        value ^= lowest
    require(value == 0, "group algebra has exactly 21 labels")
    return result


def formal_mul(left, right, table):
    value = 0
    for i in coefficients(left):
        for j in coefficients(right):
            value ^= 1 << table[i][j]
    return value


def formal_product(left, right, table):
    size = len(left)
    rows = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                rows[i][j] ^= formal_mul(left[i][k], right[k][j], table)
    return tuple(tuple(row) for row in rows)


def formal_gate(projector, label):
    validate_projector(projector)
    require(0 <= label < 21, "formal label range")
    size = len(projector)
    return tuple(tuple(int(i == j) ^ (projector[i][j] * ((1 << label) ^ 1))
                       for j in range(size)) for i in range(size))


def target(labels):
    return tuple(tuple((1 << label) if i == j else 0 for j in range(len(labels)))
                 for i, label in enumerate(labels))
