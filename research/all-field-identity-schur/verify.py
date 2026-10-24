#!/usr/bin/env python3
"""Exact, read-only corroboration of the all-field fixed-H Schur theorem."""

import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y, q):
    return x ^ y if q == 4 else (x + y) % q


def neg(x, q):
    return x if q == 4 else (-x) % q


def mul(x, y, q):
    if q != 4:
        return x * y % q
    value = (x if y & 1 else 0) ^ ((x << 1) if y & 2 else 0)
    return value ^ 7 if value & 4 else value


def inv(x, q):
    require(x != 0, "zero inverse")
    for y in range(1, q):
        if mul(x, y, q) == 1:
            return y
    raise ValueError("nonfield arithmetic")


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def plus(a, b, q, sign=1):
    require(len(a) == len(b), "matrix row mismatch")
    require(all(len(x) == len(y) for x, y in zip(a, b)), "matrix column mismatch")
    return tuple(tuple(add(x, y if sign == 1 else neg(y, q), q)
                       for x, y in zip(row, other)) for row, other in zip(a, b))


def product(a, b, q):
    require(bool(a) and bool(b), "empty matrix multiplication")
    require(len(a[0]) == len(b), "product shape mismatch")
    result = []
    for row in a:
        output = []
        for j in range(len(b[0])):
            value = 0
            for k in range(len(b)):
                value = add(value, mul(row[k], b[k][j], q), q)
            output.append(value)
        result.append(tuple(output))
    return tuple(result)


