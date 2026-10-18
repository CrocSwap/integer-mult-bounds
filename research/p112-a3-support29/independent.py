"""Separate lattice, frame, subset and witness checks. Apache-2.0.

Uses no primary checker imports. Root conventions follow the retained
E8/P112 lineage; inverses, traversals and rank calculations are local.
"""

import json
from collections import Counter
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


def check(condition, message):
    if not condition:
        raise ValueError(message)


def lattice():
    roots = set()
    for indices in combinations(range(8), 2):
        for sign in (-1, 1):
            row = tuple(
                2 if j == indices[0] else 2 * sign if j == indices[1] else 0
                for j in range(8)
            )
            roots.add(max(row, tuple(-x for x in row)))
    for tail in product((-1, 1), repeat=7):
        row = (1,) + tail
        if row.count(-1) % 2 == 0:
            roots.add(row)
    roots = tuple(sorted(roots))
    check(len(roots) == 120, "independent root count")
    rows = [
        [Fraction(SIMPLE[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for j in range(8):
        pivot = next(i for i in range(j, 8) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        factor = rows[j][j]
        rows[j] = [x / factor for x in rows[j]]
        for i in range(8):
            if i != j:
                factor = rows[i][j]
                rows[i] = [
                    x - factor * y for x, y in zip(rows[i], rows[j], strict=True)
                ]
    labels = []
    for root in roots:
        coordinate = [sum(rows[j][8 + i] * root[i] for i in range(8)) for j in range(8)]
        check(
            all(x.denominator == 1 for x in coordinate), "independent lattice integral"
        )
        labels.append(
            1 + sum((int(x) & 1) * 2 ** (j + 1) for j, x in enumerate(coordinate))
        )
    check(len(set(labels)) == 120, "independent label injectivity")
    return roots, labels


def rank_mod(matrix, prime=65537):
    check(len(matrix) <= 42 and len({len(r) for r in matrix}) == 1, "rank shape")
    rows, rank = [[x % prime for x in row] for row in matrix], 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = pow(rows[rank][column], -1, prime)
        rows[rank] = [x * scale % prime for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [
                (x - scale * y) % prime
                for x, y in zip(rows[i], rows[rank], strict=True)
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def binary_rank(labels):
    basis = [0] * 9
    for label in labels:
        for j in range(8, -1, -1):
            if label >> j & 1:
                if basis[j]:
                    label ^= basis[j]
                else:
                    basis[j] = label
                    break
    return sum(bool(x) for x in basis)


def root_values(roots):
    return tuple((0, *((r[0] + r[j]) // 2 for j in (1, 2, 3))) for r in roots)


def enumerate_frames(roots):
    orthogonal = [
        {
            j
            for j in range(i + 1, 120)
            if sum(a * b for a, b in zip(r, roots[j], strict=True)) == 0
        }
        for i, r in enumerate(roots)
    ]
    level = [((), set(range(120)))]
    for _ in range(8):
        following = []
        for prefix, candidates in level:
            for j in sorted(candidates):
                following.append((prefix + (j,), candidates & orthogonal[j]))
        check(len(following) <= 200_000, "independent frame memory capacity")
        level = following
    result = [row for row, _ in level]
    check(len(result) == len(set(result)) == 2025, "independent frame coverage")
    return result


def robust_subsets(labels, groups):
    tested, ten_rank_five = 0, []
    for group in groups:
        for subset in combinations(group, 11):
            check(
                binary_rank([labels[i] for i in subset]) == 6, "eleven-label robustness"
            )
            tested += 1
        control = next(
            subset
            for subset in combinations(group, 10)
            if binary_rank([labels[i] for i in subset]) == 5
        )
        ten_rank_five.append(control)
    check(tested == 17472, "subset coverage")
    return {
        "eleven_subsets_checked": tested,
        "ten_label_rank_five_controls": ten_rank_five,
    }


def direct_budget(punctures, support):
    feasible = []
    for frame_cost, frame_singletons in punctures:
        baseline = 136 - frame_cost - 2 * support
        for unpinned in range(5):
            for paid in range(64 + 4 * unpinned + 1):
                slack = paid - baseline
                if slack < 0:
                    continue
                for deletion_defect in range(slack + 1):
                    for nonmodal in range((slack - deletion_defect) // 2 + 1):
                        if (
                            6 * unpinned
                            <= frame_singletons + deletion_defect + nonmodal
                        ):
                            feasible.append(
                                (frame_cost, frame_singletons, unpinned, paid)
                            )
    return sorted(set(feasible))


def check_witness(witness, roots, labels, values):
    frame, live, common, endpoints = (
        witness[k] for k in ("frame", "live", "common", "endpoints")
    )
    check(
        len(frame) == len(set(frame)) == 8 and all(0 <= i < 120 for i in frame),
        "witness frame indices",
    )
    check(
        all(
            sum(x * y for x, y in zip(roots[i], roots[j], strict=True)) == 0
            for i, j in combinations(frame, 2)
        ),
        "witness orthogonal frame",
    )
    check(live == [i for i in range(120) if i not in frame], "witness live order")
    check(
        len(common) == len(set(common)) == 30 and set(common) <= set(live),
        "witness common support",
    )
    check(
        len(endpoints) == 4
        and all(len(q) == 112 and all(type(x) is int for x in q) for q in endpoints),
        "witness endpoint shape",
    )
    support = [[live[j] for j, x in enumerate(q) if x] for q in endpoints]
    check(support == witness["endpoint_supports"], "witness support binding")
    check(
        all(len(s) == 16 and binary_rank([labels[i] for i in s]) == 6 for s in support),
        "witness endpoint ranks",
    )
    check(
        all(
            not any(q[j] for q in endpoints) for j, i in enumerate(live) if i in common
        ),
        "witness common-coordinate values",
    )
    check(
        all(
            endpoints[k][j] - endpoints[0][j] == values[i][k]
            for j, i in enumerate(live)
            if i not in common
            for k in (1, 2, 3)
        ),
        "witness literal code identities",
    )
    small = [[int(i == selected) for i in live] for selected in common]
    code = [[roots[i][j] for i in live] for j in range(8)]
    ranks = [
        (rank_mod(small + endpoints, p), rank_mod(small + endpoints + code, p))
        for p in (65537, 65539)
    ]
    check(
        rank_mod(code) == 8
        and ranks == [(34, 39), (34, 39)]
        and tuple(
            witness[k]
            for k in ("piece_rank", "code_rank", "union_rank", "intersection_dimension")
        )
        == (34, 8, 39, 3),
        "witness modular ranks",
    )
    return ranks


def build():
    expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
    roots, labels = lattice()
    values = root_values(roots)
    costs = [min(sum(x != shift for x in v) for shift in set(v)) for v in values]
    groups = [[] for _ in range(4)]
    for i, v in enumerate(values):
        if costs[i] == 1:
            common = next(x for x in v if v.count(x) == 3)
            groups[next(j for j, x in enumerate(v) if x != common)].append(i)
    check(
        [r["indices"] for r in expected["singleton_facts"]] == groups,
        "independent singleton reconstruction",
    )
    subset_receipt = robust_subsets(labels, groups)
    singleton = {i for group in groups for i in group}
    histogram = Counter(
        (sum(costs[i] for i in f), len(set(f) & singleton))
        for f in enumerate_frames(roots)
    )
    punctures = [
        {"cost": f, "singletons": t, "count": n}
        for (f, t), n in sorted(histogram.items())
    ]
    check(punctures == expected["punctures"], "independent puncture census")
    check(not direct_budget(tuple(histogram), 29), "independent support29 exclusion")
    check(direct_budget(tuple(histogram), 30), "independent support30 boundary")
    ranks = check_witness(expected["witness30"], roots, labels, values)
    return {
        "schema": "p112-a3-support29-independent/v1",
        "errors": 0,
        "punctures": punctures,
        "robust_subsets": subset_receipt,
        "witness_modular_ranks": ranks,
        "literal_code_identities": 246,
    }


if __name__ == "__main__":
    result = json.loads(json.dumps(build()))
    check(
        result == json.loads((PACKAGE / "INDEPENDENT.json").read_bytes()),
        "independent receipt differs",
    )
    print("PASS_P112_A3_SUPPORT29_INDEPENDENT subsets=17472 frames=2025 errors=0")
