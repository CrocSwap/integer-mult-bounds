#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense binary matrices, integer trace elimination and exact cost layers.

Authentication is shared with verify.py. Scientific computations below do
not call its rank, trace, case-generation, reachability or fit routines.
"""

import gzip
import importlib.util
import itertools
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "c5_verify", Path(__file__).with_name("verify.py")
)
if SPEC is None or SPEC.loader is None:
    raise ImportError("fixed verifier module is unavailable")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def binary_rank(matrix):
    rows = [list(row) for row in matrix]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def pair_rank(left, right):
    return binary_rank(
        [
            [sum(x * y for x, y in zip(a, b, strict=True)) % 2 for b in right]
            for a in left
        ]
    )


def trace_consistent(a, b, hits, target, weights, blocks):
    equations = [
        [int(i == j) for j in range(5)] + [0]
        for i in range(5)
        if i not in a.intersection(b)
    ]
    equations += [
        [int(j in block) for j in range(5)] + [hits[k]]
        for k, block in enumerate(blocks)
        if weights[k] > 0 and target[k] == 2 * len(block)
    ]
    pivot = 0
    for col in range(5):
        found = next(
            (i for i in range(pivot, len(equations)) if equations[i][col]), None
        )
        if found is None:
            continue
        equations[pivot], equations[found] = equations[found], equations[pivot]
        for i in range(pivot + 1, len(equations)):
            p, q = equations[pivot][col], equations[i][col]
            equations[i] = [
                p * x - q * y
                for x, y in zip(equations[i], equations[pivot], strict=True)
            ]
        pivot += 1
    return all(any(row[:5]) or row[5] == 0 for row in equations)


def layer_count(rows, weights, target, defect, limit, blocks):
    allowed = set()
    for a, b, cost, hits, slack in rows:
        if (
            cost
            and slack <= defect
            and trace_consistent(a, b, hits, target, weights, blocks)
        ):
            allowed.add((cost, hits, slack))
    layers = [set() for _ in range(limit + 1)]
    layers[0].add((0,) * 11)
    for paid in range(limit + 1):
        for state in sorted(layers[paid]):
            for price, hits, slack in allowed:
                if paid + price > limit:
                    continue
                counts = tuple(
                    state[k] + hits[k]
                    if weights[k]
                    else min(2 * len(blocks[k]), state[k] + hits[k])
                    for k in range(10)
                )
                counts += (state[10] + slack,)
                if counts[10] <= defect and all(
                    not weights[k] or counts[k] <= target[k] for k in range(10)
                ):
                    layers[paid + price].add(counts)
    require(target + (defect,) not in layers[limit], "sub20 cost layer unreachable")
    return len(allowed), sum(len(layer) for layer in layers)


def dense_records(local, weights, masks, blocks):
    bases = [tuple(q for i in mask for q in local[i]) for mask in masks]
    rows = []
    for i, a in enumerate(masks):
        for j, b in enumerate(masks):
            price = pair_rank(bases[i], bases[j])
            hits = tuple(int(bool(a & h) and bool(b & h)) for h in blocks)
            slack = 6 * price - sum(w * h for w, h in zip(weights, hits, strict=True))
            require(slack >= 0 and (price or not any(hits)), "exact tariff inequality")
            rows.append((a, b, price, hits, slack))
    return rows


def check_core(expected, planes, masks, blocks):
    total_cases = total_states = 0
    local = [planes[i] for i in expected["cycle"]]
    weights = expected["weights"]
    rows = dense_records(local, weights, masks, blocks)
    require(
        verify.digest([r[2] for r in rows]) == expected["tariff_sha256"],
        "dense tariffs",
    )
    rhs = sum(w * 2 * len(h) for w, h in zip(weights, blocks, strict=True))
    require(rhs == expected["weighted_rank_sum"], "weighted forced rank")
    costs = list(range((rhs + 5) // 6, 20))
    require(costs == [c["cost"] for c in expected["checks"]], "all integer sub20 costs")
    for cost, group in zip(costs, expected["checks"], strict=True):
        budget = 6 * cost - rhs
        ranges = [range(budget // w + 1) if w else range(1) for w in weights]
        targets = [
            (
                tuple(2 * len(h) + e for h, e in zip(blocks, excess, strict=True)),
                budget - sum(w * e for w, e in zip(weights, excess, strict=True)),
            )
            for excess in itertools.product(*ranges)
            if sum(w * e for w, e in zip(weights, excess, strict=True)) <= budget
        ]
        require(len(targets) == len(group["cases"]), "complete excess inventory")
        for (target, defect), case in zip(targets, group["cases"], strict=True):
            require(
                list(target) == case["target"] and defect == case["defect"],
                "case equality",
            )
            profiles, states = layer_count(rows, weights, target, defect, cost, blocks)
            require(
                profiles == case["profiles"] and states == case["states"],
                "independent counts",
            )
            total_cases += 1
            total_states += states
    # Independent upper bound uses ten singleton scalar terms.
    require(
        sum(pair_rank((q,), (q,)) for p in local for q in p) == 10,
        "scalar labels are odd",
    )
    require(
        sum(pair_rank(p, p) for p in local) == 10, "complete-plane singleton tariff"
    )
    require(
        sum(expected["attaining_costs"]) == 20,
        "ten scalar singleton terms cost20",
    )
    return total_cases, total_states


def check():
    raw = verify.sources()
    recipes = json.loads(gzip.decompress(raw["DATA-PHASES.json.gz"]))["recipes"]
    labels = {r["port"]: tuple((r["q"] >> i) & 1 for i in range(9)) for r in recipes}
    planes = [
        tuple(labels[p] for p in pair)
        for pair in json.loads(raw["MATCHING.json"])["matching"]
    ]
    result = json.loads((HERE / "RESULT.json").read_bytes())
    masks = [frozenset(i for i in range(5) if mask & (1 << i)) for mask in range(32)]
    blocks = [frozenset(i for i in range(5) if h & (1 << i)) for h in result["blocks"]]
    require(
        result["blocks"] == [1, 2, 4, 8, 16, 5, 9, 10, 18, 20], "forced block inventory"
    )
    total_cases = total_states = 0
    for expected in result["cores"]:
        count, states = check_core(expected, planes, masks, blocks)
        total_cases += count
        total_states += states
    return total_cases, total_states


if __name__ == "__main__":
    cases, states = check()
    print(f"PASS_C5_RESIDUAL_INDEPENDENT cases={cases} states={states}")
