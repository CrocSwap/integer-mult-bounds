"""Exact P112 geometry, following DreamingOfClouds' pinned PR717 model.

Apache-2.0. Prepared for Mihir Srivastava with substantial OpenAI Codex
assistance. No NumPy, floating-point solves, or predecessor imports.
"""

from fractions import Fraction
from itertools import combinations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def mask(values):
    out = 0
    for value in values:
        out = (out << 1) | (value % 2)
    return out


def parity(value):
    return value.bit_count() & 1


def binary_basis(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return [pivots[p] for p in sorted(pivots, reverse=True)]


def binary_kernel(rows, width):
    basis = binary_basis(rows)
    pivots = {v.bit_length() - 1: v for v in basis}
    result = []
    for free in range(width):
        if free in pivots:
            continue
        vector = 1 << free
        for pivot, row in sorted(pivots.items()):
            if parity(vector & row):
                vector |= 1 << pivot
        result.append(vector)
    require(all(parity(r & v) == 0 for r in rows for v in result),
            'invalid binary kernel')
    return result


def rational_basis_indices(rows):
    """Select independent original rows using exact rational elimination."""
    basis = {}
    selected = []
    for index, original in enumerate(rows):
        row = list(map(Fraction, original))
        for pivot, previous in sorted(basis.items()):
            coefficient = row[pivot]
            if coefficient:
                row = [a - coefficient * b for a, b in zip(row, previous)]
        pivot = next((j for j, value in enumerate(row) if value), None)
        if pivot is not None:
            coefficient = row[pivot]
            basis[pivot] = [value / coefficient for value in row]
            selected.append(index)
        if len(basis) == len(original):
            break
    return selected


def inverse(matrix):
    size = len(matrix)
    rows = [[Fraction(x) for x in row] +
            [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = next(i for i in range(col, size) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(size):
            if i != col:
                coefficient = rows[i][col]
                rows[i] = [x - coefficient * y
                           for x, y in zip(rows[i], rows[col])]
    return [row[size:] for row in rows]


def build():
    roots = []
    for i, j in combinations(range(8), 2):
        for si, sj in product((1, -1), repeat=2):
            vector = [0] * 8
            vector[i], vector[j] = 2 * si, 2 * sj
            roots.append(vector)
    roots.extend(list(s) for s in product((1, -1), repeat=8)
                 if s.count(-1) % 2 == 0)
    simple = [[1, -1, -1, -1, -1, -1, -1, 1],
              [2, 2, 0, 0, 0, 0, 0, 0],
              [-2, 2, 0, 0, 0, 0, 0, 0]]
    for k in range(1, 6):
        vector = [0] * 8
        vector[k], vector[k + 1] = -2, 2
        simple.append(vector)
    inv = inverse(simple)
    gram = [[dot(a, b) // 4 for b in simple] for a in simple]
    frame = []
    for j in range(4):
        for sign in (1, -1):
            vector = [0] * 8
            vector[2 * j], vector[2 * j + 1] = 2, 2 * sign
            frame.append(vector)
    lines, seen = [], set()
    for root in roots:
        key = max(tuple(root), tuple(-v for v in root))
        if key not in seen:
            seen.add(key)
            lines.append(root)
    kept = [r for r in lines if r not in frame and [-v for v in r] not in frame]
    labels, duals, columns = [], [], []
    for root in kept:
        coordinates = [sum(root[k] * inv[k][j] for k in range(8))
                       for j in range(8)]
        require(all(x.denominator == 1 for x in coordinates), 'nonintegral E8 coordinates')
        coordinates = [int(x) for x in coordinates]
        require([sum(coordinates[k] * simple[k][j] for k in range(8))
                 for j in range(8)] == root, 'root reconstruction')
        labels.append(mask(coordinates + [1]))
        duals.append(mask([sum(coordinates[k] * gram[k][j] for k in range(8))
                           for j in range(8)] + [1]))
        columns.append([dot(root, f) // 4 for f in frame])
    return {'roots': kept, 'frame': frame, 'labels': labels,
            'duals': duals, 'X': columns}


def check_geometry(data):
    roots, frame = data['roots'], data['frame']
    labels, duals, x = data['labels'], data['duals'], data['X']
    require(len(roots) == len(labels) == len(duals) == len(x) == 112, 'P112 size')
    require(len(frame) == 8 and len({tuple(r) for r in roots}) == 112, 'distinct geometry')
    require(all(len(r) == 8 and dot(r, r) == 8 for r in roots), 'root norms')
    require(all(len(row) == 8 and set(row) <= {-1, 0, 1}
                and dot(row, row) == 4 for row in x), 'coordinate alphabet')
    require(len(binary_basis(labels)) == 9, 'label span')
    require(len(rational_basis_indices(x)) == 8, 'coordinate rank')
    for i in range(112):
        require(x[i] == [dot(roots[i], f) // 4 for f in frame], 'coordinate binding')
        for j in range(112):
            require(dot(roots[i], roots[j]) % 4 == 0, 'integral Gram')
            gram = dot(roots[i], roots[j]) // 4
            require(dot(x[i], x[j]) == 2 * gram, 'XX^T = 2G')
            require(parity(duals[i] & labels[j]) == (1 + gram) % 2,
                    'binary label pairing')


def reader_space(values, duals):
    return binary_basis(dual for value, dual in zip(values, duals) if value)


def evaluate(space, label):
    return sum(parity(q & label) << j for j, q in enumerate(space))


def term_cost(readers, sources, data):
    space = reader_space(readers, data['duals'])
    return len(binary_basis(evaluate(space, label)
                            for value, label in zip(sources, data['labels']) if value))
