#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact obstruction to universal fixed-weight C5 restriction charging."""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/c5-dyadic-decoder-gate/inputs/"
USAGES = {
    "certificates/selected-result.json": "provenance",
    "docs/research/agent-task-catalog.json": "provenance",
    PREFIX + "DATA-PHASES.json.gz": "input",
    PREFIX + "MATCHING.json": "input",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sources(root=ROOT, inventory=None):
    path = HERE / "SOURCES.json" if inventory is None else inventory
    require(path.stat().st_size <= 32_000, "bounded manifest")
    doc = json.loads(path.read_bytes())
    require(set(doc) == {"schema_version", "base_commit", "files"}, "manifest schema")
    require(doc["schema_version"] == 1, "manifest version")
    require(doc["base_commit"] == "463113d675af7410ac91d53a4fed51ec6494eb9a", "base")
    rows = doc["files"]
    require(isinstance(rows, list) and len(rows) == 4, "four source rows")
    require(
        all(
            isinstance(r, dict) and set(r) == {"path", "usage", "git_blob", "sha256"}
            for r in rows
        ),
        "source row schema",
    )
    require(len({r["path"] for r in rows}) == 4, "unique source paths")
    require({r["path"]: r["usage"] for r in rows} == USAGES, "fixed paths/usages")
    payloads = {}
    for row in rows:
        if row["usage"] == "provenance":
            continue  # Historical Git provenance is checked by the registered runner.
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular source")
        require(path.resolve().is_relative_to(root.resolve()), "source inside root")
        require(path.stat().st_size <= 2_000_000, "bounded input")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        require(blob == row["git_blob"], "source Git blob")
        payloads[path.name] = raw
    return payloads


def geometry(root=ROOT, inventory=None):
    raw = sources(root, inventory)
    with gzip.GzipFile(fileobj=io.BytesIO(raw["DATA-PHASES.json.gz"])) as stream:
        data = stream.read(2_000_001)
    require(len(data) <= 2_000_000, "bounded decompression")
    rows = json.loads(data)["recipes"]
    require(isinstance(rows, list) and len(rows) == 112, "112 scalar labels")
    require(
        all(
            isinstance(r, dict)
            and type(r.get("port")) is int
            and type(r.get("q")) is int
            for r in rows
        ),
        "label row schema",
    )
    labels = {r["port"]: r["q"] for r in rows}
    require(sorted(labels) == list(range(112)), "unique ports")
    require(
        len(set(labels.values())) == 112 and all(0 < q < 512 for q in labels.values()),
        "distinct nine-bit labels",
    )
    matching = json.loads(raw["MATCHING.json"])["matching"]
    require(isinstance(matching, list) and len(matching) == 56, "56 planes")
    require(
        all(
            isinstance(pair, list)
            and len(pair) == 2
            and all(type(p) is int for p in pair)
            for pair in matching
        ),
        "pair schema",
    )
    require(
        sorted(p for pair in matching for p in pair) == list(range(112)), "partition"
    )
    planes = tuple(tuple(labels[p] for p in pair) for pair in matching)
    require(
        all([[dot(x, y) for y in e] for x in e] == [[1, 0], [0, 1]] for e in planes),
        "nondegenerate complete planes",
    )
    return planes


def dot(a, b):
    return (a & b).bit_count() % 2


def pairing_rank(left, right):
    require(len(left) <= 112 and len(right) <= 112, "rank dimensions")
    pivots = [0] * len(right)
    for label in left:
        row = sum(dot(label, other) << j for j, other in enumerate(right))
        for j in range(len(right) - 1, -1, -1):
            if row >> j & 1:
                if pivots[j]:
                    row ^= pivots[j]
                else:
                    pivots[j] = row
                    break
    rank = sum(bool(p) for p in pivots)
    require(rank <= 9, "ambient rank bound")
    return rank


def cycles(planes):
    adj = [
        {j for j in range(56) if i != j and pairing_rank(planes[i], planes[j]) == 0}
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
    require(len(found) == 23, "23 induced physical C5s")
    return tuple(sorted(found))


def identity_extension(n=112):
    """I = J - sum_{i != j} e_i e_j^T, retaining J as an actual term."""
    require(type(n) is int and 2 <= n <= 112, "bounded extension dimension")
    matrix = [[1] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] -= 1
    require(
        all(matrix[i][j] == int(i == j) for i in range(n) for j in range(n)),
        "complete strict identity extension",
    )
    return 1 + n * (n - 1)


def obstruction(global_rank, local_ranks, floors):
    require(type(global_rank) is int and 0 < global_rank <= 9, "global rank")
    require(0 < len(local_ranks) == len(floors) <= 23, "bounded matched local data")
    require(
        all(type(r) is int and 0 < r <= global_rank for r in local_ranks),
        "positive restricted ranks",
    )
    require(all(type(f) is int and f >= 0 for f in floors), "nonnegative floors")
    # For every feasible lambda, sum lambda_i r_i <= global_rank.
    return global_rank * max(Fraction(f, r) for f, r in zip(floors, local_ranks))


def build():
    planes = geometry()
    labels = tuple(q for plane in planes for q in plane)
    rows = []
    for cycle in cycles(planes):
        local = tuple(q for i in cycle for q in planes[i])
        rows.append(
            {"cycle": list(cycle), "full_support_rank": pairing_rank(local, local)}
        )
    ranks = [row["full_support_rank"] for row in rows]
    global_rank = pairing_rank(labels, labels)
    ceiling = obstruction(global_rank, ranks, [20] * 23)
    require(global_rank == 9 and Counter(ranks) == {7: 4, 8: 6, 9: 13}, "rank receipt")
    require(ceiling == Fraction(180, 7) < 26, "necessary certificate ceiling")
    return {
        "schema_version": 1,
        "claim": "fixed_nonnegative_direct_C5_charging_ceiling",
        "scalar_ports": 112,
        "complete_planes": 56,
        "global_full_support_rank": global_rank,
        "cycles": rows,
        "rank_histogram": {str(k): v for k, v in sorted(Counter(ranks).items())},
        "granted_local_floors": [20] * 23,
        "certificate_ceiling": str(ceiling),
        "naive_unit_weight_restricted_cost": sum(ranks),
        "strict_fit_extension_terms": identity_extension(),
        "ceiling_attainability_claimed": False,
        "cheap_decoder_claimed": False,
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
        require(
            result == json.loads((HERE / "RESULT.json").read_bytes()), "exact receipt"
        )
        print("PASS_C5_GLOBAL_CHARGING cycles=23 ranks=7/8/9 global=9 ceiling=180/7")


if __name__ == "__main__":
    main()
