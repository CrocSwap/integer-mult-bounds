"""Separate dense-row, right-product census and faithful regular action.

No producer matrix, group, rank, generator or transition routine is imported.
Coordinates are register-major here; verify.py uses coordinate-major packing.
"""
from itertools import product


def xor_all(values):
    value = 0
    for x in values:
        value ^= x
    return value


def dimension(rows, width):
    rows = list(rows)
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> column & 1), None)
        if pivot is not None:
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            for i in range(len(rows)):
                if i != rank and rows[i] >> column & 1:
                    rows[i] ^= rows[rank]
            rank += 1
    return rank


def compose(a, b):
    return tuple(xor_all(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def address_alphabet():
    answer = []
    for i, j in product(range(3), repeat=2):
        if i != j:
            rows = [1, 2, 4]
            rows[i] |= 1 << j
            answer.append(tuple(rows))
    return answer


def scalar_projectors():
    return [rows for rows in product(range(4), repeat=2)
            if dimension(rows, 2) == 1 and compose(rows, rows) == rows]


def canonical(state):
    # Canonical index = 2*coordinate+register; native index = 3*register+coordinate.
    permutation = [0, 3, 1, 4, 2, 5]
    return sum(((state[permutation[i]] >> permutation[j]) & 1) << (6 * i + j)
               for i in range(6) for j in range(6))


def inverse(rows):
    width = len(rows)
    augmented = [row | (1 << (width + i)) for i, row in enumerate(rows)]
    for column in range(width):
        pivot = next(i for i in range(column, width) if augmented[i] >> column & 1)
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        for i in range(width):
            if i != column and augmented[i] >> column & 1:
                augmented[i] ^= augmented[column]
    return tuple(row >> width for row in augmented)


def census():
    group = {g for g in product(range(8), repeat=3) if dimension(g, 3) == 3}
    alphabet = address_alphabet()
    identity = (1, 2, 4)
    distance = {identity: 0}
    frontier = [identity]
    while frontier:
        following = []
        for state in frontier:
            for gate in alphabet:
                changed = compose(state, gate)
                if changed not in distance:
                    distance[changed] = distance[state] + 1
                    following.append(changed)
        frontier = following
    if set(distance) != group or len(group) != 168:
        raise ValueError("independent GL3 coverage failed")
    matrices = []
    for gate in alphabet:
        difference = tuple(x ^ y for x, y in zip(gate, identity))
        for projector in scalar_projectors():
            rows = [1 << i for i in range(6)]
            for p, q, i in product(range(2), range(2), range(3)):
                if projector[p] >> q & 1:
                    rows[3 * p + i] ^= difference[i] << (3 * q)
            matrices.append(tuple(rows))
    if len(set(matrices)) != 36:
        raise ValueError("independent generator count failed")
    tables = [tuple(xor_all(g[j] for j in range(6) if row >> j & 1)
                    for row in range(64)) for g in matrices]
    root = tuple(1 << i for i in range(6))
    layers = [{root}]
    seen = {root}
    for _ in range(4):
        following = set()
        for state in layers[-1]:
            for table in tables:
                changed = tuple(table[row] for row in state)
                if changed not in seen:
                    following.add(changed)
        seen.update(following)
        layers.append(following)
    # A separate meet test uses T*A^-1, instead of the producer's A*T^-1.
    target = (2, 4, 7, 2 << 3, 4 << 3, 7 << 3)
    short_ball = set().union(*layers[:4])
    meets = sum(compose(target, inverse(a)) in seen for a in short_ball)
    return distance, [{canonical(s) for s in layer} for layer in layers], meets


def check_regular(word, target):
    """Check all 2*168 basis vectors in the faithful left regular module."""
    group = [g for g in product(range(8), repeat=3) if dimension(g, 3) == 3]
    count = 0
    for role, label in product(range(2), group):
        state = [set(), set()]
        state[role].add(label)
        for i, j, u, v in word:
            source = set()
            for q in range(2):
                if v >> q & 1:
                    source.symmetric_difference_update(state[q])
            gate = [1, 2, 4]
            gate[i] ^= 1 << j
            delta = source ^ {compose(gate, g) for g in source}
            for p in range(2):
                if u >> p & 1:
                    state[p].symmetric_difference_update(delta)
        expected = [set(), set()]
        expected[role].add(compose(target, label))
        if state != expected:
            raise ValueError("faithful regular column differs")
        count += 1
    return count
