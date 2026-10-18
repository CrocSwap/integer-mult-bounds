#!/usr/bin/env python3
"""Independent exact controls for rank-one and disjoint-support reductions.

Only the pinned predecessor JSON is consumed: no primary or predecessor Python
is imported. The universal reduction and inherited floor are written proofs;
these fixtures exercise their hypotheses, identities, and scope boundaries.
Apache-2.0; substantial OpenAI Codex assistance, not human-only review.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent
GEOMETRY = HERE.parent / "p112-single-lift" / "reference-geometry.json"
GEOMETRY_SHA256 = "4f44af368e046002553d632ee90c6470990827cea3fae41f0f54018522d7a080"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational_rank(columns):
    """Column rank by a fresh rational echelon basis; no floating point."""
    basis = {}
    for column in columns:
        v = list(map(Fraction, column))
        for p in sorted(basis):
            if v[p]:
                coefficient = v[p]
                v = [a - coefficient * b for a, b in zip(v, basis[p])]
        pivot = next((i for i, a in enumerate(v) if a), None)
        if pivot is not None:
            denominator = v[pivot]
            basis[pivot] = [a / denominator for a in v]
    return len(basis)


def binary_rank(rows):
    """Rank over F2 by set symmetric difference, separate from Q arithmetic."""
    basis = {}
    for row in rows:
        v = set(row)
        while v:
            p = min(v)
            if p not in basis:
                basis[p] = v
                break
            v.symmetric_difference_update(basis[p])
    return len(basis)


def pair(u, v):
    return (u & v).bit_count() % 2


def beta(left, right, labels, duals):
    target = [i for i, v in enumerate(right) if v]
    return binary_rank(
        {j for j in target if pair(duals[i], labels[j])}
        for i, value in enumerate(left) if value
    )


def add(a, b):
    return [u + v for u, v in zip(a, b)]


def subtract(a, b):
    return [u - v for u, v in zip(a, b)]


def identity(left, right, gram):
    require(len(left) == len(right), "factor count")
    n = len(gram)
    require(all(len(v) == n for v in left + right), "factor length")
    return all(sum(d[i] * z[j] for d, z in zip(left, right)) == gram[i][j]
               for i in range(n) for j in range(n))


def gaussian_identity(left, right, gram, conjugate=False):
    """Full matrix equality in Z[i], represented by integer coefficient pairs."""
    for i in range(len(gram)):
        for j in range(len(gram)):
            real = imag = 0
            for d, z in zip(left, right):
                a, b = d[i]
                c, e = z[j]
                if conjugate:
                    e = -e
                real += a * c - b * e
                imag += a * e + b * c
            if (real, imag) != (gram[i][j], 0):
                return False
    return True


def main():
    raw = GEOMETRY.read_bytes()
    require(sha256(raw).hexdigest() == GEOMETRY_SHA256, "pinned geometry hash")
    data = json.loads(raw)
    x, labels, duals = data["X"], data["labels"], data["duals"]
    n = len(x)
    require(n == len(labels) == len(duals) == 112, "112 ports")
    require(all(len(row) == 8 for row in x), "eight fixed coordinates")
    columns = [list(c) for c in zip(*x)]
    require(rational_rank(columns) == 8, "full coordinate rank")
    gram = [[sum(a * b for a, b in zip(r, s)) for s in x] for r in x]
    for i in range(n):
        for j in range(n):
            root_dot = sum(a * b for a, b in zip(data["roots"][i], data["roots"][j]))
            require(root_dot % 4 == 0 and gram[i][j] * 2 == root_dot,
                    "exact root Gram identity")
            require(pair(duals[i], labels[j]) == (1 + root_dot // 4) % 2,
                    "all-entry binary pairing geometry")
    require([beta(c, c, labels, duals) for c in columns] == [8] * 8,
            "baseline cost is 64")

    rng = random.Random(21)
    pairs = list(combinations(range(8), 2))
    rng.shuffle(pairs)
    port = rng.randrange(n)
    unit = [int(i == port) for i in range(n)]
    require(rational_rank(columns + [unit]) == 9, "chosen port outside col(X)")
    zero = [0] * n
    counts = {"rank_one_reader": 0, "rank_one_source_outside_readers": 0,
              "rank_two_disjoint_axes": 0, "rank_two_dense_overlap_control": 0,
              "rank_two_disjoint_pairs": 0, "transposed_identities": 0,
              "rejected_source_perturbations": 0, "rejected_omitted_terms": 0}
    observed_costs = {}
    disjoint_component_costs = set()
    disjoint_checks = 0
    checks = 0

    def check_factors(name, t, d, z, ranks, quotient, merged=None):
        nonlocal checks
        require(rational_rank(d) == ranks[0] and rational_rank(z) == ranks[1],
                name + " exact reader/source ranks")
        require(rational_rank(columns + d) - 8 == quotient,
                name + " quotient rank")
        require(identity(columns + d, t + z, gram), name + " all-entry identity")
        checks += 1
        require(identity(t + z, columns + d, gram), name + " transposed identity")
        checks += 1
        counts["transposed_identities"] += 1
        original_extra = sum(beta(a, b, labels, duals) for a, b in zip(d, z))
        coordinate_cost = sum(beta(a, b, labels, duals) for a, b in zip(columns, t))
        if merged is not None:
            reader, source = merged
            require(identity(columns + [reader], t + [source], gram), name + " merge identity")
            checks += 1
            merged_cost = beta(reader, source, labels, duals)
            require(merged_cost <= original_extra, name + " beta contraction")
            require(coordinate_cost + merged_cost >= 64, name + " inherited floor fixture")
        total = coordinate_cost + original_extra
        observed_costs.setdefault(name, set()).add(total)
        counts[name] += 1
        return total

    def check_disjoint_components(supports, sources, combined_cost):
        nonlocal checks, disjoint_checks
        require(not set(supports[0]) & set(supports[1]), "disjoint coefficient supports")
        component_costs = []
        for support, source in zip(supports, sources):
            reader = [sum(columns[j][i] for j in support) for i in range(n)]
            component_t = [subtract(c, source) if j in support else c
                           for j, c in enumerate(columns)]
            require(identity(columns + [reader], component_t + [source], gram),
                    "single-lift component all-entry identity")
            checks += 1
            cost = sum(beta(c, z, labels, duals) for c, z in zip(columns, component_t))
            cost += beta(reader, source, labels, duals)
            require(cost >= 64, "single-lift component floor fixture")
            component_costs.append(cost)
        require(combined_cost == sum(component_costs) - 64 >= 64,
                "disjoint costs combine after subtracting one baseline")
        disjoint_component_costs.update(component_costs)
        disjoint_checks += 1

    for a, b in pairs:
        ca, cb = columns[a], columns[b]
        t = [c[:] for c in columns]
        t[a] = subtract(ca, cb)
        # Two independent readers whose quotient components cancel exactly.
        d, z = [unit, subtract(ca, unit)], [cb, cb]
        check_factors("rank_one_source_outside_readers", t, d, z, (2, 1), 1, (ca, cb))
        # Rank-one readers with individually non-coordinate source components.
        check_factors("rank_one_reader", t, [ca, ca], [unit, subtract(cb, unit)],
                      (1, 2), 0, (ca, cb))
        # Outside rank-one collapse, but covered by disjoint coefficient supports.
        inside_t = [c[:] for c in columns]
        inside_t[a], inside_t[b] = zero[:], zero[:]
        inside_cost = check_factors("rank_two_disjoint_axes", inside_t, [ca, cb], [ca, cb],
                                    (2, 2), 0)
        check_disjoint_components(([a], [b]), [ca, cb], inside_cost)
        # a1=e_a+e_b and a2=e_a-e_b overlap in both coordinates. Both D
        # and Z have rank two, quotient rank zero: outside both reductions.
        dense_t = [c[:] for c in columns]
        dense_t[a] = [-v for v in cb]
        dense_t[b] = subtract(add(cb, cb), ca)
        check_factors("rank_two_dense_overlap_control", dense_t,
                      [add(ca, cb), subtract(ca, cb)], [ca, cb], (2, 2), 0)
        perturbed = [v[:] for v in z]
        perturbed[0][(port + 1) % n] += 1
        require(not identity(columns + d, t + perturbed, gram), "reject perturbed source")
        counts["rejected_source_perturbations"] += 1
        require(not identity(columns + d[:1], t + z[:1], gram), "reject omitted term")
        counts["rejected_omitted_terms"] += 1

    # All unordered 2+2 disjoint coefficient-support partitions: C(8,4)*3=210.
    # Both readers use two coordinates, so these are not axis-only examples.
    for four in combinations(range(8), 4):
        for partner in four[1:]:
            left_support = [four[0], partner]
            right_support = [j for j in four if j not in left_support]
            supports = [left_support, right_support]
            readers = [[sum(columns[j][i] for j in support) for i in range(n)]
                       for support in supports]
            sources = [columns[support[0]] for support in supports]
            disjoint_t = [c[:] for c in columns]
            for support, source in zip(supports, sources):
                for j in support:
                    disjoint_t[j] = subtract(columns[j], source)
            cost = check_factors("rank_two_disjoint_pairs", disjoint_t, readers, sources,
                                 (2, 2), 0)
            check_disjoint_components(supports, sources, cost)
    require(counts["rank_two_disjoint_pairs"] == 210 and disjoint_checks == 238,
            "complete finite disjoint-support fixture domain")

    # k=3 and quotient rank k-1: all three sources collapse to one.
    second = next([int(i == p) for i in range(n)] for p in range(n)
                  if rational_rank(columns + [unit, [int(i == p) for i in range(n)]]) == 10)
    a, b = pairs[0]
    ca, cb = columns[a], columns[b]
    t = [c[:] for c in columns]
    t[a] = subtract(ca, cb)
    three_d = [unit, second, subtract(subtract(ca, unit), second)]
    require(rational_rank(three_d) == 3 and rational_rank(columns + three_d) - 8 == 2,
            "k=3 exact quotient rank")
    require(rational_rank([cb, cb, cb]) == 1 and identity(columns + three_d, t + [cb] * 3, gram),
            "k=3 exact source rank and identity")
    require(beta(ca, cb, labels, duals)
            <= sum(beta(v, cb, labels, duals) for v in three_d), "k=3 beta contraction")
    checks += 1

    # Boundary rank zero and quotient rank two with zero sources.
    require(identity(columns + [unit, second], columns + [zero, zero], gram), "zero source boundary")
    require(rational_rank([zero, zero]) == 0 and rational_rank(columns + [unit, second]) == 10,
            "zero source boundary ranks")
    require(identity(columns + [zero, zero], columns + [unit, second], gram), "zero reader boundary")
    checks += 2

    # Scale one added reader by i and its source by -i. Bilinear transpose
    # preserves the identity, whereas substituting adjoint reverses its sign.
    real_vector = lambda v: [(value, 0) for value in v]
    complex_left = list(map(real_vector, columns)) + [[(0, v) for v in ca], real_vector(zero)]
    complex_right = list(map(real_vector, t)) + [[(0, -v) for v in cb], real_vector(zero)]
    require(gaussian_identity(complex_left, complex_right, gram), "Gaussian-integer bilinear identity")
    require(not gaussian_identity(complex_left, complex_right, gram, conjugate=True),
            "reject conjugate-transpose substitution")
    checks += 1
    print(json.dumps({
        "status": "pass",
        "scope": "independent exact finite fixtures; universal proof remains in PROOF.md",
        "seed": 21,
        "source_geometry_sha256": GEOMETRY_SHA256,
        "coordinate_pairs": len(pairs),
        "outside_port": port,
        "full_matrix_identities": checks,
        "entries_per_identity": n * n,
        "controls": counts,
        "observed_total_costs": {k: sorted(v) for k, v in observed_costs.items()},
        "disjoint_support_controls": {
            "axis_pairs": 28,
            "two_plus_two_partitions": 210,
            "component_identity_count": 2 * disjoint_checks,
            "component_costs": sorted(disjoint_component_costs),
            "combined_cost_rule": "component_1 + component_2 - 64 >= 64"
        },
        "outside_both_reductions": "rank_two_dense_overlap_control",
        "general_k_control": {"k": 3, "reader_rank": 3, "source_rank": 1, "quotient_rank": 2},
        "zero_boundaries": 2,
        "conjugate_transpose_negative_control": "rejected"
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
