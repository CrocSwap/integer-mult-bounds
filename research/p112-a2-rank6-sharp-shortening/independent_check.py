"""Separate lattice, closure and modular witness check; imports no project code."""

import json
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

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
PACKAGE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def reduce_basis(values):
    pivots = [0] * 9
    for original in values:
        x = original
        for bit in range(8, -1, -1):
            if x & (1 << bit):
                if pivots[bit]:
                    x ^= pivots[bit]
                else:
                    pivots[bit] = x
                    break
    return tuple(x for x in pivots if x)


def span(values):
    basis = reduce_basis(values)
    return {xor_selected(basis, mask) for mask in range(1 << len(basis))}


def xor_selected(basis, mask):
    value = 0
    for i, row in enumerate(basis):
        if mask & (1 << i):
            value ^= row
    return value


def inverse_simple():
    rows = [
        [Fraction(SIMPLE[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for j in range(8):
        k = next(k for k in range(j, 8) if rows[k][j])
        rows[j], rows[k] = rows[k], rows[j]
        divisor = rows[j][j]
        rows[j] = [v / divisor for v in rows[j]]
        for k in range(8):
            if k != j:
                factor = rows[k][j]
                rows[k] = [
                    x - factor * y for x, y in zip(rows[k], rows[j], strict=True)
                ]
    return [row[8:] for row in rows]


def geometry():
    roots = []
    for root in product(range(-2, 3), repeat=8):
        if sum(x * x for x in root) != 8 or sum(root) % 4:
            continue
        if not (all(x % 2 == 0 for x in root) or all(x % 2 for x in root)):
            continue
        if next(x for x in root if x) > 0:
            roots.append(root)
    check(len(roots) == 120, "independent lattice root count")
    inverse = inverse_simple()
    labels = []
    for root in roots:
        coords = [sum(x * y for x, y in zip(row, root, strict=True)) for row in inverse]
        check(all(x.denominator == 1 for x in coords), "nonintegral lattice label")
        labels.append(
            1 + sum((int(x) % 2) * (1 << (j + 1)) for j, x in enumerate(coords))
        )
    frame = set()
    for i in (0, 2, 4, 6):
        for sign in (-2, 2):
            r = [0] * 8
            r[i], r[i + 1] = 2, sign
            frame.add(tuple(r))
    live = [
        (r, label) for r, label in zip(roots, labels, strict=True) if r not in frame
    ]
    return roots, labels, [r for r, _ in live], [label for _, label in live]


def closure_receipt(singletons, all_labels):
    whole = span(singletons)
    hyperplanes = {
        frozenset(x for x in whole if (f & x).bit_count() % 2 == 0)
        for f in range(1, 512)
    }
    hyperplanes.discard(frozenset(whole))
    check(
        len(hyperplanes) == 127 and all(len(h) == 64 for h in hyperplanes),
        "independent hyperplane coverage",
    )
    hist = Counter(
        (len(set(all_labels) & h), len(set(singletons) & h)) for h in hyperplanes
    )
    maxima = sorted(
        sorted(set(singletons) & h)
        for h in hyperplanes
        if len(set(singletons) & h) + len(set(all_labels) & h) == 32
    )
    maximum_five = 0
    generated = set()
    for subset in combinations(singletons, 5):
        subspace = frozenset(span(subset))
        if len(subspace) == 32 and subspace not in generated:
            generated.add(subspace)
            maximum_five = max(maximum_five, len(set(singletons) & subspace))
    check(maximum_five == 10, "independent rank-five fiber capacity")
    return {f"{a},{b}": n for (a, b), n in sorted(hist.items())}, sha256(
        json.dumps(maxima, separators=(",", ":")).encode()
    ).hexdigest()


def modular_rank(matrix, prime):
    rows = [[x % prime for x in row] for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        factor = pow(rows[rank][col], -1, prime)
        rows[rank] = [x * factor % prime for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            factor = rows[i][col]
            rows[i] = [
                (x - factor * y) % prime
                for x, y in zip(rows[i], rows[rank], strict=True)
            ]
        rank += 1
    return rank


def witness_check(result, points, labels):
    witness = result["witness30"]
    cut = set(witness["common_cut_indices"])
    check(len(cut) == 30, "independent common-cut size")
    pieces = []
    for support, coefficients in zip(
        witness["piece_support_indices"], witness["piece_coefficients"], strict=True
    ):
        check(
            len(support) == len(set(support)) == len(coefficients) == 16,
            "independent piece inventory",
        )
        check(
            len(reduce_basis([labels[t] for t in support])) == 6,
            "independent piece binary rank",
        )
        check(not set(support) & cut and all(coefficients), "independent piece support")
        pieces.append(dict(zip(support, coefficients, strict=True)))
    a, b = witness["directions"]
    rows = []
    for t, point in enumerate(points):
        if t in cut:
            continue
        q = [p.get(t, 0) for p in pieces]
        check(
            q[1] - q[0] == sum(x * y for x, y in zip(a, point, strict=True))
            and q[2] - q[0] == sum(x * y for x, y in zip(b, point, strict=True)),
            "independent code identities",
        )
        rows.append(list(point) + q)
    for prime in (101, 103):
        check(
            [
                modular_rank([r[:8] for r in rows], prime),
                modular_rank([r[8:] for r in rows], prime),
                modular_rank(rows, prime),
            ]
            == [8, 3, 9],
            "independent modular witness ranks",
        )
    # The two exact displayed dependencies bound the joined rational rank by nine.
    # Modular rank nine supplies the matching lower bound, so the Q rank is nine.


def main():
    result = json.loads((PACKAGE / "RESULT.json").read_text())
    roots, labels, points, live_labels = geometry()
    a, b = (2, 2, 0, 0, 0, 0, 0, 0), (2, 0, 2, 0, 0, 0, 0, 0)
    classes = [[], [], []]
    for r, label in zip(roots, labels, strict=True):
        v = (
            0,
            sum(x * y for x, y in zip(a, r, strict=True)),
            sum(x * y for x, y in zip(b, r, strict=True)),
        )
        for i in range(3):
            others = [v[j] for j in range(3) if j != i]
            if others[0] == others[1] != v[i]:
                classes[i].append(label)
    for labels_class, expected in zip(classes, result["class_receipts"], strict=True):
        histogram, digest = closure_receipt(labels_class, labels)
        check(
            histogram == expected["joint_total_singleton_histogram"]
            and digest == expected["maximizing_sets_sha256"],
            "independent joint receipt",
        )
    witness_check(result, points, live_labels)
    print(
        "PASS_INDEPENDENT_RANK6_CLOSURE classes=3 hyperplanes=381 "
        "five_subsets=242190 witness_modular_ranks=8,3,9"
    )


if __name__ == "__main__":
    main()
