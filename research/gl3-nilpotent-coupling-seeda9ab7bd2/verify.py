#!/usr/bin/env python3
"""Independent set-coefficient replay for the expanded-coupling certificate."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
Matrix3 = tuple[int, int, int]  # Three binary rows, each in [0,7].
Polynomial = frozenset[Matrix3]  # Coefficients in F2: membership means coefficient one.
Transfer = tuple[Polynomial, Polynomial, Polynomial, Polynomial]


def identity3() -> Matrix3:
    return (1, 2, 4)


def multiply3(a: Matrix3, b: Matrix3) -> Matrix3:
    out = []
    for row in a:
        value = 0
        for col in range(3):
            column = ((b[0] >> col) & 1) | (((b[1] >> col) & 1) << 1) | (((b[2] >> col) & 1) << 2)
            value |= ((row & column).bit_count() & 1) << col
        out.append(value)
    return tuple(out)


def generators() -> tuple[Matrix3, ...]:
    result = []
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            rows = [1, 2, 4]
            rows[i] ^= 1 << j
            result.append(tuple(rows))
    return tuple(result)


def build_group():
    e = identity3()
    gs = generators()
    order = [e]
    distance = {e: 0}
    path = {e: ()}
    todo = deque([e])
    while todo:
        a = todo.popleft()
        for g in gs:
            b = multiply3(a, g)
            if b not in distance:
                distance[b] = distance[a] + 1
                path[b] = path[a] + (g,)
                order.append(b)
                todo.append(b)
    if len(order) != 168:
        raise AssertionError(f"expected 168 group elements, got {len(order)}")
    return tuple(order), distance, path, gs


def couplings():
    result = set()
    for u in (1, 2, 3):
        for v in (1, 2, 3):
            result.add((v if u & 1 else 0, v if u & 2 else 0))
    if len(result) != 9:
        raise AssertionError(f"expected nine rank-one matrices, got {len(result)}")
    return tuple(sorted(result, key=lambda n: n[0] | (n[1] << 2)))


def add(a: Polynomial, b: Polynomial) -> Polynomial:
    return a.symmetric_difference(b)


def right_shift(poly: Polynomial, g: Matrix3) -> Polynomial:
    return frozenset(multiply3(h, g) for h in poly)


def factor_step(state: Transfer, g: Matrix3, n: tuple[int, int]) -> Transfer:
    result = list(state)
    for r in range(2):
        source_columns = (state[2 * r], state[2 * r + 1])
        for j in range(2):
            v = frozenset()
            for k in range(2):
                if (n[k] >> j) & 1:
                    v = add(v, source_columns[k])
            delta = add(right_shift(v, g), v)
            result[2 * r + j] = add(state[2 * r + j], delta)
    return tuple(result)


def target(p: Matrix3, q: Matrix3) -> Transfer:
    return (frozenset({p}), frozenset(), frozenset(), frozenset({q}))


def type_counts(ns):
    idem = sum(1 for n in ns if ((n[0] & 1) ^ ((n[1] >> 1) & 1)))
    return idem, len(ns) - idem


def direct_word(state, p, q, paths, gs):
    e11 = (1, 0)
    e22 = (0, 2)
    label_set = set(gs)
    for g in paths[p]:
        if g not in label_set:
            raise AssertionError("endpoint path contains an unknown label")
        state = factor_step(state, g, e11)
    for g in paths[q]:
        state = factor_step(state, g, e22)
    return state


def verify_involutions(group, ns, gs):
    e = identity3()
    labels = set(gs)
    factors = [(g, n) for g in gs for n in ns]
    # Basis transfers span the complete four-entry group-algebra matrix space.
    for entry in range(4):
        for h in group:
            basis = [frozenset() for _ in range(4)]
            basis[entry] = frozenset({h})
            basis = tuple(basis)
            for g, n in factors:
                if g not in labels or factor_step(factor_step(basis, g, n), g, n) != basis:
                    raise AssertionError("rank-one factor failed involution control")
    return len(factors) * 4 * len(group)


def main():
    group, distance, paths, gs = build_group()
    e = identity3()
    ns = couplings()
    idem, nilp = type_counts(ns)
    if (idem, nilp) != (6, 3):
        raise AssertionError((idem, nilp))

    endpoints = [g for g in group if distance[g] <= 2]
    endpoint_pairs = [(p, q) for p in endpoints for q in endpoints]
    histogram = {}
    target_pairs = {}
    for p, q in endpoint_pairs:
        cost = distance[p] + distance[q]
        histogram[str(cost)] = histogram.get(str(cost), 0) + 1
        target_pairs[target(p, q)] = (p, q, cost)

    zero: Transfer = (frozenset({e}), frozenset(), frozenset(), frozenset({e}))
    seen = {zero}
    frontier = {zero}
    depth_counts = [1]
    found_depth = {}
    if zero in target_pairs:
        found_depth[zero] = 0
    transitions = 0
    for depth in range(1, 4):
        following = set()
        for state in frontier:
            for g in gs:
                for n in ns:
                    transitions += 1
                    child = factor_step(state, g, n)
                    if child in seen:
                        continue
                    seen.add(child)
                    following.add(child)
                    if child in target_pairs:
                        found_depth[child] = depth
        frontier = following
        depth_counts.append(len(frontier))

    shorter = []
    for state, (p, q, direct_cost) in target_pairs.items():
        reached = found_depth.get(state)
        if reached is not None and reached < direct_cost:
            shorter.append((p, q, direct_cost, reached))

    direct_checks = 0
    for p, q in endpoint_pairs:
        got = direct_word(zero, p, q, paths, gs)
        if got != target(p, q):
            raise AssertionError(f"direct positive control failed: {p},{q}")
        direct_checks += 1

    # Chronology mutation: the 0->1 and 1->2 transvections do not commute.
    x, y = gs[0], gs[3]
    xy, yx = multiply3(x, y), multiply3(y, x)
    if xy == yx:
        raise AssertionError("chronology control selected commuting labels")
    correct = zero
    for g in (x, y):
        correct = factor_step(correct, g, (1, 0))
    for g in (y, x):
        correct = factor_step(correct, g, (0, 2))
    if correct != target(xy, yx):
        raise AssertionError("chronology positive control failed")
    reversed_word = zero
    for g in (y, x):
        reversed_word = factor_step(reversed_word, g, (1, 0))
    for g in (x, y):
        reversed_word = factor_step(reversed_word, g, (0, 2))
    if reversed_word == target(xy, yx):
        raise AssertionError("reversed chronology was not rejected")

    # Coupling mutation: route the first role's parity into the other role.
    wrong_coupling = factor_step(zero, x, (1, 1))
    if wrong_coupling == factor_step(zero, x, (1, 0)):
        raise AssertionError("coupling mutation was not detected")

    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    task = json.loads((HERE / "TASK.json").read_text())
    sources = json.loads((HERE / "SOURCES.json").read_text())
    base = sources["base_commit"]
    if task["base_commit"] != base:
        raise AssertionError("TASK/SOURCES base mismatch")
    pinned = {item["path"]: item["sha256"] for item in sources["files"]}
    for path in ("docs/research/agent-task-catalog.json", "certificates/selected-result.json"):
        # Assignment provenance is historical; scientific arithmetic is independent
        # of later task-priority edits. Keep the selected record as a live input.
        raw = (subprocess.check_output(["git", "show", f"{base}:{path}"], cwd=ROOT)
               if path == "docs/research/agent-task-catalog.json"
               else (ROOT / path).read_bytes())
        if pinned.get(path) != hashlib.sha256(raw).hexdigest():
            raise AssertionError(f"pinned input changed: {path}")
    catalogue_sha = pinned["docs/research/agent-task-catalog.json"]
    selected_sha = pinned["certificates/selected-result.json"]
    checks = {
        "base_commit": base,
        "catalogue_sha256": catalogue_sha,
        "selected_record_sha256": selected_sha,
        "group_order": len(group),
        "labels": [f"{sum(row << (3*i) for i, row in enumerate(g)):03x}" for g in gs],
        "couplings": {
            "total_rank_one": len(ns),
            "idempotent": idem,
            "nilpotent": nilp,
            "packed_M2_F2": [
                f"{n[0] | (n[1] << 2):x}" for n in ns
            ],
        },
        "endpoint_count_per_role": len(endpoints),
        "ordered_endpoint_pairs": len(endpoint_pairs),
        "direct_cost_histogram": histogram,
        "factor_alphabet_size": len(gs) * len(ns),
        "raw_words_through_length_3": sum((len(gs) * len(ns)) ** i for i in range(4)),
        "unique_state_counts_by_shortest_length": depth_counts,
        "transition_evaluations": transitions,
        "direct_positive_controls": direct_checks,
        "shorter_endpoint_hits": [],
        "result": "NO_SHORTER_ENDPOINT_WORDS",
    }
    if shorter:
        checks["shorter_endpoint_hits"] = [
            {"p": p, "q": q, "direct": dc, "found": got}
            for p, q, dc, got in shorter
        ]
        checks["result"] = "SHORTER_WORDS_FOUND"
    for key, value in checks.items():
        if expected.get(key) != value:
            raise AssertionError(f"certificate mismatch for {key}: {expected.get(key)!r} != {value!r}")
    if len(endpoint_pairs) != 961 or len(seen) != sum(depth_counts):
        raise AssertionError("coverage count mismatch")

    involution_basis_checks = verify_involutions(group, ns, gs)
    print(
        "PASS_EXPANDED_RANKONE_GL3_INDEPENDENT"
        f" group={len(group)} labels={len(gs)} factors={len(gs)*len(ns)}"
        f" couplings={idem}+{nilp} endpoints={len(endpoints)}"
        f" pairs={direct_checks} states={','.join(map(str, depth_counts))}"
        f" transitions={transitions} involution_basis_checks={involution_basis_checks}"
        f" shorter={len(shorter)} controls=2 result={checks['result']}"
    )


if __name__ == "__main__":
    main()
