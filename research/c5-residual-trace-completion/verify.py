#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact rank/trace completion of the four PR3268/3271 residual C5s."""

import gzip
import hashlib
import io
import itertools
import json
from collections import deque
from fractions import Fraction
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/c5-dyadic-decoder-gate/inputs/"
BLOCKS = (1, 2, 4, 8, 16, 5, 9, 10, 18, 20)
RANKS = tuple(2 * h.bit_count() for h in BLOCKS)
# Integer weights; denominator six. Discovery LPs are not replay dependencies.
CORES = (
    ((3, 10, 4, 6, 13), (4, 8, 2, 4, 6, 4, 2, 4, 0, 6)),
    ((3, 10, 12, 23, 13), (4, 6, 2, 4, 4, 4, 2, 4, 2, 6)),
    ((6, 13, 23, 54, 26), (6, 3, 3, 3, 3, 3, 3, 3, 6, 3)),
    ((14, 24, 47, 18, 55), (2, 8, 4, 6, 4, 4, 6, 0, 4, 2)),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def sources(root=ROOT, inventory=None):
    path = HERE / "SOURCES.json" if inventory is None else inventory
    need(path.stat().st_size <= 16000, "bounded inventory")
    rows = json.loads(path.read_bytes())["files"]
    expected = {
        "certificates/selected-result.json": "provenance",
        "docs/research/agent-task-catalog.json": "provenance",
        INPUT + "DATA-PHASES.json.gz": "input",
        INPUT + "MATCHING.json": "input",
    }
    need(isinstance(rows, list) and len(rows) == 4, "exact four rows")
    need(
        all(
            isinstance(r, dict) and set(r) == {"path", "usage", "git_blob", "sha256"}
            for r in rows
        ),
        "source row schema",
    )
    need(
        len({r["path"] for r in rows}) == 4
        and {r["path"]: r["usage"] for r in rows} == expected,
        "fixed paths and usages",
    )
    raw = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        source = root / row["path"]
        need(
            source.is_file()
            and not source.is_symlink()
            and source.resolve().is_relative_to(root.resolve())
            and source.stat().st_size <= 2000000,
            "bounded regular live source",
        )
        value = source.read_bytes()
        need(hashlib.sha256(value).hexdigest() == row["sha256"], "source SHA256")
        need(
            hashlib.sha1(f"blob {len(value)}\0".encode() + value).hexdigest()
            == row["git_blob"],
            "source Git blob",
        )
        raw[source.name] = value
    return raw


def geometry(root=ROOT, inventory=None):
    raw = sources(root, inventory)
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        payload = stream.read(2000001)
    need(len(payload) <= 2000000, "bounded decompression")
    recipes = json.loads(payload)["recipes"]
    need(isinstance(recipes, list) and len(recipes) == 112, "112 ports")
    labels = {r["port"]: r["q"] for r in recipes}
    need(
        sorted(labels) == list(range(112))
        and all(type(q) is int and 0 < q < 512 for q in labels.values()),
        "label domain",
    )
    matching = json.loads(raw["MATCHING.json"])["matching"]
    need(
        len(matching) == 56
        and all(len(p) == 2 for p in matching)
        and sorted(i for p in matching for i in p) == list(range(112)),
        "plane partition",
    )
    planes = tuple(tuple(labels[i] for i in pair) for pair in matching)
    need(
        all([[dot(a, b) for b in p] for a in p] == [[1, 0], [0, 1]] for p in planes),
        "plane Gram I2",
    )
    return planes


def dot(a, b):
    return (a & b).bit_count() % 2


def rank_pair(left, right):
    pivots = [0] * 10
    for a in left:
        row = sum(dot(a, b) << j for j, b in enumerate(right))
        for j in range(9, -1, -1):
            if row >> j & 1:
                if pivots[j]:
                    row ^= pivots[j]
                else:
                    pivots[j] = row
                    break
    return sum(bool(p) for p in pivots)


def records(local, weights):
    need(len(local) == 5 and len(weights) == 10, "local domains")
    need(
        all(
            (rank_pair(local[i], local[j]) == 0) == ((j - i) % 5 in (1, 4))
            for i in range(5)
            for j in range(5)
            if i != j
        ),
        "actual induced C5",
    )
    bases = [
        tuple(q for i, p in enumerate(local) if mask >> i & 1 for q in p)
        for mask in range(32)
    ]
    result = []
    for a in range(32):
        for b in range(32):
            cost = rank_pair(bases[a], bases[b])
            hits = tuple(int(bool(a & h) and bool(b & h)) for h in BLOCKS)
            defect = 6 * cost - sum(w * h for w, h in zip(weights, hits, strict=True))
            need(defect >= 0, "nonnegative weighted tariff defect")
            need(cost != 0 or not any(hits), "free terms advance no block")
            result.append((a, b, cost, hits, defect))
    return tuple(result)


def trace_ok(a, b, hits, target, weights):
    equations = []
    for i in range(5):
        if not (a & b) >> i & 1:
            equations.append([Fraction(i == j) for j in range(5)] + [Fraction(0)])
    for k, block in enumerate(BLOCKS):
        # Zero-weight block counts are capped, so never impose their trace.
        if weights[k] and target[k] == RANKS[k]:
            equations.append(
                [Fraction(block >> j & 1) for j in range(5)] + [Fraction(hits[k])]
            )
    for col in range(5):
        pivot = next((k for k, row in enumerate(equations) if row[col]), None)
        if pivot is None:
            continue
        row = equations.pop(pivot)
        row = [x / row[col] for x in row]
        equations = [
            [v - other[col] * x for v, x in zip(other, row, strict=True)]
            for other in equations
        ]
    return all(any(row[:5]) or not row[5] for row in equations)


def cases(weights, cost):
    budget = 6 * cost - sum(w * r for w, r in zip(weights, RANKS, strict=True))
    need(0 <= budget <= 6, "bounded equality slack")
    ranges = [range(budget // w + 1) if w else range(1) for w in weights]
    need(prod(len(r) for r in ranges) <= 200000, "bounded excess box")
    result = []
    for excess in itertools.product(*ranges):
        remaining = budget - sum(w * e for w, e in zip(weights, excess, strict=True))
        if remaining >= 0:
            result.append(
                (tuple(r + e for r, e in zip(RANKS, excess, strict=True)), remaining)
            )
    return tuple(result)


def reach(rows, weights, target, remaining, traces=True):
    types = set()
    for a, b, cost, hits, defect in rows:
        if (
            cost
            and defect <= remaining
            and (not traces or trace_ok(a, b, hits, target, weights))
        ):
            types.add(hits + (defect,))
    need(
        all(any(t[i] for i in range(10) if weights[i]) or t[10] for t in types),
        "paid profile advances a bounded coordinate",
    )
    types = sorted(types)
    zero = (0,) * 11
    seen, queue = {zero}, deque([zero])
    cap = prod(t + 1 for t in target) * (remaining + 1)
    need(cap <= 6000000, "bounded count-state capacity")
    for _ in range(cap):
        if not queue:
            break
        state = queue.popleft()
        for inc in types:
            new = tuple(
                state[i] + inc[i] if weights[i] else min(RANKS[i], state[i] + inc[i])
                for i in range(10)
            )
            new += (state[10] + inc[10],)
            if new[10] > remaining or any(
                weights[i] and new[i] > target[i] for i in range(10)
            ):
                continue
            if new not in seen:
                seen.add(new)
                queue.append(new)
    need(not queue, "complete bounded reachability")
    return {
        "target": list(target),
        "defect": remaining,
        "profiles": len(types),
        "states": len(seen),
        "reachable": target + (remaining,) in seen,
    }


def attainment(local):
    matrix = [[0] * 10 for _ in range(10)]
    costs = []
    for i in range(5):
        ports = (2 * i + 1, 2 * ((i + 1) % 5))
        labels = local[i] + local[(i + 1) % 5]
        costs.append(rank_pair(labels, labels))
        for a in ports:
            for b in ports:
                matrix[a][b] += 1
    need(
        all(
            matrix[a][b] == int(a == b)
            for a in range(10)
            for b in range(10)
            if a // 2 == b // 2 or rank_pair(local[a // 2], local[b // 2])
        ),
        "strict scalar fit",
    )
    need(costs == [4] * 5, "exact five-term cost20")
    return costs


def build():
    planes = geometry()
    out = []
    for cycle, weights in CORES:
        local = tuple(planes[i] for i in cycle)
        rows = records(local, weights)
        lower = (sum(w * r for w, r in zip(weights, RANKS, strict=True)) + 5) // 6
        checked = []
        for cost in range(lower, 20):
            checks = [reach(rows, weights, t, d) for t, d in cases(weights, cost)]
            need(all(not c["reachable"] for c in checks), "all sub20 cases excluded")
            checked.append({"cost": cost, "cases": checks})
        out.append(
            {
                "cycle": list(cycle),
                "weights": list(weights),
                "denominator": 6,
                "weighted_rank_sum": sum(
                    w * r for w, r in zip(weights, RANKS, strict=True)
                ),
                "tariff_sha256": digest([r[2] for r in rows]),
                "checks": checked,
                "attaining_costs": attainment(local),
            }
        )
    return {
        "schema_version": 1,
        "claim": "sharp_cost20_on_four_remaining_physical_C5s",
        "blocks": list(BLOCKS),
        "cores": out,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    need(build() == json.loads((HERE / "RESULT.json").read_bytes()), "exact receipt")
    print("PASS_C5_RESIDUAL_TRACE four_cores cost20 no_new_kappa")