def reduced(a, q):
    if not a:
        return (), ()
    require(len(a) <= 24 and len(a[0]) <= 48, "matrix capacity")
    require(all(len(row) == len(a[0]) for row in a), "ragged matrix")
    require(all(0 <= x < q for row in a for x in row), "field element")
    rows = [list(row) for row in a]
    pivots = []
    for j in range(len(rows[0])):
        r = len(pivots)
        if r == len(rows):
            break
        pivot = next((i for i in range(r, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        scale = inv(rows[r][j], q)
        rows[r] = [mul(x, scale, q) for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][j]:
                factor = rows[i][j]
                rows[i] = [add(x, neg(mul(factor, y, q), q), q)
                           for x, y in zip(rows[i], rows[r])]
        pivots.append(j)
    return tuple(tuple(row) for row in rows), tuple(pivots)


def rank(a, q):
    return len(reduced(a, q)[1])


def inverse(a, q):
    n = len(a)
    require(n > 0 and all(len(row) == n for row in a), "inverse shape")
    r, pivots = reduced(tuple(row + unit for row, unit in zip(a, eye(n))), q)
    require(pivots == tuple(range(n)), "singular matrix")
    return tuple(row[n:] for row in r)


def transpose(a):
    return tuple(zip(*a))


def active_factor(t, q):
    """XY=t, X onto and Y injective, through d+nullity(t)."""
    d = len(t)
    columns = [tuple(row[j] for row in t) for j in range(d)]
    current = rank(t, q)
    extra = []
    for unit in eye(d):
        candidate = transpose(columns + extra + [unit])
        if rank(candidate, q) > current:
            extra.append(unit)
            current += 1
    x = transpose(columns + extra)
    y = eye(d) + tuple((0,) * d for _ in extra)
    require(rank(x, q) == d and rank(y, q) == d, "active ranks")
    require(product(x, y, q) == t, "active product")
    return x, y


def rank_factor(t, q):
    """Rank factorization through rank(t), including the zero sector."""
    d = len(t)
    _, pivots = reduced(t, q)
    r = len(pivots)
    x = tuple(tuple(row[j] for j in pivots) for row in t)
    if r == 0:
        return x, ()
    _, rows = reduced(transpose(x), q)
    square = tuple(x[j] for j in rows)
    y = product(inverse(square, q), tuple(t[j] for j in rows), q)
    require(product(x, y, q) == t, "rank factor product")
    require(len(y) == rank(t, q), "minimal rank factor")
    return x, y


def assemble(h, q, defect=None):
    d = len(h)
    w = plus(eye(d), h, q, -1)
    factors = [rank_factor(tuple(tuple(neg(x, q) for x in row) for row in w), q),
               active_factor(w, q), active_factor(w, q), active_factor(h, q)]
    if defect is not None:
        sector, side = defect
        x, y = factors[sector]
        require(all(v == 0 for row in (h if sector == 3 else w) for v in row),
                "defect requires zero compressed product")
        if side == "x":
            x = tuple((0,) * len(x[0]) for _ in x)
        else:
            y = tuple((0,) * d for _ in y)
        factors[sector] = x, y
    sizes = tuple(len(y) for _, y in factors)
    inclusion = tuple(row for _, y in factors for row in y)
    projection = tuple(tuple(v for x, _ in factors for v in x[j]) for j in range(d))
    require(product(projection, inclusion, q) == eye(d), "split maps")
    r, pivots = reduced(projection, q)
    n = len(inclusion)
    null_columns = []
    for j in range(n):
        if j not in pivots:
            column = [0] * n
            column[j] = 1
            for i, pivot in enumerate(pivots):
                column[pivot] = neg(r[i][j], q)
            null_columns.append(tuple(column))
    basis = tuple(inclusion[j] + tuple(c[j] for c in null_columns) for j in range(n))
    basis_inverse = inverse(basis, q)
    p_mask = (0,) * sizes[0] + (1,) * sizes[1] + (0,) * sizes[2] + (1,) * sizes[3]
    q_mask = (0,) * sizes[0] + (0,) * sizes[1] + (1,) * (sizes[2] + sizes[3])
    p = product(basis_inverse, tuple(tuple(mul(v, p_mask[j], q) for v in row)
                                   for j, row in enumerate(basis)), q)
    z = product(basis_inverse, tuple(tuple(mul(v, q_mask[j], q) for v in row)
                                   for j, row in enumerate(basis)), q)
    return p, z, sizes


def block(a, row, height, col, width):
    return tuple(tuple(line[col:col + width]) for line in a[row:row + height])


def inspect(p, z, h, q, sharp=True):
    d, n = len(h), len(p)
    require(product(p, p, q) == p and product(z, z, q) == z, "idempotence")
    pq = product(p, z, q)
    require(pq == product(z, p, q), "commutation")
    require(block(p, 0, d, 0, d) == eye(d), "P identity pivot")
    require(block(z, 0, d, 0, d) == eye(d), "Q identity pivot")
    require(block(pq, 0, d, 0, d) == h, "prescribed product")
    c, e = block(p, d, n-d, 0, d), block(z, d, n-d, 0, d)
    r, l = block(p, 0, d, d, n-d), block(z, 0, d, d, n-d)
    s = plus(block(p, d, n-d, d, n-d), product(c, r, q), q, -1)
    t = plus(block(z, d, n-d, d, n-d), product(e, l, q), q, -1)
    k = plus(product(s, t, q), product(t, s, q), q, -1)
    x = plus(block(pq, d, n-d, 0, d), product(e, h, q), q, -1)
    u, v = plus(c, e, q, -1), plus(r, l, q, -1)
    y = plus(block(pq, 0, d, d, n-d), product(h, l, q), q, -1)
    require(k == plus(product(x, v, q), product(u, y, q), q, -1), "ordered factors")
    kr = rank(k, q)
    require((kr == 2*d) == sharp, "sharpness criterion")
    require(rank(s, q) == rank(p, q)-d and rank(t, q) == rank(z, q)-d,
            "Schur rank drop")
    return k, product(x, v, q), product(u, y, q)


def verify_constructions():
    counts = {}
    sign_witness = None
    for q in (2, 3, 4, 5):
        count = 0
        for d in (1, 2):
            for values in itertools.product(range(q), repeat=d*d):
                h = tuple(tuple(values[i*d:(i+1)*d]) for i in range(d))
                p, z, sizes = assemble(h, q)
                k, xv, uy = inspect(p, z, h, q)
                a, b = d-rank(h, q), d-rank(plus(eye(d), h, q, -1), q)
                require(sizes == (d-b, d+b, d+b, d+a), "sector minima")
                require(len(p) == 4*d+a+b, "ambient minimum")
                require(rank(p, q) == rank(z, q) == 2*d+a+b, "input minima")
                j = product(h, plus(eye(d), h, q, -1), q)
                require(d-rank(j, q) == a+b, "coprime nullity identity")
                if q in (3, 5) and plus(xv, uy, q) != k:
                    sign_witness = (q, h)
                count += 1
        counts[str(q)] = count
    require(sign_witness is not None, "odd-characteristic sign control")
    return counts, sign_witness


def verify_controls():
    defects = 0
    for q in (3, 4, 5):
        for sector in (1, 2, 3):
            h = ((0 if sector == 3 else 1,),)
            for side in ("x", "y"):
                p, z, _ = assemble(h, q, (sector, side))
                inspect(p, z, h, q, sharp=False)
                defects += 1
    require(mul(2, 2, 4) == 3 and add(1, 1, 4) == 0, "F4, not Z/4")
    rejected = 0
    for bad in (((0,),), ((1, 0),)):
        try:
            inverse(bad, 3)
        except ValueError:
            rejected += 1
    try:
        reduced(((0,) * 49,) * 2, 3)
    except ValueError:
        rejected += 1
    require(rejected == 3, "singular/shape/capacity rejection")
    for q in (3, 5):
        w = neg(1, q)
        require(add(add(add(w, w, q), w, q), 2, q) != 1,
                "unsigned 00 sector must fail outside characteristic two")
    for q in (3, 4, 5):
        for d in range(1, 5):
            h = tuple(tuple(2 if i == j else 0 for j in range(d)) for i in range(d))
            p, z, _ = assemble(h, q)
            inspect(p, z, h, q)
            require(len(p) == 4*d, "nonbinary unrestricted minimum")
    for q in (2, 3, 4, 5):
        for diagonal in ((0, 0, 1), (1, 1, 0), (0, 1, 2 if q > 2 else 1)):
            h = tuple(tuple(diagonal[i] if i == j else int(j == i+1)
                            for j in range(3)) for i in range(3))
            p, z, _ = assemble(h, q)
            inspect(p, z, h, q)
    return {"missing_active_maps": defects, "rejected_inputs": rejected,
            "unrestricted_witnesses": 12, "nondiagonal_size_three": 12,
            "unsigned_sector_rejections": 2}


def main():
    counts, sign_witness = verify_constructions()
    controls = verify_controls()
    root = Path(__file__).resolve().parent
    files = tuple(sorted(path for path in root.iterdir() if path.is_file()))
    require(5 <= len(files) <= 8, "receipt file capacity")
    receipt = {"claim_type": "scoped algebraic proof with finite corroboration",
               "fixed_h_constructions": counts, "controls": controls,
               "odd_sign_witness": sign_witness,
               "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in files}}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_ALL_FIELD_IDENTITY_SCHUR")


if __name__ == "__main__":
    main()
