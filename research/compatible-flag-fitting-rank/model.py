"""Exact finite helpers. Produced by Nick Petalas. Apache-2.0."""

from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(1 <= n <= 20, "identity capacity")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def rank_mod(matrix, p):
    require(p in (2, 3, 5), "unsupported finite field")
    n = len(matrix)
    require(1 <= n <= 20, "row capacity")
    m = len(matrix[0])
    require(1 <= m <= 20 and all(len(row) == m for row in matrix), "shape")
    a = [[x % p for x in row] for row in matrix]
    rank = 0
    for col in range(m):
        pivot = next((i for i in range(rank, n) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = pow(a[rank][col], -1, p)
        a[rank] = [(x * scale) % p for x in a[rank]]
        for i in range(rank + 1, n):
            scale = a[i][col]
            a[i] = [(x - scale * y) % p for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == n:
            break
    return rank


def rank_bits(rows, width):
    require(1 <= width <= 10 and 1 <= len(rows) <= 10, "binary capacity")
    basis = [0] * width
    for row in rows:
        require(0 <= row < (1 << width), "binary row range")
        for col in range(width - 1, -1, -1):
            if not (row >> col) & 1:
                continue
            if basis[col]:
                row ^= basis[col]
            else:
                basis[col] = row
                break
    return sum(bool(row) for row in basis)


def image_rank(rows, width):
    """Independent binary oracle: enumerate the entire row image."""
    require(1 <= len(rows) <= 10 and 1 <= width <= 10, "image capacity")
    image = {0}
    for row in rows:
        require(0 <= row < (1 << width), "image row range")
        image |= {value ^ row for value in tuple(image)}
    require(len(image) & (len(image) - 1) == 0, "image not a vector space")
    return len(image).bit_length() - 1


def multiply(a, b, p):
    require(p in (2, 3, 5), "unsupported finite field")
    require(1 <= len(a) <= 20 and 1 <= len(b) <= 20, "product capacity")
    require(all(len(row) == len(b) for row in a), "product shape")
    require(1 <= len(b[0]) <= 20 and all(len(row) == len(b[0]) for row in b), "right shape")
    return [[sum(x * b[k][j] for k, x in enumerate(row)) % p
             for j in range(len(b[0]))] for row in a]


def inverse(a, p):
    n = len(a)
    require(1 <= n <= 4 and all(len(row) == n for row in a), "chart shape")
    require(p in (2, 3, 5), "unsupported finite field")
    a = [[x % p for x in row] + unit for row, unit in zip(a, identity(n))]
    for col in range(n):
        pivot = next((i for i in range(col, n) if a[i][col]), None)
        require(pivot is not None, "singular chart")
        a[col], a[pivot] = a[pivot], a[col]
        scale = pow(a[col][col], -1, p)
        a[col] = [(x * scale) % p for x in a[col]]
        for i in range(n):
            if i == col:
                continue
            scale = a[i][col]
            a[i] = [(x - scale * y) % p for x, y in zip(a[i], a[col])]
    return [row[n:] for row in a]


def pairs(n):
    require(1 <= n <= 5, "port capacity")
    return [(i, j) for i in range(n) for j in range(n) if i != j]


def scalar_minimum(n, mask, p):
    edges = pairs(n)
    require(n <= 3 and 0 <= mask < (1 << len(edges)), "scalar census capacity")
    active = [edge for k, edge in enumerate(edges) if (mask >> k) & 1]
    minimum, witness, checked = n + 1, None, 0
    for values in product(range(p), repeat=len(active)):
        matrix = identity(n)
        for (i, j), value in zip(active, values):
            matrix[i][j] = value
        rank = rank_mod(matrix, p)
        if rank < minimum:
            minimum, witness = rank, matrix
        checked += 1
    require(witness is not None and minimum >= 1, "missing scalar witness")
    return minimum, witness, checked


def block(matrix, i, j, d):
    return [row[j * d:(j + 1) * d] for row in matrix[i * d:(i + 1) * d]]


def install(matrix, i, j, value, d):
    for a in range(d):
        matrix[i * d + a][j * d:(j + 1) * d] = value[a][:]


def conjugate_ports(matrix, charts, p):
    n, d = len(charts), len(charts[0])
    require(n * d == len(matrix) and n * d <= 20, "conjugation capacity")
    inverses = [inverse(chart, p) for chart in charts]
    answer = [[0] * (n * d) for _ in range(n * d)]
    for i in range(n):
        for j in range(n):
            value = multiply(multiply(charts[i], block(matrix, i, j, d), p), inverses[j], p)
            install(answer, i, j, value, d)
    return answer


def audit_flagged(matrix, mask, d, charts, p):
    n = len(charts)
    require(1 <= n <= 5 and 1 <= d <= 4 and n * d <= 20, "audit capacity")
    require(0 <= mask < (1 << len(pairs(n))), "mask range")
    require(len(matrix) == n * d and all(len(row) == n * d for row in matrix), "matrix shape")
    require(all(len(c) == d and all(len(row) == d for row in c) for c in charts), "chart size")
    inverses = [inverse(chart, p) for chart in charts]
    active = {edge for k, edge in enumerate(pairs(n)) if (mask >> k) & 1}
    layers = [identity(n) for _ in range(d)]
    for i in range(n):
        for j in range(n):
            value = [[x % p for x in row] for row in block(matrix, i, j, d)]
            if i == j:
                require(value == identity(d), "nonidentity diagonal")
            elif (i, j) not in active:
                require(not any(map(any, value)), "forbidden block")
            triangular = multiply(multiply(inverses[i], value, p), charts[j], p)
            require(not any(triangular[a][b] for a in range(d) for b in range(a)), "incompatible flag")
            for a in range(d):
                layers[a][i][j] = triangular[a][a]
    ranks = [rank_mod(layer, p) for layer in layers]
    rank = rank_mod(matrix, p)
    require(rank >= sum(ranks), "flag-layer rank bound")
    return rank, ranks
