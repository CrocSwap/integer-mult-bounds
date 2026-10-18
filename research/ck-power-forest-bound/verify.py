#!/usr/bin/env python3
"""CK forest bound with power-of-two weights. Apache-2.0.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
Finite core plus exact premises of the all-exponent proof in PROOF.md.
"""
import argparse
from collections import Counter, deque
import copy
from fractions import Fraction
from functools import cache
from pathlib import Path
import runpy
import subprocess
import sys

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need, same = C["need"], C["same"]


@cache
def price(a, b=4):
    q = Fraction(a, b)
    a, b = abs(q.numerator), q.denominator
    need(b & (b - 1) == 0, "dyadic coefficient")
    return 0 if not a else 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def source_rows(word):
    rows = {r: {} for r in range(112, 224)}
    for gate in word["compensation"]:
        need(len(gate) == 6 and gate[0] == "add", "source compensation operation")
        _, t, s, a, b, f = gate
        need(all(type(x) is int for x in gate[1:]), "typed source gate")
        need(t in rows and 224 <= s < 716 and f == 0, "source panel support/frame")
        need(word["start"][t] == word["start"][s] == 0, "panel entrance frame")
        q = 4 * Fraction(a, b)
        need(q.denominator == 1 and 0 < abs(q) <= 4, "quarter alphabet tail premise")
        need(s not in rows[t], "duplicate matrix cell")
        rows[t][s] = int(q)
    need(sum(map(len, rows.values())) == 8704, "CK panel size")
    return rows


def incremental(histogram, exponent, sign):
    numerator = sign * 2 ** max(exponent, 0)
    denominator = 2 ** max(-exponent, 0)
    old = sum(count * price(a) for (a, _), count in histogram.items())
    residual = sum(count * price(a * denominator - numerator * b, 4 * denominator)
                   for (a, b), count in histogram.items())
    return residual + 2 * price(numerator, denominator) - old


def census(rows):
    records, grouped = [], {e: [] for e in range(-3, 4)}
    row_minima = {}
    for child in sorted(rows):
        for parent in sorted(rows):
            if child == parent:
                continue
            left, right = rows[child], rows[parent]
            hist = Counter((left.get(j, 0), right.get(j, 0)) for j in left.keys() | right.keys())
            for e in range(-3, 4):
                for sign in (-1, 1):
                    delta = incremental(hist, e, sign)
                    record = [child, parent, e, sign, delta]
                    records.append(record)
                    grouped[e].append(record)
                    key = (child, e)
                    nominee = (delta, parent, sign)
                    row_minima[key] = min(row_minima.get(key, nominee), nominee)
    summary = {}
    for e, cases in grouped.items():
        values = [r[-1] for r in cases]
        if e:
            need(min(values) > 0, "nonunit root dominance failed")
        summary[str(e)] = {"cases": len(cases), "min_penalty_per_component": min(values),
                           "max_penalty_per_component": max(values),
                           "profitable": sum(x < 0 for x in values), "ties": sum(x == 0 for x in values),
                           "first_minimizer": next(r for r in cases if r[-1] == min(values))}
    return {"cases": len(records), "records_sha256": C["digest"](records), "by_exponent": summary,
            "row_minima": [[child, e, *row_minima[child, e]] for child, e in sorted(row_minima)]}, records


def tail_slope(a, b, negative):
    if not a and not b:
        return 0
    if not a:
        return int(negative)
    if not b:
        return int(not negative)
    return 1 + int(a * b < 0) + int(negative)


def tail_checks():
    records = []
    # The proof handles every k>=3. These are arithmetic checks of its finite
    # coefficient cases, including distant exponents, not an infinite replay.
    for negative in (False, True):
        for a in range(-4, 5):
            for b in range(-4, 5):
                slope = tail_slope(a, b, negative)
                anchor = price(8 * a + b, 2 ** (2 + 3 * negative))
                for k in (3, 4, 5, 8, 36, 64, 127):
                    need(price(a * 2 ** k + b, 2 ** (2 + k * negative)) == anchor + slope * (k - 3),
                         "affine tail identity")
                records.append([negative, a, b, anchor, slope])
    need(all(r[-1] >= 0 for r in records), "nonnegative entry slopes")
    return {"families": len(records), "tested_exponents": [3, 4, 5, 8, 36, 64, 127],
            "records_sha256": C["digest"](records), "basis_cost_slope": 2,
            "tail_base_exponent": 3}


def edge_list(rows):
    edges = [[sum(price(v) for v in row.values()), -1, t, 0] for t, row in rows.items()]
    for t, left in rows.items():
        for p, right in rows.items():
            if t < p:
                for sign in (-1, 1):
                    value = 8 + sum(price(left.get(j, 0) - sign * right.get(j, 0))
                                    for j in left.keys() | right.keys())
                    edges.append([value, t, p, sign])
    return edges


