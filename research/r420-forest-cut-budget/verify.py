#!/usr/bin/env python3
"""Independent exact checker: data only; never imports the constructor.

Symbolic bitsets check all 660 independent input columns, including dirty helpers.
Tree optimality is certified by the cycle property, not by rerunning an MST solver.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from functools import lru_cache
from math import gcd, isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
SOURCE_FILE_SHA256 = "9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784"
SOURCE_CONTENT_SHA256 = "e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2"
V, R, N = 120, 420, 660


class Reject(ValueError):
    """A concrete certificate, circuit, or provenance check failed."""


def need(condition, message):
    if not condition:
        raise Reject(message)


def digest(word):
    return hashlib.sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_word(path):
    with gzip.open(path, "rt") if str(path).endswith(".gz") else open(path) as stream:
        return json.load(stream)


def pinned_source(path=SOURCE):
    word = read_word(path)
    need(digest(word) == SOURCE_CONTENT_SHA256, "source canonical SHA256 mismatch")
    return word


def reduce_row(row, basis):
    row = list(row)
    for pivot, vector in basis:
        if row[pivot]:
            a, b = row[pivot], vector[pivot]
            row = [b * x - a * y for x, y in zip(row, vector)]
            divisor = 0
            for x in row:
                divisor = gcd(divisor, x)
            if divisor:
                row = [x // divisor for x in row]
    return row


def geometry(word):
    """Exact integer elimination computes rational frame spans and closure."""
    need((word["v"], word["R"], word["h"], word["form"]) == (V, R, 8, "<x,y>/2"),
         "unexpected R420 header")
    lines = word["lines"]
    need(len(lines) == V and all(len(row) == 8 for row in lines), "bad label dimensions")
    dimensions, sets = [], []
    for frame in word["frames"]:
        need(len(set(frame)) == len(frame) and all(type(i) is int and 0 <= i < V for i in frame),
             "bad frame membership")
        basis = []
        for i in frame:
            row = reduce_row(lines[i], basis)
            if any(row):
                basis.append((next(k for k, x in enumerate(row) if x), row))
                basis.sort()
        closed = {i for i, row in enumerate(lines) if not any(reduce_row(row, basis))}
        need(closed == set(frame), "frame is not closed")
        dimensions.append(len(basis))
        sets.append(closed)
    need(dimensions.count(0) == dimensions.count(8) == 1, "nonunique zero/full frame")
    need(len(word["start"]) == len(word["final"]) == N, "bad register boundary size")
    for register, frame in enumerate(word["start"]):
        need(type(frame) is int and 0 <= frame < len(sets), "invalid start frame")
        need(sets[frame] == ({register} if register < V else set()), "wrong initial frame")
    for register, frame in enumerate(word["final"]):
        need(type(frame) is int and 0 <= frame < len(sets), "invalid final frame")
        if V <= register < 2 * V:
            target = register - V
            expected = {i for i in range(V) if sum(a * b for a, b in zip(lines[i], lines[target])) == 0}
            need(sets[frame] == expected, "target final frame is not its perpendicular")
        else:
            need(dimensions[frame] == 8, "source/helper final frame not full")
    return dimensions, sets


def gate_shape(gate, frame_count):
    need(isinstance(gate, list) and len(gate) == 3, "malformed gate")
    frame, dst, srcs = gate
    need(type(frame) is int and 0 <= frame < frame_count, "invalid gate frame")
    need(isinstance(srcs, list) and srcs, "empty/malformed gate sources")
    operands = [dst] + srcs
    need(all(type(r) is int and 0 <= r < N for r in operands), "invalid gate register")
    need(len(set(operands)) == len(operands), "duplicate/self gate operand")


def scalar_replay(word, sections):
    """Return the complete linear map, using independent arbitrary input symbols."""
    values = [1 << i for i in range(N)]
    for section in sections:
        if section == "scatter":
            copies = [values[q] for q in word["ret"]]
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[V + t] ^= copies[k]
        else:
            for gate in word[section]:
                gate_shape(gate, len(word["frames"]))
                _, dst, srcs = gate
                for src in srcs:
                    values[dst] ^= values[src]
    return values


def kernel(word):
    """Derive K from A/scatter/B, independently of both source and candidate D."""
    raw = scalar_replay(word, ("A", "scatter", "B"))
    target_mask = ((1 << V) - 1) << V
    source_mask = (1 << V) - 1
    helper_mask = ((1 << R) - 1) << (2 * V)
    for r in range(N):
        if V <= r < 2 * V:
            need(raw[r] & target_mask == 1 << r, "raw target block is not identity")
            need(raw[r] & source_mask == 1 << (r - V), "raw source-to-target block is not identity")
        else:
            need(raw[r] & target_mask == 0, "raw target-to-source/helper leakage")
    return [raw[V + t] & helper_mask for t in range(V)]


def check_d(word, kernels):
    zero = word["frames"].index([])
    for gate in word["D"]:
        gate_shape(gate, len(word["frames"]))
        frame, dst, srcs = gate
        need(frame == zero and V <= dst < 2 * V and all(s >= V for s in srcs),
             "D must stay at frame zero, write targets, and read targets/helpers")
    actual = scalar_replay(word, ("D",))
    for r in range(N):
        expected = (1 << r) ^ (kernels[r - V] if V <= r < 2 * V else 0)
        need(actual[r] == expected, "D endpoint mismatch at register %d" % r)
    return sum(len(g[2]) for g in word["D"])


def whole_word(word, geom):
    """Replay all scalar columns and the complete MOVE/COPY/ERASE path."""
    dimensions, frame_sets = geom
    cur = list(word["start"])
    path, events, histogram = [], [], Counter()
    zero = dimensions.index(0)

    def move(register, frame):
        old = cur[register]
        if old == frame:
            return
        rank = dimensions[frame] - dimensions[old]
        need(rank > 0 and frame_sets[old] <= frame_sets[frame], "illegal frame climb")
        path.append(("MOVE", register, old, frame, rank))
        histogram[rank] += 1
        cur[register] = frame

    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            need(len(word["scatter"]) == V, "scatter must have120 rows")
            need(len(set(word["ret"])) == len(word["ret"]) == 9, "invalid retained totals")
            need(all(type(q) is int and 2 * V <= q < N for q in word["ret"]), "retained total not helper")
            need(all(cur[V + t] == zero for t in range(V)), "target left zero before scatter")
            for row in word["scatter"]:
                need(len(set(row)) == len(row) and all(type(k) is int and 0 <= k < 9 for k in row),
                     "invalid scatter indices")
            for k, q in enumerate(word["ret"]):
                path.append(("COPY", q, N, cur[q], zero, dimensions[cur[q]]))
                histogram[dimensions[cur[q]]] += 1
                events.append(("COPY", N, q))
                for t, row in enumerate(word["scatter"]):
                    if k in row:
                        events.append(("ADD", V + t, N))
                events.append(("ERASE", N, q))
                path.append(("ERASE", q, N, cur[q], zero, 0))
        else:
            for gate in word[section]:
                gate_shape(gate, len(dimensions))
                frame, dst, srcs = gate
                for r in [dst] + srcs:
                    move(r, frame)
                events.extend(("ADD", dst, src) for src in srcs)
    for register, frame in enumerate(word["final"]):
        move(register, frame)
    values = [1 << r for r in range(N)] + [0]
    active = None
    for kind, dst, src in events:
        if kind == "COPY":
            need(active is None and dst == N, "invalid copy opening")
            values[N], active = values[src], src
        elif kind == "ERASE":
            need(active == src and values[N] == values[src], "invalid copy closure")
            values[N], active = 0, None
        else:
            need(dst != N and (src != N or active is not None), "invalid temporary use")
            need(dst != active, "retained source changed in copy window")
            values[dst] ^= values[src]
    need(active is None and values[N] == 0, "unclosed temporary")
    for r in range(N):
        need(values[r] == ((1 << r) ^ (1 << (r - V) if V <= r < 2 * V else 0)),
             "full endpoint mismatch at register %d" % r)
    adds = sum(kind == "ADD" for kind, _, _ in events)
    return {"columns": N, "additions": adds, "records": adds + len(path),
            "paid_histogram": dict(sorted(histogram.items())),
            "rank_mass": sum(k * v for k, v in histogram.items()),
            "path": path, "events": events}


def positive_prefix(events):
    """Cancellation-free signed row bounds in native exporter scalar-event order."""
    maxima = []
    for reverse in (False, True):
        norms, largest, active = [1] * (N + 1), 1, None
        for kind, dst, src in reversed(events) if reverse else events:
            if reverse and kind != "ADD":
                kind = "ERASE" if kind == "COPY" else "COPY"
            if kind == "ADD":
                norms[dst] += norms[src]
                largest = max(largest, norms[dst])
            elif kind == "COPY":
                need(active is None, "prefix copy opening")
                norms[N], active = norms[src], src
            else:
                need(active == src, "prefix copy closure")
                norms[N], active = 0, None
        need(active is None, "prefix unclosed copy")
        maxima.append(largest)
    forward, reverse = maxima
    payload = 64 * forward ** 3 * reverse ** 2
    return {"forward": forward, "reverse": reverse, "payload_upper": payload,
            "payload_bits": payload.bit_length(), "below_2_pow_104": payload < 2 ** 104}


def cut_budget(word, recipe, kernels, replay):
    """Independent DP lower bound over all cuts of the pinned minimum tree.

    Fixed source/helper forward norms give a necessary reverse cap for every
    feasible cut. A candidate attaining this cost and passing full prefix replay
    proves cut-class optimality without assuming forward norms are constant.
    """
    events, parent = replay["events"], recipe["mst_parents"]
    need(all(V <= d < 2 * V or all(not V <= s < 2 * V for s in srcs)
             for phase in ("A", "B", "C") for _, d, srcs in word[phase]), "target feeds source/helper")
    fixed_forward, norms = 1, [1] * (N + 1)
    for kind, dst, src in events:
        if kind == "ADD":
            norms[dst] += norms[src]
            if not V <= dst < 2 * V:
                fixed_forward = max(fixed_forward, norms[dst])
        else:
            norms[N] = norms[src] if kind == "COPY" else 0
    cap = isqrt(((1 << 104) - 1) // (64 * fixed_forward ** 3))
    base = [1] * (N + 1)
    d_count = sum(len(g[2]) for g in word["D"])
    for kind, dst, src in reversed(events[d_count:]):
        if kind == "ADD":
            base[dst] += base[src]
        else:
            base[N] = base[src] if kind == "ERASE" else 0
    children = [[] for _ in range(V + 1)]
    for i, p in enumerate(parent):
        children[p].append(i)
    root_norm, edge_norm = [], []
    for i, p in enumerate(parent):
        root_norm.append(base[V + i] + sum(base[s] for s in range(2 * V, N) if kernels[i] >> s & 1))
        delta = kernels[i] ^ (kernels[p] if p != V else 0)
        edge_norm.append(base[V + i] + (base[V + p] if p != V else 0) +
                         sum(base[s] for s in range(2 * V, N) if delta >> s & 1))

    @lru_cache(None)
    def endpoint(i, root):
        return root_norm[i] if i == root else edge_norm[i] + endpoint(parent[i], root)

    @lru_cache(None)
    def cost(i, root):
        if endpoint(i, root) > cap:
            return 10 ** 9
        local = kernels[i].bit_count() if i == root else (kernels[i] ^ kernels[parent[i]]).bit_count() + 2
        return local + sum(min(cost(child, root), cost(child, child)) for child in children[i])

    optimum = sum(cost(root, root) for root in children[V])
    selected_cost = sum(len(g[2]) for g in word["D"])
    prefix = positive_prefix(events)
    return {"scope": "all edge cuts of the certified seed-6 minimum tree",
            "fixed_source_helper_forward_lower_bound": fixed_forward, "necessary_reverse_cap": cap,
            "minimum_D_additions": optimum, "dynamic_states": cost.cache_info().currsize,
            "selected_feasible": prefix["below_2_pow_104"],
            "selected_attains_cut_class_optimum": prefix["below_2_pow_104"] and selected_cost == optimum}


def check_tree(recipe, kernels, minimal=True):
    """Validate a spanning tree then all non-tree edges by the cycle criterion."""
    parent = recipe["parents"]
    need(len(parent) == V and all(type(p) is int and 0 <= p <= V for p in parent), "invalid parent")
    need(all(p != i for i, p in enumerate(parent)), "self parent")
    adjacency = [[] for _ in range(V + 1)]

    def weight(i, j):
        return kernels[min(i, j)].bit_count() if V in (i, j) else (kernels[i] ^ kernels[j]).bit_count() + 2

    def key(i, j):
        i, j = sorted((i, j))
        return weight(i, j), hashlib.sha256(f"6:{i}:{j}".encode("ascii")).hexdigest(), i, j

    expected_edges = {tuple(sorted((i, p))) for i, p in enumerate(parent)}
    need(len(expected_edges) == V, "repeated tree edge")
    for i, p in enumerate(parent):
        cost = weight(i, p)
        adjacency[i].append((p, cost))
        adjacency[p].append((i, cost))
    depths, stack = {V: 0}, [V]
    while stack:
        i = stack.pop()
        for j, _ in adjacency[i]:
            if j not in depths:
                depths[j] = depths[i] + 1
                stack.append(j)
    need(len(depths) == V + 1, "parents contain cycle/disconnected component")
    need(all(depths[i] == depths[p] + 1 for i, p in enumerate(parent)), "parents point away from dummy root")
    listed = recipe["mst_edges"]
    need(len(listed) == V, "wrong number of listed MST edges")
    actual_edges = set()
    for edge in listed:
        i, j, cost = edge["u"], edge["v"], edge["weight"]
        need(type(i) is int and type(j) is int and 0 <= i < j <= V, "invalid listed edge")
        need(type(cost) is int and cost == weight(i, j), "underpriced/mispriced edge")
        actual_edges.add((i, j))
    need(actual_edges == expected_edges, "listed edges do not match parents")
    checked, slack_min = 0, None
    for start in range(V + 1) if minimal else ():
        maxima, visit = {start: (-1, "", -1, -1)}, [start]
        while visit:
            i = visit.pop()
            for j, cost in adjacency[i]:
                if j not in maxima:
                    maxima[j] = max(maxima[i], key(i, j))
                    visit.append(j)
        for end in range(start + 1, V + 1):
            if (start, end) not in expected_edges:
                slack = weight(start, end) - maxima[end][0]
                need(slack >= 0, "nonminimal tree: cycle property violated")
                need(key(start, end) >= maxima[end], "seed-6 tie certificate violated")
                slack_min = slack if slack_min is None else min(slack_min, slack)
                checked += 1
    return {"total_weight": sum(weight(i, p) for i, p in enumerate(parent)),
            "non_tree_edges_checked": checked, "minimum_cycle_slack": slack_min,
            "roots": sum(p == V for p in parent), "target_edges": sum(p != V for p in parent),
            "maximum_target_depth": max(depths.values()) - 1}


def check_recipe(source, candidate, recipe, kernels):
    need(recipe["format"] == "r420-target-forest/1" and recipe["dummy_vertex"] == V,
         "invalid recipe format/dummy")
    need(recipe["source"]["file_sha256"] == SOURCE_FILE_SHA256 and
         recipe["source"]["canonical_sha256"] == SOURCE_CONTENT_SHA256, "malformed source pin")
    need(recipe["source"]["path"] == "research/e8-bit-r420/data/bitE8mut-r420.json.gz" and
         recipe["source"]["base_commit"] == "66849e1475c930fd7732b1a0067ffee7e1e95f60", "wrong source provenance")
    need(type(recipe["seed"]) is int and recipe["seed"] == 6, "wrong assignment seed")
    need(recipe["algorithm"] == "Kruskal, ascending (weight, SHA256(ASCII seed:u:v), u, v)", "wrong algorithm declaration")
    need(recipe["optimality_scope"] == "The uncut MST minimizes XOR count within the rooted target-forest "
         "construction; cut variants have no unrestricted optimality claim.", "unsupported optimality claim")
    need(recipe["candidate_canonical_sha256"] == digest(candidate), "candidate digest mismatch")
    mst = check_tree({"parents": recipe["mst_parents"], "mst_edges": recipe["mst_edges"]}, kernels)
    tree = check_tree({"parents": recipe["parents"], "mst_edges": recipe["tree_edges"]}, kernels, minimal=False)
    cuts = recipe["cuts"]
    need(all(type(i) is int and 0 <= i < V for i in cuts) and cuts == sorted(set(cuts)), "invalid cut list")
    need(all(recipe["mst_parents"][i] != V for i in cuts), "cut is already a root")
    expected_parent = [V if i in cuts else p for i, p in enumerate(recipe["mst_parents"])]
    need(recipe["parents"] == expected_parent, "selected tree is not declared cut of minimum tree")
    parent, order = recipe["parents"], recipe["child_before_parent_order"]
    need(sorted(order) == list(range(V)), "bad preparation order")
    position = {t: i for i, t in enumerate(order)}
    need(all(p == V or position[i] < position[p] for i, p in enumerate(parent)), "not children before parents")
    need(recipe["roots"] == [i for i, p in enumerate(parent) if p == V], "wrong root list")
    zero = source["frames"].index([])
    prepare = [[zero, V + i, [V + parent[i]]] for i in order if parent[i] != V]
    inject, injection_order = [], []
    for i, p in enumerate(parent):
        residual = kernels[i] ^ (kernels[p] if p != V else 0)
        sources = [r for r in range(2 * V, N) if residual >> r & 1]
        if sources:
            inject.append([zero, V + i, sources])
            injection_order.append(i)
    e, j = len(prepare), len(inject)
    need(recipe["D_boundaries"] == {"prepare": [0, e], "inject": [e, e + j],
         "unprepare": [e + j, 2 * e + j], "injection_order": injection_order}, "invalid D boundaries")
    need(candidate["D"] == prepare + inject + list(reversed(prepare)), "D does not implement claimed recipe")
    need(sum(len(g[2]) for g in candidate["D"]) == tree["total_weight"], "circuit cost does not equal tree weight")
    vertices = [{"vertex": i, "target_register": V + i,
                 "kernel_weight": kernels[i].bit_count()} for i in range(V)]
    vertices.append({"vertex": V, "target_register": None, "kernel_weight": 0})
    need(recipe["vertices"] == vertices, "declared kernels do not match raw word")
    levels = []
    for i in range(V):
        level, current = 0, i
        for _ in range(V + 1):
            if current == V:
                break
            current, level = parent[current], level + 1
        levels.append(level)
    need(recipe["levels_from_dummy"] == levels and recipe["forest_height_edges"] == max(levels) - 1,
         "incorrect declared depth")
    need(recipe["metrics"]["mst_weight"] == mst["total_weight"], "mispriced minimum tree cost")
    need(recipe["metrics"]["tree_weight"] == tree["total_weight"], "mispriced selected tree cost")
    need(recipe["metrics"]["xor_saved"] == sum(len(g[2]) for g in source["D"]) - tree["total_weight"],
         "incorrect declared savings")
    for label, word in (("source", source), ("candidate", candidate)):
        scatter = [[0, V + t, [word["ret"][k] for k in row]] for t, row in enumerate(word["scatter"]) if row]
        for section, gates in (("D", word["D"]), ("full", word["D"] + word["A"] + scatter + word["B"] + word["C"])):
            data, wires, count = [0] * N, [0] * N, 0
            for _, dst, srcs in gates:
                for src in srcs:
                    count += 1
                    data[dst] = max(data[dst], data[src]) + 1
                    wires[dst] = wires[src] = max(wires[dst], wires[src]) + 1
            measured = {"xor_count": count, "gate_records": len(gates),
                        "ordered_data_dependency_depth": max(data), "ordered_wire_disjoint_depth": max(wires)}
            need(recipe["metrics"][label][section] == measured, "incorrect declared circuit metrics")
    return {"minimum_tree": mst, "selected_tree": tree, "cuts": cuts}


def verify(source, candidate, recipe):
    need(digest(source) == SOURCE_CONTENT_SHA256, "source canonical SHA256 mismatch")
    need(digest({k: v for k, v in source.items() if k != "D"}) ==
         digest({k: v for k, v in candidate.items() if k != "D"}), "changed word outside D")
    geom = geometry(source)
    kernels = kernel(source)
    source_d, candidate_d = check_d(source, kernels), check_d(candidate, kernels)
    tree = check_recipe(source, candidate, recipe, kernels)
    old, new = whole_word(source, geom), whole_word(candidate, geom)
    need(old["path"] == new["path"], "MOVE/COPY/ERASE path changed")
    need(old["paid_histogram"] == new["paid_histogram"] == {1: 1320, 2: 1440, 4: 60, 5: 120, 8: 9},
         "paid histogram changed")
    need(old["rank_mass"] == new["rank_mass"] == 5112, "rank mass changed")
    return {"status": "PASS", "source_sha256": digest(source), "candidate_sha256": digest(candidate),
            "D_additions": {"source": source_d, "candidate": candidate_d, "saved": source_d - candidate_d},
            "tree_certificate": tree, "identical_frame_path": True,
            "source": {k: v for k, v in old.items() if k not in ("path", "events")},
            "candidate": {k: v for k, v in new.items() if k not in ("path", "events")},
            "positive_prefix": {"source": positive_prefix(old["events"]), "candidate": positive_prefix(new["events"])},
            "cut_budget": cut_budget(candidate, recipe, kernels, new)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--candidate", type=Path, default=HERE / "data/word.json.gz")
    parser.add_argument("--recipe", type=Path, default=HERE / "data/recipe.json")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--expect-prefix-rejection", action="store_true",
                        help="verify the uncut optimum calibration and require its expected prefix failure")
    args = parser.parse_args()
    try:
        result = verify(pinned_source(args.source), read_word(args.candidate), json.loads(args.recipe.read_text()))
        if args.expect_prefix_rejection:
            need(not result["tree_certificate"]["cuts"] and not result["positive_prefix"]["candidate"]["below_2_pow_104"],
                 "expected uncut optimum prefix rejection not observed")
            result["status"] = "PASS_CIRCUIT_AND_TREE_CALIBRATION_EXPECTED_PREFIX_REJECTION"
        else:
            need(result["positive_prefix"]["candidate"]["below_2_pow_104"], "candidate exceeds unchanged104-bit prefix cap")
            need(result["cut_budget"]["selected_attains_cut_class_optimum"], "candidate is not an optimal feasible tree cut")
            result["status"] = "PASS_ADMITTED_CIRCUIT_AND_OPTIMAL_TREE_CUT"
    except (Reject, KeyError, TypeError, IndexError) as error:
        parser.exit(1, "REJECT: %s\n" % error)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
