#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the new column completion and forced-label obstruction, read-only."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import types


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXTRACTOR = "research/centre-block-repair-information/independent.py"
PREMISES = "research/centre-block-moore-bound/RESULT.json"
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
        raw = path.read_bytes()
        require(len(raw) <= 8 * 1024 * 1024, "bounded input")
        require(sha256(raw).hexdigest() == row["sha256"], "input SHA256")
        require(row["path"] not in inputs, "unique input path")
        inputs[row["path"]] = raw
    require(len(inputs) == 4, "complete four-input closure")
    return inputs


def selected_columns(inputs):
    # Execute only the fixed, authenticated extractor to prepare the input R.
    # Its main verifier, route census and old scientific comparisons do not run.
    source = types.ModuleType("retained_row_extractor")
    source.__file__ = str(ROOT / EXTRACTOR)
    exec(compile(inputs[EXTRACTOR], source.__file__, "exec", optimize=0),
         source.__dict__)
    word, _phases = source.sources()
    rows, _later_rows = source.query_rows(word)
    require(len(rows) == 8 and all(len(row) == 112 for row in rows),
            "selected R shape")
    return tuple(zip(*rows))


def completions(columns, a, b):
    require(2 <= len(columns) <= 112 and 0 <= a < b < len(columns),
            "bounded column pair")
    width = len(columns[0])
    require(2 <= width <= 8 and all(len(x) == width for x in columns),
            "bounded equal column dimensions")
    x, y = columns[a], columns[b]
    pivots = [(i, j) for i, j in combinations(range(width), 2)
              if x[i] * y[j] != x[j] * y[i]]
    require(bool(pivots), "independent pair")
    i, j = pivots[0]
    determinant = x[i] * y[j] - x[j] * y[i]
    found = []
    for c, z in enumerate(columns):
        if c in (a, b):
            continue
        u = z[i] * y[j] - z[j] * y[i]
        v = x[i] * z[j] - x[j] * z[i]
        if all(u * xx + v * yy == determinant * zz
               for xx, yy, zz in zip(x, y, z)):
            require(u != 0 and v != 0, "nonparallel completion")
            found.append(c)
    return found


def completion_certificate(columns, pairs):
    require(len(pairs) == 50 and len({tuple(p) for p in pairs}) == 50,
            "complete cited braid-pair inventory")
    result = []
    for a, b in pairs:
        found = completions(columns, a, b)
        require(len(found) == 1, "unique third column for every braid pair")
        result.append([a, b, found[0]])
    return result


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
    # A third coordinate defeats an incorrect two-coordinate span test.
    require(completions(((1, 0, 0), (0, 1, 0), (1, 1, 1)), 0, 1) == [],
            "full-coordinate span control")
    require(completions(((1, 0), (0, 1), (1, 1), (1, -1)), 0, 1) == [2, 3],
            "nonunique completion control")
    expect_failure(lambda: completions(((1, 0), (2, 0)), 0, 1),
                   "independent pair")
    leaf_rows = [[1, 2, 3], [0, 2, 4], [0, 1, 5], [0], [1], [2]]
    one_cycle = [{"B": [0, 1, 2], "D": [0, 1, 2]}]
    require(forcing_certificate(leaf_rows, one_cycle) is None,
            "one legal cycle boundary has no forced-label collision")
    broken = [list(row) for row in rows]
    broken[0].remove(1)
    expect_failure(lambda: forcing_certificate(broken, cycles),
                   "two cycle edges and one external edge on B")
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
    return {"span_controls": 2, "rejections": 2,
            "positive_cycle_boundary": 1, "relabelings": 3}


def main():
    inputs = read_inputs()
    columns = selected_columns(inputs)
    premises = json.loads(inputs[PREMISES])["source_premises"]
    completed = completion_certificate(columns, premises["braid_edges"])
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
               "completion_tests": 50 * 110, "completions": completed,
               "forcing": forcing, "controls": controls(rows, cycles)}
    receipt["package_sha256"] = {
        p.relative_to(HERE).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(HERE.rglob("*")) if p.is_file()
        and "__pycache__" not in p.parts}
    receipt["inputs_sha256"] = {p: sha256(raw).hexdigest()
                                 for p, raw in sorted(inputs.items())}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_FIFTEEN_OWNER_CYCLE_ROUTE_OBSTRUCTION pairs=50 tests=5500 collision=B3")


if __name__ == "__main__":
    main()
