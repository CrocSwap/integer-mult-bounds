"""Small exact prime-field linear algebra. Apache-2.0."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduce_system(width, equations, prime):
    rows = [list(row) for row in equations]
    pivots = []
    for column in range(width):
        pivot = next((i for i in range(len(pivots), len(rows))
                      if rows[i][column] % prime), None)
        if pivot is None:
            continue
        index = len(pivots)
        rows[index], rows[pivot] = rows[pivot], rows[index]
        inverse = pow(rows[index][column], -1, prime)
        rows[index] = [x * inverse % prime for x in rows[index]]
        for i in range(len(rows)):
            if i != index:
                coefficient = rows[i][column]
                rows[i] = [(x - coefficient * y) % prime
                           for x, y in zip(rows[i], rows[index])]
        pivots.append(column)
    if any(not any(row[:width]) and row[width] for row in rows):
        return None
    return tuple(tuple(row) for row in rows[:len(pivots)]), tuple(pivots)


def basis(rows, n, prime):
    reduced = reduce_system(n, [tuple(row) + (0,) for row in rows], prime)
    return tuple(row[:n] for row in reduced[0])


def orthogonal(rows, n, prime):
    reduced, pivots = reduce_system(n, [tuple(row) + (0,) for row in rows], prime)
    answer = []
    for free in range(n):
        if free not in pivots:
            vector = [0] * n
            vector[free] = 1
            for row, pivot in zip(reduced, pivots):
                vector[pivot] = -row[free] % prime
            answer.append(tuple(vector))
    return tuple(answer)


def intersection(left, right, n, prime):
    return orthogonal(orthogonal(left, n, prime) + orthogonal(right, n, prime),
                      n, prime)


def coordinates(rows, vector, prime):
    equations = [tuple(row[i] for row in rows) + (entry,)
                 for i, entry in enumerate(vector)]
    result = reduce_system(len(rows), equations, prime)
    require(result is not None, "Vector outside prescribed domain")
    reduced, pivots = result
    require(len(pivots) == len(rows), "Dependent prescribed domain")
    answer = [0] * len(rows)
    for row, pivot in zip(reduced, pivots):
        answer[pivot] = row[-1]
    return tuple(answer)


def apply(columns, vector, prime):
    return tuple(sum(x * column[i] for x, column in zip(vector, columns)) % prime
                 for i in range(len(vector)))


def mapped(rows, fixed, n, prime):
    domain = tuple(pair[0] for pair in fixed)
    images = tuple(pair[1] for pair in fixed)
    answer = []
    for row in rows:
        coefficients = coordinates(domain, row, prime)
        answer.append(tuple(sum(c * y[i] for c, y in zip(coefficients, images)) % prime
                            for i in range(n)))
    return basis(tuple(answer), n, prime)
