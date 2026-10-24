#!/usr/bin/env python3
"""Direct finite-field witnesses for the common scalar-block dimension theorem.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable or external input is imported.
"""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digits(value, prime, degree):
    result = []
    for _ in range(degree):
        result.append(value % prime)
        value //= prime
    return result


def polynomial_product(a, b, prime, modulus):
    degree = len(modulus) - 1
    left, right = digits(a, prime, degree), digits(b, prime, degree)
    work = [0] * (2 * degree - 1)
    for i in range(degree):
        for j in range(degree):
            work[i + j] = (work[i + j] + left[i] * right[j]) % prime
    for k in range(2 * degree - 2, degree - 1, -1):
        coefficient = work[k]
        for j in range(degree + 1):
            work[k - degree + j] -= coefficient * modulus[j]
            work[k - degree + j] %= prime
    return sum(work[j] * prime ** j for j in range(degree))


class Field:
    def __init__(self, order):
        definitions = {2: (2, (0, 1)), 3: (3, (0, 1)),
                       4: (2, (1, 1, 1)), 5: (5, (0, 1)),
                       7: (7, (0, 1)), 8: (2, (1, 1, 0, 1)),
                       9: (3, (1, 0, 1))}
        require(order in definitions, "unsupported field order")
        prime, modulus = definitions[order]
        degree = len(modulus) - 1
        self.q = order
        self.add = [[sum(((x + y) % prime) * prime ** k
                         for k, (x, y) in enumerate(zip(digits(a, prime, degree),
                                                        digits(b, prime, degree))))
                     for b in range(order)] for a in range(order)]
        self.mul = [[polynomial_product(a, b, prime, modulus)
                     for b in range(order)] for a in range(order)]
        self.neg = [next(b for b in range(order) if self.add[a][b] == 0)
                    for a in range(order)]
        self.inv = [0] + [next(b for b in range(1, order) if self.mul[a][b] == 1)
                          for a in range(1, order)]


class Matrix:
    __slots__ = ("rows", "cols")

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def __eq__(self, other):
        return isinstance(other, Matrix) and self.cols == other.cols and self.rows == other.rows


def matrix(rows, cols=None):
    values = tuple(tuple(row) for row in rows)
    width = len(values[0]) if values and cols is None else (cols or 0)
    require(len(values) <= 24 and 0 <= width <= 48, "matrix capacity")
    require(all(len(row) == width for row in values), "ragged matrix")
    return Matrix(values, width)


def zero(rows, cols):
    require(0 <= rows <= 24 and 0 <= cols <= 48, "zero capacity")
    return matrix([[0] * cols for _ in range(rows)], cols)


def identity(size):
    require(0 <= size <= 24, "identity capacity")
    return matrix([[int(i == j) for j in range(size)] for i in range(size)], size)


def transpose(a):
    return matrix([[a.rows[i][j] for i in range(len(a.rows))]
                   for j in range(a.cols)], len(a.rows))


def scale(a, coefficient, field):
    require(0 <= coefficient < field.q, "invalid scalar")
    return matrix([[field.mul[coefficient][v] for v in row] for row in a.rows], a.cols)


def add(a, b, field):
    require((len(a.rows), a.cols) == (len(b.rows), b.cols), "sum shape")
    return matrix([[field.add[x][y] for x, y in zip(row_a, row_b)]
                   for row_a, row_b in zip(a.rows, b.rows)], a.cols)


def subtract(a, b, field):
    return add(a, scale(b, field.neg[1], field), field)


def multiply(a, b, field):
    require(a.cols == len(b.rows), "product shape")
    output = [[0] * b.cols for _ in a.rows]
    for i, row in enumerate(a.rows):
        for k, value in enumerate(row):
            if value:
                for j in range(b.cols):
                    output[i][j] = field.add[output[i][j]][field.mul[value][b.rows[k][j]]]
    return matrix(output, b.cols)


def join_horizontal(a, b):
    require(len(a.rows) == len(b.rows), "horizontal shape")
    return matrix([x + y for x, y in zip(a.rows, b.rows)], a.cols + b.cols)


def join_vertical(a, b):
    require(a.cols == b.cols, "vertical shape")
    return matrix(a.rows + b.rows, a.cols)