def tree_structure(edges, vertices):
    need(len(edges) == len(vertices) - 1, "spanning tree edge count")
    adj = {v: [] for v in vertices}
    for w, a, b, sign in edges:
        need(all(type(x) is int for x in (w, a, b, sign)) and a in adj and b in adj and a != b,
             "tree vertex/type")
        need(sign == 0 if a == -1 or b == -1 else sign in (-1, 1), "unit tree coefficient")
        adj[a].append((b, sign, w))
        adj[b].append((a, sign, w))
    parents, depth = {-1: None}, {-1: -1}
    pending = deque([-1])
    order = []
    while pending:
        vertex = pending.popleft()
        for child, sign, weight in sorted(adj[vertex]):
            if child == parents[vertex]:
                continue
            need(child not in parents, "tree cycle")
            parents[child], depth[child] = vertex, depth[vertex] + 1
            order.append((child, vertex, sign, depth[child]))
            pending.append(child)
    need(set(parents) == set(vertices), "disconnected tree")
    return adj, order


def unit_certificate(rows, recipe):
    edges = edge_list(rows)
    tree = recipe["tree_edges"]
    adj, order = tree_structure(tree, [-1, *rows])
    available = {tuple(x) for x in edges}
    need(all(tuple(x) in available for x in tree), "unpriced tree edge")
    maxima = {}
    for start in adj:
        queue = [(start, None, 0)]
        for v, previous, maximum in queue:
            maxima[start, v] = maximum
            for child, _, weight in adj[v]:
                if child != previous:
                    queue.append((child, v, max(maximum, weight)))
    slacks = [w - maxima[a, b] for w, a, b, _ in edges]
    need(min(slacks) >= 0, "MST cycle inequality")
    cost = sum(w for w, _, _, _ in tree)
    need(cost == 16364, "retained unit floor")
    preparation = [["add", t, p, -s, 1, 0] for t, p, s, _ in reversed(order) if p != -1]
    middle = []
    for t, p, sign, _ in order:
        row = rows[t] if p == -1 else {j: rows[t].get(j, 0) - sign * rows[p].get(j, 0)
                                       for j in rows[t].keys() | rows[p].keys()}
        for j, value in sorted(row.items()):
            if value:
                q = Fraction(value, 4)
                middle.append(["add", t, j, q.numerator, q.denominator, 0])
    restore = [[op, t, s, -a, b, f] for op, t, s, a, b, f in preparation[::-1]]
    same(preparation + middle + restore, recipe["compensation"], "retained panel recipe")
    need(sum(price(g[3], g[4]) for g in recipe["compensation"]) == cost, "complete forest gate cost")
    return {"floor_per_component": cost, "cycle_inequalities": len(edges), "min_cycle_slack": min(slacks),
            "cycle_slacks_sha256": C["digest"](slacks), "roots": sum(p == -1 for _, p, _, _ in order),
            "max_depth": max(d for _, _, _, d in order), "preparation": len(preparation),
            "residual": len(middle), "restoration": len(restore), "panel_macros": len(recipe["compensation"])}, order


def replay_panel(word, replacement):
    results = {}
    for dual in (False, True):
        images = []
        for panel in (word["compensation"], replacement):
            values = [{i: Fraction(1)} for i in range(716)]
            for _, t, s, a, b, f in panel:
                if dual:
                    t, s, a = s, t, -a
                q = Fraction(a, b)
                for j, value in list(values[s].items()):
                    new = values[t].get(j, 0) + q * value
                    if new:
                        values[t][j] = new
                    else:
                        values[t].pop(j, None)
            images.append(values)
        need(images[0] == images[1], "arbitrary-target panel operator")
        results["inverse_transpose" if dual else "forward"] = {"columns": 716, "output_rows": 716}
    return results


def source_invoice(word, programs, checks):
    totals = {}
    for name, events in programs.items():
        first = len(word["precondition"]) + 1
        expected = []
        for _, t, s, a, b, f in word["compensation"]:
            if name == "backward":
                t, s, a = s, t, -a
            expected.append(["scalar", ["add", ["L", t], ["L", s], a, b], f])
        same(events[first:first + len(expected)], expected, "canonical/emitted panel binding")
        need(events[first + len(expected)] == ["phase", "entry_adapters"], "source panel exit")
        total = 0
        for event in events:
            if event[0] != "scalar":
                continue
            op = event[1]
            if op[0] == "add":
                total += 2 * price(op[3], op[4])
            elif op[0] in ("clear", "copy"):
                total += 2
            else:
                need(op[0] == "scale", "source scalar type")
                q = Fraction(op[2], op[3])
                a, b = abs(q.numerator), q.denominator
                need(a > 0 and a & (a - 1) == 0 and b & (b - 1) == 0, "source scale")
                total += 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
        need(total == checks[name]["real_component_primitive_bound"], "unchanged source lowering invoice")
        totals[name] = total
    return totals


