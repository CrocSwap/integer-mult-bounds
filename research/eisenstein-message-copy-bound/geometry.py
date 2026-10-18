"""Exact rational geometry for the 40 Eisenstein E8 lines; standard library only.

Independent implementation of the geometry specified by PR620. Coordinates use
the doubled standard E8 roots, and rotation4 is four times an order-three
orthogonal transformation. No predecessor executable code is imported.
"""

from functools import reduce
from itertools import combinations, product
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def primitive(row):
    divisor = reduce(gcd, row, 0)
    if not divisor:
        return tuple(row)
    first = next(x for x in row if x)
    divisor = divisor if first > 0 else -divisor
    return tuple(x // divisor for x in row)


def basis(rows):
    """Canonical rational row space, with primitive integer rows (exact RREF)."""
    pivots = {}
    for original in rows:
        row = primitive(original)
        for p, old in sorted(pivots.items()):
            if row[p]:
                row = primitive([old[p] * x - row[p] * y for x, y in zip(row, old)])
        if any(row):
            p = next(i for i, x in enumerate(row) if x)
            pivots[p] = row
    for p in sorted(pivots, reverse=True):
        row = pivots[p]
        for q in sorted(pivots):
            if q >= p:
                break
            old = pivots[q]
            if old[p]:
                pivots[q] = primitive([row[p] * x - old[p] * y for x, y in zip(old, row)])
    return tuple(pivots[p] for p in sorted(pivots))


def contains(span, row):
    row = tuple(row)
    for old in span:
        p = next(i for i, x in enumerate(old) if x)
        if row[p]:
            row = primitive([old[p] * x - row[p] * y for x, y in zip(row, old)])
    return not any(row)


def matmul(a, b):
    columns = tuple(zip(*b))
    return tuple(tuple(dot(row, col) for col in columns) for row in a)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def roots():
    """The PR620/standard_e8 order: positive representatives, then negatives."""
    positive = []
    for i, j in combinations(range(8), 2):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            positive.append(tuple(row))
    positive.extend((1,) + s for s in product((1, -1), repeat=7) if s.count(-1) % 2 == 0)
    return tuple(positive + [tuple(-x for x in r) for r in positive])


def rotation(roots_):
    """Product of Coxeter rotations on the first four orthogonal A2 planes."""
    chosen = []
    for a in roots_:
        if len(chosen) == 4:
            break
        if any(dot(a, x) for pair in chosen for x in pair):
            continue
        for b in roots_:
            if dot(a, b) == -4 and all(dot(b, x) == 0 for pair in chosen for x in pair):
                chosen.append((a, b))
                break
    require(len(chosen) == 4, "four orthogonal A2 planes missing")
    g = identity(8)
    for pair in chosen:
        for a in pair:
            reflection8 = tuple(tuple(8 * int(i == j) - 2 * a[i] * a[j] for j in range(8)) for i in range(8))
            g = matmul(g, reflection8)
    denominator = 8 ** 8 // 4
    require(all(x % denominator == 0 for row in g for x in row), "nonintegral rotation4")
    return tuple(tuple(x // denominator for x in row) for row in g), tuple(chosen)


def image(g, r):
    values = tuple(dot(row, r) for row in g)
    require(all(x % 4 == 0 for x in values), "rotation does not preserve integral roots")
    return tuple(x // 4 for x in values)


def make_geometry():
    rr = roots()
    require(len(set(rr)) == 240 and all(dot(r, r) == 8 for r in rr), "bad E8 roots")
    g, planes = rotation(rr)
    square = matmul(g, g)
    require(all(square[i][j] + 4 * g[i][j] + 16 * int(i == j) == 0 for i in range(8) for j in range(8)), "bad order-three polynomial")
    require(matmul(g, tuple(zip(*g))) == tuple(tuple(16 * x for x in row) for row in identity(8)), "rotation is not orthogonal")
    require(set(image(g, r) for r in rr) == set(rr), "rotation changes root set")
    representatives, spans, orbits, seen = [], [], [], set()
    for r in rr:
        if r in seen:
            continue
        gr = image(g, r)
        orbit3 = (r, gr, image(g, gr))
        orbit = set(orbit3) | {tuple(-x for x in v) for v in orbit3}
        require(len(orbit) == 6 and not orbit & seen, "bad six-root orbit")
        span = basis((r, gr))
        require(len(span) == 2, "line is not rational rank two")
        require({v for v in rr if contains(span, v)} == orbit, "orbit is not the full root line")
        representatives.append(r)
        spans.append(span)
        orbits.append(tuple(sorted(orbit)))
        seen.update(orbit)
    require(len(spans) == 40 and len(set(spans)) == 40 and seen == set(rr), "wrong Eisenstein line partition")
    adjacent = []
    for i, left in enumerate(spans):
        mask = 0
        for j, right in enumerate(spans):
            if i != j and any(dot(a, b) for a in left for b in right):
                mask |= 1 << j
        adjacent.append(mask)
    require({a.bit_count() for a in adjacent} == {27}, "nonorthogonality degree changed")
    return rr, g, planes, tuple(representatives), tuple(spans), tuple(orbits), tuple(adjacent)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def maximal_cliques(adjacent):
    """Bron-Kerbosch with pivot; returns every inclusion-maximal clique."""
    result = []

    def visit(chosen, possible, excluded):
        if not possible and not excluded:
            result.append(chosen)
            return
        union = possible | excluded
        pivot = max(bits(union), key=lambda i: (possible & adjacent[i]).bit_count())
        candidates = possible & ~adjacent[pivot]
        for i in bits(candidates):
            bit = 1 << i
            visit(chosen | bit, possible & adjacent[i], excluded & adjacent[i])
            possible &= ~bit
            excluded |= bit

    visit(0, (1 << len(adjacent)) - 1, 0)
    return tuple(sorted(result))


def flats(line_spans):
    """All line-generated subspaces; adding one line is a complete closure walk."""
    levels = [{(): ()}]
    for rank in range(4):
        next_level = {}
        for span, generators in levels[-1].items():
            for i, line in enumerate(line_spans):
                if contains(span, line[0]):
                    require(all(contains(span, r) for r in line), "partial Eisenstein line")
                    continue
                child = basis(span + line)
                require(len(child) == 2 * (rank + 1), "rank did not increase by one Eisenstein unit")
                next_level.setdefault(child, generators + (i,))
        levels.append(next_level)
    result = []
    for rank, level in enumerate(levels):
        for span, generators in level.items():
            mask = sum(1 << i for i, line in enumerate(line_spans) if contains(span, line[0]))
            require(basis([row for i in bits(mask) for row in line_spans[i]]) == span, "flat closure span changed")
            result.append((rank, mask, span, generators))
    require(len({x[1] for x in result}) == len(result), "duplicate flat masks")
    return tuple(sorted(result, key=lambda x: (x[0], x[1])))


def pairing_rank(left, right):
    gram = tuple(tuple(dot(a, b) for b in right) for a in left)
    rational_rank = len(basis(gram))
    require(rational_rank % 2 == 0, "odd rational pairing rank")
    return rational_rank // 2
