#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound centre block floor; precise model and proof in PROOF.md.

Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Reuses PR3071's independent source extraction and PR3168's relation census.
"""

import argparse
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb, gcd, lcm
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXTRACTOR = "research/centre-block-repair-information/independent.py"
RELATORS = "research/centre-seven-owner-fano-independent/verify.py"
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def authenticate(root=ROOT):
    """Authenticate every declared input before executing retained source."""
    rows = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    inputs = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular source: " + row["path"])
        raw = path.read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        require(row["path"] not in inputs, "duplicate source path")
        inputs[row["path"]] = raw
    require({EXTRACTOR, RELATORS, ARCHIVE} <= inputs.keys(), "complete executable source closure")
    return inputs


def source_module(path, raw, root):
    module = types.ModuleType("retained_" + path.split("/")[-2].replace("-", "_"))
    module.__file__ = str(root / path)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def load_sources(root=ROOT):
    inputs = authenticate(root)
    source = source_module(EXTRACTOR, inputs[EXTRACTOR], root)
    census = source_module(RELATORS, inputs[RELATORS], root)
    word, phases = source.sources()
    old, later = source.query_rows(word)
    require(len(old) == 8 and all(len(row) == 112 for row in old), "eight old query rows")
    require(later == [[x / 4 for x in row] for row in old], "H=R/4")
    pivots = source.pivot_columns(old)
    require(len(pivots) == 8, "rank R is eight")
    require(len(source.pair_certificates(old)) == comb(112, 2), "all column pairs nonparallel")
    routes, products, _ = source.route_certificates(word, phases)
    require(len(products) == 112 * 111, "unique ordered relative routes")
    return source, census, old, routes, pivots


def validate_relations(total, histogram, relations):
    """Check the exhaustive census reduction from six-cycles to braid pairs."""
    require(total == 112 * 111**2, "complete reduced triple domain")
    require(dict(histogram) == {1: 1379852, 2: 50}, "exact product-class inventory")
    words = {tuple(word) for word in relations}
    require(len(words) == 100, "complete oriented six-relator inventory")
    for word in words:
        require(len(word) == 6 and all(type(x) is int and 0 <= x < 112 for x in word),
                "six route labels")
        require(all(word[i] != word[(i + 1) % 6] for i in range(6)), "cyclic reduction")
        require(len(set(word)) == 2, "every six-relator is a braid")
        require(word[1:] + word[:1] in words and word[::-1] in words,
                "complete relator symmetries")
    edges = sorted({tuple(sorted(set(word))) for word in words})
    require(len(edges) == 50, "fifty braid edges")
    return edges


def primitive_columns(rows):
    columns = []
    for column in zip(*rows):
        denominator = lcm(*(x.denominator for x in column))
        values = [int(x * denominator) for x in column]
        divisor = 0
        for value in values:
            divisor = gcd(divisor, value)
        require(divisor != 0, "nonzero query column")
        columns.append(tuple(value // divisor for value in values))
    return columns


def dependent_triple_certificate(columns, edges):
    """Exact 2x2-minor elimination over the reconstructed scalar columns."""
    edge_set = set(map(tuple, edges))
    triples, histogram = [], Counter()
    for a, b in combinations(range(len(columns)), 2):
        x, y = columns[a], columns[b]
        i, j = next((i, j) for i, j in combinations(range(8), 2)
                    if x[i] * y[j] != x[j] * y[i])
        determinant = x[i] * y[j] - x[j] * y[i]
        for c in range(b + 1, len(columns)):
            z = columns[c]
            u, v = z[i] * y[j] - z[j] * y[i], x[i] * z[j] - x[j] * z[i]
            if all(u * xx + v * yy == determinant * zz for xx, yy, zz in zip(x, y, z)):
                require(u != 0 and v != 0, "nonparallel triple coefficients")
                triple = (a, b, c)
                triples.append(triple)
                histogram[sum(pair in edge_set for pair in combinations(triple, 2))] += 1
    require(len(triples) == 896 and histogram == {0: 846, 1: 50},
            "dependent degree-three support has at most one braid")
    return {"checked": comb(112, 3), "dependent": len(triples),
            "braid_edge_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "triples_sha256": digest(triples)}


def scientific_premises(root=ROOT):
    source, census, rows, routes, pivots = load_sources(root)
    active = [census.to_rows(route) for route in routes]
    total, histogram, relations = census.relation_census(active)
    edges = validate_relations(total, histogram, relations)
    require(all(census.product_is_identity(active, word) for word in relations),
            "every retained relator is an actual identity")
    edge_set = set(edges)
    require(not any(all(pair in edge_set for pair in combinations(triple, 2))
                    for triple in combinations(range(112), 3)), "triangle-free braid graph")
    triple_certificate = dependent_triple_certificate(primitive_columns(rows), edges)
    complement = [i for i in range(112) if i not in pivots]
    coordinate_rows = [[Fraction(int(i == j)) for j in range(112)] for i in complement]
    require(len(complement) == 104 and len(source.pivot_columns(rows + coordinate_rows)) == 112,
            "104 complementary reads attain complete information")
    return {"old_rank": 8, "later_is_old_quarter": True, "ports": 112,
            "route_dimension": 73, "active_dimension": 17, "fixed_spectators": 56,
            "ordered_relative_products": 12432, "reduced_triples": total,
            "product_class_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "cyclic_relations": [list(w) for w in sorted(relations)],
            "braid_edges": [list(e) for e in edges], "braid_triangles": 0,
            "dependent_triples": triple_certificate,
            "R_sha256": digest([[str(x) for x in row] for row in rows]),
            "repair_coordinate_reads": complement}


def cap(degree):
    return 1 if degree == 3 else degree * degree // 4


def triangle_lower_bound(m, missing_edges):
    quotient, remainder = divmod(2 * missing_edges, m)
    wedges = remainder * comb(quotient + 1, 2) + (m - remainder) * comb(quotient, 2)
    return max(0, comb(m, 3) - missing_edges * (m - 2) + (2 * wedges + 2) // 3)


def pals_graph():
    """Nine affine points, using the three nonvertical parallel classes."""
    return tuple(tuple(3 * x + (slope * x + offset) % 3 for x in range(3))
                 for slope in range(3) for offset in range(3))


def duad_graph():
    duads = list(combinations(range(6), 2))

    def matchings(points):
        if not points:
            yield ()
        else:
            first = points[0]
            for second in points[1:]:
                rest = tuple(x for x in points if x not in (first, second))
                for tail in matchings(rest):
                    yield (duads.index((first, second)),) + tail

    return tuple(sorted(tuple(sorted(row)) for row in matchings(tuple(range(6)))))


def graph_certificate(neighborhoods, b_count=None):
    lines = [set(row) for row in neighborhoods]
    require(lines and all(len(row) == len(line) for row, line in zip(neighborhoods, lines)),
            "simple nonempty incidence inventory")
    require(all(type(v) is int and v >= 0 for line in lines for v in line), "integer vertices")
    m = max((v for line in lines for v in line), default=-1) + 1 if b_count is None else b_count
    require(type(m) is int and 0 < m <= 64 and len(lines) <= 64, "bounded incidence domain")
    require(all(v < m for line in lines for v in line), "vertex range")
    inverse = [{d for d, line in enumerate(lines) if b in line} for b in range(m)]
    four = sum(comb(len(a & b), 2) for a, b in combinations(lines, 2))
    counts_b, counts_d = [0] * m, [0] * len(lines)
    for a, b, c in combinations(range(m), 3):
        for x, y, z in product(inverse[a] & inverse[b], inverse[b] & inverse[c], inverse[c] & inverse[a]):
            if len({x, y, z}) == 3:
                for v in (a, b, c):
                    counts_b[v] += 1
                for v in (x, y, z):
                    counts_d[v] += 1
    adjacent = [{j for j in range(m) if i != j and inverse[i] & inverse[j]} for i in range(m)]
    complement = [set(range(m)) - row - {i} for i, row in enumerate(adjacent)]
    triangles = sum(b in adjacent[a] and c in adjacent[a] and c in adjacent[b]
                    for a, b, c in combinations(range(m), 3))
    comp_tri = sum(b in complement[a] and c in complement[a] and c in complement[b]
                   for a, b, c in combinations(range(m), 3))
    missing = sum(map(len, complement)) // 2
    wedges = sum(comb(len(row), 2) for row in complement)
    quotient, remainder = divmod(2 * missing, m)
    balanced = remainder * comb(quotient + 1, 2) + (m - remainder) * comb(quotient, 2)
    moore = []
    for d, line in enumerate(lines):
        second = set().union(*(inverse[b] for b in line)) - {d}
        third = set().union(*(lines[e] for e in second)) - line
        edges = sum(len(lines[e] & third) for e in second)
        moore.append([d, len(line), len(second), edges, len(third), counts_d[d], 5 * len(line) - counts_d[d]])
    return {"B": m, "D": len(lines), "E": sum(map(len, lines)),
            "B_degrees": list(map(len, inverse)), "D_degrees": list(map(len, lines)),
            "min_degree": min(map(len, inverse + lines)), "c4": four,
            "c6": sum(counts_b) // 3, "per_B_c6": counts_b, "per_D_c6": counts_d,
            "distance2_triangles": triangles, "claws": sum(comb(len(row), 3) for row in lines),
            "complement_edges": missing, "complement_wedges": wedges,
            "complement_triangles": comp_tri,
            "source_triangle_claim": comb(m, 3) - missing * (m - 2) + balanced,
            "sound_triangle_bound": triangle_lower_bound(m, missing),
            "moore_root_bounds": moore}


def validate_caps(certificate):
    require(certificate["min_degree"] >= 3, "minimum degree three")
    require(certificate["c4"] == 0, "C4-free incidence")
    require(all(cycles <= cap(degree) for cycles, degree in
                zip(certificate["per_D_c6"], certificate["D_degrees"])),
            "six-cycle cap on D")


def predecessor_triangle(certificate):
    """Evaluate the authenticated predecessor expression, not a retyped one."""
    metadata = json.loads((HERE / "PREDECESSOR.json").read_bytes())
    raw = (HERE / metadata["excerpt"]).read_bytes()
    require(sha256(raw).hexdigest() == metadata["excerpt_sha256"], "predecessor excerpt SHA256")
    assignments = [node.value for node in ast.walk(ast.parse(raw))
                   if isinstance(node, ast.Assign) and len(node.targets) == 1
                   and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "min_tri_g2"]
    require(len(assignments) == 1, "one predecessor triangle expression")
    expression = ast.Expression(assignments[0])
    allowed = (ast.Expression, ast.BinOp, ast.Name, ast.Constant, ast.Load,
               ast.Add, ast.Sub, ast.Mult, ast.FloorDiv)
    require(all(isinstance(node, allowed) for node in ast.walk(expression)),
            "arithmetic-only predecessor expression")
    m, missing = certificate["B"], certificate["complement_edges"]
    quotient, remainder = divmod(2 * missing, m)
    wedges = remainder * comb(quotient + 1, 2) + (m - remainder) * comb(quotient, 2)
    value = eval(compile(expression, metadata["excerpt"], "eval"), {"__builtins__": {}},
                 {"m": m, "U": missing, "sum_c2_nondeg": wedges})
    require(value == certificate["source_triangle_claim"], "literal source-expression binding")
    return {"commit": metadata["commit"], "excerpt_sha256": metadata["excerpt_sha256"],
            "counterexample_bound": value, "actual_triangles": certificate["distance2_triangles"]}


def floor_certificate():
    bounds = [[k, 5 * k - cap(k)] for k in range(3, 15)]
    require(all(bound > 13 for _, bound in bounds), "Moore exclusion through thirteen")
    require(all(bound > 14 for degree, bound in bounds if degree >= 4),
            "at fourteen all output degrees are three")
    require(3 + 2 * 7 - cap(3) > 14, "at fourteen all source degrees are three")
    require(14 % 3 != 0, "one six-cycle per output contradicts triple incidence")
    return {"minimum_nonzero_owner_support": 15, "blocks_proved": [1, 14],
            "repair_per_owner": 104, "degree_bounds": bounds,
            "degree14_divisibility": [14, 3, 14 % 3]}


def build(root=ROOT):
    premises = scientific_premises(root)
    nine, fifteen = graph_certificate(pals_graph()), graph_certificate(duad_graph())
    require(nine["c4"] == 0 and nine["distance2_triangles"] == 27
            and nine["source_triangle_claim"] == 30, "actual counterexample to source triangle bound")
    require(nine["complement_triangles"] == 3, "missing complement term")
    predecessor = predecessor_triangle(nine)
    validate_caps(fifteen)
    require(fifteen["B"] == fifteen["D"] == 15 and fifteen["c6"] == 0,
            "sharp abstract fifteen-owner positive control")
    return {"schema_version": 1, "claim": "selected_two_stage_block_repair_through_fourteen",
            "source_premises": premises, "floor15": floor_certificate(),
            "predecessor_counterexample": predecessor,
            "graph_certificates": {"affine_nine": nine, "duad_fifteen": fifteen},
            "scope": "regular cover owners, scalar linear block repairs, whole later query",
            "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_bytes()), "exact receipt")
        print("PASS_CENTRE_BLOCK_MOORE_BOUND support>=15 blocks=1..14 repair=104*b no_new_kappa")


if __name__ == "__main__":
    main()
