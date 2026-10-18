#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact rank-product certificate for one already cost-20 physical C5.

The arbitrary-coefficient and moment reductions are in PROOF.md. Only the
named covered core is inspected. No unresolved physical core is searched.
"""

import argparse
import gzip
import hashlib
import io
import itertools
import json
from dataclasses import dataclass
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/c5-dyadic-decoder-gate/inputs/"
CORE = (13, 23, 35, 16, 34)
PAIRS = ((0, 2), (0, 3), (1, 3), (1, 4))
LIVE = {PREFIX + "DATA-PHASES.json.gz", PREFIX + "MATCHING.json"}
PROVENANCE = {
    "certificates/selected-result.json",
    "docs/research/agent-task-catalog.json",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def load_sources(root=ROOT, inventory=None):
    inventory = HERE / "SOURCES.json" if inventory is None else inventory
    need(inventory.stat().st_size < 32_000, "bounded inventory")
    rows = json.loads(inventory.read_bytes())["files"]
    need(isinstance(rows, list) and len(rows) == 4, "four exact source rows")
    need(
        all(set(r) == {"path", "usage", "sha256", "git_blob"} for r in rows),
        "source schema",
    )
    expected = dict.fromkeys(LIVE, "input") | dict.fromkeys(PROVENANCE, "provenance")
    need({r["path"]: r["usage"] for r in rows} == expected, "source usages")
    raw = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular input")
        need(path.resolve().is_relative_to(root.resolve()), "input containment")
        need(path.stat().st_size <= 2_000_000, "bounded input")
        value = path.read_bytes()
        need(hashlib.sha256(value).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(value)}\0".encode() + value).hexdigest()
        need(blob == row["git_blob"], "source Git blob")
        raw[path.name] = value
    return raw


def geometry(root=ROOT, inventory=None):
    raw = load_sources(root, inventory)
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        payload = stream.read(2_000_001)
    need(len(payload) <= 2_000_000, "bounded decompression")
    recipes = json.loads(payload)["recipes"]
    labels = {r["port"]: r["q"] for r in recipes}
    need(len(recipes) == 112 and sorted(labels) == list(range(112)), "112 ports")
    need(
        all(type(q) is int and 0 < q < 512 for q in labels.values()), "nine-bit labels"
    )
    matching = json.loads(raw["MATCHING.json"])["matching"]
    need(len(matching) == 56 and all(len(p) == 2 for p in matching), "56 planes")
    need(sorted(p for pair in matching for p in pair) == list(range(112)), "partition")
    local = tuple(tuple(labels[p] for p in matching[i]) for i in CORE)
    for i, plane in enumerate(local):
        need(
            [[dot(a, b) for b in plane] for a in plane] == [[1, 0], [0, 1]], "I2 plane"
        )
        for j in range(i):
            need((rank_pair(plane, local[j]) == 0) == ((i - j) in (1, 4)), "C5 mask")
    return local


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
    need(rank <= 9, "ambient rank nine")
    return rank


@dataclass(frozen=True)
class Term:
    left: int
    right: int
    cost: int
    increment: tuple


def records(local):
    bases = [
        tuple(q for i, p in enumerate(local) if m >> i & 1 for q in p)
        for m in range(32)
    ]
    result = []
    for a, b in itertools.product(range(32), repeat=2):
        cost = rank_pair(bases[a], bases[b])
        hits = tuple(int(bool(a & h) and bool(b & h)) for h in (5, 9, 10, 18, 4, 16))
        defect = 2 * cost - 2 * sum(hits[:4]) - sum(hits[4:])
        need(defect >= 0, "physical weighted-cover inequality")
        missing = int(bool(a & 20) and bool(b & 20))
        inc = hits + (defect, missing)
        need(cost != 0 or not any(inc), "free term has no constrained block")
        result.append(Term(a, b, cost, inc))
    return tuple(result)


def trace_ok(term, target):
    # The four selected pairs form a path. Every component is affine in one
    # free scalar; absent diagonal supports and tight singletons anchor it.
    graph = [[] for _ in range(5)]
    for k, (i, j) in enumerate(PAIRS):
        if target[k] == 4:
            graph[i].append((j, term.increment[k]))
            graph[j].append((i, term.increment[k]))
    anchors = {i: 0 for i in range(5) if not (term.left & term.right) >> i & 1}
    for i, k in ((2, 4), (4, 5)):
        if target[k] == 2:
            anchors[i] = term.increment[k]
    visited = set()
    for start in range(5):
        if start in visited:
            continue
        affine, queue, fixed = {start: (1, 0)}, [start], None
        for _ in range(5):
            if not queue:
                break
            i = queue.pop()
            visited.add(i)
            sign, offset = affine[i]
            if i in anchors:
                value = (anchors[i] - offset) * sign
                if fixed is not None and fixed != value:
                    return False
                fixed = value
            for j, total in graph[i]:
                if j not in affine:
                    affine[j] = (-sign, total - offset)
                    queue.append(j)
        need(not queue, "bounded affine path")
    return True


def targets(cost):
    need(cost in (18, 19, 20), "three exact costs")
    slack = 2 * cost - 36
    result = []
    for x in itertools.product(range(slack // 2 + 1), repeat=4):
        if 2 * sum(x) > slack:
            continue
        for y in itertools.product(range(slack + 1), repeat=2):
            defect = slack - 2 * sum(x) - sum(y)
            if defect >= 0:
                result.append(
                    tuple(4 + a for a in x) + tuple(2 + a for a in y) + (defect,)
                )
    return tuple(result)


def maximize(rows, target, cost, traces=True):
    profiles = {
        t.increment: t.cost
        for t in rows
        if t.cost and (not traces or trace_ok(t, target))
    }
    layers = [{} for _ in range(cost + 1)]
    layers[0][(0,) * 9] = 1
    bound = 35 * prod(t + 1 for t in target)
    visited = 0
    for paid in range(cost + 1):
        visited += len(layers[paid])
        need(visited <= bound, "bounded product-state domain")
        for state, product in layers[paid].items():
            for inc, rank in profiles.items():
                if paid + rank > cost:
                    continue
                new = tuple(state[i] + inc[i] for i in range(7))
                if any(new[i] > target[i] for i in range(7)):
                    continue
                new += (min(4, state[7] + inc[7]), min(6, state[8] + 1))
                value = product * rank**rank
                need(value <= 9**cost, "bounded exact rank product")
                layer = layers[paid + rank]
                if value > layer.get(new, 0):
                    layer[new] = value
    endpoints = [layers[cost].get(target + (4, n), 0) for n in range(7)]
    return {
        "states": visited,
        "reachable": any(endpoints),
        "six_term_max_product": endpoints[6],
    }


def attainment(local):
    matrix = [[0] * 10 for _ in range(10)]
    ranks = []
    for i in range(5):
        ports = (2 * i + 1, 2 * ((i + 1) % 5))
        ranks.append(
            rank_pair(local[i] + local[(i + 1) % 5], local[i] + local[(i + 1) % 5])
        )
        for a, b in itertools.product(ports, repeat=2):
            matrix[a][b] += 1
    for a, b in itertools.product(range(10), repeat=2):
        if a // 2 == b // 2 or rank_pair(local[a // 2], local[b // 2]):
            need(matrix[a][b] == int(a == b), "exact strict-scalar attainment")
    need(ranks == [4] * 5, "five rank-four terms")
    return ranks


def build():
    local = geometry()
    rows = records(local)
    cases = []
    for cost in (18, 19, 20):
        for target in targets(cost):
            result = maximize(rows, target, cost)
            if cost < 20:
                need(not result["reachable"], "no cost18 or cost19 fit")
            cases.append({"cost": cost, "target": list(target), **result})
    maximum = max(c["six_term_max_product"] for c in cases if c["cost"] == 20)
    need(maximum == 640_000_000_000 < 4**20, "strict cost20 rank-product floor")
    need(9 * 20**20 < 4 * 21**20, "cost21-plus rational moment comparison")
    return {
        "schema_version": 1,
        "core": list(CORE),
        "tariff_sha256": digest([t.cost for t in rows]),
        "cases": cases,
        "cost20_six_term_max_product": maximum,
        "five_rank4_product": 4**20,
        "attaining_ranks": attainment(local),
        "saving_interval": ["0", "1/20"],
        "moment_floor": "5 * 4**(1-a)",
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
        receipt = HERE / "RESULT.json"
        need(receipt.stat().st_size < 1_000_000, "bounded receipt")
        need(result == json.loads(receipt.read_bytes()), "exact receipt")
        print("PASS_C5_RECURSIVE_MOMENT core=13,23,35,16,34 a<=1/20 no_new_kappa")


if __name__ == "__main__":
    main()
