#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Enumerate reverse-positive cleanup maps for every shortest R420 quad4 word.

The copied PR1058 certificate fixes six ordered registers and a nonnegative
integer target.  This script enumerates every shortest in-place positive ADD
factorization of that target, then reports the exact cleanup amplification
envelope.  It does not make a kappa claim.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"


def read_json(name):
    return json.loads((SOURCES / name).read_text())


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add_matrix(left, right):
    n = len(left)
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def gate_matrix(n, dst, src):
    rows = [list(row) for row in identity(n)]
    rows[dst][src] += 1
    return tuple(tuple(row) for row in rows)


def apply_word(n, operations):
    matrix = identity(n)
    for dst, src in operations:
        matrix = add_matrix(gate_matrix(n, dst, src), matrix)
    return matrix


def row_sums(matrix):
    return tuple(map(sum, matrix))


def inverse_integer(matrix):
    """Exact Gauss-Jordan inverse; reject nonintegral inverses."""
    from fractions import Fraction
    n = len(matrix)
    work = [[Fraction(x) for x in matrix[i]] +
            [Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if work[r][col]), None)
        if pivot is None:
            raise ValueError("singular target")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [x / scale for x in work[col]]
        for r in range(n):
            if r == col:
                continue
            scale = work[r][col]
            work[r] = [x - scale * y for x, y in zip(work[r], work[col])]
    inverse = [row[n:] for row in work]
    if any(x.denominator != 1 for row in inverse for x in row):
        raise ValueError("target inverse is not integral")
    return tuple(tuple(int(abs(x)) for x in row) for row in inverse)


