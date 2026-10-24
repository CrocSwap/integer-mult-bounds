#!/usr/bin/env python3
"""Exact finite ingredients and tensor controls for the written rank proof."""

import hashlib
import json
import platform
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() % 2


def multiply(a, b, order):
    require(order in (2, 4, 8), "unsupported field")
    require(0 <= a < order and 0 <= b < order, "field element out of range")
    modulus = {2: 3, 4: 7, 8: 11}[order]
    value = 0
    for _ in range(3):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & order:
            a ^= modulus
    return value


def inverse(a, order):
    require(0 < a < order, "inverse of zero or invalid element")
    for b in range(1, order):
        if multiply(a, b, order) == 1:
            return b
    raise ValueError("field inverse missing")


def identity(n):
    require(1 <= n <= 136, "identity dimension out of range")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def product(left, right, order):
    require(1 <= len(left) <= 136 and 1 <= len(right) <= 136, "matrix size")
    inner, width = len(right), len(right[0])
    require(1 <= width <= 136, "matrix width")
    require(all(len(row) == inner for row in left), "product dimensions")
    require(all(len(row) == width for row in right), "ragged right matrix")
    result = [[0] * width for _ in left]
    for i, row in enumerate(left):
        for k, a in enumerate(row):
            if a:
                for j, b in enumerate(right[k]):
                    result[i][j] ^= multiply(a, b, order)
    return result


