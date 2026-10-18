"""Separate dense/norm reconstruction of the capacity evidence. Apache-2.0."""

import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dense_rank(rows, width):
    require(len(rows) <= 256 and 1 <= width <= 9, "dense rank bound")
    work = [[value >> i & 1 for i in range(width)] for value in rows]
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        for i in range(pivot + 1, len(work)):
            if work[i][column]:
                work[i] = [x ^ y for x, y in zip(work[i], work[pivot], strict=True)]
        pivot += 1
    return pivot


def coordinates(root):
    rows = [
        [Fraction(SIMPLE[j][i]) for j in range(8)] + [Fraction(root[i])]
        for i in range(8)
    ]
    for column in range(8):
        found = next((i for i in range(column, 8) if rows[i][column]), None)
        require(found is not None, "integral lattice basis")
        rows[column], rows[found] = rows[found], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(8):
            if i != column:
                scale = rows[i][column]
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[column], strict=True)
                ]
    result = tuple(row[-1] for row in rows)
    require(all(x.denominator == 1 for x in result), "root has integral coordinates")
    return sum((int(x) % 2) << i for i, x in enumerate(result))


def norm_quadratic(value):
    vector = [sum(SIMPLE[j][i] for j in range(8) if value >> j & 1) for i in range(8)]
    norm = sum(x * x for x in vector)
    require(norm % 8 == 0, "even E8 norm")
    return norm // 8 % 2


def root_model():
    roots = set()
    frame = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            root = tuple(2 if k == i else sign if k == j else 0 for k in range(8))
            roots.add(root)
            if i % 2 == 0 and j == i + 1:
                frame.add(root)
    for signs in product((-1, 1), repeat=8):
        if signs[0] == 1 and sum(x < 0 for x in signs) % 2 == 0:
            roots.add(signs)
    require((len(roots), len(frame)) == (120, 8), "separate root inventory")
    residues = {root: coordinates(root) for root in roots}
    return residues, {value for root, value in residues.items() if root not in frame}


def check():
    result = json.loads((PACKAGE / "RESULT.json").read_bytes())
    table = [norm_quadratic(x) for x in range(256)]
    polar_rows = [
        sum(
            (table[(1 << i) ^ (1 << j)] ^ table[1 << i] ^ table[1 << j]) << j
            for j in range(8)
        )
        for i in range(8)
    ]
    require(dense_rank(polar_rows, 8) == result["polar_rank"] == 8, "polar rank")
    require(
        sum((-1) ** value for value in table) == result["Gauss_sum"] == 16, "Gauss sum"
    )
    residues, live = root_model()
    require(
        set(residues.values()) == {x for x in range(256) if table[x]}, "root bijection"
    )
    for witness in result["P112_attainment"]:
        basis, offset = witness["direction_basis"], witness["affine_offset"]
        values = {offset}
        for vector in basis:
            values |= {x ^ vector for x in values}
        support = sorted(1 | (x << 1) for x in values & live)
        require(support == witness["support_labels"], "independent live witness")
        require(dense_rank(support, 9) == witness["binary_rank"], "witness binary rank")
        require(len(support) == witness["support_size"], "witness cardinality")
    maxima = {}
    for row in result["restriction_cases"]:
        k, p = row["affine_dimension"], row["polar_rank"]
        t = k - p
        if row["balanced"]:
            value = 2 ** (k - 1)
        elif k + t == 8:
            value = (2**k - 16) // 2
        else:
            value = 2 ** (k - 1) + 2 ** (k - p // 2 - 1)
        require(value == row["upper_bound"], "independent branch arithmetic")
        maxima[k] = max(maxima.get(k, 0), value)
    require(maxima == {4: 12, 5: 20}, "capacity maxima")
    print("PASS_E8_QUADRATIC_INDEPENDENT dense_rank norm_model root_binding witnesses")


if __name__ == "__main__":
    check()
