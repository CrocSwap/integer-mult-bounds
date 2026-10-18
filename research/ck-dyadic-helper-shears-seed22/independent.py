#!/usr/bin/env python3
"""Independent complete census for the fixed CK forest and six helper shears.

Inputs are the canonical CK word, predecessor *data* recipe, and certificate. No
experiment, cost formula, search, or arithmetic module is imported.  Matrices
are integer quarters.  Prices count explicitly emitted binary-Horner primitive
instructions, checked on symbolic arbitrary source, target, and work inputs.

For h_a <- h_a + q h_b, the only residual change is
D_b <- D_b - q D_a.  Restoring h_a subtracts q h_b, hence the overhead is 2*p(q)
and arbitrary helper values are restored.  Register-disjoint gains add.
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/CANONICAL-WORD.json.gz"
RECIPE = ROOT / "research/complex-ck-two-sided/RECIPE.json"
CERTIFICATE = Path(__file__).with_name("CERTIFICATE.json")
WORD_SHA256 = "9bbc75dede090cfd7a0a0252424ea9d9f6211e2350d2a801d4e4f2f0784167c7"
RECIPE_SHA256 = "8eae0f1036c2c455dd59017c4b37903e45aeff6d0c66d7a3ce74e9b78e4f4aac"
FOREST_SHA256 = "3415bef759d448a76da82917ef4d2d2f0bd8a81d82359a3d075bcbe2012e5b88"
ALPHABET = ((-2, 1), (-1, 1), (-1, 2), (1, 2), (1, 1), (2, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=None)
def primitives(numerator, denominator=1, modern=False):
    """Emit a scalar target += (numerator/denominator)*source program."""
    q = Fraction(numerator, denominator)
    if not q:
        return ()
    if q.denominator & (q.denominator - 1):
        raise ValueError("Only dyadic coefficients are allowed")
    if modern and abs(q) == 1:
        return (("add_direct_target", 1 if q > 0 else -1), ("clear",))
    instructions = [("copy_source",)] if modern else [("clear",)]
    digits = bin(abs(q.numerator))[2:]
    for position, bit in enumerate(digits):
        if position:
            instructions.append(("double",))
        if modern and position == 0:
            continue  # The leading one is already in work after its source copy.
        if bit == "1":
            instructions.append(("add_source",))
    for _ in range(q.denominator.bit_length() - 1):
        instructions.append(("half",))
    instructions.append(("add_target", 1 if q > 0 else -1))
    instructions.append(("clear",))
    return tuple(instructions)


def execute_primitives(target, source, work, instructions):
    """Interpret a primitive word on exact independent symbolic input columns."""
    for instruction in instructions:
        op = instruction[0]
        if op == "clear":
            work = [Fraction(0)] * len(work)
        elif op == "copy_source":
            work = source[:]
        elif op == "add_direct_target":
            target = [x + instruction[1] * y for x, y in zip(target, source)]
        elif op == "double":
            work = [2 * x for x in work]
        elif op == "half":
            work = [x / 2 for x in work]
        elif op == "add_source":
            work = [x + y for x, y in zip(work, source)]
        elif op == "add_target":
            target = [x + instruction[1] * y for x, y in zip(target, work)]
        else:
            raise ValueError("Unknown primitive: " + op)
    return target, work


def check_primitives(numerator, denominator, modern=False):
    """Replay on three independent input columns, including dirty private work."""
    zero = Fraction(0)
    source = [Fraction(1), zero, zero]
    target = [zero, Fraction(1), zero]
    work = [zero, zero, Fraction(1)]
    q = Fraction(numerator, denominator)
    target, work = execute_primitives(target, source, work, primitives(numerator, denominator, modern))
    require(target == [q, Fraction(1), zero], "Primitive target map differs")
    require(source == [Fraction(1), zero, zero], "Primitive source map differs")
    require(work == ([zero, zero, zero] if q else [zero, zero, Fraction(1)]), "Primitive work endpoint differs")


def check_helper_identity(numerator, denominator, coefficients, modern=False):
    """Literal replay on arbitrary target, two helpers, and dirty work inputs.

    The coefficient combinations cover all pairs of values appearing in D.
    Each scalar macro is lowered, then its full primitive word is executed.
    """
    q = Fraction(numerator, denominator)
    basis = [[Fraction(i == j) for j in range(4)] for i in range(4)]
    checked = 0
    for left in coefficients:
        for right in coefficients:
            target, ha, hb, work = [row[:] for row in basis]
            ha, work = execute_primitives(ha, hb, work, primitives(numerator, denominator, modern))
            target, work = execute_primitives(target, ha, work, primitives(left.numerator, left.denominator, modern))
            residual = right - q * left
            target, work = execute_primitives(target, hb, work, primitives(residual.numerator, residual.denominator, modern))
            ha, work = execute_primitives(ha, hb, work, primitives(-numerator, denominator, modern))
            require(target == [Fraction(1), left, right, Fraction(0)], "Shear compensation map differs")
            require(ha == basis[1] and hb == basis[2], "Shear fails arbitrary helper restoration")
            require(work == [0, 0, 0, 0], "Shear fails work cleanup")
            checked += 1
    return checked


def read_matrix(word_path=WORD, recipe_path=RECIPE):
    payload = gzip.decompress(Path(word_path).read_bytes())
    require(hashlib.sha256(payload).hexdigest() == WORD_SHA256, "Canonical source digest mismatch")
    word = json.loads(payload)
    recipe_payload = Path(recipe_path).read_bytes()
    require(hashlib.sha256(recipe_payload).hexdigest() == RECIPE_SHA256, "Predecessor recipe source digest mismatch")
    recipe = json.loads(recipe_payload)
    panel = word["compensation"]
    targets = sorted({gate[1] for gate in panel})
    helpers = sorted({gate[2] for gate in panel})
    require(targets == recipe["targets"], "Target indices differ from the predecessor")
    require(helpers == recipe["sources"], "Helper indices differ from the predecessor")
    require(set(targets).isdisjoint(helpers), "Target and helper banks overlap")
    target_index = {value: index for index, value in enumerate(targets)}
    helper_index = {value: index for index, value in enumerate(helpers)}
    matrix = [[0] * len(helpers) for _ in targets]
    for gate in panel:
        op, target, source, numerator, denominator, frame = gate
        require(op == "add" and frame == 0, "Panel is not a frame-zero addition")
        value = Fraction(4 * numerator, denominator)
        require(value.denominator == 1, "Panel coefficient is not an integer quarter")
        matrix[target_index[target]][helper_index[source]] += int(value)
    # Compute each D row from the original C, independently of schedule order.
    transformed = [row[:] for row in matrix]
    edges = recipe["target_forest"]
    require(digest(edges) == FOREST_SHA256, "The claimed target forest changed")
    parent = {}
    for child, ancestor, sign, depth in edges:
        require(child not in parent and child != ancestor and sign in (-1, 1), "Invalid forest edge")
        require(0 <= child < len(targets) and 0 <= ancestor < len(targets), "Forest vertex out of range")
        parent[child] = ancestor
        transformed[child] = [a - sign * b for a, b in zip(matrix[child], matrix[ancestor])]
    for child, ancestor, sign, depth in edges:
        visited = set()
        current = child
        while current in parent:
            require(current not in visited, "Cycle in the fixed target forest")
            visited.add(current)
            current = parent[current]
        require(len(visited) == depth, "Forest depth differs")
    # The recorded chronological preparation must realize the literal T*C.
    scheduled = [row[:] for row in matrix]
    for child, ancestor, sign, _ in edges:
        scheduled[child] = [a - sign * b for a, b in zip(scheduled[child], scheduled[ancestor])]
    require(scheduled == transformed, "Forest schedule does not implement T*C")
    for child, ancestor, sign, _ in reversed(edges):
        scheduled[child] = [a + sign * b for a, b in zip(scheduled[child], scheduled[ancestor])]
    require(scheduled == matrix, "Forest inverse does not restore C")
    return matrix, transformed, recipe, panel


def check_matching(certificate, all_edges, width, alphabet):
    """Check a matching and an odd-set LP dual with integer doubled prices.

    Vertex variables store 2*y_v and odd-set variables store z_S. Thus an edge
    requires y2_a+y2_b+2*sum(z_S: a,b in S) >= 2*w_ab. The doubled objective is
    sum(y2_v)+sum((|S|-1)*z_S). Weak duality bounds every disjoint matching.
    """
    require(isinstance(certificate, dict), "Matching certificate must be an object")
    dual = certificate["vertex_dual_twice"]
    require(isinstance(dual, list) and len(dual) == width, "Wrong vertex dual size")
    require(all(type(x) is int and x >= 0 for x in dual), "Vertex duals must be nonnegative integers")
    odd_sets = certificate["odd_sets"]
    require(isinstance(odd_sets, list), "Odd sets must be a list")
    parsed_odd_sets = []
    for odd_set in odd_sets:
        require(isinstance(odd_set, dict), "Odd-set entry must be an object")
        vertices, z = odd_set["vertices"], odd_set["dual"]
        require(isinstance(vertices, list) and len(vertices) >= 3 and len(vertices) % 2 == 1,
                "A dual set must have odd cardinality at least three")
        require(all(type(v) is int and 0 <= v < width for v in vertices), "Invalid odd-set vertex")
        require(len(set(vertices)) == len(vertices), "Repeated vertex in odd set")
        require(type(z) is int and z >= 0, "Odd-set dual must be a nonnegative integer")
        parsed_odd_sets.append((set(vertices), z))
    matching = certificate["matching"]
    require(isinstance(matching, list), "Matching must be a list")
    require(type(certificate["matching_pairs"]) is int and certificate["matching_pairs"] == len(matching),
            "Matching pair count differs")
    used = set()
    gain = 0
    nonunit = []
    for edge in matching:
        require(isinstance(edge, dict), "Matching edge must be an object")
        values = [edge[key] for key in ("a", "b", "numerator", "denominator", "gain")]
        require(all(type(v) is int for v in values), "Matching edge fields must be integers")
        a, b, n, d, claimed = values
        require(0 <= a < width and 0 <= b < width and a != b, "Invalid matching endpoints")
        require((n, d) in alphabet, "Matching coefficient outside checked alphabet")
        require(a not in used and b not in used, "Matching edges overlap")
        require(claimed == all_edges[a, b, n, d] and claimed > 0, "Incorrect or nonpositive matching gain")
        used.update((a, b))
        gain += claimed
        if abs(n) != d:
            nonunit.append(edge)
    require(type(certificate["gain"]) is int and certificate["gain"] == gain, "Matching total differs")
    edge_count = 0
    minimum_slack = None
    # Cover all ordered coefficients, not just the chosen representative edge.
    for (a, b, n, d), actual in all_edges.items():
        if (n, d) not in alphabet:
            continue
        lhs = dual[a] + dual[b] + 2 * sum(z for vertices, z in parsed_odd_sets if a in vertices and b in vertices)
        slack = lhs - 2 * actual
        require(slack >= 0, "Dual does not cover an independently priced edge")
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
        edge_count += 1
    objective = sum(dual) + sum((len(vertices) - 1) * z for vertices, z in parsed_odd_sets)
    require(objective == 2 * gain, "Primal and dual objectives differ")
    return {"gain": gain, "matching_pairs": len(matching), "primal_twice": 2 * gain,
            "dual_twice": objective, "ordered_edges_covered": edge_count,
            "minimum_edge_slack_twice": minimum_slack, "odd_sets": len(parsed_odd_sets),
            "nonunit_edges": nonunit}


def check_certificate(certificate_path, all_edges, width, matching_key="matchings"):
    certificate = json.loads(Path(certificate_path).read_text())
    require(certificate["format"] == "ck-helper-matching-dual-v1", "Unknown certificate format")
    require(type(certificate["seed"]) is int and certificate["seed"] == 22, "Wrong certificate seed")
    require(certificate["alphabet"] == [list(q) for q in ALPHABET], "Wrong certificate alphabet")
    require(all(type(value) is int for q in certificate["alphabet"] for value in q),
            "Certificate alphabet must contain integers")
    result = {}
    for name, alphabet in (("unit", ((-1, 1), (1, 1))), ("extended", ALPHABET)):
        result[name] = check_matching(certificate[matching_key][name], all_edges, width, alphabet)
    # Deliberately corrupt a real certificate and require rejection. No input
    # file is modified. The controls test distinct obligations of weak duality.
    original = certificate[matching_key]["extended"]
    corruptions = []
    bad = copy.deepcopy(original)
    bad["matching"][0]["gain"] += 1
    corruptions.append(("wrong_edge_gain", bad))
    bad = copy.deepcopy(original)
    bad["matching"][1] = copy.deepcopy(bad["matching"][0])
    corruptions.append(("overlapping_edges", bad))
    bad = copy.deepcopy(original)
    bad["vertex_dual_twice"] = [0] * width
    corruptions.append(("uncovered_edge", bad))
    bad = copy.deepcopy(original)
    bad["odd_sets"].append({"vertices": [0, 1], "dual": 1})
    corruptions.append(("even_odd_set", bad))
    bad = copy.deepcopy(original)
    bad["odd_sets"].append({"vertices": [0, 0, 1], "dual": 1})
    corruptions.append(("repeated_odd_set_vertex", bad))
    bad = copy.deepcopy(original)
    bad["vertex_dual_twice"][0] = True
    corruptions.append(("boolean_dual", bad))
    bad = copy.deepcopy(original)
    bad["odd_sets"].append({"vertices": [0, 1, 2], "dual": -1})
    corruptions.append(("negative_odd_set_dual", bad))
    bad = copy.deepcopy(original)
    bad["matching"][0]["numerator"] = 3
    corruptions.append(("out_of_alphabet_edge", bad))
    bad = copy.deepcopy(original)
    bad["vertex_dual_twice"] = [value + 1 for value in bad["vertex_dual_twice"]]
    corruptions.append(("nonmatching_objective", bad))
    rejected = []
    for name, bad in corruptions:
        try:
            check_matching(bad, all_edges, width, ALPHABET)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Failed to reject certificate control: " + name)
    result["rejected_controls"] = rejected
    return result


def model_census(matrix, transformed, recipe, panel, certificate_path, modern=False):
    columns = list(zip(*transformed))
    width = len(columns)
    extreme = max(abs(value) for row in transformed for value in row)
    prices = {}
    checked = set()
    for numerator, denominator in ALPHABET:
        bound = extreme * (abs(numerator) + denominator)
        d = 4 * denominator
        prices[d] = {n: len(primitives(n, d, modern)) for n in range(-bound, bound + 1)} | prices.get(d, {})
    for d, table in prices.items():
        for n in table:
            check_primitives(n, d, modern)
            checked.add(Fraction(n, d))
    coefficients = {Fraction(value, 4) for row in transformed for value in row}
    restoration_checks = 0
    for n, d in ALPHABET:
        check_primitives(n, d, modern)
        restoration_checks += check_helper_identity(n, d, coefficients, modern)
    base_columns = [sum(prices[4][v] for v in col) for col in columns]
    by_coefficient = {}
    all_edges = {}
    census_hash = hashlib.sha256()
    for n, d in ALPHABET:
        by_coefficient[str(Fraction(n, d))] = {"cases": 0, "positive": 0, "zero": 0, "negative": 0, "best_gain": None, "best_edges": []}
    # Hash order is a, b, then ALPHABET; each line is a,b,n,d,gain followed by LF.
    for a in range(width):
        left = columns[a]
        for b in range(width):
            if a == b:
                continue
            right = columns[b]
            for n, d in ALPHABET:
                residual_price = sum(prices[4 * d][d * y - n * x] for x, y in zip(left, right))
                gain = base_columns[b] - residual_price - 2 * len(primitives(n, d, modern))
                all_edges[a, b, n, d] = gain
                census_hash.update(f"{a},{b},{n},{d},{gain}\n".encode())
                bucket = by_coefficient[str(Fraction(n, d))]
                bucket["cases"] += 1
                bucket["positive" if gain > 0 else "zero" if gain == 0 else "negative"] += 1
                edge = [a, b, n, d]
                if bucket["best_gain"] is None or gain > bucket["best_gain"]:
                    bucket["best_gain"] = gain
                    bucket["best_edges"] = [edge]
                elif gain == bucket["best_gain"]:
                    bucket["best_edges"].append(edge)
    relation = Counter()
    individual = Counter()
    improved_pairs = []
    max_delta = None
    max_delta_pairs = []
    for a in range(width):
        for b in range(a + 1, width):
            unit = max(all_edges[x, y, n, 1] for x, y in ((a, b), (b, a)) for n in (-1, 1))
            nonunit = [(all_edges[x, y, n, d], [x, y, n, d]) for x, y in ((a, b), (b, a)) for n, d in ALPHABET if abs(n) != d]
            best = max(g for g, _ in nonunit)
            delta = best - max(0, unit)
            relation["better" if best > unit else "equal" if best == unit else "worse"] += 1
            for gain, edge in nonunit:
                individual["strictly_improves_unit_or_omit" if gain > max(0, unit) else "dominated_by_unit_or_omit"] += 1
            if delta > 0:
                improved_pairs.append({"pair": [a, b], "unit_gain": unit, "nonunit_gain": best,
                                       "edges": [edge for gain, edge in nonunit if gain == best]})
            if max_delta is None or delta > max_delta:
                max_delta = delta
                max_delta_pairs = [[a, b]]
            elif delta == max_delta:
                max_delta_pairs.append([a, b])
    baseline = sum(len(primitives(value, 4, modern)) for row in matrix for value in row)
    target_price = 2 * len(recipe["target_forest"]) * len(primitives(1, modern=modern)) + sum(base_columns)
    if not modern:
        require(baseline == recipe["baseline_panel_price"], "Original panel price differs")
        require(target_price == recipe["forest_search"]["price"], "Target-only panel price differs")
    return {
        "cost_model": "PR696 direct units and source-copy Horner" if modern else "retained binary Horner",
        "matching_certificates": check_certificate(certificate_path, all_edges, width,
                                                   "pr696_matchings" if modern else "matchings"),
        "scope": "fixed CK target forest; all ordered distinct helper pairs; q=-2,-1,-1/2,1/2,1,2",
        "canonical_payload_sha256": WORD_SHA256,
        "predecessor_recipe_sha256": RECIPE_SHA256,
        "panel_sha256": digest(panel),
        "matrix_quarters_sha256": digest(matrix),
        "transformed_quarters_sha256": digest(transformed),
        "target_forest_sha256": digest(recipe["target_forest"]),
        "target_count": len(matrix), "helper_count": width,
        "baseline_panel_price": baseline, "target_forest_panel_price": target_price,
        "census_cases": len(all_edges), "census_sha256": census_hash.hexdigest(),
        "census_serialization": "a,b,numerator,denominator,gain\n; a,b increasing; q=-2,-1,-1/2,1/2,1,2",
        "by_coefficient": by_coefficient,
        "undirected_pairs": width * (width - 1) // 2,
        "best_nonunit_vs_best_unit_pairs": dict(sorted(relation.items())),
        "nonunit_edge_dominance": dict(sorted(individual.items())),
        "strict_improvement_pairs": improved_pairs,
        "maximum_nonunit_minus_unit_or_omit_gain": max_delta,
        "maximum_delta_pairs": max_delta_pairs,
        "lowering_coefficients_checked": len(checked),
        "arbitrary_input_helper_identity_checks": restoration_checks,
        "helper_roundtrip_prices": {str(Fraction(n, d)): 2 * len(primitives(n, d, modern)) for n, d in ALPHABET},
    }


def run(word_path=WORD, recipe_path=RECIPE, certificate_path=CERTIFICATE):
    matrix, transformed, recipe, panel = read_matrix(word_path, recipe_path)
    retained = model_census(matrix, transformed, recipe, panel, certificate_path)
    retained["pr696"] = model_census(matrix, transformed, recipe, panel, certificate_path, modern=True)
    return retained


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
