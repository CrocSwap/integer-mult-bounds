#!/usr/bin/env python3
"""Exact independent check of the B2 edge-count counterexample.

ROTl24, with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only; no predecessor implementation is imported.
"""

from copy import deepcopy
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_binary(rows):
    """Eliminate binary row bitsets without using the block formula."""
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def rank_by_span(rows):
    """Independent small-matrix oracle: enumerate the complete row space."""
    span = {0}
    for row in rows:
        span |= {value ^ row for value in span}
    return len(span).bit_length() - 1


def row_bits(matrix):
    return [sum(value << j for j, value in enumerate(row)) for row in matrix]


def acyclic(vertices, edges):
    remaining = set(vertices)
    while remaining:
        sources = {v for v in remaining
                   if not any(u in remaining and w == v for u, w in edges)}
        if not sources:
            return False
        remaining -= sources
    return True


def acyclic_extrema(n, edges):
    """Exact edge optimum over all topological orders, and vertex optimum.

    An acyclic edge set has a topological order. For any order all forward
    edges can be retained, so maximizing forward edges is exactly masE.
    """
    incoming = [0] * n
    for u, v in edges:
        incoming[v] |= 1 << u
    dp = [0] * (1 << n)
    last = [0] * (1 << n)
    vertex_max = 0
    for mask in range(1, 1 << n):
        vertices = [v for v in range(n) if mask >> v & 1]
        choices = [(dp[mask ^ (1 << v)]
                    + (incoming[v] & (mask ^ (1 << v))).bit_count(), v)
                   for v in vertices]
        dp[mask], last[mask] = max(choices)
        if len(vertices) > vertex_max and acyclic(vertices, edges):
            vertex_max = len(vertices)
    order = []
    mask = (1 << n) - 1
    while mask:
        v = last[mask]
        order.append(v)
        mask ^= 1 << v
    order.reverse()
    positions = {v: i for i, v in enumerate(order)}
    forward = {(u, v) for u, v in edges if positions[u] < positions[v]}
    require(acyclic(range(n), forward), "edge certificate contains a cycle")
    require(len(forward) == dp[-1], "edge certificate size disagrees with DP")
    return dp[-1], vertex_max


def model(p, q, matrix):
    n = len(p)
    require(n > 0 and len(q) == len(matrix) == n, "inconsistent dimensions")
    require(all(len(row) == 3 and all(type(x) is int for x in row)
                for row in p + q), "fixture must have integer triples")
    require(all(len(row) == n and all(type(x) is int and x in (0, 1)
                                     for x in row) for row in matrix),
            "pairing must be a square binary matrix")
    dots = [[sum(a * b for a, b in zip(pt, qs)) for qs in q] for pt in p]
    require(all(dots[t][t] != 0 for t in range(n)), "zero rational diagonal")
    require(all(matrix[t][t] == 1 for t in range(n)), "pairing diagonal is not one")
    require(all(t == s or matrix[t][s] == 0 or dots[t][s] == 0
                for t in range(n) for s in range(n)),
            "pairing uses a nonincidence")
    ps = [{j for j in range(3) if row[j] != 0} for row in p]
    qs = [{j for j in range(3) if row[j] != 0} for row in q]
    harmonic = []
    for t in range(n):
        terms = [p[t][j] * q[t][j] for j in sorted(ps[t] & qs[t])]
        if len(terms) == 2 and terms[0] == terms[1]:
            harmonic.append(t)
    full = [t for t in range(n) if len(ps[t]) == len(qs[t]) == 3]
    wild = {(t, s) for t in range(n) for s in range(n)
            if t != s and dots[t][s] == 0 and len(ps[t] & qs[s]) == 3}
    supported = {(t, s) for t in range(n) for s in range(n)
                 if t != s and matrix[t][s] == 1}
    ranks = []
    for j in range(3):
        columns = [s for s in range(n) if j in qs[s]]
        block = [[matrix[t][s] for s in columns]
                 for t in range(n) if j in ps[t]]
        bits = row_bits(block)
        rank = rank_binary(bits)
        require(rank == rank_by_span(bits), "independent rank oracles disagree")
        ranks.append(rank)
    return harmonic, full, wild, supported, ranks


