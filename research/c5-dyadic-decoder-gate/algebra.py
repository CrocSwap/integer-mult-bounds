"""Exact algebra for the scoped decoder gate. Tekalign; Apache-2.0; AI-assisted."""
from itertools import combinations, product


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() % 2


def pairing(left, right):
    return rank([sum(dot(x, y) << j for j, y in enumerate(right)) for x in left])


def costs_for(planes):
    result = []
    for mask in range(32):
        basis = [x for i, plane in enumerate(planes) if mask >> i & 1 for x in plane]
        result.append(pairing(basis, basis))
    return result


def roots_e8():
    """120 unoriented integral norm-four E8 roots in a scaled coordinate chart."""
    roots = []
    for i in range(8):
        row = [0] * 8
        row[i] = 2
        roots.append(row)
    quads = sorted({tuple(x for x in range(8) if dot(x, a) == b)
                    for a in range(1, 8) for b in (0, 1)})
    for quad in quads:
        for signs in product((-1, 1), repeat=3):
            row = [0] * 8
            for i, sign in zip(quad, (1,) + signs):
                row[i] = sign
            roots.append(row)
    need(len(roots) == 120 and len({tuple(r) for r in roots}) == 120, 'root menu')
    need(all(sum(x*x for x in row) == 4 for row in roots), 'norm-four menu')
    return roots


def scalar_gram(rows, signs=None):
    signs = signs if signs is not None else [1] * len(rows[0])
    return [[sum(s*x*y for s, x, y in zip(signs, u, v)) for v in rows] for u in rows]


def check_fit(rows, planes, denominator=4):
    matrix = scalar_gram(rows)
    for i in range(len(rows)):
        for j in range(len(rows)):
            if i == j or any(dot(a, b) for a in planes[i//2] for b in planes[j//2]):
                need(matrix[i][j] == (denominator if i == j else 0), 'scalar mask')
    prices = costs_for(planes)
    charges = [prices[sum(1 << g for g in range(5)
                          if rows[2*g][k] or rows[2*g+1][k])]
               for k in range(len(rows[0]))]
    return charges


def baseline(planes):
    rows = []
    for i in range(5):
        for k in ((i-1) % 5, i):
            row = [0] * 8
            row[k] = 2
            rows.append(row)
    need(sum(check_fit(rows, planes)) == 20, 'five-axis positive control')
    return rows


def tariff_from_matrix(rows, binary):
    charges = []
    for k in range(len(rows[0])):
        indices = [i for i, row in enumerate(rows) if row[k]]
        charges.append(rank([sum(binary[i][j] << t for t, j in enumerate(indices))
                             for i in indices]))
    return charges


def escape_controls():
    # These are inherited E8 geometry, independently generated controls, not new suppliers.
    roots = roots_e8()
    gram = scalar_gram(roots)
    need(all(x % 2 == 0 for row in gram for x in row), 'even E8 products')
    binary = [[1 ^ ((x // 2) % 2) for x in row] for row in gram]
    need(all(gram[i][i] == 4 and binary[i][i] == 1 for i in range(120)), 'quarter diagonal')
    need(all(gram[i][j] == 0 for i in range(120) for j in range(120)
             if i != j and binary[i][j]), 'quarter mask')
    quarter = tariff_from_matrix(roots, binary)
    need(quarter == [9] * 8, 'quarter escape tariff')
    # E8 roots in the orthogonal complement of (-3,1,...,1) in I_(8,1).
    lorentz = []
    for i, j in combinations(range(8), 2):
        row = [0] * 9
        row[i], row[j] = 1, -1
        lorentz.append(row)
    for count, height in ((3, 1), (6, 2)):
        for indices in combinations(range(8), count):
            row = [0] * 9
            row[8] = height
            for i in indices:
                row[i] = 1
            lorentz.append(row)
    for i in range(8):
        row = [1] * 9
        row[i], row[8] = 2, 3
        lorentz.append(row)
    gram_l = scalar_gram(lorentz, [1] * 8 + [-1])
    binary_l = [[1 ^ (x % 2) for x in row] for row in gram_l]
    need(len(lorentz) == 120 and all(gram_l[i][i] == 2 for i in range(120)), 'signed-half diagonal')
    need(all(gram_l[i][j] == 0 for i in range(120) for j in range(120)
             if i != j and binary_l[i][j]), 'signed-half mask')
    signed = tariff_from_matrix(lorentz, binary_l)
    need(signed == [9] * 9, 'signed-half escape tariff')
    need(rank([sum(x << j for j, x in enumerate(r)) for r in binary]) == 9, 'quarter ambient rank')
    need(rank([sum(x << j for j, x in enumerate(r)) for r in binary_l]) == 9, 'signed ambient rank')
    return {'quarter_positive_cost': sum(quarter), 'signed_half_cost': sum(signed),
            'line_ports': 120, 'binary_quotient_dimension': 9}


def half_fixtures():
    records = []
    for n in range(2, 8):
        rows = []
        for i, j in combinations(range(n), 2):
            for sign in (-1, 1):
                row = [0] * n
                row[i], row[j] = 1, sign
                rows.append(row)
        gram = scalar_gram(rows)
        binary = [[int(i == j or gram[i][j] == 0) for j in range(len(rows))]
                  for i in range(len(rows))]
        need(all(gram[i][i] == 2 for i in range(len(rows))), 'half norm')
        prices = tariff_from_matrix(rows, binary)
        for dim in (1, 2, 3):
            # Tensoring the pairing by I_dim multiplies every rank by dim.
            cost = dim * sum(prices)
            need(cost == dim * len(rows), 'sharp positive-half fixture')
            records.append([n, len(rows), dim, cost])
    return records
