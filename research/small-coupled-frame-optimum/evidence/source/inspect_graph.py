#!/usr/bin/env python3
"""Source-bound graph-size probe for published elimination theorem fit.

No candidate schedule or physical admission is produced. The retained source
construct function and frame-DAG implementation are authenticated and reused;
this is not an independent replay of their mathematical/physical correctness.
Prepared with OpenAI Codex assistance. Apache-2.0 for this diagnostic.
"""
from pathlib import Path
from fractions import Fraction as Q
from types import SimpleNamespace
from collections import Counter
import ast
import copy
import gzip
import hashlib
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "frozen"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load():
    manifest = json.loads((HERE / "SOURCE-MANIFEST.json").read_text())
    for entry in manifest:
        need(hashlib.sha256((FROZEN / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
             "Snapshot hash mismatch: " + entry["path"])
    source = FROZEN / "research/native-frame-carrying-swaps"
    data = json.loads(gzip.decompress((source / "SOURCE-WORD.json.gz").read_bytes()))
    module = ast.parse((source / "verify.py").read_text())
    construct = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == "construct")
    canonical = data["canonical"]
    def pointset(vectors):
        points = {0}
        for v in vectors:
            points |= {x ^ v for x in tuple(points)}
        return points
    namespace = {"c": canonical, "spaces": list(map(pointset, canonical["frames"])),
                 "Q": Q, "copy": copy, "V": SimpleNamespace(need=need)}
    # Execute only the already inspected, unchanged source construction function.
    exec(compile(ast.Module(body=[construct], type_ignores=[]), str(source / "verify.py"), "exec"), namespace)
    path = FROZEN / "research/carried-warp-frame-intervals/frame_dag.py"
    spec = importlib.util.spec_from_file_location("frozen_frame_dag", path)
    frame = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(frame)
    return data, namespace["construct"], frame


def domains_by_gap(max_gap):
    # Gaussian-binomial recurrence: subspaces of F2^d by dimension.
    rows = [[1]]
    for d in range(1, max_gap + 1):
        prev = rows[-1]
        rows.append([1] + [prev[k] + (2 ** (d-k)) * prev[k-1] for k in range(1, d)] + [1])
    return [sum(r) for r in rows]


def components(adjacency):
    unseen = set(adjacency)
    result = []
    while unseen:
        seed = min(unseen)
        found, queue = {seed}, [seed]
        unseen.remove(seed)
        while queue:
            v = queue.pop()
            for w in adjacency[v] & unseen:
                unseen.remove(w)
                found.add(w)
                queue.append(w)
        result.append(found)
    return sorted(result, key=lambda s: (-len(s), min(s)))


def elimination_bound(adjacency, component, domain_sizes):
    current = {v: adjacency[v] & component for v in component}
    order, max_width, max_states, total_states = [], 0, 0, 0
    while current:
        # Min current bucket cardinality; deterministic, not an optimal-width claim.
        def score(v):
            states = domain_sizes[v] * math.prod(domain_sizes[w] for w in current[v])
            return states, len(current[v]), v
        v = min(current, key=score)
        neighbors = sorted(current[v])
        states = score(v)[0]
        max_width = max(max_width, len(neighbors))
        max_states = max(max_states, states)
        total_states += states
        order.append(v)
        for w in neighbors:
            current[w].discard(v)
            current[w].update(set(neighbors) - {w})
        del current[v]
    return {"variables": len(component), "induced_width_upper": max_width,
            "maximum_bucket_assignments": max_states, "sum_bucket_assignments": total_states,
            "ordering": order}


def pair_submodularity_counterexample(graph, lower, upper, original, frame):
    variable = {i for i, (a, b) in enumerate(zip(lower, upper)) if a != b}
    for a in sorted(variable):
        if frame.dimension(upper[a])-frame.dimension(lower[a]) != 1:
            continue
        for b, _ in graph.children[a]:
            if b not in variable or frame.dimension(upper[b])-frame.dimension(lower[b]) != 1:
                continue
            choices = [(lower[a], lower[b]), (upper[a], lower[b]),
                       (lower[a], upper[b]), (upper[a], upper[b])]
            def feasible(av, bv):
                changed = {a: av, b: bv}
                for v in (a, b):
                    value = changed[v]
                    for p, columns in graph.parents[v]:
                        moved = frame.image(columns, changed.get(p, original[p]))
                        if moved & value != moved:
                            return False
                    for child, columns in graph.children[v]:
                        moved = frame.image(columns, value)
                        target = changed.get(child, original[child])
                        if moved & target != moved:
                            return False
                return True
            if all(feasible(av, bv) for av, bv in choices):
                gap = frame.dimension(lower[b])-frame.dimension(lower[a])
                need(gap >= 1, "Four feasible ascending pair choices require positive lower gap")
                multiplicity = sum(child == b for child, _ in graph.children[a])
                return {"a": a, "b": b, "lower_dimensions": [frame.dimension(lower[a]),frame.dimension(lower[b])],
                        "upper_dimensions": [frame.dimension(upper[a]),frame.dimension(upper[b])],
                        "edge_multiplicity": multiplicity, "all_other_contacts": "fixed at source original values",
                        "four_assignments_feasible": True,
                        "submodular_difference": f"{multiplicity}*(f({gap-1})+f({gap+1})-2*f({gap})) < 0 for strictly concave f",
                        "selected_subspaces_decimal": [[str(av), str(bv)] for av,bv in choices]}
    return None


def main():
    data, construct, frame = load()
    published = json.loads((FROZEN / "research/carried-warp-frame-intervals/RESULT.json").read_text())
    cardinality = domains_by_gap(9)
    result = {"status": "SOURCE_BOUND_GRAPH_STRUCTURE_ONLY", "pin": "ef2810fe43829960789f783e44ee6484d0368f09",
              "domain_cardinality_by_gap": cardinality, "directions": {}, "new_candidate_emitted": False}
    for direction, source_program in data["programs"].items():
        program, swaps, unequal = construct(source_program)
        need((swaps, unequal) == (534, 43), "Retained swap construction census")
        schedule = frame.NativeSchedule(data["canonical"], program)
        graph = schedule.graph
        lower, upper = graph.bounds()
        record = published["directions"][direction]
        need(len(graph.fixed) == record["graph_nodes"] and sum(map(len, graph.parents)) == record["graph_edges"],
             "Published graph census")
        variable = {i for i, (a,b) in enumerate(zip(lower, upper)) if a != b}
        gaps = {i: frame.dimension(upper[i])-frame.dimension(lower[i]) for i in variable}
        sizes = {i: cardinality[gaps[i]] for i in variable}
        adjacency = {v: set() for v in variable}
        for v in variable:
            for p, _ in graph.parents[v]:
                if p in variable:
                    adjacency[v].add(p)
                    adjacency[p].add(v)
        comps = components(adjacency)
        bounds = [elimination_bound(adjacency, c, sizes) for c in comps]
        report = {"all_nodes": len(graph.fixed), "variable_nodes": len(variable),
                  "variable_edges_simple": sum(map(len,adjacency.values()))//2,
                  "gap_histogram": dict(sorted(Counter(gaps.values()).items())),
                  "domain_size_histogram": dict(sorted(Counter(sizes.values()).items())),
                  "components": len(comps), "component_size_histogram": dict(sorted(Counter(map(len, comps)).items())),
                  "maximum_bucket_assignments": max(x["maximum_bucket_assignments"] for x in bounds),
                  "sum_bucket_assignments": sum(x["sum_bucket_assignments"] for x in bounds),
                  "max_induced_width_upper": max(x["induced_width_upper"] for x in bounds),
                  "submodularity_counterexample": pair_submodularity_counterexample(graph, lower, upper, schedule.original_values, frame),
                  "elimination_components": bounds}
        result["directions"][direction] = report
        print(direction, json.dumps({k:v for k,v in report.items() if k not in ('elimination_components','submodularity_counterexample')}, sort_keys=True), flush=True)
        print("actual_four_assignment_submodularity_counterexample", report["submodularity_counterexample"] is not None, flush=True)
    (HERE / "GRAPH-STRUCTURE.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__ == "__main__":
    main()
