#!/usr/bin/env python3
"""Independent Fraction/Prim replay for the selected X4 target-forest experiment.

No imports from the experiment's generator or pending predecessors.  Graph prices
are obtained by constructing old binary-Horner primitive lists, rather than by
using the generator's integer coefficient-cost formula.  Attribution: PR799 X4
sources, PR901 target pairs, PR816 signed forests and PR759 binary forests.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ARCHIVE_SHA256 = "70dfdfcf2ff95352c6020ee9dfca6dca9032b33c10daed3f3dc574c014f4e2cb"
MEMBER_PINS = {
    "native/local/CANONICAL-WORD.json.gz": "1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa",
    "native/local/LOCAL-PROGRAMS.json.gz": "223c2bb27ad68a4e9468c3ddaece1899d577b661190922fdd25f5976052c4cab",
    "native/local/LOCAL-CHECKS.json": "bbde5cea7bfd5df3d3ee7dfada0ff9d165af43a4d1dec6a9597cbfd8f87cc3b2",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def primitive_word(q):
    """Construct S-preserving, W-clearing old Horner for T += q*S."""
    q = Q(q)
    if not q:
        return ()
    denominator = q.denominator
    require(denominator & (denominator - 1) == 0, "non-dyadic coefficient")
    ops = [("clear", "W")]
    for index, bit in enumerate(bin(abs(q.numerator))[2:]):
        if index:
            ops.append(("double", "W"))
        if bit == "1":
            ops.append(("add", "W", "S"))
    while denominator > 1:
        ops.append(("half", "W"))
        denominator //= 2
    ops += [("add" if q > 0 else "sub", "T", "W"), ("clear", "W")]
    return tuple(ops)


def row_difference(a, b, sign):
    return {source: q for source in a.keys() | b.keys()
            if (q := a.get(source, Q(0)) - sign * b.get(source, Q(0)))}


def row_price(row):
    return sum(len(primitive_word(q)) for q in row.values())


def rows_from_word(word):
    rows = {}
    for op in word["compensation"]:
        require(len(op) == 6 and op[0] == "add" and op[5] == 0,
                "compensation must be zero-frame additions")
        _, target, source, numerator, denominator, _ = op
        q = Q(numerator, denominator)
        require(q and source not in rows.get(target, {}), "zero or repeated coefficient")
        rows.setdefault(target, {})[source] = q
    helpers = set().union(*(set(row) for row in rows.values()))
    require(not helpers.intersection(rows), "target/helper alias")
    require(all(word["start"][r] == 0 for r in set(rows) | helpers),
            "forest register does not enter in the zero frame")
    require(all(op[-1] == 0 for op in word["precondition"]),
            "precondition changes the frame used by the forest")
    return rows, helpers


def complete_graph(rows):
    targets = sorted(rows)
    edges = [(-1, t, 0, row_price(rows[t])) for t in targets]
    for offset, left in enumerate(targets):
        for right in targets[offset + 1:]:
            for sign in (-1, 1):
                price = row_price(row_difference(rows[left], rows[right], sign))
                edges.append((left, right, sign, price + 2 * len(primitive_word(Q(1)))))
    return edges


def prim_cost(nodes, edges):
    adjacency = {n: [] for n in nodes}
    for left, right, _, weight in edges:
        adjacency[left].append((right, weight))
        adjacency[right].append((left, weight))
    remaining = set(nodes)
    distance = {node: float("inf") for node in nodes}
    distance[-1] = 0
    result = 0
    while remaining:
        vertex = min(remaining, key=lambda n: (distance[n], n))
        require(distance[vertex] != float("inf"), "disconnected full graph")
        result += distance[vertex]
        remaining.remove(vertex)
        for neighbour, price in adjacency[vertex]:
            if neighbour in remaining:
                distance[neighbour] = min(distance[neighbour], price)
    return result


def check_tree(recipe, rows, graph):
    edges = [tuple(e) for e in recipe["edges"]]
    nodes = set(rows) | {-1}
    require(len(edges) == len(rows), "tree must have one edge per target")
    adjacency = {n: [] for n in nodes}
    prices = {(a, b, s): w for a, b, s, w in graph}
    for a, b, sign, weight in edges:
        key = (min(a, b), max(a, b), sign)
        require(key in prices and weight == prices[key], "incorrect edge or edge price")
        adjacency[a].append((b, sign, weight))
        adjacency[b].append((a, sign, weight))
    parent = {-1: None}
    order = []
    queue = deque([-1])
    while queue:
        a = queue.popleft()
        for b, sign, weight in sorted(adjacency[a]):
            if b == parent[a]:
                continue
            require(b not in parent, "cycle or repeated edge")
            parent[b] = a
            order.append((b, a, sign))
            queue.append(b)
    require(set(parent) == nodes, "disconnected recipe")
    cost = sum(e[3] for e in edges)
    require(cost == prim_cost(nodes, graph), "recipe cost differs from independent Prim optimum")
    # Check the MST cycle property for EVERY signed edge, including unused signs.
    maximum = {}
    for start in sorted(nodes):
        todo = [(start, None, 0)]
        while todo:
            node, previous, peak = todo.pop()
            maximum[start, node] = peak
            for neighbour, _, weight in adjacency[node]:
                if neighbour != previous:
                    todo.append((neighbour, node, max(peak, weight)))
    for a, b, _, weight in graph:
        require(weight >= maximum[a, b], "negative cycle-exchange opportunity")
    return order, cost


def forest_operations(order, rows):
    prepare = [(child, parent, Q(-sign)) for child, parent, sign in reversed(order)
               if parent != -1]
    inject = []
    for child, parent, sign in order:
        row = rows[child] if parent == -1 else row_difference(rows[child], rows[parent], sign)
        inject.extend((child, source, q) for source, q in sorted(row.items()))
    restore = [(child, parent, Q(sign)) for child, parent, sign in order if parent != -1]
    return prepare, inject, restore


def linear_replay(ops, registers, backward=False):
    state = {r: {r: Q(1)} for r in registers}
    for target, source, q in ops:
        if backward:
            target, source, q = source, target, -q
        require(target != source, "aliased shear")
        row = state[target].copy()
        for column, value in state[source].items():
            result = row.get(column, Q(0)) + q * value
            if result:
                row[column] = result
            else:
                row.pop(column, None)
        state[target] = row
    return state


def expected_map(rows, helpers, backward):
    state = {r: {r: Q(1)} for r in set(rows) | helpers}
    for target, row in rows.items():
        for source, q in row.items():
            if backward:
                state[source][target] = -q
            else:
                state[target][source] = q
    return state


def check_microcircuit(q):
    state = {name: {name: Q(1)} for name in ("S", "T", "W")}
    for op in primitive_word(q):
        tag, target, *rest = op
        if tag == "clear":
            state[target] = {}
        elif tag in ("double", "half"):
            factor = Q(2) if tag == "double" else Q(1, 2)
            state[target] = {k: v * factor for k, v in state[target].items()}
        else:
            factor = 1 if tag == "add" else -1
            for key, value in state[rest[0]].items():
                value = state[target].get(key, Q(0)) + factor * value
                if value:
                    state[target][key] = value
                else:
                    state[target].pop(key, None)
    require(state == {"S": {"S": Q(1)}, "T": {"T": Q(1), "S": q}, "W": {}},
            "coefficient primitive lowering failed on arbitrary S,T,W")


def verify(recipe, word):
    rows, helpers = rows_from_word(word)
    graph = complete_graph(rows)
    order, optimum = check_tree(recipe, rows, graph)
    prepare, inject, restore = forest_operations(order, rows)
    operations = prepare + inject + restore
    require(sum(len(primitive_word(q)) for _, _, q in operations) == optimum,
            "realization price differs from graph price")
    coefficients = sorted(set(q for _, _, q in operations))
    for q in coefficients:
        check_microcircuit(q)
    controls = []
    for backward in (False, True):
        orientation = "backward" if backward else "forward"
        expected = expected_map(rows, helpers, backward)
        require(linear_replay(operations, expected, backward) == expected,
                orientation + " arbitrary-input operator mismatch")
        for label, mutant in (
            ("omit_prepare", inject + restore),
            ("omit_restore", prepare + inject),
            ("wrong_injection_sign", prepare + [(inject[0][0], inject[0][1], -inject[0][2])] + inject[1:] + restore),
        ):
            require(linear_replay(mutant, expected, backward) != expected,
                    orientation + " failed to reject " + label)
            controls.append(orientation + ":" + label)
    bad_edges = [list(e) for e in recipe["edges"]]
    bad_edges[0][3] += 1
    try:
        check_tree({"edges": bad_edges}, rows, graph)
    except ValueError:
        controls.append("incorrect_edge_price")
    else:
        raise ValueError("incorrect edge price accepted")
    baseline = sum(row_price(row) for row in rows.values())
    return {
        "status": "PASS_INDEPENDENT_X4_TARGET_FOREST",
        "method": "Fraction symbolic maps; explicit Horner lists; Prim; all-edge cycle property",
        "targets": len(rows), "helpers": len(helpers), "arbitrary_input_columns": len(rows) + len(helpers),
        "signed_graph_edges": len(graph), "cycle_inequalities_checked": len(graph),
        "roots": sum(parent == -1 for _, parent, _ in order),
        "forest_edges": len(prepare), "scalar_macros": len(operations),
        "unique_microcircuit_coefficients": len(coefficients),
        "component_primitive_baseline": baseline, "component_primitive_optimum": optimum,
        "real_primitive_baseline": 2 * baseline, "real_primitive_optimum": 2 * optimum,
        "real_primitive_savings_each_orientation": 2 * (baseline - optimum),
        "orientations": ["forward", "backward"], "negative_controls": controls,
        "all_forest_registers_enter_in_zero_frame": True,
        "scope": "Exact finite compensation operator and forest-class optimum only; no full theorem or kappa claim.",
    }


def read_sources(path):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA256, "source archive pin mismatch")
    parsed = {}
    with tarfile.open(path, "r:gz") as archive:
        for name, digest in MEMBER_PINS.items():
            member = archive.extractfile(name)
            require(member is not None, "missing source member")
            payload = member.read()
            if name.endswith(".gz"):
                payload = gzip.decompress(payload)
            require(hashlib.sha256(payload).hexdigest() == digest, "source member pin mismatch")
            parsed[name] = json.loads(payload)
    word = parsed["native/local/CANONICAL-WORD.json.gz"]
    programs = parsed["native/local/LOCAL-PROGRAMS.json.gz"]
    begin = 1 + len(word["precondition"])
    for orientation in ("forward", "backward"):
        expected = []
        for _, target, source, numerator, denominator, frame in word["compensation"]:
            if orientation == "backward":
                target, source, numerator = source, target, -numerator
            expected.append(["scalar", ["add", ["L", target], ["L", source], numerator, denominator], frame])
        require(programs[orientation][0] == ["phase", "zero_frame_precondition"], "wrong initial phase")
        require(programs[orientation][begin:begin + len(expected)] == expected,
                "canonical compensation/local program binding mismatch")
        require(programs[orientation][begin + len(expected)] == ["phase", "entry_adapters"],
                "compensation boundary mismatch")
    return word, parsed["native/local/LOCAL-CHECKS.json"]


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe", type=Path, default=here / "RECIPE.json")
    parser.add_argument("--archive", type=Path,
                        default=here.parent / "community-frontier799-audit/integrated799-replay.tar.gz")
    args = parser.parse_args()
    word, checks = read_sources(args.archive)
    result = verify(json.loads(args.recipe.read_text()), word)
    result["archive_sha256"] = ARCHIVE_SHA256
    result["source_payload_sha256"] = MEMBER_PINS
    result["source_local_programs_compensation_bound"] = True
    result["inherited_full_real_primitive_bounds"] = {
        orientation: checks[orientation]["real_component_primitive_bound"] for orientation in checks}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
