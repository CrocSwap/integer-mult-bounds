"""Finite-field flags and the literal edge-query word.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(matrix, p):
    a = [row[:] for row in matrix]
    if not a:
        return 0
    m, n, r = len(a), len(a[0]), 0
    for j in range(n):
        pivot = next((i for i in range(r, m) if a[i][j] % p), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = pow(a[r][j] % p, -1, p)
        a[r] = [v*scale % p for v in a[r]]
        for i in range(r+1, m):
            z = a[i][j] % p
            a[i] = [(x-z*y) % p for x, y in zip(a[i], a[r])]
        r += 1
        if r == m:
            break
    return r


def audit(matrix, levels, allowed, p):
    require(p in (2, 3, 5), 'unsupported replay field')
    require(type(levels) is tuple and levels and all(type(v) is tuple and v for v in levels), 'levels shape')
    require(all(all(type(x) is int for x in v) and list(v) == sorted(set(v)) for v in levels), 'levels not strictly increasing')
    coordinates = [(i, t) for i, layer in enumerate(levels) for t in layer]
    size = len(coordinates)
    require(size <= 120, 'replay size limit')
    require(type(allowed) is frozenset and all(type(e) is tuple and len(e) == 2 and
            all(type(i) is int and 0 <= i < len(levels) for i in e) and e[0] != e[1]
            for e in allowed), 'invalid directed mask')
    require(len(matrix) == size and all(len(row) == size for row in matrix), 'matrix shape')
    require(all(type(x) is int and 0 <= x < p for row in matrix for x in row), 'noncanonical field entry')
    defect = [[0]*size for _ in range(size)]
    for a, (i, t) in enumerate(coordinates):
        for b, (j, u) in enumerate(coordinates):
            if i == j:
                require(matrix[a][b] == int(a == b), 'diagonal block is not identity')
            elif (i, j) not in allowed:
                require(matrix[a][b] == 0, 'forbidden block')
            if t > u:
                defect[a][b] = matrix[a][b]
    return rank(matrix, p), rank(defect, p), defect


def cycle(n, copies):
    require(type(n) is int and n >= 5 and n % 2 == 1, 'cycle must be odd and at least five')
    require(type(copies) is int and copies > 0 and 2*n*copies <= 120, 'copy limit')
    labels = [(c, (i-1) % n if a == 0 else i) for i in range(n)
              for c in range(copies) for a in range(2)]
    matrix = [[int(x == y) for y in labels] for x in labels]
    allowed = frozenset((i, j) for i in range(n) for j in range(n) if (i-j) % n in (1, n-1))
    return matrix, allowed


def word(n, copies, dirty):
    require(type(dirty) is bool, 'dirty mode must be boolean')
    require(type(n) is int and n >= 5 and n % 2 == 1, 'cycle must be odd and at least five')
    require(type(copies) is int and copies > 0 and 2*n*copies <= 120, 'copy limit')
    size = 2*n*copies
    q = 2*size
    result = []
    for i in range(n):
        for c in range(copies):
            a = 2*copies*i+2*c+1
            b = 2*copies*((i+1) % n)+2*c
            u, v = size+a, size+b
            if dirty:
                result += [(u, q, -1), (v, q, -1)]
            result += [(q, a, 1), (q, b, 1), (u, q, 1), (v, q, 1),
                       (q, b, -1), (q, a, -1)]
    return tuple(result)


def execute(values, operations):
    values = list(values)
    maximum = max(map(abs, values), default=0)
    for dst, src, sign in operations:
        require(dst != src and sign in (-1, 1), 'invalid ADD')
        values[dst] += sign*values[src]
        maximum = max(maximum, abs(values[dst]))
    return values, maximum
