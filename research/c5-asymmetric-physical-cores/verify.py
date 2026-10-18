#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Physical C5 extension of thakrarsagar's PR3256 rank/trace certificate.

The reduction from arbitrary scalar factors is in PROOF.md. This checker
reconstructs every physical tariff, not just the abstract C5 graph.
"""

import argparse
import gzip
import hashlib
import io
import json
from collections import deque
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/c5-dyadic-decoder-gate/inputs/"
PAIRS = ((0, 2), (0, 3), (1, 3), (1, 4))
BASE = (4, 4, 4, 4, 2, 2, 0)
SOURCE_CORE = (13, 23, 35, 16, 34)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def source_payloads(root, inventory):
    inventory = HERE / "SOURCES.json" if inventory is None else inventory
    need(inventory.stat().st_size < 32_000, "bounded source inventory")
    rows = json.loads(inventory.read_bytes())["files"]
    need(isinstance(rows, list) and len(rows) == 4, "exact four source rows")
    expected_all = {
        "certificates/selected-result.json": "provenance",
        "docs/research/agent-task-catalog.json": "provenance",
        INPUT + "DATA-PHASES.json.gz": "input",
        INPUT + "MATCHING.json": "input",
    }
    need(
        all(
            isinstance(row, dict)
            and set(row) == {"path", "usage", "sha256", "git_blob"}
            for row in rows
        ),
        "source row schema",
    )
    need(
        len({row["path"] for row in rows}) == 4
        and {row["path"]: row["usage"] for row in rows} == expected_all,
        "exact source paths and usages",
    )
    live = [row for row in rows if row["usage"] == "input"]
    expected = {INPUT + "DATA-PHASES.json.gz", INPUT + "MATCHING.json"}
    need(
        len(live) == 2 and {row["path"] for row in live} == expected,
        "exact two live scientific sources",
    )
    raw = {}
    for row in live:
        path = root / row["path"]
        need(
            path.is_file()
            and not path.is_symlink()
            and path.resolve().is_relative_to(root.resolve())
            and path.stat().st_size <= 2_000_000,
            "bounded regular source",
        )
        value = path.read_bytes()
        need(hashlib.sha256(value).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(value)}\0".encode() + value).hexdigest()
        need(blob == row["git_blob"], "source Git blob")
        raw[path.name] = value
    return raw


def geometry(root=ROOT, inventory=None):
    raw = source_payloads(root, inventory)
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        payload = stream.read(2_000_001)
    need(len(payload) <= 2_000_000, "bounded decompression")
    recipes = json.loads(payload)["recipes"]
    need(isinstance(recipes, list) and len(recipes) == 112, "112 scalar ports")
    labels = {r["port"]: r["q"] for r in recipes}
    need(
        sorted(labels) == list(range(112))
        and all(type(q) is int and 0 < q < 512 for q in labels.values()),
        "complete nine-bit label domain",
    )
    matching = json.loads(raw["MATCHING.json"])["matching"]
    need(
        len(matching) == 56
        and all(len(pair) == 2 for pair in matching)
        and sorted(p for pair in matching for p in pair) == list(range(112)),
        "complete paired-plane partition",
    )
    planes = tuple(tuple(labels[p] for p in pair) for pair in matching)
    need(
        all(
            [[dot(a, b) for b in plane] for a in plane] == [[1, 0], [0, 1]]
            for plane in planes
        ),
        "complete planes have Gram I2",
    )
    return planes


def dot(a, b):
    return (a & b).bit_count() % 2


def rank_pair(left, right):
    pivots = [0] * 10
    rank = 0
    for label in left:
        row = sum(dot(label, other) << j for j, other in enumerate(right))
        for bit in range(9, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    rank += 1
                    break
    need(rank <= 9, "nine-bit label rank")
    return rank


def cycles(planes):
    adj = [
        {j for j in range(56) if j != i and rank_pair(planes[i], planes[j]) == 0}
        for i in range(56)
    ]
    found = set()
    for a in range(56):
        for b in adj[a]:
            for c in adj[b] - adj[a] - {a}:
                for d in adj[c] - adj[a] - adj[b] - {a, b}:
                    for e in (adj[d] & adj[a]) - adj[b] - adj[c] - {b, c}:
                        if a == min(a, b, c, d, e) and b < e:
                            found.add((a, b, c, d, e))
    need(len(found) == 23, "all 23 chordless physical C5s")
    return tuple(sorted(found))


def orientations(cycle):
    return tuple(
        order[k:] + order[:k] for order in (cycle, cycle[::-1]) for k in range(5)
    )


def records(local):
    need(len(local) == 5, "five planes")
    bases = [
        tuple(q for i, plane in enumerate(local) if mask >> i & 1 for q in plane)
        for mask in range(32)
    ]
    result = []
    for a in range(32):
        for b in range(32):
            cost = rank_pair(bases[a], bases[b])
            hits = tuple(
                int(bool(a & ((1 << i) | (1 << j))) and bool(b & ((1 << i) | (1 << j))))
                for i, j in PAIRS
            )
            hits += (int(bool(a & b & 4)), int(bool(a & b & 16)))
            defect = 2 * cost - 2 * sum(hits[:4]) - sum(hits[4:])
            missing = int(bool(a & 20) and bool(b & 20))
            result.append((a, b, cost, hits + (defect, missing)))
    return tuple(result)


def trace_ok(record, target):
    a, b, _, inc = record
    graph = [[] for _ in range(5)]
    for k, (i, j) in enumerate(PAIRS):
        if target[k] == 4:
            graph[i].append((j, inc[k]))
            graph[j].append((i, inc[k]))
    anchors = {i: 0 for i in range(5) if not (a & b) >> i & 1}
    for i, k in ((2, 4), (4, 5)):
        if target[k] == 2:
            anchors[i] = inc[k]
    visited = set()
    for start in range(5):
        if start in visited:
            continue
        affine, todo, fixed = {start: (1, 0)}, [start], None
        for _ in range(5):
            if not todo:
                break
            i = todo.pop()
            visited.add(i)
            sign, offset = affine[i]
            if i in anchors:
                value = (anchors[i] - offset) * sign
                if fixed is not None and value != fixed:
                    return False
                fixed = value
            for j, total in graph[i]:
                if j not in affine:
                    affine[j] = (-sign, total - offset)
                    todo.append(j)
        need(not todo, "five-vertex path exhausted")
    return True


def targets():
    result = [BASE, BASE[:6] + (2,)]
    for i in range(4):
        row = list(BASE)
        row[i] += 1
        result.append(tuple(row))
    result.extend(
        (4, 4, 4, 4, a, b, 6 - a - b)
        for a, b in ((3, 2), (2, 3), (4, 2), (2, 4), (3, 3))
    )
    return tuple(result)


def reach(rows, target, traces=True):
    profiles = set()
    for row in rows:
        inc = row[3]
        need(inc[6] >= 0, "nonnegative tariff defect")
        if row[2] == 0:
            need(not any(inc), "free terms advance no certificate count")
            continue
        need(any(inc[:7]), "paid term advances bounded count")
        if inc[6] <= target[6] and (not traces or trace_ok(row, target)):
            profiles.add(inc)
    profiles = sorted(profiles)
    zero, seen = (0,) * 8, {(0,) * 8}
    todo = deque([zero])
    cap = 5 * prod(t + 1 for t in target)
    for _ in range(cap):
        if not todo:
            break
        state = todo.popleft()
        for inc in profiles:
            new = tuple(state[i] + inc[i] for i in range(7))
            if any(new[i] > target[i] for i in range(7)):
                continue
            new += (min(4, state[7] + inc[7]),)
            if new not in seen:
                seen.add(new)
                todo.append(new)
    need(not todo and len(seen) <= cap, "finite count domain exhausted")
    return {
        "target": list(target),
        "states": len(seen),
        "profiles": len(profiles),
        "reachable": target + (4,) in seen,
    }


def certificate(rows):
    if min(row[3][6] for row in rows) < 0:
        return None
    checks = [reach(rows, target) for target in targets()]
    return checks if all(not case["reachable"] for case in checks) else None


def baseline(local):
    matrix = [[0] * 10 for _ in range(10)]
    cost = 0
    for i in range(5):
        ports = (2 * i + 1, 2 * ((i + 1) % 5))
        labels = local[i] + local[(i + 1) % 5]
        cost += rank_pair(labels, labels)
        for a in ports:
            for b in ports:
                matrix[a][b] += 1
    for a in range(10):
        for b in range(10):
            if a // 2 == b // 2 or rank_pair(local[a // 2], local[b // 2]):
                need(matrix[a][b] == int(a == b), "complete strict scalar fit")
    need(cost == 20, "five-term cost20 attainment")
    return cost


def build():
    planes = geometry()
    covered, residual = [], []
    for cycle in cycles(planes):
        accepted = None
        for order in orientations(cycle):
            local = tuple(planes[i] for i in order)
            rows = records(local)
            checks = certificate(rows)
            if checks is not None:
                accepted = {
                    "cycle": list(cycle),
                    "order": list(order),
                    "tariff_sha256": digest([r[2] for r in rows]),
                    "cases": checks,
                    "attained_cost": baseline(local),
                }
                break
        if accepted is None:
            residual.append(list(cycle))
        else:
            covered.append(accepted)
    need(len(covered) == 18 and len(residual) == 5, "exact covered/residual inventory")
    need(any(tuple(row["cycle"]) == SOURCE_CORE for row in covered), "source control")
    return {
        "schema_version": 1,
        "claim": "sharp_asymmetric_cost20_on18_physical_C5s",
        "new_cores": 17,
        "covered": covered,
        "unresolved": residual,
        "coefficient_fields": ["Q", "R", "C"],
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((HERE / "RESULT.json").read_bytes()), "exact receipt")
        print(
            "PASS_C5_PHYSICAL_CORES covered=18 new=17 unresolved=5 cost=20 no_new_kappa"
        )


if __name__ == "__main__":
    main()
