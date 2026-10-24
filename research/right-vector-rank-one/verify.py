#!/usr/bin/env python3
"""Literal finite corroboration of the rank-one matrix-algebra cost theorem.

Produced by Nick Petalas. Apache-2.0. No predecessor verifier is imported.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    need(q in (2, 3, 4), "unsupported finite control field")
    add = [[(x + y) % q for y in range(q)] for x in range(q)]
    mul = [[(x * y) % q for y in range(q)] for x in range(q)]
    if q == 4:
        # Polynomial basis F2[t]/(t^2+t+1), encoded as two bits.
        add = [[x ^ y for y in range(q)] for x in range(q)]
        for x, y in product(range(q), repeat=2):
            raw = (x if y & 1 else 0) ^ (x << 1 if y & 2 else 0)
            mul[x][y] = raw ^ (7 if raw & 4 else 0)
    neg = [next(y for y in range(q) if add[x][y] == 0) for x in range(q)]
    inv = [0] + [next(y for y in range(1, q) if mul[x][y] == 1)
                 for x in range(1, q)]
    for x, y in product(range(q), repeat=2):
        need(add[x][y] == add[y][x] and mul[x][y] == mul[y][x], "field commutativity")
        need(add[x][0] == x and mul[x][1] == x and mul[x][0] == 0, "field identities")
    for x, y, z in product(range(q), repeat=3):
        need(add[add[x][y]][z] == add[x][add[y][z]], "addition associativity")
        need(mul[mul[x][y]][z] == mul[x][mul[y][z]], "multiplication associativity")
        need(mul[x][add[y][z]] == add[mul[x][y]][mul[x][z]], "distributivity")
    return add, mul, neg, inv


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def mm(left, right, f):
    add, mul, _, _ = f
    size = len(left)
    out = [[0] * size for _ in range(size)]
    for i, k in product(range(size), repeat=2):
        if left[i][k]:
            for j in range(size):
                out[i][j] = add[out[i][j]][mul[left[i][k]][right[k][j]]]
    return out


def mv(matrix, vector, f):
    add, mul, _, _ = f
    out = [0] * len(vector)
    for i, j in product(range(len(vector)), repeat=2):
        out[i] = add[out[i]][mul[matrix[i][j]][vector[j]]]
    return out


def rank(matrix, f):
    add, mul, neg, inv = f
    rows = [row[:] for row in matrix]
    height, width = len(rows), len(rows[0])
    pivot = 0
    for col in range(width):
        candidates = [r for r in range(pivot, height) if rows[r][col]]
        if not candidates:
            continue
        r = candidates[0]
        rows[pivot], rows[r] = rows[r], rows[pivot]
        scale = inv[rows[pivot][col]]
        rows[pivot] = [mul[scale][x] for x in rows[pivot]]
        for r in range(pivot + 1, height):
            scale = rows[r][col]
            rows[r] = [add[x][neg[mul[scale][y]]]
                       for x, y in zip(rows[r], rows[pivot])]
        pivot += 1
        if pivot == height:
            break
    return pivot


def factor(left, right, n, m, f):
    need(len(left) == n * m and len(right) == n, "factor dimensions")
    need(all(len(row) == m for row in left), "left block dimensions")
    add, mul, _, _ = f
    out = identity(n * m)
    for i, j, k in product(range(n * m), range(n), range(m)):
        out[i][j * m + k] = add[out[i][j * m + k]][mul[left[i][k]][right[j]]]
    return out


def outer(a, b, f):
    return [[f[1][x][y] for y in b] for x in a]


def construction(a, b, n, m, f):
    need(1 <= n <= 4 and 1 <= m <= 3 and n * m <= 8, "finite control bounds")
    need(len(a) == len(b) == n * m and any(a) and any(b), "rank-one input")
    add, mul, neg, inv = f
    first = next(j for j in range(n) if any(b[j * m:(j + 1) * m]))
    permuted = list(b)
    permuted[:m], permuted[first * m:(first + 1) * m] = (
        b[first * m:(first + 1) * m], b[:m])
    h = next(k for k in range(m) if permuted[k])
    left = outer(a, permuted[:m], f)
    for k in range(m):
        left[k][k] = add[left[k][k]][neg[1]]
    words = [(left, [1] + [0] * (n - 1))]
    for j in range(1, n):
        left = [[0] * m for _ in range(n * m)]
        left[h] = [mul[inv[permuted[h]]][x]
                   for x in permuted[j * m:(j + 1) * m]]
        for k in range(m):
            left[j * m + k][k] = neg[1]
        words.append((left, [int(k == j) for k in range(n)]))
    free = identity(n * m)
    for k in range(m):
        free[k], free[first * m + k] = free[first * m + k], free[k]
    return words, free


def matrix_word(words, free, n, m, f):
    out = identity(n * m)
    for left, right in words:
        out = mm(out, factor(left, right, n, m, f), f)
    return mm(out, free, f)


def data_word(words, free, vector, n, m, f):
    # Execute the mathematical product on column data in reverse factor order.
    add, mul, _, _ = f
    state = mv(free, vector, f)
    for left, right in reversed(words):
        selected = [0] * m
        for j, k in product(range(n), range(m)):
            selected[k] = add[selected[k]][mul[right[j]][state[j * m + k]]]
        change = [0] * (n * m)
        for i, k in product(range(n * m), range(m)):
            change[i] = add[change[i]][mul[left[i][k]][selected[k]]]
        state = [add[x][y] for x, y in zip(state, change)]
    return state


def check_target(a, b, q, n, m, f):
    target = outer(a, b, f)
    words, free = construction(a, b, n, m, f)
    need(len(words) == n, "unpaid column replacement")
    need(matrix_word(words, free, n, m, f) == target, "literal matrix product")
    need(rank(target, f) == 1, "ordinary target rank")
    need(rank(free, f) == n * m, "free map invertibility")
    for left, right in words:
        need(all(0 <= x < q for row in left for x in row), "coefficient field")
        need(rank(factor(left, right, n, m, f), f) >= (n - 1) * m,
             "paid factor nullity exceeds m")
    for vector in identity(n * m):
        need(data_word(words, free, vector, n, m, f) == mv(target, vector, f),
             "independent basis-data execution")


def census(q, n, m):
    f = field(q)
    size = n * m
    need(1 <= n <= 4 and 1 <= m <= 3 and q ** size <= 4096, "finite vector capacity")
    vectors = tuple(product(range(q), repeat=size))
    normalized = [a for a in vectors if any(a) and next(x for x in a if x) == 1]
    count = 0
    for a in normalized:
        for b in vectors[1:]:
            check_target(a, b, q, n, m, f)
            count += 1
    expected = (q ** size - 1) ** 2 // (q - 1)
    need(count == expected, "rank-one enumeration count")
    return {"q": q, "n": n, "m": m, "rank_one_targets": count, "exact_cost": n}


def controls():
    n, m, f = 2, 2, field(3)
    a, b = (1, 0, 0, 1), (1, 0, 0, 1)
    words, free = construction(a, b, n, m, f)
    target = outer(a, b, f)
    need(matrix_word(words[:-1], free, n, m, f) != target, "dropped-factor control")
    need(matrix_word(words[::-1], free, n, m, f) != target, "reversed-word control")
    left, right = words[1]
    changed = [row[:] for row in left]
    changed[2][0] = changed[3][1] = 1
    need(matrix_word([words[0], (changed, right)], free, n, m, f) != target,
         "odd-field sign control")
    changed = [row[:] for row in left]
    changed[0][:], changed[1][:] = [0, 0], [1, 0]
    need(matrix_word([words[0], (changed, right)], free, n, m, f) != target,
         "wrong right-ideal multiplication control")
    b = (0, 0, 1, 1)
    words, free = construction(a, b, n, m, f)
    need(matrix_word(words, identity(4), n, m, f) != outer(a, b, f),
         "missing free input permutation control")
    for omitted in range(n):
        remaining = words[:omitted] + words[omitted + 1:]
        need(rank(matrix_word(remaining, free, n, m, f), f) >= m,
             "n-minus-one rank-loss control")
    zero_words = []
    for j in range(n):
        left = [[0] * m for _ in range(n * m)]
        for k in range(m):
            left[j * m + k][k] = f[2][1]
        zero_words.append((left, [int(k == j) for k in range(n)]))
    need(matrix_word(zero_words, identity(4), n, m, f) == [[0] * 4 for _ in range(4)],
         "predecessor zero-target boundary")
    scalar = [[1, 0], [0, 0]]
    need(rank(scalar, f) == 1 and scalar == factor([[0], [2]], [0, 1], 2, 1, f),
         "m-equals-one has cost n-minus-one")
    return 9


def main():
    cases = [(2, 1, 2), (2, 2, 2), (3, 2, 2), (4, 2, 2), (2, 3, 2), (2, 2, 3)]
    results = [census(q, n, m) for q, n, m in cases]
    boundary_controls = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    receipt = {"results": results, "controls": boundary_controls,
               "files": {name: sha256((package / name).read_bytes()).hexdigest()
                         for name in names}}
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_RIGHT_VECTOR_RANK_ONE",
          "targets=" + str(sum(row["rank_one_targets"] for row in results)),
          "controls=" + str(boundary_controls), "receipt=" + sha256(encoded).hexdigest(),
          "no_new_kappa")


if __name__ == "__main__":
    main()