def rank(matrix, order):
    require(1 <= len(matrix) <= 136, "rank row bound")
    width = len(matrix[0])
    require(1 <= width <= 136, "rank column bound")
    require(all(len(row) == width for row in matrix), "ragged rank input")
    rows = [row[:] for row in matrix]
    pivot = 0
    for col in range(width):
        candidates = [i for i in range(pivot, len(rows)) if rows[i][col]]
        if not candidates:
            continue
        chosen = candidates[0]
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        scale = inverse(rows[pivot][col], order)
        rows[pivot] = [multiply(x, scale, order) for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            scale = rows[i][col]
            if scale:
                rows[i] = [x ^ multiply(scale, y, order)
                           for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def mask(types):
    require(1 <= len(types) <= 136, "type count bound")
    require(all(0 < q < 32 and 0 < w < 32 for q, w in types), "label bound")
    return [[dot(w, q) for q, _ in types] for _, w in types]


def outer_sum(types):
    return [[sum(((q >> a) & 1) * ((w >> b) & 1) for q, w in types) % 2
             for b in range(5)] for a in range(5)]


def fitting(matrix, binary_mask):
    n = len(matrix)
    require(len(binary_mask) == n, "fitting dimensions")
    require(all(len(row) == n for row in matrix + binary_mask), "square input")
    require(all(matrix[i][i] for i in range(n)), "zero diagonal")
    require(all(not binary_mask[i][j] or not matrix[i][j]
                for i in range(n) for j in range(n) if i != j), "forbidden entry")


def normalized(matrix, order):
    return [[multiply(x, inverse(row[i], order), order) for x in row]
            for i, row in enumerate(matrix)]


def geometry():
    odd = [x for x in range(32) if dot(x, x)]
    all_types = [(q, w) for q in odd for w in odd if dot(q, w)]
    regular = [(q, w) for q, w in all_types if q != 31 and w != 31]
    special = [(q, w) for q, w in all_types if q == 31 or w == 31]
    require((len(odd), len(all_types), len(regular), len(special)) ==
            (16, 136, 105, 31), "type census")
    require(all(sum(q == x for q, _ in regular) == 7 for x in odd if x != 31),
            "regular fiber count")
    require(outer_sum(regular) == [[1] * 5 for _ in range(5)], "regular moment")
    binary_mask = mask(all_types)
    require(rank(binary_mask, 2) == 5, "mask rank")
    for i, (q, w) in enumerate(all_types):
        if q == 31:
            require(all(row[i] == 1 for row in binary_mask), "special column")
        if w == 31:
            require(all(x == 1 for x in binary_mask[i]), "special row")
    return all_types, regular, binary_mask


def saturation_possible(types, paid_rank):
    require(len(types) == 5 * paid_rank, "not a saturation case")
    expected = [[(paid_rank % 2) * int(a == b) for b in range(5)]
                for a in range(5)]
    require(outer_sum(types) == expected, "saturation moment obstruction")


def tensor_fixture(order, copies, seed):
    require(copies in (1, 2) and seed in range(3), "fixture bounds")
    types = [(1 << a, 1 << a) for _ in range(copies) for a in range(5)]
    n = len(types)
    right = [[0] * n for _ in range(copies)]
    left = [[0] * copies for _ in range(n)]
    for i in range(n):
        b = 1 + (i + seed) % (order - 1)
        left[i][i // 5] = inverse(b, order)
        right[i // 5][i] = b
    matrix = product(left, right, order)
    scales = [1 + (2 * i + seed) % (order - 1) for i in range(n)]
    raw = [[multiply(scales[i], x, order) for x in row]
           for i, row in enumerate(matrix)]
    fitting(raw, mask(types))
    require(normalized(raw, order) == matrix, "diagonal normalization")
    require(rank(matrix, order) == copies, "fixture rank")
    u = [[((w >> a) & 1) * left[i][k]
          for a in range(5) for k in range(copies)]
         for i, (_, w) in enumerate(types)]
    v = [[((q >> a) & 1) * right[k][j] for j, (q, _) in enumerate(types)]
         for a in range(5) for k in range(copies)]
    require(product(u, v, order) == identity(n), "forward tensor inverse")
    reverse = product(v, u, order)
    require(reverse == identity(n), "reverse tensor inverse")
    traces = [[0] * 5 for _ in range(5)]
    for a in range(5):
        for b in range(5):
            for k in range(copies):
                traces[a][b] ^= reverse[a * copies + k][b * copies + k]
    require(traces == outer_sum(types), "block trace identity")
    saturation_possible(types, copies)
    return raw, u, v


def rank_addition(all_types, binary_mask, order):
    n = len(all_types)
    matrix = identity(n)
    coordinate = [i for i, (q, w) in enumerate(all_types)
                  if q == w and q.bit_count() == 1]
    require(len(coordinate) == 5, "coordinate class")
    for i in coordinate:
        for j in coordinate:
            matrix[i][j] = 1
    for i, (q, w) in enumerate(all_types):
        for j, (r, z) in enumerate(all_types):
            if not binary_mask[i][j] and 31 in (q, w, r, z):
                matrix[i][j] = (3 * i + 5 * j + 1) % order
    fitting(matrix, binary_mask)
    indices = [i for i, (q, w) in enumerate(all_types) if q != 31 and w != 31]
    regular = [[matrix[i][j] for j in indices] for i in indices]
    total_rank, regular_rank = rank(matrix, order), rank(regular, order)
    require(total_rank == 31 + regular_rank, "special rank addition")
    require((total_rank, regular_rank) == (132, 101), "fixture ranks")
    return [order, total_rank, regular_rank]


def rejected(call, message):
    try:
        call()
    except ValueError as error:
        require(message in str(error), "wrong rejection reason")
        return
    raise ValueError("negative control accepted")


def controls(regular, binary_mask):
    rejected(lambda: saturation_possible(regular, 21), "moment obstruction")
    rejected(lambda: saturation_possible(regular[:-1], 21), "saturation case")
    bad = identity(136)
    i, j = next((i, j) for i in range(136) for j in range(136)
                if i != j and binary_mask[i][j])
    bad[i][j] = 1
    rejected(lambda: fitting(bad, binary_mask), "forbidden entry")
    bad[i][i] = 0
    rejected(lambda: fitting(bad, binary_mask), "zero diagonal")
    raw, u, v = tensor_fixture(4, 1, 0)
    require(raw != normalized(raw, 4), "normalization control has no effect")
    raw_product = [[x * int(i == j) for j, x in enumerate(row)]
                   for i, row in enumerate(raw)]
    rejected(lambda: require(raw_product == identity(5), "unnormalized identity"),
             "unnormalized identity")
    v[0][0] ^= 1
    rejected(lambda: require(product(u, v, 4) == identity(5), "mutated tensor"),
             "mutated tensor")
    rejected(lambda: inverse(0, 4), "inverse of zero")
    return 7


def receipt(results):
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(path.stat().st_size <= 1024 * 1024, "package file size bound")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"files_sha256": hashes, "results": results,
            "result_sha256": hashlib.sha256(json.dumps(results, sort_keys=True).encode()).hexdigest(),
            "python": platform.python_version()}


def main():
    all_types, regular, binary_mask = geometry()
    fixtures = 0
    for order in (2, 4, 8):
        for copies in (1, 2):
            for seed in range(3):
                tensor_fixture(order, copies, seed)
                fixtures += 1
    additions = [rank_addition(all_types, binary_mask, order) for order in (2, 4)]
    count = controls(regular, binary_mask)
    results = {"regular_types": 105, "regular_lower": 22, "full_types": 136,
               "full_lower": 53, "mask_rank_F2": 5, "tensor_fixtures": fixtures,
               "rank_addition_fixtures": additions, "controls": count}
    print(json.dumps(receipt(results), sort_keys=True))
    print("PASS_ODD_FIVE_CHAR2_MINRANK regular_types=105 regular_lower=22 "
          f"full_types=136 full_lower=53 tensor_fixtures={fixtures} controls={count}")


if __name__ == "__main__":
    main()
