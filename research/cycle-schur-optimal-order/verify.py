#!/usr/bin/env python3
"""Exact corroboration of the new ordering theorem; standard library only."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

MAX_VERTICES = 96
MAX_BRUTE_VERTICES = 8
MAX_CYCLE_VERTICES = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def domain(m, w):
    require(type(m) is int and type(w) is int, "integer dimensions required")
    require(1 <= m <= MAX_VERTICES, "survivor count outside verifier domain")
    require(1 <= w <= MAX_VERTICES, "radius outside verifier domain")


def graph(m, w):
    """Path power plus the clique on the two end strips."""
    domain(m, w)
    boundary = set(range(min(w, m))) | set(range(max(0, m - w), m))
    return tuple(
        (i, j)
        for i in range(m)
        for j in range(i + 1, m)
        if j - i <= w or (i in boundary and j in boundary)
    )


def folded_order(m):
    domain(m, 1)
    return tuple(k // 2 if k % 2 == 0 else m - 1 - k // 2 for k in range(m))


def bandwidth(order, edges):
    m = len(order)
    require(1 <= m <= MAX_VERTICES, "ordering size outside verifier domain")
    require(all(type(v) is int for v in order), "ordering entries must be integers")
    require(sorted(order) == list(range(m)), "ordering is not a permutation")
    require(all(0 <= i < j < m for i, j in edges), "invalid undirected edge")
    positions = [0] * m
    for rank, vertex in enumerate(order):
        positions[vertex] = rank
    return max((abs(positions[i] - positions[j]) for i, j in edges), default=0)


def ordering_checks():
    count = 0
    edge_count = 0
    for m in range(1, MAX_VERTICES + 1):
        for w in range(1, m + 1):
            edges = graph(m, w)
            target = min(m - 1, 2 * w)
            degrees = [0] * m
            for i, j in edges:
                degrees[i] += 1
                degrees[j] += 1
            require(min(degrees) == target, f"minimum-degree floor: {m},{w}")
            require(bandwidth(folded_order(m), edges) == target,
                    f"folded upper bound: {m},{w}")
            count += 1
            edge_count += len(edges)
    return {"graphs": count, "undirected_edges": edge_count}


def brute_checks():
    """All orders, with no degree bound or folded-order pruning."""
    graphs = 0
    orders = 0
    for m in range(1, MAX_BRUTE_VERTICES + 1):
        for w in range(1, m + 1):
            edges = graph(m, w)
            best = m
            for order in itertools.permutations(range(m)):
                # Independent direct evaluation, without bandwidth().
                labels = dict(zip(order, range(m), strict=True))
                measured = 0
                for i, j in edges:
                    measured = max(measured, abs(labels[i] - labels[j]))
                best = min(best, measured)
                orders += 1
            require(best == min(m - 1, 2 * w), f"exhaustive optimum: {m},{w}")
            graphs += 1
    return {"graphs": graphs, "permutations": orders}


def literal_fill(n, w, killed):
    """Combinatorial vertex elimination on the original circular graph."""
    require(3 <= n <= MAX_CYCLE_VERTICES and 1 <= w <= n // 2,
            "invalid circular graph")
    require(1 <= killed < n, "the eliminated arc must be nonempty and proper")
    adjacent = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            distance = min(abs(i - j), n - abs(i - j))
            adjacent[i][j] = 0 < distance <= w
    for k in range(killed):
        remaining_neighbors = [i for i in range(k + 1, n) if adjacent[k][i]]
        for i in remaining_neighbors:
            for j in remaining_neighbors:
                if i != j:
                    adjacent[i][j] = True
    return tuple(
        (i - killed, j - killed)
        for i in range(killed, n)
        for j in range(i + 1, n)
        if adjacent[i][j]
    )


def support_checks():
    layouts = 0
    for n in range(3, MAX_CYCLE_VERTICES + 1):
        for w in range(1, n // 2 + 1):
            for killed in range(1, n):
                edges = literal_fill(n, w, killed)
                require(edges == graph(n - killed, w),
                        f"circular support identification: {n},{w},{killed}")
                require(bandwidth(folded_order(n - killed), edges)
                        == min(n - killed - 1, 2 * w), "circular ordering")
                layouts += 1
    return {"circular_layouts": layouts}


def controls():
    invalid = ((0, 1), (97, 1), (3, 0), (3, 97), (True, 1), (3, 1.0))
    rejected = 0
    for m, w in invalid:
        try:
            graph(m, w)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid graph domain accepted")
    for order, edges in (((0, 0), ()), ((0, True), ()), ((0, 1), ((1, 0),))):
        try:
            bandwidth(order, edges)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid ordering or edge accepted")
    # Semantic mutants: retaining the path, the old order, or a 2w-1 cap.
    edges = graph(9, 2)
    require(bandwidth(tuple(range(9)), edges) == 8, "old-order control")
    require(bandwidth(folded_order(9), edges) == 4, "changed-order control")
    require(bandwidth(folded_order(9), edges) > 2 * 2 - 1, "sharp constant")
    require(bandwidth(tuple(range(9)), tuple((i, j) for i, j in edges if j-i <= 2))
            == 2, "omitted-fill control")
    # Saturation uses M-1, rather than 2w, when M <= 2w.
    require(bandwidth(folded_order(4), graph(4, 2)) == 3, "saturation control")
    return {"invalid_inputs_rejected": rejected, "semantic_controls": 4}


def receipt():
    package = Path(__file__).resolve().parent
    checks = {
        "ordering": ordering_checks(),
        "exhaustive": brute_checks(),
        "support": support_checks(),
        "controls": controls(),
    }
    names = ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    return {"claim_type": "scoped proof with finite corroboration", "checks": checks,
            "source_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(receipt(), indent=2, sort_keys=True) + "\n"
    if args.write_receipt is not None:
        with args.write_receipt.open("x", encoding="utf-8") as stream:
            written = stream.write(encoded)
            require(written == len(encoded), "short receipt write")
    print(encoded, end="")
    print("PASS_CYCLE_SCHUR_OPTIMAL_ORDER")


if __name__ == "__main__":
    main()
