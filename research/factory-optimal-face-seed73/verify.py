#!/usr/bin/env python3
"""Independent local rigidity audit. Prepared for @ToikY with Codex assistance.
Apache-2.0. Imports no predecessor implementation. See SOURCES.json.
"""
import hashlib
import json
from collections import Counter, deque
from fractions import Fraction as Q
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def reject(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def load_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    objects = []
    for entry in manifest["sources"]:
        data = (HERE / entry["file"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "source pin")
        objects.append(json.loads(data))
    return objects[0]["replacement"], objects[1]


def power(q):
    q = abs(q)
    n, d = q.numerator, q.denominator
    require(n > 0 and n & (n - 1) == 0 and d & (d - 1) == 0, "dyadic power")
    return n.bit_length() - d.bit_length()


def topology(word):
    # Logical rows y evolve through unit additions; physical rows are 2**p * y.
    diagonal = [Q(1)] * 8
    adds = []
    for op in word:
        if op[0] == "scale":
            diagonal[op[1]] *= Q(op[2], op[3])
        else:
            require(op[0] == "add", "macro tag")
            t, s = op[1:3]
            require(0 <= t < 8 and 0 <= s < 8 and t != s, "macro registers")
            coefficient = Q(op[3], op[4]) * diagonal[s] / diagonal[t]
            adds.append([t, s, power(coefficient), 1 if coefficient > 0 else -1])
    ends = [power(q) for q in diagonal]
    signs = [1 if q > 0 else -1 for q in diagonal]
    require(len(adds) == 26, "26-add scope")
    # Derive each register path separately, rather than copying the producer's
    # interleaved edge builder. Stable sorting restores its documented flow order.
    paths = [[] for _ in range(8)]
    for j, (t, s, e, _) in enumerate(adds):
        paths[t].append((j, 0, 0))
        paths[s].append((j, e, 1))
    edges = []
    for r, events in enumerate(paths):
        a, u = -1, 0
        for b, v, slot in events:
            edges.append((2 * b + slot, a, b, u - v, r))
            a, u = b, v
        edges.append((52 + r, a, -1, u - ends[r], r))
    edges.sort()
    require([x[0] for x in edges] == list(range(60)), "edge order")
    return adds, ends, signs, [list(x[1:]) for x in edges]


def audit_dual(edges, flow):
    require(len(flow) == len(edges), "flow size")
    divergence = [0] * 26
    bound = 0
    for (a, b, c, _), f in zip(edges, flow):
        require(type(f) is int and abs(f) <= 1, "dual capacity")
        if a != -1:
            divergence[a] -= f
        if b != -1:
            divergence[b] += f
        bound -= f * c
    require(divergence == [0] * 26, "dual conservation")
    require(bound == 9, "dual bound")
    return bound


def anchored_tree(edges, flow, allowed=None):
    adjacency = {i: [] for i in range(-1, 26)}
    for i, (a, b, c, _) in enumerate(edges):
        if flow[i] == 0 and (allowed is None or i in allowed):
            adjacency[a].append((b, c, i))
            adjacency[b].append((a, -c, i))
    levels = {-1: 0}
    queue = deque([-1])
    tree = []
    while queue:
        a = queue.popleft()
        for b, c, i in adjacency[a]:
            if b in levels:
                require(levels[b] == levels[a] + c, "zero-edge consistency")
            else:
                levels[b] = levels[a] + c
                tree.append({"edge": i, "parent": a, "child": b})
                queue.append(b)
    require(len(levels) == 27, "zero-edge graph is not anchored and connected")
    return [levels[j] for j in range(26)], tree


def residuals(edges, levels):
    value = lambda j: Q(0) if j == -1 else Q(levels[j])
    return [value(b) - value(a) - c for a, b, c, _ in edges]


def objective(edges, levels):
    return sum(map(abs, residuals(edges, levels)))


def check_optimal(edges, flow, levels):
    require(len(levels) == 26, "level size")
    d = residuals(edges, levels)
    require(sum(map(abs, d)) == 9, "nonoptimal levels")
    require(all(abs(x) == f * x for x, f in zip(d, flow)), "dual slack")


def compile_word(adds, ends, signs, levels):
    require(all(type(x) is int for x in levels), "physical binary levels must be integers")
    current = [0] * 8
    out = []
    def shift(r, value):
        delta = value - current[r]
        out.extend([["double" if delta > 0 else "halve", r]] * abs(delta))
        current[r] = value
    for j, (t, s, e, sign) in enumerate(adds):
        shift(t, levels[j])
        shift(s, levels[j] + e)
        out.append(["add" if sign > 0 else "subtract", t, s])
    for r in range(8):
        shift(r, ends[r])
        if signs[r] < 0:
            out.append(["negate", r])
    return out


def inverse(word):
    tags = {"add": "subtract", "subtract": "add", "double": "halve",
            "halve": "double", "negate": "negate", "scale": "scale"}
    out = []
    for op in reversed(word):
        x = list(op)
        if x[0] == "add" and len(x) > 3:
            x[3] = -x[3]
        elif x[0] == "scale":
            x[2], x[3] = x[3], x[2]
        else:
            x[0] = tags[x[0]]
        out.append(x)
    return out


def transpose_word(word):
    out = []
    for op in reversed(word):
        x = list(op)
        if x[0] in ("add", "subtract"):
            x[1], x[2] = x[2], x[1]
        out.append(x)
    return out


def orientations(word):
    inv = inverse(word)
    return {"main": word, "cleanup": inv,
            "dual_main": transpose_word(inv), "dual_cleanup": transpose_word(word)}


def replay(word):
    # Dense exact matrices include all 8 arbitrary input columns at every prefix.
    matrix = [[Q(i == j) for j in range(8)] for i in range(8)]
    peak, depth = Q(1), 0
    for op in word:
        tag, t = op[:2]
        if tag == "scale":
            q = Q(op[2], op[3])
            matrix[t] = [q * x for x in matrix[t]]
        elif tag in ("double", "halve", "negate"):
            q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            matrix[t] = [q * x for x in matrix[t]]
        else:
            require(tag in ("add", "subtract"), "replay tag")
            s = op[2]
            q = Q(op[3], op[4]) if len(op) > 3 else Q(1 if tag == "add" else -1)
            matrix[t] = [x + q * y for x, y in zip(matrix[t], matrix[s])]
        peak = max(peak, max(sum(map(abs, row)) for row in matrix))
        for row in matrix:
            for x in row:
                require(x.denominator & (x.denominator - 1) == 0, "dyadic prefix")
                depth = max(depth, x.denominator.bit_length() - 1)
    return matrix, {"peak_row_l1": str(peak), "fractional_depth": depth}


def main(write=False):
    word, supplied = load_sources()
    adds, ends, signs, edges = topology(word)
    flow = supplied["dual_flow"]
    audit_dual(edges, flow)
    levels, tree = anchored_tree(edges, flow)
    require(levels == supplied["levels"], "unique optimum disagrees with source")
    check_optimal(edges, flow, levels)
    require(len(tree) == 26, "tree rank")
    # Balanced in/out degrees imply sum(d)=5 for every level vector.
    incidence = [0] * 26
    for a, b, c, r in edges:
        if a != -1:
            incidence[a] -= 1
        if b != -1:
            incidence[b] += 1
    require(incidence == [0] * 26 and sum(e[2] for e in edges) == -5, "parity premise")
    primitives = compile_word(adds, ends, signs, levels)
    require(primitives == supplied["primitives"] and len(primitives) == 37, "primitive witness")
    profiles = {}
    for name, program in orientations(primitives).items():
        matrix, stats = replay(program)
        expected, _ = replay(orientations(word)[name])
        require(matrix == expected, "boundary matrix " + name)
        profiles[name] = stats
    costs = Counter()
    for j in range(26):
        for delta in (-1, 1):
            changed = levels.copy()
            changed[j] += delta
            cost = objective(edges, changed)
            require(cost.denominator == 1 and cost % 2 == 1 and cost >= 11, "integer cost gap")
            costs[str(cost)] += 1
            reject(lambda: check_optimal(edges, flow, changed), "changed level")
        # Rational samples exercise the all-real gap identity; the theorem's
        # quantification follows from the connected tree, not these samples.
        for delta in (Q(-1, 2), Q(1, 2)):
            changed = levels.copy()
            changed[j] += delta
            d = residuals(edges, changed)
            gap = objective(edges, changed) - 9
            require(gap == sum(abs(x) - f * x for x, f in zip(d, flow)), "gap identity")
            require(gap >= max(abs(Q(x) - y) for x, y in zip(changed, levels)), "stability")
    sharp = levels.copy()
    sharp[0] -= 1
    require(objective(edges, sharp) == 11, "sharp integer gap witness")
    bad_flow = flow.copy(); bad_flow[0] = 0
    reject(lambda: audit_dual(edges, bad_flow), "unbalanced flow")
    bad_capacity = flow.copy(); bad_capacity[0] = 2
    reject(lambda: audit_dual(edges, bad_capacity), "flow capacity")
    unanchored = {i for i, (a, b, _, _) in enumerate(edges) if a != -1 and b != -1}
    reject(lambda: anchored_tree(edges, flow, unanchored), "missing boundary anchor")
    truncated = {x["edge"] for x in tree[:-1]}
    reject(lambda: anchored_tree(edges, flow, truncated), "incomplete spanning tree")
    target, _ = replay(primitives)
    for name, mutant in [("missing shift", primitives[1:]),
                         ("missing sign", primitives[:-1]),
                         ("missing addition", primitives[:1] + primitives[2:])]:
        reject(lambda p=mutant: require(replay(p)[0] == target, "boundary changed"), name)
    result = {"format": "factory-optimal-face-seed73-v1", "new_kappa": False,
              "normalized_additions": adds, "final_exponents": ends, "final_signs": signs,
              "distance_edges": edges, "dual_lower_bound": 9,
              "zero_flow_edges": [i for i, f in enumerate(flow) if f == 0],
              "anchored_spanning_tree": tree, "unique_real_optimum": levels,
              "optimal_integer_gauges": 1, "next_integer_cost": 11,
              "signed_unit_perturbation_costs": dict(sorted(costs.items())),
              "sum_residuals": 5, "local_prefixes": profiles,
              "primitive_count": 37, "paid_exit_work_clear": 1,
              "controls": {"nonoptimal_integer_levels": 52, "rational_gap_samples": 52,
                           "flow_anchor_tree_rejections": 4, "boundary_rejections": 3}}
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(json.loads(path.read_text()) == result, "certificate mismatch")
    print("PASS_FACTORY_OPTIMAL_FACE unique_real_gauge=1 shifts=9 next_integer_cost=11 orientations=4 no_new_kappa")


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--write-certificate"]), "arguments")
    main(bool(sys.argv[1:]))
