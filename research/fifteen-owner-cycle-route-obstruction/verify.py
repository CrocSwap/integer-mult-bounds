#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the new forced-label obstruction, with cited column premises."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRAPH = "research/centre-equality-six-cycles/WITNESS.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    inputs = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular input")
        require(path.stat().st_size <= 4096, "bounded input")
        raw = path.read_bytes()
        require(len(raw) <= 4096, "bounded input")
        require(sha256(raw).hexdigest() == row["sha256"], "input SHA256")
        require(row["path"] not in inputs, "unique input path")
        inputs[row["path"]] = raw
    require(set(inputs) == {GRAPH}, "complete graph-input closure")
    return inputs


def cycle_boundaries(rows, cycles):
    require(1 <= len(rows) <= 32 and 1 <= len(cycles) <= 8,
            "bounded graph and cycle inventory")
    require(all(len(row) == len(set(row)) <= 3 for row in rows),
            "simple graph with degrees at most three")
    require(all(type(d) is int and 0 <= d < len(rows)
                for row in rows for d in row), "bounded D vertices")
    inverse = [set() for _ in rows]
    for b, row in enumerate(rows):
        for d in row:
            inverse[d].add(b)
    owners_b, owners_d, boundaries = {}, {}, []
    for k, cycle in enumerate(cycles):
        bs, ds = set(cycle["B"]), set(cycle["D"])
        require(len(bs) == len(ds) == 3, "three vertices on each cycle side")
        require(all(type(v) is int and 0 <= v < len(rows) for v in bs | ds),
                "cycle vertex range")
        require(not (bs & owners_b.keys() or ds & owners_d.keys()),
                "disjoint named cycles")
        require(all(len(rows[b]) == 3 and len(set(rows[b]) & ds) == 2
                    for b in bs), "two cycle edges and one external edge on B")
        require(all(len(inverse[d]) == 3 and len(inverse[d] & bs) == 2
                    for d in ds), "two cycle edges and one external edge on D")
        edges = {(b, d) for b in bs for d in set(rows[b]) - ds}
        edges.update((b, d) for d in ds for b in inverse[d] - bs)
        require(len(edges) == 6, "six distinct external cycle edges")
        boundaries.append(edges)
        owners_b.update((b, k) for b in bs)
        owners_d.update((d, k) for d in ds)
    return inverse, owners_b, owners_d, boundaries


def forcing_certificate(rows, cycles):
    inverse, owners_b, owners_d, boundaries = cycle_boundaries(rows, cycles)
    links = set()
    for b, row in enumerate(rows):
        for d in row:
            if b in owners_b and d in owners_d:
                a, c = owners_b[b], owners_d[d]
                if a != c:
                    links.add(tuple(sorted((a, c))))
    components = []
    for start in range(len(cycles)):
        seen = {start}
        for _ in range(len(cycles)):
            seen |= {b for a, b in links if a in seen}
            seen |= {a for a, b in links if b in seen}
        if sorted(seen) not in components:
            components.append(sorted(seen))
    for component in components:
        external = set().union(*(boundaries[k] for k in component))
        for side, adjacency in (("B", rows), ("D", inverse)):
            for v, neighbors in enumerate(adjacency):
                edges = [(v, w) if side == "B" else (w, v)
                         for w in sorted(neighbors)]
                forced = [list(edge) for edge in edges if edge in external]
                if len(forced) >= 2:
                    return {"cycle_links": [list(x) for x in sorted(links)],
                            "component": component, "side": side,
                            "vertex": v, "equal_label_edges": forced[:2]}
    return None


def expect_failure(function, message):
    try:
        function()
    except ValueError as error:
        require(str(error) == message, "expected failure reason")
    else:
        raise ValueError("missing rejection: " + message)


def controls(rows, cycles):
    leaf_rows = [[1, 2, 3], [0, 2, 4], [0, 1, 5], [0], [1], [2]]
    one_cycle = [{"B": [0, 1, 2], "D": [0, 1, 2]}]
    require(forcing_certificate(leaf_rows, one_cycle) is None,
            "one legal cycle boundary has no forced-label collision")
    broken = [list(row) for row in rows]
    broken[0].remove(1)
    expect_failure(lambda: forcing_certificate(broken, cycles),
                   "two cycle edges and one external edge on B")
    expect_failure(lambda: forcing_certificate(rows, cycles + cycles[:1]),
                   "disjoint named cycles")
    # Independent permutations of both parts must preserve the obstruction.
    for shift in range(1, 4):
        pb = [(v + shift) % 15 for v in range(15)]
        pd = [(7 * v + shift) % 15 for v in range(15)]
        moved = [[] for _ in rows]
        for b, row in enumerate(rows):
            moved[pb[b]] = [pd[d] for d in row]
        moved_cycles = [{"B": [pb[b] for b in c["B"]],
                         "D": [pd[d] for d in c["D"]]} for c in cycles]
        require(forcing_certificate(moved, moved_cycles) is not None,
                "part-preserving relabeling")
    return {"rejections": 2,
            "positive_cycle_boundary": 1, "relabelings": 3}


def assignment_certificate(forcing):
    # Four cycle labels use at most four distinct values, after renaming.
    checked, linked, legal = 0, 0, 0
    for labels in product(range(4), repeat=4):
        checked += 1
        if all(labels[a] == labels[b] for a, b in forcing["cycle_links"]):
            linked += 1
            if labels[0] != labels[3]:
                legal += 1
    require((checked, linked, legal) == (256, 4, 0),
            "complete external-label assignment certificate")
    return {"assignments": checked, "obey_cycle_links": linked,
            "distinct_ports_at_B3": legal}


def main():
    inputs = read_inputs()
    graph = json.loads(inputs[GRAPH])
    rows, cycles = graph["rows"], graph["six_cycles"]
    require(len(rows) == 15 and len(cycles) == 4, "cited equality graph shape")
    forcing = forcing_certificate(rows, cycles)
    require(forcing is not None, "forced-label collision")
    require(forcing["component"] == [0, 1, 2, 3]
            and forcing["side"] == "B" and forcing["vertex"] == 3
            and forcing["equal_label_edges"] == [[3, 0], [3, 7]],
            "explicit collision at B3")
    receipt = {"claim_type": "scoped proof with exact finite corroboration",
               "forcing": forcing, "controls": controls(rows, cycles),
               "label_assignments": assignment_certificate(forcing)}
    receipt["package_sha256"] = {
        p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(HERE.rglob("*")) if p.is_file()
        and "__pycache__" not in p.parts}
    receipt["inputs_sha256"] = {p: sha256(raw).hexdigest()
                                 for p, raw in sorted(inputs.items())}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_FIFTEEN_OWNER_CYCLE_ROUTE_OBSTRUCTION assignments=256 legal=0 collision=B3")


if __name__ == "__main__":
    main()
