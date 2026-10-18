"""Separate dense root/label reconstruction and hyperplane check. Apache-2.0."""

import json
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product

import verify as primary


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(matrix):
    rows = [
        [Fraction(x) for x in row] + [Fraction(i == j) for j in range(8)]
        for i, row in enumerate(matrix)
    ]
    for j in range(8):
        k = next((k for k in range(j, 8) if rows[k][j]), None)
        require(k is not None, "invertible simple-root matrix")
        rows[j], rows[k] = rows[k], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(8):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j], strict=True)]
    return tuple(tuple(row[8:]) for row in rows)


def roots_and_labels(simple):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = tuple(2 if k == i else 2 * sign if k == j else 0 for k in range(8))
            roots.add(max(root, tuple(-x for x in root)))
    for signs in product((-1, 1), repeat=8):
        if sum(x < 0 for x in signs) % 2 == 0:
            roots.add(max(signs, tuple(-x for x in signs)))
    roots = tuple(sorted(roots))
    inv = inverse(tuple(zip(*simple, strict=True)))
    labels = []
    for root in roots:
        coords = [sum(a * b for a, b in zip(row, root, strict=True)) for row in inv]
        require(all(x.denominator == 1 for x in coords), "integer root coordinates")
        labels.append(
            1 + sum((int(x) % 2) * 2 ** (i + 1) for i, x in enumerate(coords))
        )
    require(len(roots) == len(set(labels)) == 120, "full roots")
    return roots, tuple(labels)


def dense_rank(rows):
    require(
        len(rows) <= 512 and all(type(x) is int and 0 <= x < 512 for x in rows),
        "bounded dense rows",
    )
    matrix = [[(x >> j) & 1 for j in range(9)] for x in rows]
    pivot = 0
    for j in range(9):
        found = next((i for i in range(pivot, len(matrix)) if matrix[i][j]), None)
        if found is not None:
            matrix[pivot], matrix[found] = matrix[found], matrix[pivot]
            for i in range(pivot + 1, len(matrix)):
                if matrix[i][j]:
                    matrix[i] = [
                        a ^ b for a, b in zip(matrix[i], matrix[pivot], strict=True)
                    ]
            pivot += 1
    return pivot


def realize_fiber(roots, labels, fiber):
    for a, b in combinations(roots, 2):
        if abs(sum(x * y for x, y in zip(a, b, strict=True))) != 4:
            continue
        groups = {}
        for root, label in zip(roots, labels, strict=True):
            x = sum(t * u for t, u in zip(a, root, strict=True))
            y = sum(t * u for t, u in zip(b, root, strict=True))
            key = (True, Fraction(y, x)) if x else (False, bool(y))
            groups.setdefault(key, set()).add(label)
        if fiber in groups.values():
            return
    raise ValueError("canonical set is not an actual A2 projective fiber")


def main():
    g = primary.geometry()
    roots, labels = roots_and_labels(g.SIMPLE)
    result = json.loads(primary.read_bytes(primary.PACKAGE / "RESULT.json"))
    require(
        sha256(json.dumps(labels).encode()).hexdigest() == result["root_labels_sha256"],
        "separate label reconstruction",
    )
    fiber = set(result["canonical_fiber"])
    realize_fiber(roots, labels, fiber)
    require(dense_rank(tuple(fiber)) == 7, "fiber span")
    # Ambient kernels give each distinct W-hyperplane four times.
    space = closure(fiber)
    sections = {
        tuple(sorted(x for x in labels if not (x & u).bit_count() % 2 and x in space))
        for u in range(1, 512)
    }
    # Three kernels containing all W induce W itself; remove its 28-root closure.
    sections = {s for s in sections if len(s) != 28}
    require(len(sections) == 127, "canonical hyperplanes complete")
    histogram = Counter((len(s), len(set(s) & fiber)) for s in sections)
    observed = {f"{m},{j}": n for (m, j), n in sorted(histogram.items())}
    require(
        observed == result["canonical"]["histogram"], "independent hyperplane table"
    )
    witness = tuple(result["canonical"]["witness_labels"])
    require(dense_rank(witness) == 6, "witness rank")
    require(
        set(labels) & closure(witness) == set(witness) <= fiber,
        "exact equality closure",
    )
    frame = {
        tuple(2 if k == i else 2 * s if k == i + 1 else 0 for k in range(8))
        for i in range(0, 8, 2)
        for s in (-1, 1)
    }
    live = {
        label for root, label in zip(roots, labels, strict=True) if root not in frame
    }
    require(set(witness) <= live, "actual P112 equality witness")
    print("PASS_INDEPENDENT_A2_RANK6")


def closure(values):
    require(
        len(values) <= 512 and all(type(x) is int and 0 <= x < 512 for x in values),
        "bounded closure",
    )
    result = {0}
    for value in sorted(values):
        if value not in result:
            result |= {x ^ value for x in tuple(result)}
    return result


if __name__ == "__main__":
    main()
