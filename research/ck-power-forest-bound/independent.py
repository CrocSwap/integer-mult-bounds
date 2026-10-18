#!/usr/bin/env python3
"""Dense integer, literal-Horner and Prim crosscheck. Apache-2.0.

No verifier/search implementation is imported. Source-admission and JSON I/O
helpers are shared; all mathematical computations below are separate.
Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import math
from pathlib import Path
import runpy

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need, same = C["need"], C["same"]


def lower(numerator, denominator):
    need(type(numerator) is int and type(denominator) is int and denominator > 0, "coefficient type")
    if not numerator:
        return [], (0, 1)
    factor = math.gcd(abs(numerator), denominator)
    numerator //= factor
    denominator //= factor
    power, d = 0, denominator
    while d > 1:
        need(d % 2 == 0, "dyadic denominator")
        d //= 2
        power += 1
    bits, n = [], abs(numerator)
    while n:
        n, digit = divmod(n, 2)
        bits.append(digit)
    operations = ["clear"]
    for i, digit in enumerate(bits[::-1]):
        if i:
            operations.append("double")
        if digit:
            operations.append("source")
    operations.extend(["halve"] * power)
    operations.extend(["plus" if numerator > 0 else "minus", "clear"])
    return operations, (numerator, denominator)


def execute(operations, numerator, denominator):
    # Fixed integer grid. No Fraction arithmetic or cost formula is used here.
    target, source, work = [denominator, 0, 0], [0, denominator, 0], [0, 0, denominator]
    for op in operations:
        if op == "clear":
            work = [0, 0, 0]
        elif op == "double":
            work = [2 * x for x in work]
        elif op == "source":
            work = [x + y for x, y in zip(work, source)]
        elif op == "halve":
            need(all(x % 2 == 0 for x in work), "exact coefficient grid")
            work = [x // 2 for x in work]
        else:
            need(op in ("plus", "minus"), "primitive type")
            sign = 1 if op == "plus" else -1
            target = [x + sign * y for x, y in zip(target, work)]
    need(target == [denominator, numerator, 0] and work == [0, 0, 0] and source == [0, denominator, 0],
         "literal arbitrary-work coefficient operator")


class Prices:
    def __init__(self):
        self.cache = {}
        self.operations = 0

    def __call__(self, n, d=4):
        if n == 0:
            return 0
        key = (n, d)
        if key not in self.cache:
            ops, (a, b) = lower(n, d)
            execute(ops, a, b)
            self.operations += len(ops)
            self.cache[key] = len(ops)
        return self.cache[key]


def extract(word):
    helpers = sorted({g[2] for g in word["compensation"]})
    index = {s: i for i, s in enumerate(helpers)}
    matrix = [[0] * len(helpers) for _ in range(112)]
    for op, t, s, a, b, f in word["compensation"]:
        need(op == "add" and 112 <= t < 224 and s >= 224 and f == 0, "dense panel shape")
        need(b > 0 and 4 * a % b == 0 and 0 < abs(4 * a // b) <= 4, "dense quarter alphabet")
        need(matrix[t - 112][index[s]] == 0, "dense repeated cell")
        matrix[t - 112][index[s]] = 4 * a // b
    need(len(helpers) == 254, "dense helper support")
    return matrix


def census(matrix, prices):
    root_cost = [sum(prices(a) for a in row) for row in matrix]
    records = []
    summary = {e: [] for e in range(-3, 4)}
    weights = {}
    for child, left in enumerate(matrix):
        for parent, right in enumerate(matrix):
            if child == parent:
                continue
            for e in range(-3, 4):
                for sign in (-1, 1):
                    numerator, denominator = sign * (1 << max(e, 0)), 1 << max(-e, 0)
                    total = 2 * prices(numerator, denominator)
                    # Direct dense column scan, without sparse row histograms.
                    for a, b in zip(left, right):
                        total += prices(denominator * a - numerator * b, 4 * denominator)
                    delta = total - root_cost[child]
                    rec = [child + 112, parent + 112, e, sign, delta]
                    records.append(rec)
                    summary[e].append(rec)
                    if e == 0:
                        weights[child, parent, sign] = total
    out = {}
    row_minima = {}
    for e, cases in summary.items():
        costs = [r[-1] for r in cases]
        if e:
            need(all(x > 0 for x in costs), "independent nonunit root dominance")
        out[str(e)] = {"cases": len(cases), "min_penalty_per_component": min(costs),
                       "max_penalty_per_component": max(costs), "profitable": sum(x < 0 for x in costs),
                       "ties": sum(x == 0 for x in costs),
                       "first_minimizer": next(r for r in cases if r[-1] == min(costs))}
    for t, p, e, sign, delta in records:
        row_minima.setdefault((t, e), []).append((delta, p, sign))
    result = {"cases": len(records), "records_sha256": C["digest"](records), "by_exponent": out,
              "row_minima": [[t, e, *min(row_minima[t, e])] for t, e in sorted(row_minima)]}
    return result, root_cost, weights


def prim(roots, weights):
    remaining = set(range(112))
    best = {i: (roots[i], -1, 0) for i in remaining}
    chosen = []
    while remaining:
        vertex = min(remaining, key=lambda i: (*best[i], i))
        cost, parent, sign = best[vertex]
        chosen.append([parent, vertex, sign, cost])
        remaining.remove(vertex)
        for child in remaining:
            for s in (-1, 1):
                need(weights[child, vertex, s] == weights[vertex, child, s], "unit symmetry")
                proposal = (weights[child, vertex, s], vertex, s)
                if proposal < best[child]:
                    best[child] = proposal
    return {"vertices": 113, "edges": len(chosen), "floor_per_component": sum(e[-1] for e in chosen),
            "edges_sha256": C["digest"](chosen)}


def dense_panel(word, recipe):
    count, digest = 0, hashlib.sha256()
    for dual in (False, True):
        panels = []
        for original in (word["compensation"], recipe["compensation"]):
            panels.append([(s, t, -a, b) if dual else (t, s, a, b) for _, t, s, a, b, _ in original])
        for col in range(716):
            results = []
            for panel in panels:
                values = [0] * 716
                values[col] = 4
                for t, s, a, b in panel:
                    change = a * values[s]
                    need(change % b == 0, "quarter-grid panel replay")
                    values[t] += change // b
                results.append(values)
            need(results[0] == results[1], "independent complete panel operator")
            digest.update(C["canonical"]([dual, col, results[1]]))
            count += 1
    return {"orientations": 2, "columns_each": 716, "column_comparisons": count,
            "column_images_sha256": digest.hexdigest()}


def tails(prices):
    report = []
    for negative in (False, True):
        for a in range(-4, 5):
            for b in range(-4, 5):
                # Infer the slope from two literal costs; test all other listed
                # exponents independently of verify.py's sign-case function.
                def literal(k):
                    return prices(a * (1 << k) + b, 1 << (2 + int(negative) * k))
                anchor = literal(3)
                slope = literal(4) - anchor
                need(slope >= 0, "independent nonnegative tail slope")
                for k in (3, 4, 5, 8, 36, 64, 127):
                    need(literal(k) == anchor + (k - 3) * slope, "independent affine tail cost")
                report.append([negative, a, b, anchor, slope])
    return {"families": len(report), "records_sha256": C["digest"](report)}


def native_price_binding(root, prices):
    path = Path(root) / "research/complex-k492-owner-repair/code/hpe_emit_local.py"
    tree = ast.parse(path.read_text())
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "primitive_bound"]
    need(len(definitions) == 1, "native price function")
    # Execute only this exact hash-pinned, closed function, keeping its source
    # assertions enabled even if the verifier driver uses -O.
    namespace = {"Q": Fraction}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec", optimize=0), namespace)
    for (a, b), count in prices.cache.items():
        need(namespace["primitive_bound"](["add", ["L", 0], ["L", 1], a, b]) == count,
             "literal/native primitive price mismatch")
    return len(prices.cache)


def run(root):
    word, _, _, recipe, _ = C["inputs"](root)
    prices = Prices()
    print("independent dense core and literal coefficient circuits", flush=True)
    core, roots, weights = census(extract(word), prices)
    expected = C["load"](C["HERE"] / "EXPECTED.json")
    same(core, expected["core"], "independent complete finite-core receipt")
    mst = prim(roots, weights)
    need(mst["floor_per_component"] == expected["unit_witness"]["floor_per_component"], "independent Prim floor")
    tail = tails(prices)
    need(tail["records_sha256"] == expected["tail"]["records_sha256"], "independent tail families")
    print("independent integer-grid arbitrary-target witness replay", flush=True)
    panels = dense_panel(word, recipe)
    native = native_price_binding(root, prices)
    ops, (a, b) = lower(3, 4)
    rejected = []
    for name, wrong in (("initial clear omitted", ops[1:]), ("final clear omitted", ops[:-1])):
        try:
            execute(wrong, a, b)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("coefficient control accepted")
    return {"status": "PASS_INDEPENDENT_CK_POWER_FOREST", "core_records_sha256": core["records_sha256"],
            "cases": core["cases"], "unit_prim": mst, "tails": tail, "panel": panels,
            "literal_coefficient_cases": len(prices.cache), "literal_primitive_executions": prices.operations,
            "native_price_comparisons": native, "coefficient_controls": rejected}


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
        same(result, C["load"](C["HERE"] / "INDEPENDENT.json"), "independent receipt changed")
    print("PASS_INDEPENDENT_CK_POWER_FOREST: 174048 cases; literal coefficients; "
          "Prim floor 16364; 716 columns each orientation; no new kappa")


if __name__ == "__main__":
    main()
