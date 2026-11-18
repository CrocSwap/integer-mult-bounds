"""Check the census through full matrices. Ali Romman, with Codex. Apache-2.0."""

from itertools import combinations, product

IDENTITY = (1, 2, 4, 8)


def xor_span(rows):
    values = [0]
    for row in rows:
        for old in tuple(values):
            value = old ^ row
            if value not in values:
                values.append(value)
    return frozenset(values)


def inverse(matrix):
    rows = [matrix[i] | (1 << (4 + i)) for i in range(4)]
    for j in range(4):
        pivot = next((i for i in range(j, 4) if rows[i] & (1 << j)), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(4):
            if i != j and rows[i] & (1 << j):
                rows[i] ^= rows[j]
    return tuple(row >> 4 for row in rows)


def table(matrix):
    values = [0]
    for row in matrix:
        values += [value ^ row for value in values]
    return values


def multiply(a, b):
    sums = table(b)
    return tuple(sums[row] for row in a)


def matrix(image, covector):
    return tuple(covector if image & (1 << i) else 0 for i in range(4))


def packed(rows):
    return sum(row << (4 * i) for i, row in enumerate(rows))


def unpacked(value):
    return tuple((value >> (4 * i)) & 15 for i in range(4))


def pattern(rows):
    return packed(tuple(row & ~(1 << i) for i, row in enumerate(rows)))


def second_census():
    projectors = []
    for rows in product(range(16), repeat=4):
        nonzero = set(rows) - {0}
        if len(nonzero) == 1 and multiply(rows, rows) == rows:
            projectors.append(rows)
    lookup = {}
    for rows in projectors:
        key = pattern(rows)
        if key:
            lookup.setdefault(key, []).append(rows)
    found = {}
    for a, b in combinations(lookup, 2):
        space = xor_span((2, a, b))
        if len(space) != 8:
            continue
        edges = {frozenset(divmod(value.bit_length() - 1, 4))
                 for value in space if value and value & (value - 1) == 0}
        if any(x.isdisjoint(y) for x, y in combinations(edges, 2)):
            continue
        pool = tuple(sorted(packed(rows) for value in space for rows in lookup.get(value, ())))
        columns = [sum(((row >> j) & 1) << i for i, row in enumerate(unpacked(value)))
                   for value in pool for j in range(4)]
        if len(xor_span(columns)) != 16:
            continue
        if len(xor_span(pattern(unpacked(value)) for value in pool)) != 8:
            continue
        found[tuple(sorted(space - {0}))] = pool
    return projectors, found


def group_actions(projectors):
    labels = {rows: i for i, rows in enumerate(projectors)}
    actions = []
    for transform in product(range(16), repeat=4):
        back = inverse(transform)
        if back is None:
            continue
        if multiply(transform, back) != IDENTITY or multiply(back, transform) != IDENTITY:
            raise ValueError('incorrect matrix inverse')
        sums = table(transform)
        image = []
        for projector in projectors:
            partial = table(projector)
            conjugate = tuple(sums[partial[row]] for row in back)
            image.append(labels[conjugate])
        actions.append(bytes(image))
    return actions, labels


def invariant_subspaces(pool):
    spaces = {frozenset({0})}
    for size in range(1, 5):
        spaces.update(xor_span(basis) for basis in combinations(range(1, 16), size))
    if len(spaces) != 67:
        raise ValueError('subspace enumeration')
    counts = [0] * 5
    for space in spaces:
        if all(sum(((row & v).bit_count() % 2) << i for i, row in enumerate(operator)) in space
               for operator in pool for v in space):
            counts[len(space).bit_length() - 1] += 1
    return counts


def orbit_summary(pool, actions, labels):
    original = tuple(sorted(labels[rows] for rows in pool))
    best = None
    stabilizer = 0
    for action in actions:
        key = tuple(sorted(action[index] for index in original))
        stabilizer += key == original
        if best is None or key < best:
            best = key
    if not stabilizer or len(actions) % stabilizer:
        raise ValueError('orbit-stabilizer')
    return best, stabilizer, len(actions) // stabilizer
