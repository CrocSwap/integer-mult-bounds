#!/usr/bin/env python3
"""Exact finite witnesses for the scope of PR288's abelian-metric assertion.

Standard library only. The general cut argument is written in README.md.
Copyright 2026 Jerry Chen. SPDX-License-Identifier: Apache-2.0
Prepared with substantial OpenAI Codex assistance.
"""

import argparse
from collections import deque
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
QUOTE = "- Abelian or cyclic frame groups (units mod N, digit rotations, Z/N translations) have l₁-embeddable metrics, so\n  their gap is 1. [arg]"
MARKER = "PASS_ABELIAN_METRIC_SCOPE cayley=2 rational_shears=8 cycle_controls=2 distortion=4/3,3/2 no_new_kappa"
SHEAR_POINTS = [
    [[0, 0], [0, 0]], [[0, 0], [-1, 1]],
    [[1, 0], [0, 1]], [[0, 1], [0, 1]],
    [[0, 1], [-1, 0]], [[1, 0], [-1, 0]],
    [[1, 1], [-1, 1]], [[1, 1], [0, 0]],
]


class VerificationError(ValueError):
    """A mathematical witness or its recorded source failed admission."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def cayley_metric(order, generators):
    """Shortest unit-cost word metric on the additive cyclic group."""
    require(type(order) is int and order >= 2, "invalid group order")
    require(all(type(g) is int and 0 < g < order for g in generators),
            "generators must be nonzero canonical residues")
    require(len(set(generators)) == len(generators), "duplicate generator")
    require(set(generators) == {(-g) % order for g in generators},
            "generator set is not inverse-closed")
    distances = [None] * order
    distances[0] = 0
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for generator in generators:
            neighbor = (current + generator) % order
            if distances[neighbor] is None:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    require(None not in distances, "Cayley graph is disconnected")
    return [[distances[(b - a) % order] for b in range(order)]
            for a in range(order)]


def quadratic_value(metric, points, coefficients):
    require(len(points) == len(coefficients), "coefficient length mismatch")
    require(len(points) == len(set(points)), "witness repeats a point")
    require(all(type(i) is int and 0 <= i < len(metric) for i in points),
            "invalid witness point")
    require(all(type(b) is int for b in coefficients), "noninteger coefficient")
    return sum(coefficients[i] * coefficients[j] * metric[points[i]][points[j]]
               for i, j in combinations(range(len(points)), 2))


def cut_inequality_control(coefficients):
    """Check every cut, including trivial cuts, against t(total-t)."""
    require(sum(coefficients) in (0, 1), "unsupported cut inequality")
    size = len(coefficients)
    for mask in range(1 << size):
        metric = [[int(bool(mask & (1 << i)) != bool(mask & (1 << j)))
                   for j in range(size)] for i in range(size)]
        value = quadratic_value(metric, list(range(size)), coefficients)
        subtotal = sum(b for i, b in enumerate(coefficients) if mask & (1 << i))
        require(value == subtotal * (sum(coefficients) - subtotal),
                "cut identity failed")
        require(value <= 0, "cut violates the proposed inequality")
    return 1 << size


def weighted_cuts(order, masks, weight):
    require(isinstance(weight, Fraction) and weight >= 0, "invalid cut weight")
    require(all(type(mask) is int and 0 < mask < (1 << order) - 1 for mask in masks),
            "invalid cut mask")
    return [[sum((weight for mask in masks
                  if bool(mask & (1 << i)) != bool(mask & (1 << j))), Fraction(0))
             for j in range(order)] for i in range(order)]


def validate_counterexample(order, metric):
    require(order in (6, 8), "case is outside the two frozen witnesses")
    expected = [[0 if i == j else 1 if (i - j) % 2 else 2
                 for j in range(order)] for i in range(order)]
    require(metric == expected, "metric is not the stated complete bipartite graph")
    points = [0, 2, 4, 1, 3]
    coefficients = [1, 1, 1, -1, -1]
    value = quadratic_value(metric, points, coefficients)
    require(value == 2, "five-point witness does not have excess two")
    full_coefficients = [1 if i % 2 == 0 else -1 for i in range(order)]
    full_value = quadratic_value(metric, list(range(order)), full_coefficients)
    half = order // 2
    require(full_value == half * (half - 2) > 0, "negative-type witness failed")

    # One cut {e,o} for every even/odd pair, with weight 1/half.
    masks = [(1 << even) | (1 << odd)
             for even in range(0, order, 2) for odd in range(1, order, 2)]
    embedding = weighted_cuts(order, masks, Fraction(1, half))
    ratios = [embedding[i][j] / metric[i][j]
              for i, j in combinations(range(order), 2)]
    distortion = Fraction(2 * (half - 1), half)
    require(min(ratios) == 1 and max(ratios) == distortion,
            "cut embedding does not attain the claimed distortion")
    within_sum = sum(metric[i][j] for i, j in combinations(range(order), 2)
                     if (i - j) % 2 == 0)
    cross_sum = sum(metric[i][j] for i, j in combinations(range(order), 2)
                    if (i - j) % 2)
    require(Fraction(within_sum, cross_sum) == distortion,
            "distortion lower and upper bounds do not agree")
    return {
        "order": order,
        "generators": list(range(1, order, 2)),
        "distances": metric,
        "five_point_witness": {"points": points, "coefficients": coefficients,
                               "value": value},
        "negative_type_witness": {"coefficients": full_coefficients,
                                  "value": full_value,
                                  "all_cuts_checked": cut_inequality_control(full_coefficients)},
        "optimal_l1_distortion": str(distortion),
        "attaining_cut_masks": masks,
        "cut_weight": str(Fraction(1, half)),
        "involutive_target": {"element": 4, "distance": metric[0][4]}
                              if order == 8 else None,
    }


def validate_cycle(order, metric):
    masks = [sum(1 << ((start + k) % order) for k in range(order // 2))
             for start in range(order)]
    embedded = weighted_cuts(order, masks, Fraction(1, 2))
    require(embedded == metric, "cycle metric fails its exact cut embedding")
    return {"order": order, "generators": [1, order - 1], "distances": metric,
            "cut_masks": masks, "cut_weight": "1/2"}


def matrix_product(left, right):
    return [[sum(a * b for a, b in zip(row, column))
             for column in zip(*right)] for row in left]


def shear(matrix):
    return [[1, 0, *matrix[0]], [0, 1, *matrix[1]],
            [0, 0, 1, 0], [0, 0, 0, 1]]


def validate_shears(points, reference):
    require(len(points) == 8, "the shear witness needs all eight points")
    require(all(len(m) == 2 and all(len(row) == 2 for row in m)
                and all(type(x) is int for row in m for x in row) for m in points),
            "invalid integral shear matrix")
    distances = []
    determinants = set()
    for left in points:
        row = []
        for right in points:
            difference = [[right[i][j] - left[i][j] for j in range(2)] for i in range(2)]
            determinant = difference[0][0] * difference[1][1] - difference[0][1] * difference[1][0]
            rank = 2 if determinant else int(any(x for line in difference for x in line))
            row.append(rank)
            if rank == 2:
                determinants.add(determinant)
            elif rank == 1:
                require(any(abs(x) == 1 for line in difference for x in line),
                        "rank-one difference has no unit entry")
            inverse = shear([[-x for x in line] for line in left])
            require(matrix_product(inverse, shear(right)) == shear(difference),
                    "relative shear identity failed")
            require(matrix_product(shear(left), shear(right))
                    == matrix_product(shear(right), shear(left)), "shears do not commute")
        distances.append(row)
    require(distances == reference, "rational rank metric is not the stated K4,4 metric")
    require(determinants <= {-2, -1, 1, 2}, "unexpected determinant in odd-field control")
    return {"matrices_in_vertex_order": points, "rank_distances": distances,
            "ordered_pairs_checked": 64, "nonzero_determinants": sorted(determinants),
            "rank_one_differences_have_unit_entries": True,
            "metric_isometry_only_not_a_cyclic_group_homomorphism": True}


def check_source(package):
    manifest = (package / "SOURCES.json").read_bytes()
    sources = json.loads(manifest)
    pin = sources["source"]
    data = (package / "sources/pr288-README.md").read_bytes()
    require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source SHA256 mismatch")
    blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    require(blob == pin["git_blob"], "source Git blob mismatch")
    require(len(data) == pin["bytes"], "source byte count mismatch")
    require(QUOTE in data.decode("utf-8"), "quoted source premise is absent")
    return {"head": pin["commit"], "git_blob": blob, "sha256": pin["sha256"],
            "repository": pin["repository"], "path": pin["path"],
            "source_manifest_sha256": hashlib.sha256(manifest).hexdigest()}


def build_certificate(package=HERE):
    source = check_source(package)
    counterexamples = [validate_counterexample(n, cayley_metric(n, list(range(1, n, 2))))
                       for n in (6, 8)]
    cycles = [validate_cycle(n, cayley_metric(n, [1, n - 1])) for n in (6, 8)]
    require((2 * 4) % 8 == 0, "C8 target is not an involution")
    return {
        "format": "abelian-cayley-metric-scope-v1",
        "status": "metric premise counterexample; no supplier or kappa claim",
        "source": source,
        "pentagonal_cut_controls": cut_inequality_control([1, 1, 1, -1, -1]),
        "counterexamples": counterexamples,
        "cycle_controls": cycles,
        "rational_shear_witness": validate_shears(SHEAR_POINTS, counterexamples[1]["distances"]),
    }


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write", type=Path, help="write a checked receipt to a new path")
    args = parser.parse_args()
    try:
        result = build_certificate()
        expected = json.loads(args.certificate.read_text(encoding="utf-8"))
        # Canonical serialization preserves JSON types (True must not equal 1).
        require(canonical(result) == canonical(expected), "recorded certificate differs")
        if args.write is not None:
            with args.write.open("x", encoding="utf-8", newline="\n") as output:
                output.write(canonical(result))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, "FAIL_ABELIAN_METRIC_SCOPE: " + str(error) + "\n")
    print(MARKER)


if __name__ == "__main__":
    main()
