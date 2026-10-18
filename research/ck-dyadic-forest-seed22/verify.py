"""Exact CK dyadic edge census. Lauren, substantial OpenAI Codex assistance.

Apache-2.0. New census implementation; cost model/forest mechanism credited
to PR816 and all-dyadic reduction/exchange argument credited to PR961.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/CANONICAL-WORD.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def exact_equal(left, right):
    return canonical(left) == canonical(right)


def price(q):
    q = Q(q)
    if not q:
        return 0
    a, b = abs(q.numerator), q.denominator
    need(b & (b - 1) == 0, "non-dyadic coefficient")
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def row_price(row):
    return sum(price(Q(a, 4)) for a in row)


def edge_price(child, parent, coefficient):
    return 2 * price(coefficient) + sum(
        price(Q(a, 4) - coefficient * Q(b, 4)) for a, b in zip(child, parent))


def horner(q):
    q = Q(q)
    if not q:
        return []
    price(q)  # validate domain
    result = ["clear"]
    for i, bit in enumerate(bin(abs(q.numerator))[2:]):
        if i:
            result.append("double")
        if bit == "1":
            result.append("source")
    result += ["halve"] * (q.denominator.bit_length() - 1)
    return result + ["target+" if q > 0 else "target-", "clear"]


def run_horner(word):
    # Exact target row in independent (target, source, dirty work) columns.
    work, target = [Q(0), Q(0), Q(1)], [Q(1), Q(0), Q(0)]
    for step in word:
        if step == "clear":
            work = [Q(0)] * 3
        elif step == "source":
            work[1] += 1
        elif step in ("double", "halve"):
            work = [v * (2 if step == "double" else Q(1, 2)) for v in work]
        elif step in ("target+", "target-"):
            target = [a + (1 if step == "target+" else -1) * b for a, b in zip(target, work)]
        else:
            raise ValueError("unknown primitive")
    # Include uncleared work in a separate check; q=0 emits no macro.
    if word:
        need(work == [0, 0, 0], "uncleared private work")
    return tuple(target)


def source_rows(root=ROOT):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, pin in pins["files"].items():
        raw = (root / name).read_bytes()
        if pin["encoding"] == "gzip-payload":
            raw = gzip.decompress(raw)
        need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source pin: " + name)
    word = json.loads(gzip.decompress((root / WORD).read_bytes()))
    spec = json.loads((root / pins["spec_path"]).read_bytes())["providers"]["ck"]
    need(hashlib.sha256(canonical(word).encode()).hexdigest() ==
         spec["artifact_semantic_sha256"]["CANONICAL-WORD.json.gz"], "SPEC word binding")
    need((word["v"], word["R"], word["h"]) == (112, 492, 9), "geometry")
    sparse = {i: {} for i in range(112, 224)}
    for op, t, s, a, b, frame in word["compensation"]:
        need(op == "add" and t in sparse and 224 <= s < 716 and frame == 0,
             "panel interface")
        need(word["start"][t] == word["start"][s] == 0, "panel entrance")
        value = 4 * Q(a, b)
        need(value.denominator == 1 and 0 < abs(value) <= 4, "quarter alphabet")
        need(s not in sparse[t], "duplicate cell")
        sparse[t][s] = int(value)
    sources = sorted({s for row in sparse.values() for s in row})
    need(len(sources) == 254 and sum(map(len, sparse.values())) == 8704, "panel coverage")
    return [[sparse[t].get(s, 0) for s in sources] for t in sparse], sources


def minimum_tree(rows, roots, unit_edges):
    edges = [(roots[i], -1, i, 0) for i in range(len(rows))]
    for (i, j), weights in unit_edges.items():
        if i < j:
            edges += [(w, i, j, s) for s, w in zip((-1, 1), weights)]
    parent = list(range(len(rows) + 1))

    def find(a):
        a += 1
        while a != parent[a]:
            a = parent[a]
        return a

    tree = []
    # Seed22 selects equal-price edges only; the mathematical domain is full.
    key = lambda e: (e[0], hashlib.sha256(("22:" + canonical(e)).encode()).hexdigest())
    for edge in sorted(edges, key=key):
        w, i, j, s = edge
        a, b = find(i), find(j)
        if a != b:
            parent[a] = b
            tree.append(edge)
    need(len(tree) == len(rows), "spanning tree")
    adjacency = {i: [] for i in range(-1, len(rows))}
    for w, i, j, _ in tree:
        adjacency[i].append((j, w))
        adjacency[j].append((i, w))
    maxima = {}
    for start in adjacency:
        pending = [(start, None, 0)]
        for vertex, previous, maximum in pending:
            maxima[start, vertex] = maximum
            for nxt, w in adjacency[vertex]:
                if nxt != previous:
                    pending.append((nxt, vertex, max(maximum, w)))
    slacks = [w - maxima[i, j] for w, i, j, _ in edges]
    need(min(slacks) >= 0, "MST cycle inequality")
    return {"cost": sum(e[0] for e in tree), "edges": tree,
            "cycle_inequalities": len(slacks), "minimum_cycle_slack": min(slacks)}


def census(rows):
    roots = list(map(row_price, rows))
    pairs, signatures = [], {}
    for i, child in enumerate(rows):
        for j, parent in enumerate(rows):
            if i == j:
                continue
            signature = tuple(sorted(Counter(zip(child, parent)).items()))
            index = signatures.setdefault(signature, len(signatures))
            pairs.append((i, j, index))
    sigs = list(signatures)
    units = {sign: [edge_price(rows[i], rows[j], Q(sign)) for i, j, _ in pairs]
             for sign in (-1, 1)}
    benchmarks = [min(roots[i], units[-1][k], units[1][k])
                  for k, (i, j, _) in enumerate(pairs)]
    minimum, root_minimum = None, None
    minima_count = negative_root = nonunit_ties = nonunit_better = 0
    witness, root_witness = None, None
    digest = hashlib.sha256()
    coefficients_done = cases_done = nonunit_done = 0
    for n in [*range(-543, 0), *range(1, 544)]:
        coefficients_done += 1
        cases_done += len(pairs)
        coefficient = Q(n, 8)
        table = {(a, b): price(Q(8*a - n*b, 32))
                 for a in range(-4, 5) for b in range(-4, 5)}
        edge_values = [2 * price(coefficient) + sum(count * table[cell] for cell, count in sig)
                       for sig in sigs]
        values = [edge_values[k] for _, _, k in pairs]
        digest.update((canonical([n, values]) + "\n").encode())
        if abs(n) == 8:
            need(values == units[n//8], "unit comparison disagrees")
            continue
        nonunit_done += len(pairs)
        for index, (i, j, signature) in enumerate(pairs):
            cost = edge_values[signature]
            gap, root_gap = cost - benchmarks[index], cost - roots[i]
            if minimum is None or gap < minimum:
                minimum, minima_count = gap, 1
                witness = {"child": i+112, "parent": j+112, "lambda": str(coefficient),
                           "cost": cost, "alternative": benchmarks[index]}
            elif gap == minimum:
                minima_count += 1
            if root_minimum is None or root_gap < root_minimum:
                root_minimum = root_gap
                root_witness = {"child": i+112, "parent": j+112, "lambda": str(coefficient),
                                "cost": cost, "root": roots[i]}
            negative_root += root_gap < 0
            nonunit_ties += gap == 0
            nonunit_better += gap < 0
    unit_edges = {(i, j): (units[-1][k], units[1][k]) for k, (i, j, _) in enumerate(pairs)}
    need(coefficients_done == 1086 and cases_done == 13501152 and nonunit_done == 13476288,
         "incomplete coefficient/pair coverage")
    return {"targets": len(rows), "ordered_pairs": len(pairs), "coefficients": coefficients_done,
            "cases": cases_done, "nonunit_cases": nonunit_done,
            "pair_histograms": len(sigs), "minimum_nonunit_margin": minimum,
            "minimum_margin_count": minima_count, "minimum_witness": witness,
            "minimum_root_margin": root_minimum, "root_witness": root_witness,
            "nonunit_beats_root": negative_root, "nonunit_ties_alternative": nonunit_ties,
            "nonunit_beats_alternative": nonunit_better,
            "census_sha256": digest.hexdigest(), "original_panel_cost": sum(roots),
            "unit_tree": minimum_tree(rows, roots, unit_edges)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="create a new receipt, refusing overwrite")
    parser.add_argument("--primary-only", action="store_true", help="omit separate checker")
    args = parser.parse_args()
    rows, sources = source_rows()
    result = census(rows)
    result["source_columns"] = len(sources)
    need(result["minimum_nonunit_margin"] > 0, "nonunit domination failed: inspect census")
    need(result["unit_tree"]["cost"] == 16364, "unit floor changed")
    if not args.primary_only:
        independent = subprocess.run([sys.executable, "-I", "-B", str(HERE / "independent.py")],
                                     check=True, capture_output=True, text=True)
        second = json.loads(independent.stdout)
        for key in ("cases", "nonunit_cases", "ordered_pairs", "minimum_nonunit_margin",
                    "minimum_root_margin", "minimum_margin_count", "nonunit_beats_root",
                    "nonunit_beats_alternative", "nonunit_ties_alternative"):
            need(exact_equal(result[key], second["census"][key]), "independent mismatch: " + key)
        need(result["census_sha256"] == second["census"]["full_census_sha256"],
             "independent full edge census mismatch")
        need(result["unit_tree"]["cost"] == second["signed_unit_prim"]["complex_primitive_floor"],
             "independent Prim mismatch")
        print("PASS_INDEPENDENT_CK_CENSUS digest=" + result["census_sha256"])
    if args.write:
        with args.write.open("x", encoding="utf-8") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        need(exact_equal(result, json.loads((HERE / "RESULT.json").read_text())), "receipt mismatch")
    print("PASS_CK_DYADIC_FOREST cases=%s minimum_margin=%s floor=16364 no_new_kappa" %
          (result["cases"], result["minimum_nonunit_margin"]))


if __name__ == "__main__":
    main()