def main():
    source_manifest = json.loads((HERE / "SOURCES.json").read_text())
    if source_manifest["base_commit"] != "1b59b624d21924f8e3537cdc1ac52d3be6eda2fe":
        raise SystemExit("base commit pin changed")
    for relative, pin in source_manifest["files"].items():
        data = (HERE / relative).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != pin["sha256"]:
            raise SystemExit(f"source pin mismatch: {relative}")
    pin = read_json("PR1058-CIRCUIT.json")
    expected = read_json("PR1058-EXPECTED.json")
    source_ops = tuple(tuple(x) for x in pin["operations"])
    n = len(pin["registers"])
    target = apply_word(n, source_ops)
    if [list(row) for row in target] != expected["local"]["forward_integer_matrix"]:
        raise SystemExit("source replay does not match PR1058 forward matrix")
    want_len = expected["local"]["optimality"]["minimum_additions"]
    ident = identity(n)
    dag_edges = 0
    distance_values = {}

    @lru_cache(None)
    def distance(matrix):
        nonlocal dag_edges
        if matrix == ident:
            distance_values[matrix] = 0
            return 0
        best = None
        for dst in range(n):
            for src in range(n):
                if src == dst:
                    continue
                row = tuple(a - b for a, b in zip(matrix[dst], matrix[src]))
                if row[dst] < 1 or min(row) < 0:
                    continue
                dag_edges += 1
                child = list(matrix)
                child[dst] = row
                cost = distance(tuple(child))
                if cost is not None and (best is None or cost + 1 < best):
                    best = cost + 1
        distance_values[matrix] = best
        return best

    if distance(target) != want_len:
        raise SystemExit("shortest distance disagrees with pinned PR1058 certificate")
    dag_histogram = Counter("unreachable" if value is None else str(value)
                            for value in distance_values.values())
    dag_digest = hashlib.sha256()
    for matrix, value in sorted(distance_values.items()):
        dag_digest.update((json.dumps([matrix, value], separators=(",", ":")) + "\n").encode())
    pinned_dag = expected["local"]["optimality"]
    if (len(distance_values) != pinned_dag["states"] or
            dag_edges != pinned_dag["edges"] or
            dict(sorted(dag_histogram.items())) != pinned_dag["distance_histogram"] or
            dag_digest.hexdigest() != pinned_dag["state_distance_sha256"]):
        raise SystemExit("recomputed inverse DAG disagrees with pinned PR1058 digest/counts")

    path_count = 0
    cleanup_maps = set()
    witnesses = []

    def enumerate_shortest(matrix, path, cleanup):
        nonlocal path_count
        if matrix == ident:
            path_count += 1
            forward_word = tuple(reversed(path))
            if apply_word(n, forward_word) != target:
                raise SystemExit("enumerated shortest word failed forward target replay")
            if apply_word(n, tuple(path)) != cleanup:
                raise SystemExit("enumerated cleanup word failed exact matrix replay")
            cleanup_maps.add(cleanup)
            witnesses.append((cleanup, tuple(path)))
            return
        depth = distance(matrix)
        for dst in range(n):
            for src in range(n):
                if src == dst:
                    continue
                row = tuple(a - b for a, b in zip(matrix[dst], matrix[src]))
                if row[dst] < 1 or min(row) < 0:
                    continue
                child = list(matrix)
                child[dst] = row
                child = tuple(child)
                if distance(child) == depth - 1:
                    # Along target-to-identity inverse steps, each selected
                    # positive ADD is the next operation of the cleanup word.
                    next_cleanup = add_matrix(gate_matrix(n, dst, src), cleanup)
                    path.append((dst, src))
                    enumerate_shortest(child, path, next_cleanup)
                    path.pop()

    enumerate_shortest(target, [], ident)
    if path_count != 1768:
        raise SystemExit(f"shortest path count changed: {path_count}, expected 1768")

    old_cleanup = apply_word(n, tuple(reversed(source_ops)))
    pinned_cleanup = tuple(tuple(row) for row in expected["local"]["after_reverse_positive_matrix"])
    if old_cleanup != pinned_cleanup:
        raise SystemExit("existing word cleanup replay disagrees with pinned certificate")
    if old_cleanup not in cleanup_maps:
        raise SystemExit("existing word absent from shortest-path enumeration")

    row_vectors = {q: row_sums(q) for q in cleanup_maps}
    max_hist = Counter(str(max(v)) for v in row_vectors.values())
    abs_inv = inverse_integer(target)
    if any(any(abs_inv[i][j] > q[i][j] for i in range(n) for j in range(n))
           for q in cleanup_maps):
        raise SystemExit("triangle-inequality lower bound violated")
    rotation = 16 % n
    order = tuple((rotation + i) % n for i in range(n))
    best_q = min(cleanup_maps,
                 key=lambda q: (max(row_sums(q)),
                                tuple(row_sums(q)[i] for i in order),
                                tuple(x for row in q for x in row)))
    best_rows = row_sums(best_q)

    envelope = []
    for q in sorted(cleanup_maps,
                    key=lambda q: (max(row_sums(q)), row_sums(q),
                                   tuple(x for row in q for x in row))):
        representative_path = next(path for candidate, path in witnesses if candidate == q)
        envelope.append({
            "paths_with_this_matrix": sum(candidate == q for candidate, _ in witnesses),
            "cleanup_matrix": [list(row) for row in q],
            "row_sums": list(row_sums(q)),
            "maximum_row_sum": max(row_sums(q)),
            "representative_forward_add_word": [list(edge) for edge in reversed(representative_path)],
        })

    # Strictly detect two malformed source words as negative controls.
    dropped_gate_matches = apply_word(n, source_ops[:-1]) == target
    wrong = list(source_ops)
    d, s = wrong[0]
    wrong[0] = (d, (s + 1) % n if (s + 1) % n != d else (s + 2) % n)
    wrong_source_matches = apply_word(n, tuple(wrong)) == target
    if dropped_gate_matches or wrong_source_matches:
        raise SystemExit("negative control unexpectedly matched target")

    result = {
        "status": "PASS_R420_QUAD4_SHORTEST_CLEANUP_ENUMERATION",
        "scope": "All shortest positive ADD factorizations of the pinned six-register target; no claim over longer words, native frame edits, or kappa.",
        "assignment_seed": 16,
        "base_commit": "1b59b624d21924f8e3537cdc1ac52d3be6eda2fe",
        "source_pr": 1058,
        "source_head": "d148d200f2d64c90504fa3a9608e455aaa4c0c21",
        "source_pins_validated": len(source_manifest["files"]),
        "domain": "Six ordered registers; dst += src for distinct registers; exact nonnegative integer matrices; no auxiliary registers, permutations, or subtraction.",
        "minimum_adds": want_len,
        "inverse_DAG": {
            "states": len(distance_values),
            "legal_edges": dag_edges,
            "distance_histogram": dict(sorted(dag_histogram.items(), key=lambda item: (item[0] == "unreachable", int(item[0]) if item[0] != "unreachable" else 0))),
            "state_distance_sha256": dag_digest.hexdigest(),
        },
        "shortest_paths_enumerated": path_count,
        "distinct_cleanup_matrices": len(cleanup_maps),
        "distinct_row_sum_vectors": len(set(row_vectors.values())),
        "exact_cleanup_envelope": envelope,
        "maximum_row_sum_histogram": dict(sorted(max_hist.items(), key=lambda item: int(item[0]))),
        "existing_word": {
            "cleanup_matrix": [list(row) for row in old_cleanup],
            "row_sums": list(row_sums(old_cleanup)),
            "maximum_row_sum": max(row_sums(old_cleanup)),
        },
        "best_shortest_word": {
            "inverse_DAG_edge_order": [list(edge) for edge in next(path for q, path in witnesses if q == best_q)],
            "forward_add_word": [list(edge) for edge in reversed(next(path for q, path in witnesses if q == best_q))],
            "cleanup_matrix": [list(row) for row in best_q],
            "row_sums": list(best_rows),
            "maximum_row_sum": max(best_rows),
            "tie_break_register_order_seed16": list(order),
        },
        "entrywise_lower_bound_abs_inverse": [list(row) for row in abs_inv],
        "lower_bound_maximum_row_sum": max(row_sums(abs_inv)),
        "negative_controls": {
            "drop_last_source_gate_reaches_target": dropped_gate_matches,
            "change_first_source_reaches_target": wrong_source_matches,
        },
        "coverage_note": "Each optimal factorization is represented once by its inverse-subtraction path; the DAG distance strictly decreases at every enumerated edge. The pinned PR certificate independently fixes minimum length 11 and its complete 165828-state, 917020-edge DAG.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
