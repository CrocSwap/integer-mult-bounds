#!/usr/bin/env python3
"""Exact jf0 pairing certificate; stdlib only, no solver or source imports.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SOURCE_COMMIT = "113a718265c62aec301c5695f4bfb9c421bef7ab"
SOURCE_SHA256 = "cd8a8c2436e0a025348af0b52ccb48a4f64535b0ff8df32cbe13da73673266b7"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def model(points, lines):
    n = len(points)
    require(n > 0 and len(lines) == n, "model dimensions")
    require(all(len(row) == 3 for row in points + lines), "three coordinates")
    require(all(type(x) is int for row in points + lines for x in row), "integer source coordinates")
    require(all(dot(points[i], lines[i]) != 0 for i in range(n)), "nonzero rational diagonal")
    rows = [[i for i in range(n) if points[i][j] != 0] for j in range(3)]
    cols = [[i for i in range(n) if lines[i][j] != 0] for j in range(3)]
    edges = [(i, k) for i in range(n) for k in range(n)
             if i != k and dot(points[i], lines[k]) == 0]
    relevant = [(i, k) for i, k in edges
                if any(points[i][j] != 0 and lines[k][j] != 0 for j in range(3))]
    return rows, cols, edges, relevant


def binary_rank(matrix):
    """Exact F2 elimination on packed rows, independent of oracle row spans."""
    pivots = {}
    for row in matrix:
        require(all(type(x) is int and x in (0, 1) for x in row), "binary rank input")
        word = sum(x << j for j, x in enumerate(row))
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    return len(pivots)


def lower_bound(points, lines, orders):
    """A unit diagonal plus forced zeros below each order is triangular."""
    rows, cols, _, _ = model(points, lines)
    require(len(orders) == 3, "one lower minor per coordinate")
    forced = []
    for j, order in enumerate(orders):
        require(all(type(i) is int for i in order), "minor index domain")
        require(len(order) == len(set(order)), "distinct minor indices")
        require(set(order) <= set(rows[j]) & set(cols[j]), "minor support")
        for a, i in enumerate(order):
            for k in order[:a]:
                require(dot(points[i], lines[k]) != 0, "forced triangular zero")
        forced.append(len(order) * (len(order) - 1) // 2)
    return [len(order) for order in orders], forced


def witness_ranks(points, lines, matrix):
    rows, cols, edges, _ = model(points, lines)
    n = len(points)
    require(len(matrix) == n and all(len(row) == n for row in matrix), "pairing dimensions")
    require(all(type(x) is int and x in (0, 1) for row in matrix for x in row), "binary pairing")
    require(all(matrix[i][i] == 1 for i in range(n)), "unit pairing diagonal")
    edge_set = set(edges)
    require(all(not matrix[i][k] or (i, k) in edge_set
                for i in range(n) for k in range(n) if i != k), "rational incidence support")
    return [binary_rank([[matrix[i][k] for k in cols[j]] for i in rows[j]])
            for j in range(3)]


def certify(points, lines, orders, matrix):
    rows, cols, edges, relevant = model(points, lines)
    lower, forced = lower_bound(points, lines, orders)
    ranks = witness_ranks(points, lines, matrix)
    require(lower == ranks, "lower and attaining ranks agree")
    return {"status": "PASS_JF0_PAIRING_OPTIMUM", "lines": len(points),
            "coordinate_rows": rows, "coordinate_columns": cols,
            "admissible_offdiagonal_count": len(edges),
            "relevant_offdiagonal_count": len(relevant),
            "pairing_domain_size": 1 << len(edges),
            "lower_minor_orders": orders, "forced_lower_zeros": forced,
            "coordinate_lower_bounds": lower, "attaining_ranks": ranks,
            "attaining_offdiagonal_ones": sum(matrix[i][k] for i in range(len(points))
                                              for k in range(len(points)) if i != k),
            "minimum_pairing_cost": sum(ranks), "no_new_kappa": True}


def check_sources(package):
    manifest = json.loads((package / "PREDECESSOR.json").read_text())
    require(manifest["commit"] == SOURCE_COMMIT and manifest["pull_request"] == 2162,
            "predecessor identity")
    require({r["path"] for r in manifest["files"]} ==
            {"source/jf0.json", "source/NOTICE.md", "source/LICENSE"}, "source inventory")
    require(len(manifest["files"]) == 3, "source inventory uniqueness")
    for row in manifest["files"]:
        data = (package / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
    require(hashlib.sha256((package / "source/jf0.json").read_bytes()).hexdigest()
            == SOURCE_SHA256, "fixed jf0 source binding")


def verify(package=PACKAGE):
    check_sources(package)
    points, lines = json.loads((package / "source/jf0.json").read_text())
    certificate = json.loads((package / "CERTIFICATE.json").read_text())
    witness = json.loads((package / "candidate-witness.json").read_text())
    result = certify(points, lines, certificate["lower_minor_orders"], witness["binary_matrix"])
    require(witness["expected_ranks"] == result["attaining_ranks"], "witness rank claim")
    require(result == json.loads((package / "RESULT.json").read_text()), "fixed result receipt")
    return result


if __name__ == "__main__":
    result = verify()
    print(result["status"], "cost=19 ranks=6,6,7 all_pairings=2^41 no_new_kappa")