def audit(p, q, matrix):
    harmonic, full, wild, supported, ranks = model(p, q, matrix)
    n = len(p)
    # The delivered witness deliberately makes these two conventions equal.
    require(wild == supported, "wild pattern differs from pairing support")
    index = {v: i for i, v in enumerate(full)}
    edges = {(index[u], index[v]) for u, v in wild if u in index and v in index}
    edge_max, vertex_max = acyclic_extrema(len(full), edges)
    offset = n - len(harmonic) - len(full)
    cost = sum(ranks)
    return {"v": n, "harmonic_lines": len(harmonic), "full_support_lines": len(full),
            "wild_edges": len(wild), "block_ranks": ranks, "cost": cost,
            "mas_edges": edge_max, "mas_vertices": vertex_max,
            "edge_bound": offset + edge_max, "vertex_bound": offset + vertex_max,
            "edge_gap": offset + edge_max - cost}


def pairing(k):
    return [[int(t == s or t // k != s // k) for s in range(3 * k)]
            for t in range(3 * k)]


def expect_rejection(action, expected_message):
    try:
        action()
    except ValueError as exc:
        require(str(exc) == expected_message, "control failed for the wrong reason")
    else:
        raise ValueError("malformed control was accepted: " + expected_message)


def controls(fixture, expected):
    p, q, matrix = (fixture[key] for key in ("p", "q", "B"))
    bad = deepcopy(matrix)
    bad[0][0] = 0
    expect_rejection(lambda: audit(p, q, bad), "pairing diagonal is not one")
    bad = deepcopy(matrix)
    bad[0][1] = 1
    expect_rejection(lambda: audit(p, q, bad), "pairing uses a nonincidence")
    bad_p = deepcopy(p)
    bad_p[0][0] += 1
    expect_rejection(lambda: audit(bad_p, q, matrix), "pairing uses a nonincidence")
    bad_q = deepcopy(q)
    bad_q[0] = list(q[3])
    expect_rejection(lambda: audit(p, bad_q, matrix), "zero rational diagonal")
    require(not acyclic([0, 1], {(0, 1), (1, 0)}), "2-cycle was accepted")
    require(rank_binary([0b101, 0b110, 0b011]) == 2
            and rank_by_span([0b101, 0b110, 0b011]) == 2,
            "dependent rows were counted as independent")

    # Reindexing must not turn a block-structure assumption into an oracle.
    for order in ([0, 3, 6, 1, 4, 7, 2, 5, 8], list(reversed(range(9)))):
        report = audit([p[i] for i in order], [q[i] for i in order],
                       [[matrix[i][j] for j in order] for i in order])
        require(report == expected, "simultaneous reindexing changed the result")

    prototypes_p, prototypes_q = p[::3], q[::3]
    small = []
    for k in (1, 2):
        report = audit([row for row in prototypes_p for _ in range(k)],
                       [row for row in prototypes_q for _ in range(k)], pairing(k))
        require(report["edge_gap"] <= 0, "positive control became a counterexample")
        require(report["mas_edges"] == 3 * k * k
                and report["mas_vertices"] == k, "small graph oracle mismatch")
        small.append({"k": k, "cost": report["cost"], "mas_edges": report["mas_edges"]})
    require(small == [{"k": 1, "cost": 3, "mas_edges": 3},
                      {"k": 2, "cost": 18, "mas_edges": 12}],
            "tight/nonviolating controls changed")
    return small


def main():
    fixture = json.loads(Path(__file__).with_name("WITNESS.json").read_text(encoding="utf-8"))
    report = audit(fixture["p"], fixture["q"], fixture["B"])
    require(report == fixture["expected"], "witness claim differs from exact calculation")
    require(report["edge_gap"] > 0, "edge bound is not falsified")
    require(report["cost"] >= report["vertex_bound"], "vertex bound is violated")
    small = controls(fixture, report)
    family = []
    for k in range(1, 17):
        rank = rank_binary(row_bits(pairing(k)))
        require(rank == 3 * k - (2 if k % 2 else 0), "family rank formula failed")
        gap = 3 * k * k - 3 * rank
        require((gap > 0) == (k >= 3), "family threshold failed")
        family.append({"k": k, "rank": rank, "edge_gap": gap})
    print(json.dumps({"status": "PASS_B2_TRIPARTITE_EDGE_COUNTEREXAMPLE",
                      "witness": report, "positive_controls": small,
                      "rejection_controls": 4, "graph_and_rank_controls": 2,
                      "reindexings": 2, "family_rank_checks": family}, indent=2))


if __name__ == "__main__":
    main()