def controls(rows, recipe, word):
    result = []

    def reject(name, function, reason):
        try:
            function()
        except ValueError as error:
            need(reason in str(error), "wrong rejection for " + name)
            result.append(name)
        else:
            raise ValueError("accepted control: " + name)

    need(incremental(Counter({(2, 1): 10}), 1, 1) == -40, "nonunit synthetic positive control")
    result.append("synthetic matrix admits profitable nonunit edge")
    bad = copy.deepcopy(word)
    bad["compensation"][0][3] = 5
    bad["compensation"][0][4] = 4
    reject("out-of-alphabet tail premise", lambda: source_rows(bad), "tail premise")
    bad = copy.deepcopy(recipe)
    bad["tree_edges"][0][0] -= 1
    reject("underbilled unit edge", lambda: unit_certificate(rows, bad), "unpriced tree edge")
    all_roots = {"tree_edges": [[sum(price(v) for v in row.values()), -1, t, 0] for t, row in rows.items()]}
    reject("valid but nonminimal all-root tree", lambda: unit_certificate(rows, all_roots), "MST cycle inequality")
    cyclic = [[8, 0, 1, 1], [8, 1, 2, 1], [8, 2, 0, 1]]
    reject("disconnected cycle", lambda: tree_structure(cyclic, [-1, 0, 1, 2]), "disconnected tree")
    bad = copy.deepcopy(recipe["compensation"])
    bad.pop(0)
    reject("missing arbitrary-target preparation", lambda: replay_panel(word, bad), "arbitrary-target")
    bad = copy.deepcopy(recipe["compensation"])
    bad.pop()
    reject("missing restoration", lambda: replay_panel(word, bad), "arbitrary-target")
    reject("weak integer receipt equality", lambda: same({"cost": 1}, {"cost": True}, "strict receipt"), "strict receipt")
    # A synthetic chain has overlapping parent/child roles. Deleting a parent
    # edge leaves each child's residual row formula tied to the original C.
    original = [[Fraction(1, 2)], [Fraction(1, 4)], [Fraction(3, 4)]]
    parent = {0: (1, Fraction(2)), 1: (2, Fraction(-1, 2))}
    def row_cost(row):
        return sum(price(x.numerator, x.denominator) for x in row)
    def complete(parents):
        return sum(row_cost(original[t]) if t not in parents else
                   2 * price(parents[t][1].numerator, parents[t][1].denominator)
                   + row_cost([a - parents[t][1] * b for a, b in zip(original[t], original[parents[t][0]])])
                   for t in range(3))
    without = dict(parent)
    del without[1]
    edge_difference = 2 * price(-1, 2) + row_cost([Fraction(5, 8)]) - row_cost(original[1])
    need(complete(parent) - complete(without) == edge_difference, "overlapping forest deletion formula")
    result.append("overlapping weighted-chain edge deletion")
    return result


def run(root):
    word, programs, checks, recipe, manifest = C["inputs"](root)
    rows = source_rows(word)
    print("complete ordered-pair finite core", flush=True)
    core, _ = census(rows)
    tails = tail_checks()
    print("retained unit optimum and arbitrary-target panel boundary", flush=True)
    unit, _ = unit_certificate(rows, recipe)
    panel = replay_panel(word, recipe["compensation"])
    invoice = source_invoice(word, programs, checks)
    controls_result = controls(rows, recipe, word)
    roots = sum(price(v) for row in rows.values() for v in row.values())
    return {"status": "PASS_CK_POWER_FOREST_BOUND", "assignment_seed": 36,
            "source_manifest_sha256": C["digest"](manifest), "word_sha256": C["digest"](word),
            "targets": len(rows), "active_helpers": len(set().union(*(set(r) for r in rows.values()))),
            "source_panel_additions": sum(map(len, rows.values())), "source_panel_per_component": roots,
            "core": core, "tail": tails, "unit_witness": unit, "panel_replay": panel,
            "source_program_real_primitives": invoice, "retained_saving_real_per_orientation": 2 * (roots - 16364),
            "minimum_nonunit_penalty_per_component": min(v["min_penalty_per_component"] for e, v in core["by_exponent"].items() if e != "0"),
            "controls": controls_result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "output already exists")
    result = run(args.source_root)
    if args.write:
        C["write"](args.write, result)
    else:
        same(result, C["load"](C["HERE"] / "EXPECTED.json"), "complete receipt changed")
        subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "independent.py",
                        "--source-root", args.source_root], check=True)
    print("PASS_CK_POWER_FOREST_BOUND: 174048 finite cases; all integer exponents; "
          "forest floor 16364; original witness retained; no new kappa")


if __name__ == "__main__":
    main()
