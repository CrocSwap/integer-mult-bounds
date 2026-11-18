"""Enumerate complete binary projector pools. Ali Romman, with Codex. Apache-2.0."""

from itertools import combinations, permutations

COORDINATES = tuple((i, j) for i in range(4) for j in range(4) if i != j)
PROJECTORS = tuple((x, y) for x in range(1, 16) for y in range(1, 16)
                   if (x & y).bit_count() % 2)


def span(rows):
    result = {0}
    for row in rows:
        result |= {row ^ value for value in tuple(result)}
    return result


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def off(image, covector):
    return sum(((image >> i) & (covector >> j) & 1) << bit
               for bit, (i, j) in enumerate(COORDINATES))


PATTERNS = {}
for _pair in PROJECTORS:
    _pattern = off(*_pair)
    if _pattern:
        PATTERNS.setdefault(_pattern, []).append(_pair)


def qualifying(patterns):
    edges = {frozenset(COORDINATES[value.bit_length() - 1])
             for value in patterns if value and value & (value - 1) == 0}
    if not edges or any(a.isdisjoint(b) for a, b in combinations(edges, 2)):
        return None
    pool = tuple(sorted(pair for value in patterns for pair in PATTERNS.get(value, ())))
    if rank(x for x, _ in pool) != 4 or rank(off(*pair) for pair in pool) != 3:
        return None
    return pool


def census():
    found = {}
    count = 0
    for p in range(10):
        for q in range(p + 1, 11):
            for low in range(1 << p):
                a = (1 << p) | low
                for bits in range(1 << (q - 1)):
                    b = (1 << q) | (bits & ((1 << p) - 1)) | ((bits >> p) << (p + 1))
                    patterns = tuple(sorted((1, a << 1, (a << 1) ^ 1,
                                             b << 1, (b << 1) ^ 1,
                                             (a ^ b) << 1, ((a ^ b) << 1) ^ 1)))
                    count += 1
                    pool = qualifying(patterns)
                    if pool is not None:
                        found[patterns] = pool
    return count, found


def canonical(pool):
    best = None
    witness = None
    for basis in permutations(sorted({x for x, _ in pool}), 4):
        if rank(basis) != 4:
            continue
        table = [0]
        for value in basis:
            table += [entry ^ value for entry in table]
        inverse = {value: index for index, value in enumerate(table)}
        key = tuple(sorted(16 * inverse[x] + sum(((y & v).bit_count() % 2) << i
                                                 for i, v in enumerate(basis))
                           for x, y in pool))
        if best is None or key < best:
            best, witness = key, basis
    return best, witness
