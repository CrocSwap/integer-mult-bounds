#!/usr/bin/env python3
"""Exact radius-three search for rank-one couplings in GL3(F2)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import argparse
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def mul3(a: int, b: int) -> int:
    """Multiply packed 3x3 binary matrices; row r occupies bits 3r..3r+2."""
    out = 0
    for i in range(3):
        row = (a >> (3 * i)) & 7
        for j in range(3):
            col = ((b >> j) & 1) | (((b >> (3 + j)) & 1) << 1) | (((b >> (6 + j)) & 1) << 2)
            if (row & col).bit_count() & 1:
                out |= 1 << (3 * i + j)
    return out


def cnot_generators() -> tuple[int, ...]:
    eye = sum(1 << (4 * i) for i in range(3))
    return tuple(eye ^ (1 << (3 * i + j)) for i in range(3) for j in range(3) if i != j)


def address_group():
    eye = sum(1 << (4 * i) for i in range(3))
    gens = cnot_generators()
    order = [eye]
    distance = {eye: 0}
    words = {eye: ()}
    todo = deque([eye])
    while todo:
        a = todo.popleft()
        for g in gens:
            b = mul3(a, g)
            if b not in distance:
                distance[b] = distance[a] + 1
                words[b] = words[a] + (g,)
                order.append(b)
                todo.append(b)
    if len(order) != 168:
        raise AssertionError(f"GL3(F2) order: {len(order)}")
    index = {g: i for i, g in enumerate(order)}
    return order, index, distance, words, gens


def rank_one_couplings():
    out = set()
    for u in range(1, 4):
        for v in range(1, 4):
            n = 0
            for i in range(2):
                for j in range(2):
                    if ((u >> i) & 1) and ((v >> j) & 1):
                        n |= 1 << (2 * i + j)
            out.add(n)
    if len(out) != 9:
        raise AssertionError(f"rank-one coupling count: {len(out)}")
    return tuple(sorted(out))


def right_permutations(group, index):
    return tuple(tuple(index[mul3(h, g)] for h in group) for g in cnot_generators())


def permute(bits: int, permutation: tuple[int, ...]) -> int:
    out = 0
    while bits:
        low = bits & -bits
        out |= 1 << permutation[low.bit_length() - 1]
        bits ^= low
    return out


def step(state, label_index: int, n: int, permutations):
    p = permutations[label_index]
    out = list(state)
    for row in range(2):
        a, b = state[2 * row], state[2 * row + 1]
        for col in range(2):
            source = 0
            if (n >> col) & 1:  # N[0,col]
                source ^= a
            if (n >> (2 + col)) & 1:  # N[1,col]
                source ^= b
            out[2 * row + col] ^= permute(source, p) ^ source
    return tuple(out)


def target_state(p: int, q: int, index):
    out = [0, 0, 0, 0]
    out[0] = 1 << index[p]
    out[3] = 1 << index[q]
    return tuple(out)


def rank_one_type_counts(couplings):
    idempotents = sum(1 for n in couplings if (n & 1) ^ ((n >> 3) & 1))
    return idempotents, len(couplings) - idempotents


def reconstruct(state, parents, factors):
    word = []
    while state in parents:
        state, fidx = parents[state]
        word.append(factors[fidx])
    word.reverse()
    return word


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="recompute and compare without rewriting the certificate")
    args = ap.parse_args()

    group, index, distance, words, generators = address_group()
    eye = group[0]
    couplings = rank_one_couplings()
    idempotents, nilpotents = rank_one_type_counts(couplings)
    if (idempotents, nilpotents) != (6, 3):
        raise AssertionError((idempotents, nilpotents))

    perm_by_label = right_permutations(group, index)
    label_index = {g: i for i, g in enumerate(generators)}
    factors = tuple((label_index[g], n) for g in generators for n in couplings)
    identity = (1 << index[eye], 0, 0, 1 << index[eye])

    endpoints = [g for g in group if distance[g] <= 2]
    pairs = [(p, q) for p in endpoints for q in endpoints]
    direct = {(p, q): distance[p] + distance[q] for p, q in pairs}
    targets = {target_state(p, q, index): (p, q) for p, q in pairs}

    seen = {identity}
    frontier = {identity}
    parents = {}
    first_depth = {identity: 0}
    transitions = 0
    states_at_depth = [1]
    for depth in range(1, 4):
        following = set()
        for state in frontier:
            for fidx, (li, n) in enumerate(factors):
                transitions += 1
                child = step(state, li, n, perm_by_label)
                if child in seen:
                    continue
                seen.add(child)
                first_depth[child] = depth
                parents[child] = (state, fidx)
                following.add(child)
        frontier = following
        states_at_depth.append(len(frontier))

    hits = []
    for state, (p, q) in targets.items():
        d = direct[(p, q)]
        got = first_depth.get(state)
        if got is not None and got < d:
            word = reconstruct(state, parents, factors)
            hits.append({
                "p": f"{p:03x}", "q": f"{q:03x}", "direct": d,
                "found": got,
                "word": [[f"{generators[li]:03x}", f"{n:x}"] for li, n in word],
            })

    direct_checks = 0
    e11 = 1  # [[1,0],[0,0]]
    e22 = 8  # [[0,0],[0,1]]
    for p, q in pairs:
        state = identity
        for g in words[p]:
            state = step(state, label_index[g], e11, perm_by_label)
        for g in words[q]:
            state = step(state, label_index[g], e22, perm_by_label)
        if state != target_state(p, q, index):
            raise AssertionError(f"direct positive control failed for {(p, q)}")
        direct_checks += 1

    histogram = {}
    for d in direct.values():
        histogram[str(d)] = histogram.get(str(d), 0) + 1

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
    cert = {
        "schema": 1,
        "seed": "a9ab7bd2bdc2d83089d7ee5ca0948454",
        "base_commit": base,
        "catalogue_sha256": catalogue_sha,
        "selected_record_sha256": selected_sha,
        "group": "GL3(F2)",
        "group_order": len(group),
        "labels": [f"{g:03x}" for g in generators],
        "register_roles": 2,
        "register_state_scope": "arbitrary dirty inputs; exact diagonal endpoints",
        "couplings": {
            "total_rank_one": len(couplings),
            "idempotent": idempotents,
            "nilpotent": nilpotents,
            "packed_M2_F2": [f"{n:x}" for n in couplings],
        },
        "endpoint_radius_per_role": 2,
        "endpoint_count_per_role": len(endpoints),
        "ordered_endpoint_pairs": len(pairs),
        "direct_cost_histogram": histogram,
        "factor_alphabet_size": len(factors),
        "raw_words_through_length_3": sum(len(factors) ** i for i in range(4)),
        "unique_state_counts_by_shortest_length": states_at_depth,
        "transition_evaluations": transitions,
        "direct_positive_controls": direct_checks,
        "shorter_endpoint_hits": hits,
        "result": "NO_SHORTER_ENDPOINT_WORDS" if not hits else "SHORTER_WORDS_FOUND",
    }
    encoded = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    if args.check:
        if (HERE / "CERTIFICATE.json").read_text() != encoded:
            raise AssertionError("recomputed certificate differs from committed CERTIFICATE.json")
    else:
        (HERE / "CERTIFICATE.json").write_text(encoded)
    print(
        "PASS_EXPANDED_RANKONE_GL3"
        f" group={len(group)} labels={len(generators)} factors={len(factors)}"
        f" couplings={idempotents}+{nilpotents} endpoints={len(endpoints)}"
        f" pairs={len(pairs)} direct={direct_checks}"
        f" states={','.join(map(str, states_at_depth))}"
        f" transitions={transitions} shorter={len(hits)} result={cert['result']}"
    )


if __name__ == "__main__":
    main()
