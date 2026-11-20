"""Construct each rational address projector from the literal binary source."""

from collections import Counter
from fractions import Fraction
from functools import cache
from math import lcm

from cover import require


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(rows):
    return list(map(list, zip(*rows, strict=True)))


def multiply(a, b):
    cols = transpose(b)
    return [
        [sum(x * y for x, y in zip(row, col, strict=True)) for col in cols] for row in a
    ]


def inverse(a):
    n = len(a)
    rows = [
        list(map(Fraction, row + unit))
        for row, unit in zip(a, identity(n), strict=True)
    ]
    for j in range(n):
        k = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[k] = rows[k], rows[j]
        pivot = rows[j][j]
        rows[j] = [x / pivot for x in rows[j]]
        for k in range(n):
            if k != j and rows[k][j]:
                c = rows[k][j]
                rows[k] = [u - c * v for u, v in zip(rows[k], rows[j], strict=True)]
    return [row[n:] for row in rows]


def projector(frame):
    basis = transpose([list(map(Fraction, row)) for row in frame["B"] + frame["A"]])
    rank = frame["dim"]
    require(len(basis) == 8 and rank == len(frame["B"]), "rational chart dimensions")
    complement = [[x if j < rank else 0 for j, x in enumerate(row)] for row in basis]
    matrix = multiply(complement, inverse(basis))
    den = lcm(*(x.denominator for row in matrix for x in row))
    scaled = [[int(den * x) for x in row] for row in matrix]
    require(
        scaled == transpose(scaled)
        and multiply(scaled, scaled) == [[den * x for x in row] for row in scaled]
        and sum(scaled[i][i] for i in range(8)) == rank * den,
        "orthogonal split projector",
    )
    return rank, den, scaled


def native_rows(word, reverse=False):
    n = word["public"]
    tags = (
        list(word["final"] if reverse else word["start"])
        + [None] * word["owned_fields"]
    )
    fields = [1 << j for j in range(n)] + [0] * word["owned_fields"]
    for op, r, *p in reversed(word["program"]) if reverse else word["program"]:
        if op in ("INIT", "CLEAR"):
            enter = (op == "INIT") != reverse
            require(r >= n and tags[r] == (None if enter else p[0]), "private lifetime")
            tags[r] = p[0] if enter else None
            fields[r] = 0
        elif op == "ADD":
            s, k = p
            require(r != s and tags[r] == tags[s] == k, "common XOR chart")
            if reverse:
                r, s = s, r
            fields[r] ^= fields[s]
        elif op == "SWAP":
            (s,) = p
            require(tags[r] is not None and tags[s] is not None, "complete swap")
            tags[r], tags[s] = tags[s], tags[r]
            fields[r], fields[s] = fields[s], fields[r]
        else:
            require(op == "MOVE", "binary instruction")
            a, b = reversed(p) if reverse else p
            require(tags[r] == a, "source chart at movement")
            tags[r] = b
    require(
        tags
        == list(word["start"] if reverse else word["final"])
        + [None] * word["owned_fields"],
        "complete return",
    )
    for r in range(n):
        src = r + 111 if reverse else r - 111
        cross = r < 111 if reverse else 111 <= r < 222
        require(
            fields[r] == ((1 << r) ^ (1 << src if cross else 0)),
            "entire native XOR matrix",
        )


def binary_native(word):
    raw = word["frames"]
    charts = {int(k): projector(frame) for k, frame in raw.items()}

    @cache
    def difference(a, b):
        (lo, d, x), (hi, e, y) = sorted((charts[a], charts[b]), key=lambda z: z[0])
        require(
            lo < hi
            and multiply(x, y) == multiply(y, x) == [[e * s for s in row] for row in x],
            "nested native pair",
        )
        return hi - lo

    paid = Counter(
        difference(a, b)
        for op, _r, a, b in (e for e in word["program"] if e[0] == "MOVE")
    )
    helpers = Counter(
        difference(a, b)
        for a, b in zip(word["start"][222:], word["final"][222:], strict=True)
    )
    ports = []
    for i in range(111):
        h, v = word["start"][i], word["final"][i + 111]
        h_rank, d, head = charts[h]
        v_rank, e, body = charts[v]
        require(
            (
                h_rank,
                v_rank,
                charts[word["final"][i]][0],
                charts[word["start"][i + 111]][0],
            )
            == (1, 7, 8, 0),
            "head and body quartet",
        )
        require(
            all(
                e * head[j][k] + d * body[j][k] == int(j == k) * d * e
                for j in range(8)
                for k in range(8)
            ),
            "complementary port projectors",
        )
        change = transpose(
            [list(map(Fraction, row)) for row in raw[str(h)]["B"] + raw[str(v)]["B"]]
        )
        undo = inverse(change)
        diagonal = multiply(multiply(undo, head), change)
        require(
            all(
                diagonal[j][k] == d * int(j == k == 0)
                for j in range(8)
                for k in range(8)
            ),
            "full port basis",
        )
        ports.append((change, undo))
    for dual in (False, True):
        native_rows(word, dual)
    return charts, ports, paid, helpers


def placed_port(port, stage, coordinates):
    """Apply S in the 134-axis caller. Each port keeps its own head line."""
    u, undo = port
    j = 8 + 7 * stage
    result = list(coordinates)
    work = [row[0] for row in multiply(undo, [[c] for c in result[:8]])]
    work[1:], result[j : j + 7] = result[j : j + 7], work[1:]
    result[:8] = [row[0] for row in multiply(u, [[c] for c in work])]
    return result