def select(a, row_indices, column_indices):
    require(len(row_indices) <= 24 and len(column_indices) <= 48, "selection capacity")
    require(all(0 <= i < len(a.rows) for i in row_indices), "invalid row")
    require(all(0 <= j < a.cols for j in column_indices), "invalid column")
    return matrix([[a.rows[i][j] for j in column_indices] for i in row_indices],
                  len(column_indices))


def reduce_rows(a, field):
    work = [list(row) for row in a.rows]
    pivots = []
    for column in range(a.cols):
        pivot = next((i for i in range(len(pivots), len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        target = len(pivots)
        work[target], work[pivot] = work[pivot], work[target]
        inverse_value = field.inv[work[target][column]]
        work[target] = [field.mul[inverse_value][v] for v in work[target]]
        for i in range(len(work)):
            if i != target and work[i][column]:
                coefficient = work[i][column]
                work[i] = [field.add[x][field.neg[field.mul[coefficient][y]]]
                           for x, y in zip(work[i], work[target])]
        pivots.append(column)
        if len(pivots) == len(work):
            break
    return matrix(work, a.cols), tuple(pivots)


def rank(a, field):
    return len(reduce_rows(a, field)[1])


def inverse(a, field):
    size = len(a.rows)
    require(size == a.cols and size > 0, "inverse shape")
    reduced, pivots = reduce_rows(join_horizontal(a, identity(size)), field)
    require(pivots == tuple(range(size)), "singular matrix")
    return select(reduced, tuple(range(size)), tuple(range(size, 2 * size)))


def kernel(a, field):
    reduced, pivots = reduce_rows(a, field)
    free = tuple(j for j in range(a.cols) if j not in pivots)
    columns = []
    for j in free:
        vector = [0] * a.cols
        vector[j] = 1
        for i, pivot in enumerate(pivots):
            vector[pivot] = field.neg[reduced.rows[i][j]]
        columns.append(vector)
    return transpose(matrix(columns, a.cols))


def factor_product(target, active, field):
    size = len(target.rows)
    require(size == target.cols and 1 <= size <= 3, "target shape")
    if active:
        extended = join_horizontal(target, identity(size))
        pivots = reduce_rows(extended, field)[1]
        complement = select(extended, tuple(range(size)), tuple(j for j in pivots if j >= size))
        x = join_horizontal(target, complement)
        y = join_vertical(identity(size), zero(complement.cols, size))
    else:
        columns = reduce_rows(target, field)[1]
        x = select(target, tuple(range(size)), columns)
        rows = reduce_rows(transpose(x), field)[1]
        if columns:
            square = select(x, rows, tuple(range(len(columns))))
            y = multiply(inverse(square, field), select(target, rows, tuple(range(size))), field)
        else:
            y = zero(0, size)
    require(multiply(x, y, field) == target, "factor product")
    return x, y


def sector_products(size, pivot, h, field):
    require(1 <= size <= 3 and len(h.rows) == size and h.cols == size, "product-block shape")
    require(0 < pivot < field.q, "zero or invalid pivot")
    scalar_i = scale(identity(size), pivot, field)
    t0 = add(subtract(identity(size), add(scalar_i, scalar_i, field), field), h, field)
    difference = subtract(scalar_i, h, field)
    return t0, difference, difference, h


def build_pair(size, pivot, h, field, defect=None):
    targets = sector_products(size, pivot, h, field)
    factors = [factor_product(t, j > 0, field) for j, t in enumerate(targets)]
    if defect is not None:
        sector, side = defect
        x, y = factors[sector]
        require(targets[sector] == zero(size, size), "defect needs a zero product")
        if side == "Y":
            rows = [list(row) for row in y.rows]
            rows[0][0] = 0
            y = matrix(rows, size)
        else:
            require(side == "X", "unknown defect side")
            rows = [list(row) for row in x.rows]
            rows[0][size] = 0
            x = matrix(rows)
        require(multiply(x, y, field) == targets[sector], "defect changed compressed product")
        factors[sector] = x, y
    include, project = zero(0, size), zero(size, 0)
    masks_p, masks_q, dimensions = [], [], []
    for j, (x, y) in enumerate(factors):
        include, project = join_vertical(include, y), join_horizontal(project, x)
        dimensions.append(len(y.rows))
        masks_p.extend([int(j in (1, 3))] * len(y.rows))
        masks_q.extend([int(j in (2, 3))] * len(y.rows))
    require(multiply(project, include, field) == identity(size), "coordinate splitting")
    basis = join_horizontal(include, kernel(project, field))
    back = inverse(basis, field)
    p_basis = matrix([[field.mul[masks_p[i]][v] for v in row] for i, row in enumerate(basis.rows)])
    q_basis = matrix([[field.mul[masks_q[i]][v] for v in row] for i, row in enumerate(basis.rows)])
    return multiply(back, p_basis, field), multiply(back, q_basis, field), tuple(dimensions)


def inspect_pair(p, q, size, pivot, h, field):
    count = len(p.rows)
    require(p.cols == count and q.cols == count and len(q.rows) == count, "pair shape")
    require(multiply(p, p, field) == p and multiply(q, q, field) == q, "idempotence")
    pq = multiply(p, q, field)
    require(pq == multiply(q, p, field), "commutation")
    top, tail = tuple(range(size)), tuple(range(size, count))
    expected = scale(identity(size), pivot, field)
    require(select(p, top, top) == expected and select(q, top, top) == expected, "pivot blocks")
    require(select(pq, top, top) == h, "prescribed product")
    r, c = select(p, top, tail), select(p, tail, top)
    l, e = select(q, top, tail), select(q, tail, top)
    s = subtract(select(p, tail, tail), scale(multiply(c, r, field), field.inv[pivot], field), field)
    z = subtract(select(q, tail, tail), scale(multiply(e, l, field), field.inv[pivot], field), field)
    commutator = subtract(multiply(s, z, field), multiply(z, s, field), field)
    require(multiply(s, s, field) == s and multiply(z, z, field) == z, "Schur idempotence")
    require(rank(s, field) == rank(p, field) - size, "P rank drop")
    require(rank(z, field) == rank(q, field) - size, "Q rank drop")
    u = scale(subtract(c, e, field), field.inv[pivot], field)
    v = scale(subtract(r, l, field), field.inv[pivot], field)
    x = subtract(select(pq, tail, top), scale(multiply(e, h, field), field.inv[pivot], field), field)
    y = subtract(select(pq, top, tail), scale(multiply(h, l, field), field.inv[pivot], field), field)
    require(commutator == subtract(multiply(x, v, field), multiply(u, y, field), field),
            "ordered Schur factorization")
    sectors = (add(subtract(subtract(identity(count), p, field), q, field), pq, field),
               subtract(p, pq, field), subtract(q, pq, field), pq)
    active_ranks = tuple((rank(select(t, top, tuple(range(count))), field),
                          rank(select(t, tuple(range(count)), top), field)) for t in sectors[1:])
    require((rank(commutator, field) == 2 * size) ==
            all(a == size and b == size for a, b in active_ranks), "six-map criterion")
    return rank(commutator, field), tuple(rank(t, field) for t in sectors), rank(p, field), active_ranks


def check_case(size, pivot, h, field):
    p, q, dimensions = build_pair(size, pivot, h, field)
    sharp_rank, measured_dims, input_rank, _ = inspect_pair(p, q, size, pivot, h, field)
    products = sector_products(size, pivot, h, field)
    a = size - rank(h, field)
    b = size - rank(products[1], field)
    predicted_dims = (rank(products[0], field), size + b, size + b, size + a)
    require(dimensions == measured_dims == predicted_dims, "sector minima")
    require(len(p.rows) == 3 * size + rank(products[0], field) + 2 * b + a, "dimension formula")
    require(sharp_rank == 2 * size and input_rank == 2 * size + a + b, "attained ranks")
    require(rank(q, field) == input_rank, "second input rank")
    return len(p.rows), dimensions


def all_blocks(size, order):
    require(1 <= size <= 2 and 2 <= order <= 5, "exhaustive domain")
    for entries in product(range(order), repeat=size * size):
        yield matrix([entries[i * size:(i + 1) * size] for i in range(size)])


def field_controls(field):
    count = 0
    for a, b, c in product(range(field.q), repeat=3):
        require(field.mul[a][field.add[b][c]] ==
                field.add[field.mul[a][b]][field.mul[a][c]], "distributivity")
        require(field.mul[a][field.mul[b][c]] == field.mul[field.mul[a][b]][c], "associativity")
        require(field.add[a][b] == field.add[b][a], "commutative addition")
        count += 1
    for a in range(1, field.q):
        require(field.mul[a][field.inv[a]] == 1, "field inverse")
    return count


def independent_factor_census():
    field = Field(2)
    minima = {}
    pairs = 0
    for middle in (2, 3, 4):
        onto = []
        for entries in product(range(2), repeat=2 * middle):
            x = matrix([entries[:middle], entries[middle:]])
            if rank(x, field) == 2:
                onto.append(x)
        for x, yt in product(onto, repeat=2):
            target = multiply(x, transpose(yt), field)
            key = target.rows
            minima[key] = min(middle, minima.get(key, 5))
            pairs += 1
    require(len(minima) == 16, "factor census coverage")
    for h in all_blocks(2, 2):
        require(minima[h.rows] == 4 - rank(h, field), "independent middle-space minimum")
    return pairs, len(minima)


def rejection_controls():
    field = Field(3)
    defects = 0
    for sector, side in product((1, 2, 3), ("X", "Y")):
        h = zero(2, 2) if sector == 3 else scale(identity(2), 2, field)
        p, q, _ = build_pair(2, 2, h, field, (sector, side))
        result = inspect_pair(p, q, 2, 2, h, field)
        require(result[0] < 4 and result[3][sector - 1] != (2, 2), "missing-map control")
        defects += 1
    rejected = 0
    for mode in range(5):
        try:
            if mode == 0:
                sector_products(2, 0, identity(2), field)
            elif mode == 1:
                sector_products(2, 2, identity(1), field)
            elif mode == 2:
                matrix([[0] * 49])
            elif mode == 3:
                inverse(matrix([[1, 0], [1, 0]]), field)
            else:
                Field(6)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed control accepted")
    return defects, rejected


def sampled_cases(field):
    count = 0
    for size, pivot in product((2, 3), range(1, field.q)):
        for diagonal in range(field.q):
            rows = [list(row) for row in scale(identity(size), diagonal, field).rows]
            for i in range(size - 1):
                rows[i][i + 1] = 1
            check_case(size, pivot, matrix(rows), field)
            count += 1
        rows = [[0] * size for _ in range(size)]
        for i in range(size - 1):
            rows[i + 1][i] = 1
        rows[0][-1] = 1
        rows[1][-1] = 1
        check_case(size, pivot, matrix(rows), field)
        count += 1
    return count


def receipt():
    directory = Path(__file__).resolve().parent
    expected = {"README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"}
    files = sorted(p.name for p in directory.iterdir() if p.is_file())
    require(set(files) == expected, "unexpected package files")
    return {name: sha256((directory / name).read_bytes()).hexdigest() for name in files}


def main():
    exhaustive, sampled, scalar, field_checks = 0, 0, 0, 0
    by_field = {}
    for order in (2, 3, 4, 5, 7, 8, 9):
        field = Field(order)
        field_checks += field_controls(field)
        for pivot, h in product(range(1, order), range(order)):
            dimension, _ = check_case(1, pivot, matrix([[h]]), field)
            if h == 0:
                expected = 4 + int(field.add[pivot][pivot] != 1)
            elif h == pivot:
                expected = 5 + int(pivot != 1)
            else:
                t0 = field.add[field.add[1][field.neg[field.add[pivot][pivot]]]][h]
                expected = 3 + int(t0 != 0)
            require(dimension == expected, "scalar predecessor specialization")
            scalar += 1
        local_count = 0
        if order <= 5:
            for pivot in range(1, order):
                for h in all_blocks(2, order):
                    check_case(2, pivot, h, field)
                    local_count += 1
            exhaustive += local_count
        by_field[str(order)] = local_count
        sampled += sampled_cases(field)
    pairs, targets = independent_factor_census()
    defects, rejected = rejection_controls()
    example = check_case(2, 2, matrix([[3, 1], [0, 3]]), Field(5))
    require(example == (7, (1, 2, 2, 2)), "nondiagonal example")
    diagonal = check_case(2, 2, scale(identity(2), 3, Field(5)), Field(5))
    require(diagonal[0] == 6, "diagonal control")
    print("PASS_SCALAR_BLOCK_SCHUR_DIMENSION")
    print(json.dumps({"scalar_cases": scalar, "exhaustive_d2": exhaustive,
                      "d2_by_field": by_field, "sampled_d2_d3": sampled,
                      "field_triples": field_checks, "factor_pairs": pairs,
                      "factor_targets": targets, "missing_map_controls": defects,
                      "malformed_controls": rejected, "nondiagonal_example": example,
                      "python": platform.python_version(), "sha256": receipt()}, sort_keys=True))


if __name__ == "__main__":
    main()
