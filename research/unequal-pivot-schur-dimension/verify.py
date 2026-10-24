#!/usr/bin/env python3
"""Unequal-pivot Schur minima, produced by Nick Petalas. Apache-2.0.

Finite-field/matrix helpers adapted from Nick Petalas, PR4771 verify.py.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digits(value, prime, degree):
    return [(value // prime**i) % prime for i in range(degree)]


def field_product(a, b, prime, modulus):
    degree = len(modulus) - 1
    left, right = digits(a, prime, degree), digits(b, prime, degree)
    coefficients = [0] * (2 * degree - 1)
    for i in range(degree):
        for j in range(degree):
            coefficients[i + j] += left[i] * right[j]
    for i in range(2 * degree - 2, degree - 1, -1):
        for j in range(degree):
            coefficients[i - degree + j] -= coefficients[i] * modulus[j]
    return sum((coefficients[i] % prime) * prime**i for i in range(degree))


class Field:
    def __init__(self, order):
        definitions = {2: (2, (0, 1)), 3: (3, (0, 1)),
                       4: (2, (1, 1, 1)), 5: (5, (0, 1)),
                       7: (7, (0, 1)), 8: (2, (1, 1, 0, 1)),
                       9: (3, (1, 0, 1))}
        require(order in definitions, "unsupported field")
        prime, modulus = definitions[order]
        self.q = order
        degree = len(modulus) - 1
        self.add = [[sum(((a // prime**i + b // prime**i) % prime)
                         * prime**i for i in range(degree))
                     for b in range(order)] for a in range(order)]
        self.mul = [[field_product(a, b, prime, modulus)
                     for b in range(order)] for a in range(order)]
        self.neg = [self.add[a].index(0) for a in range(order)]
        self.inv = [0] + [self.mul[a].index(1) for a in range(1, order)]
        require(all(self.mul[a][self.inv[a]] == 1 for a in range(1, order)),
                "field inverses")

    def sub(self, a, b):
        return self.add[a][self.neg[b]]

    def dot(self, left, right):
        require(len(left) == len(right) <= 12, "dot capacity")
        value = 0
        for a, b in zip(left, right, strict=True):
            value = self.add[value][self.mul[a][b]]
        return value


def identity(size):
    require(0 <= size <= 6, "identity capacity")
    return [[int(i == j) for j in range(size)] for i in range(size)]


def mm(field, left, right):
    require(1 <= len(left) <= 6 and 1 <= len(right) <= 6, "matrix capacity")
    require(all(len(row) == len(right) for row in left), "matrix shape")
    columns = list(zip(*right, strict=True))
    return [[field.dot(row, column) for column in columns] for row in left]


def subtract(field, left, right):
    return [[field.sub(a, b) for a, b in zip(x, y, strict=True)]
            for x, y in zip(left, right, strict=True)]


def eliminate(field, matrix):
    require(1 <= len(matrix) <= 6 and 1 <= len(matrix[0]) <= 12,
            "elimination capacity")
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    result = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(width):
        candidates = [i for i in range(pivot_row, len(result)) if result[i][column]]
        if not candidates:
            continue
        index = candidates[0]
        result[pivot_row], result[index] = result[index], result[pivot_row]
        scale = field.inv[result[pivot_row][column]]
        result[pivot_row] = [field.mul[scale][a] for a in result[pivot_row]]
        for i in range(len(result)):
            if i != pivot_row:
                scale = result[i][column]
                result[i] = [field.sub(a, field.mul[scale][b])
                             for a, b in zip(result[i], result[pivot_row], strict=True)]
        pivot_row += 1
        if pivot_row == len(result):
            break
    return result, pivot_row


def inverse(field, matrix):
    size = len(matrix)
    unit = identity(size)
    augmented = [row + unit[i] for i, row in enumerate(matrix)]
    reduced, rank = eliminate(field, augmented)
    require(rank == size and [row[:size] for row in reduced] == unit,
            "singular basis")
    result = [row[size:] for row in reduced]
    require(mm(field, matrix, result) == unit, "inverse product")
    return result


def pair_types(field):
    """Enumerate every scalar X,Y type through dimensions zero, one and two."""
    options = [{} for _ in range(field.q)]
    count = 0
    for size in range(3):
        for vector in product(range(field.q), repeat=2 * size):
            x, y = vector[:size], vector[size:]
            target = field.dot(x, y)
            flags = (any(x), any(y))
            options[target].setdefault(flags, size)
            count += 1
    return options, count


def products(field, p, q, h):
    require(0 < p < field.q and 0 < q < field.q and p != q,
            "distinct nonzero pivots required")
    require(0 <= h < field.q, "invalid product")
    return [field.add[field.sub(field.sub(1, p), q)][h],
            field.sub(p, h), field.sub(q, h), h]


def minimum(field, p, q, h):
    return 3 + int(h in (0, p, q)) + int(products(field, p, q, h)[0] != 0)


def directions(field, p, q, h):
    ip, iq = field.inv[p], field.inv[q]
    hq = field.mul[h][iq]
    return [[0, 0], [0, ip], [field.neg[hq], field.neg[iq]],
            [field.sub(1, hq), field.sub(ip, iq)]]


def construct(field, p, q, h, omit_required=False):
    targets = products(field, p, q, h)
    required = 3 if h == 0 else 1 if h == p else 2 if h == q else -1
    inclusion, projection, p_mask, q_mask, sizes = [], [], [], [], []
    for sector, target in enumerate(targets):
        size = 1 if target else 2 if sector == required and not omit_required else 0
        sizes.append(size)
        if size:
            inclusion.extend([1] + [0] * (size - 1))
            projection.extend([target] if size == 1 else [0, 1])
            p_mask.extend([int(sector in (1, 3))] * size)
            q_mask.extend([int(sector in (2, 3))] * size)
    require(field.dot(projection, inclusion) == 1, "compression sum")
    size = len(inclusion)
    anchor = next(i for i in range(size) if projection[i])
    columns = [inclusion]
    for j in range(size):
        if j != anchor:
            vector = [int(i == j) for i in range(size)]
            vector[anchor] = field.neg[field.mul[projection[j]][field.inv[projection[anchor]]]]
            columns.append(vector)
    basis = [list(row) for row in zip(*columns, strict=True)]
    back = inverse(field, basis)
    left = mm(field, back, [[field.mul[p_mask[i]][a] for a in row]
                           for i, row in enumerate(basis)])
    right = mm(field, back, [[field.mul[q_mask[i]][a] for a in row]
                            for i, row in enumerate(basis)])
    return left, right, sizes


def schur(field, matrix):
    require(matrix[0][0] != 0, "zero Schur pivot")
    scale = field.inv[matrix[0][0]]
    return [[field.sub(matrix[i][j], field.mul[field.mul[matrix[i][0]][scale]][matrix[0][j]])
             for j in range(1, len(matrix))] for i in range(1, len(matrix))]


def verify_pair(field, p, q, h, left, right):
    pq = mm(field, left, right)
    require(mm(field, left, left) == left and mm(field, right, right) == right,
            "idempotence")
    require(pq == mm(field, right, left), "commutation")
    require(left[0][0] == p and right[0][0] == q and pq[0][0] == h,
            "prescribed compression")
    s, t = schur(field, left), schur(field, right)
    commutator = subtract(field, mm(field, s, t), mm(field, t, s))
    ip, iq = field.inv[p], field.inv[q]
    hq = field.mul[h][iq]
    a = [[field.sub(pq[i][0], field.mul[hq][right[i][0]]),
          field.sub(field.mul[ip][left[i][0]], field.mul[iq][right[i][0]])]
         for i in range(1, len(left))]
    b = [[field.sub(field.mul[ip][left[0][j]], field.mul[iq][right[0][j]])
          for j in range(1, len(left))],
         [field.sub(field.mul[hq][right[0][j]], pq[0][j])
          for j in range(1, len(left))]]
    require(mm(field, a, b) == commutator, "ordered scalar factorization")
    return eliminate(field, commutator)[1]


def enumerated_minimum(field, p, q, h, options):
    rows = directions(field, p, q, h)
    choices = [list(options[t].items()) for t in products(field, p, q, h)]
    best, patterns = 99, 0
    for combination in product(*choices):
        x_rows = [row if flags[0] else [0, 0]
                  for row, (flags, _) in zip(rows, combination, strict=True)]
        y_rows = [row if flags[1] else [0, 0]
                  for row, (flags, _) in zip(rows, combination, strict=True)]
        if eliminate(field, x_rows)[1] == eliminate(field, y_rows)[1] == 2:
            best = min(best, sum(size for _, size in combination))
        patterns += 1
    require(best != 99, "no attaining pattern")
    return best, patterns


def controls():
    field = Field(5)
    count = 0
    for h in (0, 2, 3):
        left, right, _ = construct(field, 2, 3, h, omit_required=True)
        require(verify_pair(field, 2, 3, h, left, right) < 2,
                "necessary zero-product sector omitted undetected")
        count += 1
    for p, q, h in ((0, 2, 1), (2, 2, 1), (2, 3, 5)):
        try:
            products(field, p, q, h)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid parameters accepted")
    try:
        Field(6)
    except ValueError:
        count += 1
    else:
        raise ValueError("nonfield order accepted")
    left, right, _ = construct(field, 2, 3, 4)
    require(minimum(field, 2, 3, 4) == 3, "dimension-three fixture")
    left[0][0] = 1
    try:
        verify_pair(field, 2, 3, 4, left, right)
    except ValueError:
        count += 1
    else:
        raise ValueError("mutated projector accepted")
    require(minimum(Field(3), 1, 2, 0) == 5, "endpoint correction fixture")
    require(minimum(Field(3), 1, 2, 2) == 4, "zero-00 fixture")
    return count


def main():
    cases, patterns, vector_pairs = 0, 0, 0
    histograms = {}
    for order in (3, 4, 5, 7, 8, 9):
        field = Field(order)
        options, count = pair_types(field)
        vector_pairs += count
        histogram = {}
        for p, q, h in product(range(1, order), range(1, order), range(order)):
            if p == q:
                continue
            expected = minimum(field, p, q, h)
            observed, count = enumerated_minimum(field, p, q, h, options)
            left, right, sizes = construct(field, p, q, h)
            require(sum(sizes) == observed == expected, "dimension minimum")
            require(verify_pair(field, p, q, h, left, right) == 2, "sharp commutator")
            require(minimum(field, q, p, h) == expected, "pivot exchange symmetry")
            histogram[expected] = histogram.get(expected, 0) + 1
            cases += 1
            patterns += count
        histograms[order] = histogram
    count = controls()
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = root / name
        require(path.stat().st_size <= 100_000, "receipt file capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"status": "PASS_UNEQUAL_PIVOT_SCHUR_DIMENSION",
                      "constructed_triples": cases, "sector_patterns": patterns,
                      "enumerated_vector_pairs": vector_pairs, "minima": histograms,
                      "rejection_controls": count, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
