#!/usr/bin/env python3
"""Independent exact census of the pinned CK single-parent compensation edges.

Lauren, with substantial OpenAI Codex assistance.

This program imports no other research checker.  It reads the original compressed
word, builds its own matrix, literally counts Horner operations, enumerates the
finite n/8 candidate domain, and obtains the signed-unit floor using Prim's
algorithm and the full cycle criterion.  Extending the finite census to every
dyadic coefficient requires the analytic bounds in the accompanying proof.
Only the Python standard library is needed.  Run from any working directory.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from pathlib import Path


WORD = (Path(__file__).resolve().parents[2] /
        "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"
        "CANONICAL-WORD.json.gz")
WORD_PAYLOAD_SHA256 = "9bbc75dede090cfd7a0a0252424ea9d9f6211e2350d2a801d4e4f2f0784167c7"
TARGETS = tuple(range(112, 224))
NUMERATORS = tuple(range(-543, 0)) + tuple(range(1, 544))


def require(condition, message):
    """Checks remain active under python -O."""
    if not condition:
        raise ValueError(message)


@cache
def horner(numerator: int, exponent: int) -> tuple[int, Fraction]:
    """Return literal primitive count and the accumulated source coefficient.

    One clear, binary doublings/additions, halvings, one signed accumulation,
    and the final clear are charged.  The work register is represented by its
    exact coefficient on the unchanged source.  Its arbitrary initial value
    disappears at the first clear.  A zero macro emits nothing.
    """
    require(exponent >= 0, "negative denominator exponent")
    if numerator == 0:
        return 0, Fraction(0)
    sign = -1 if numerator < 0 else 1
    magnitude = abs(numerator)
    while exponent and magnitude % 2 == 0:
        magnitude //= 2
        exponent -= 1
    digits = []
    unprocessed = magnitude
    while unprocessed:
        unprocessed, bit = divmod(unprocessed, 2)
        digits.append(bit)
    operations = 1  # work <- 0
    work = Fraction(0)
    for position, bit in enumerate(reversed(digits)):
        if position:
            work += work
            operations += 1
        if bit:
            work += 1  # unchanged source has formal coefficient one
            operations += 1
    for _ in range(exponent):
        work /= 2
        operations += 1
    accumulated = sign * work  # target <- target +/- work
    operations += 1
    work = Fraction(0)
    operations += 1
    require(work == 0, "private work not cleared")
    return operations, accumulated


def h(numerator: int, exponent: int) -> int:
    return horner(numerator, exponent)[0]


def closed_price(value: Fraction) -> int:
    """Separate reduced-Fraction/bit-count oracle, used only for controls."""
    if value == 0:
        return 0
    denominator = value.denominator
    require(denominator & (denominator - 1) == 0, "non-dyadic value")
    n = abs(value.numerator)
    return 3 + n.bit_length() - 1 + n.bit_count() + denominator.bit_length() - 1


def check_macro_claim(numerator, exponent, claimed_count, claimed_coefficient):
    count, coefficient = horner(numerator, exponent)
    require(count == claimed_count, "incorrect primitive count")
    require(coefficient == claimed_coefficient, "incorrect accumulated coefficient")


def rejected(label, operation):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("negative control was accepted: " + label)


def arithmetic_controls():
    # Every possible residual coefficient (8*a - n*b)/32, plus every shear.
    # This interval deliberately includes unused atoms, avoiding a shared
    # assumption about which histogram entries happen to occur.
    checked = set((n, 5) for n in range(-2204, 2205))
    checked.update((n, 3) for n in NUMERATORS)
    checked.update((n, 2) for n in range(-8, 9))
    for n, exponent in checked:
        value = Fraction(n, 1 << exponent)
        count, coefficient = horner(n, exponent)
        require(count == closed_price(value), "Horner/formula price disagreement")
        require(coefficient == value, "Horner coefficient disagreement")
    failures = [
        rejected("unreduced 6/8 price", lambda: check_macro_claim(6, 3, 10, Fraction(3, 4))),
        rejected("omitted closing clear", lambda: check_macro_claim(3, 3, 8, Fraction(3, 8))),
        rejected("wrong accumulation sign", lambda: check_macro_claim(3, 3, 9, Fraction(-3, 8))),
        rejected("wrong halving exponent", lambda: check_macro_claim(3, 3, 9, Fraction(3, 4))),
        rejected("non-dyadic denominator", lambda: closed_price(Fraction(1, 3))),
    ]
    return {"exact_macro_atoms_checked": len(checked), "rejected_mutations": failures}


def load_matrix():
    compressed = WORD.read_bytes()
    payload = gzip.decompress(compressed)
    digest = hashlib.sha256(payload).hexdigest()
    require(digest == WORD_PAYLOAD_SHA256, "pinned decompressed word digest mismatch")
    word = json.loads(payload)
    panel = word["compensation"]
    require(len(panel) == 8704, "unexpected compensation gate count")
    sparse = {target: {} for target in TARGETS}
    alphabet = set()
    for row in panel:
        require(isinstance(row, list) and len(row) == 6, "malformed compensation gate")
        operation, target, source, numerator, denominator, frame = row
        require(all(type(x) is int for x in row[1:]), "noninteger gate field")
        require(operation == "add" and frame == 0, "unexpected operation or frame")
        require(target in sparse and 224 <= source < 716, "target/source interface mismatch")
        require(word["start"][target] == word["start"][source] == 0, "nonzero entrance frame")
        require(denominator > 0, "nonpositive denominator")
        coefficient = Fraction(numerator, denominator) * 4
        require(coefficient.denominator == 1, "coefficient not an integer quarter")
        require(coefficient != 0 and abs(coefficient) <= 4, "coefficient outside certified alphabet")
        require(source not in sparse[target], "duplicate target/source gate")
        sparse[target][source] = int(coefficient)
        alphabet.add(int(coefficient))
    require(all(sparse.values()), "missing target row")
    require(alphabet == {-4, -3, -2, -1, 1, 2, 3, 4}, "unexpected coefficient alphabet")
    sources = sorted({source for row in sparse.values() for source in row})
    require(len(sources) == 254, "unexpected source count")
    matrix = tuple(tuple(sparse[t].get(s, 0) for s in sources) for t in TARGETS)
    encoded = json.dumps({"targets": TARGETS, "sources": sources, "quarter_rows": matrix},
                         sort_keys=True, separators=(",", ":")).encode()
    metadata = {"decompressed_word_sha256": digest,
                "matrix_sha256": hashlib.sha256(encoded).hexdigest(),
                "target_count": len(matrix), "source_count": len(sources),
                "nonzero_entries": len(panel), "quarter_numerator_alphabet": sorted(alphabet)}
    return matrix, metadata


def edge_price(left, right, numerator):
    return 2 * h(numerator, 3) + sum(h(8 * a - numerator * b, 5)
                                      for a, b in zip(left, right))


def synthetic_controls():
    results = []
    for sign in (1, -1):
        left = (3, 3, 3, 3)  # four coefficients of 3/4
        right = (sign, sign, sign, sign)
        baseline = min(sum(h(a, 2) for a in left), edge_price(left, right, 8),
                       edge_price(left, right, -8))
        winning_numerator = 24 * sign
        exact = edge_price(left, right, winning_numerator)
        candidates = [(edge_price(left, right, n), n) for n in NUMERATORS]
        optimum = min(price for price, _ in candidates)
        minimizers = [str(Fraction(n, 8)) for price, n in candidates if price == optimum]
        require(baseline == 24 and exact == 12 and optimum == 12,
                "synthetic non-unit improvement not detected")
        require(str(3 * sign) in minimizers, "synthetic lambda=3 minimizer missing")
        results.append({"left_quarters": list(left), "right_quarters": list(right),
                        "signed_or_root_baseline": baseline, "best_cost": optimum,
                        "minimizing_lambdas": minimizers, "improvement": baseline - optimum})
    return results


def histogram_census(matrix):
    # H is sign symmetric, so (a,b) and (-a,-b) have identical contribution
    # for every lambda.  No interchange of parent and child is performed.
    letters = tuple((a, b) for a in range(5) for b in range(-4, 5)
                    if a > 0 or b > 0)
    index = {letter: i for i, letter in enumerate(letters)}
    groups = defaultdict(list)
    for child, left in enumerate(matrix):
        for parent, right in enumerate(matrix):
            if child == parent:
                continue
            histogram = Counter()
            for a, b in zip(left, right):
                if a == b == 0:
                    continue
                if a < 0 or (a == 0 and b < 0):
                    a, b = -a, -b
                histogram[index[a, b]] += 1
            groups[tuple(sorted(histogram.items()))].append((child + 112, parent + 112))
    records = []
    for signature, pairs in groups.items():
        root = sum(count * h(letters[code][0], 2) for code, count in signature)
        plus = 8 + sum(count * h(letters[code][0] - letters[code][1], 2)
                       for code, count in signature)
        minus = 8 + sum(count * h(letters[code][0] + letters[code][1], 2)
                        for code, count in signature)
        baseline = min(root, plus, minus)
        # A direct dense-row Fraction oracle checks each distinct histogram's
        # baseline, independently of its sign normalization and atom indexing.
        child, parent = pairs[0]
        left, right = matrix[child - 112], matrix[parent - 112]
        oracle_root = sum(closed_price(Fraction(a, 4)) for a in left)
        oracle_plus = 8 + sum(closed_price(Fraction(a - b, 4)) for a, b in zip(left, right))
        oracle_minus = 8 + sum(closed_price(Fraction(a + b, 4)) for a, b in zip(left, right))
        require((root, plus, minus) == (oracle_root, oracle_plus, oracle_minus),
                "histogram/dense signed-unit baseline disagreement")
        positions = tuple((child - 112) * 111 + (parent - 112) - int(parent > child)
                          for child, parent in pairs)
        records.append((signature, len(pairs), pairs[0], baseline, root, positions))
    ordered_pairs = sum(record[1] for record in records)
    require(ordered_pairs == 112 * 111, "ordered-pair coverage mismatch")

    minimum = None
    witness = None
    ties = 0
    improving = 0
    equal = 0
    root_improvements = 0
    root_minimum = None
    by_denominator = {}
    minima_digest = hashlib.sha256()
    full_census_digest = hashlib.sha256()
    evaluated = 0
    for numerator in NUMERATORS:
        atom_costs = [h(8 * a - numerator * b, 5) for a, b in letters]
        basis = 2 * h(numerator, 3)
        lambda_minimum = None
        is_unit = abs(numerator) == 8
        reduced = Fraction(numerator, 8)
        expanded_costs = [None] * ordered_pairs
        exponent = reduced.denominator.bit_length() - 1
        if not is_unit and exponent not in by_denominator:
            by_denominator[exponent] = {"lambda_count": 0, "comparison_count": 0,
                                        "minimum_margin": None}
        for signature, multiplicity, pair, baseline, root, positions in records:
            cost = basis + sum(count * atom_costs[code] for code, count in signature)
            for position in positions:
                expanded_costs[position] = cost
            margin = cost - baseline
            evaluated += multiplicity
            if lambda_minimum is None or margin < lambda_minimum:
                lambda_minimum = margin
            if is_unit:
                require(margin >= 0, "unit edge below its own baseline")
                continue
            stat = by_denominator[exponent]
            if stat["minimum_margin"] is None or margin < stat["minimum_margin"]:
                stat["minimum_margin"] = margin
            if margin < 0:
                improving += multiplicity
            if margin == 0:
                equal += multiplicity
            root_margin = cost - root
            if root_minimum is None or root_margin < root_minimum:
                root_minimum = root_margin
            if root_margin < 0:
                root_improvements += multiplicity
            if minimum is None or margin < minimum:
                minimum, ties = margin, multiplicity
                witness = {"child": pair[0], "parent": pair[1],
                           "lambda": str(reduced), "lambda_numerator_over_8": numerator,
                           "edge_cost": cost, "baseline_cost": baseline}
            elif margin == minimum:
                ties += multiplicity
        minima_digest.update(f"{numerator}:{lambda_minimum}\n".encode("ascii"))
        require(all(cost is not None for cost in expanded_costs), "digest expansion omitted a pair")
        full_census_digest.update((json.dumps([numerator, expanded_costs], sort_keys=True,
                                             separators=(",", ":")) + "\n").encode("utf-8"))
        if not is_unit:
            by_denominator[exponent]["lambda_count"] += 1
            by_denominator[exponent]["comparison_count"] += ordered_pairs
    require(evaluated == 1086 * 12432, "census comparison count mismatch")
    require(sum(x["comparison_count"] for x in by_denominator.values()) == 1084 * 12432,
            "non-unit comparison count mismatch")
    # Re-evaluate the reported minimizing witness densely without histogram
    # compression, so a wrong pair representative cannot silently pass.
    require(edge_price(matrix[witness["child"] - 112], matrix[witness["parent"] - 112],
                       witness["lambda_numerator_over_8"]) == witness["edge_cost"],
            "dense minimum-witness cost disagreement")
    return {"ordered_pairs": ordered_pairs, "distinct_pair_histograms": len(records),
            "lambdas": len(NUMERATORS), "cases": evaluated,
            "nonunit_cases": 1084 * ordered_pairs,
            "nonunit_improvements": improving, "nonunit_equalities": equal,
            "nonunit_beats_alternative": improving, "nonunit_ties_alternative": equal,
            "nonunit_beats_root": root_improvements, "minimum_root_margin": root_minimum,
            "minimum_nonunit_margin": minimum, "minimum_margin_count": ties,
            "minimum_witness": witness,
            "by_reduced_denominator_exponent": by_denominator,
            "lambda_minima_sha256": minima_digest.hexdigest(),
            "full_census_sha256": full_census_digest.hexdigest()}


def signed_unit_prim(matrix):
    count = len(matrix)
    superroot = count
    adjacency = [[None] * (count + 1) for _ in range(count + 1)]
    all_edges = []
    for i, row in enumerate(matrix):
        root_cost = sum(h(a, 2) for a in row)
        adjacency[superroot][i] = adjacency[i][superroot] = root_cost
        all_edges.append((superroot, i, root_cost))
        for j in range(i):
            plus = 8 + sum(h(a - b, 2) for a, b in zip(row, matrix[j]))
            minus = 8 + sum(h(a + b, 2) for a, b in zip(row, matrix[j]))
            adjacency[i][j] = adjacency[j][i] = min(plus, minus)
            all_edges.extend(((i, j, plus), (i, j, minus)))
    require(len(all_edges) == 12544, "signed multigraph edge count mismatch")
    used = set()
    distances = [10**30] * (count + 1)
    predecessors = [None] * (count + 1)
    distances[superroot] = 0
    tree = [[] for _ in range(count + 1)]
    total = 0
    while len(used) < count + 1:
        vertex = min((i for i in range(count + 1) if i not in used),
                     key=lambda i: (distances[i], i))
        require(distances[vertex] < 10**30, "disconnected signed-unit graph")
        total += distances[vertex]
        parent = predecessors[vertex]
        if parent is not None:
            tree[parent].append((vertex, distances[vertex]))
            tree[vertex].append((parent, distances[vertex]))
        used.add(vertex)
        for neighbor, weight in enumerate(adjacency[vertex]):
            if neighbor not in used and weight is not None and weight < distances[neighbor]:
                distances[neighbor] = weight
                predecessors[neighbor] = vertex
    max_on_path = []
    for start in range(count + 1):
        maxima = [None] * (count + 1)
        stack = [(start, -1, 0)]
        while stack:
            vertex, parent, path_maximum = stack.pop()
            maxima[vertex] = path_maximum
            stack.extend((neighbor, vertex, max(path_maximum, weight))
                         for neighbor, weight in tree[vertex] if neighbor != parent)
        require(all(weight is not None for weight in maxima), "Prim tree disconnected")
        max_on_path.append(maxima)
    for left, right, weight in all_edges:
        require(weight >= max_on_path[left][right], "spanning-tree cycle criterion failed")
    require(total == 16364, "independent signed-unit floor differs from 16364")
    return {"complex_primitive_floor": total, "vertices": count + 1,
            "multigraph_edges": len(all_edges), "cycle_inequalities_checked": len(all_edges),
            "forest_components": len(tree[superroot]),
            "target_edges": count - len(tree[superroot])}


def main():
    arithmetic = arithmetic_controls()
    synthetic = synthetic_controls()
    matrix, metadata = load_matrix()
    prim = signed_unit_prim(matrix)
    census = histogram_census(matrix)
    result = {"attribution": "Lauren, with substantial OpenAI Codex assistance",
              "scope": "independent finite dyadic single-parent edge census and signed-unit floor",
              "matrix": metadata, "arithmetic_controls": arithmetic,
              "synthetic_nonunit_improvements": synthetic, "signed_unit_prim": prim,
              "census": census,
              "finite_edge_dominance_verified": census["nonunit_improvements"] == 0,
              "all_dyadic_extension": "requires the analytic bounds in the accompanying proof"}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["finite_edge_dominance_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
