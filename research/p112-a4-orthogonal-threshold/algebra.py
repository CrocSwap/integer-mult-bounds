"""Bounded exact linear algebra for the nine-piece P112 witness."""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def support(row):
    return frozenset(i for i, x in enumerate(row) if x)


def rank(rows):
    require(1 <= len(rows) <= 17, "rank row bound")
    width = len(rows[0])
    require(1 <= width <= 112 and all(len(r) == width for r in rows), "rank shape")
    require(
        all(type(x) is int and abs(x) <= 8 for r in rows for x in r), "rank entries"
    )
    matrix = [[Fraction(x) for x in row] for row in rows]
    pivots = []
    for col in range(width):
        pivot = next((i for i in range(len(pivots), len(rows)) if matrix[i][col]), None)
        if pivot is None:
            continue
        index = len(pivots)
        matrix[index], matrix[pivot] = matrix[pivot], matrix[index]
        divisor = matrix[index][col]
        matrix[index] = [x / divisor for x in matrix[index]]
        for i in range(index + 1, len(rows)):
            factor = matrix[i][col]
            matrix[i] = [
                x - factor * y for x, y in zip(matrix[i], matrix[index], strict=True)
            ]
        pivots.append(col)
        if len(pivots) == len(rows):
            break
    return tuple(pivots)


def parse_witness(raw):
    require(
        type(raw) is dict
        and set(raw) == {"directions_doubled", "cuts", "endpoints_sparse"},
        "witness fields",
    )
    directions, cuts, sparse = (
        raw["directions_doubled"],
        raw["cuts"],
        raw["endpoints_sparse"],
    )
    require(type(directions) is list and len(directions) == 4, "direction count")
    require(all(type(r) is list and len(r) == 8 for r in directions), "direction shape")
    require(
        all(type(x) is int and -2 <= x <= 2 for r in directions for x in r),
        "direction entries",
    )
    require(type(cuts) is list and len(cuts) == 29, "cut count")
    require(all(type(i) is int and 0 <= i < 112 for i in cuts), "cut indices")
    require(cuts == sorted(set(cuts)), "duplicate or unsorted cuts")
    require(type(sparse) is list and len(sparse) == 5, "endpoint count")
    endpoints = []
    for entries in sparse:
        require(type(entries) is list and 1 <= len(entries) <= 20, "endpoint size")
        require(all(type(p) is list and len(p) == 2 for p in entries), "sparse pair")
        require(
            all(
                type(i) is int and 0 <= i < 112 and type(x) is int and 0 < abs(x) <= 2
                for i, x in entries
            ),
            "endpoint entries",
        )
        require(
            len({i for i, _ in entries}) == len(entries), "duplicate endpoint index"
        )
        row = [0] * 112
        for i, x in entries:
            row[i] = x
        endpoints.append(tuple(row))
    return tuple(map(tuple, directions)), frozenset(cuts), tuple(endpoints)
