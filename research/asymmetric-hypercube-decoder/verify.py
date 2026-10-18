#!/usr/bin/env python3
"""Exact finite checks for README.md; Python >= 3.10, standard library only.

Copyright 2026 Sam Sung. Apache-2.0. Prepared with substantial OpenAI assistance.
Integer bits encode F2 vectors; all checks remain active under python -O.
"""
import argparse
from collections import Counter
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import random


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ports(p, k):
    return [frozenset(2 * pair + sign for pair, sign in zip(pairs, signs))
            for pairs in combinations(range(p), k)
            for signs in product(range(2), repeat=k)]


def variable_count(k):
    return (1 << k) - 2 + k - 1


def intersection_row(intersection, k):
    """Star variable L has index L-1; correction b_j follows all stars."""
    full = (1 << k) - 1
    row, subset = 0, intersection
    while subset:
        if subset != full:
            row |= 1 << (subset - 1)
        subset = (subset - 1) & intersection
    j = intersection.bit_count()
    if 0 < j < k:
        row |= 1 << (full - 1 + j - 1)
    if intersection == full:
        row |= 1 << variable_count(k)  # Augmented right-hand side: x_T.
    return row


def solve(rows, n):
    """Return coefficient rank, one solution (or None), and nullspace basis."""
    coefficient_mask, rhs = (1 << n) - 1, 1 << n
    pivots, inconsistent = {}, False
    for original in rows:
        row = original
        while row & coefficient_mask:
            pivot = (row & coefficient_mask).bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
        else:
            inconsistent |= bool(row & rhs)

    def back_substitute(free, homogeneous):
        value = free
        for pivot, row in sorted(pivots.items()):
            bit = (row & value).bit_count() % 2
            if not homogeneous:
                bit ^= bool(row & rhs)
            value |= int(bit) << pivot
        return value

    basis = [back_substitute(1 << free, True)
             for free in range(n) if free not in pivots]
    return len(pivots), None if inconsistent else back_substitute(0, False), basis


def satisfies(rows, n, witness):
    return all(((row & witness).bit_count() & 1) == ((row >> n) & 1)
               for row in rows)


def symmetric(witness, k):
    levels = {}
    for subset in range(1, (1 << k) - 1):
        size, value = subset.bit_count(), (witness >> (subset - 1)) & 1
        if size in levels and levels[size] != value:
            return False
        levels[size] = value
    return True


def actual_problem(p, k, seed):
    """Build rows directly from sets of physical coordinates, independently."""
    family = ports(p, k)
    target = random.Random(seed).choice(family)
    coordinates = sorted(target)
    stars = [frozenset(coordinates[i] for i in range(k) if mask >> i & 1)
             for mask in range(1, (1 << k) - 1)]
    rows, intersections = [], []
    for source in family:
        row = sum(1 << i for i, star in enumerate(stars) if star <= source)
        overlap = len(source & target)
        if 0 < overlap < k:
            row |= 1 << (len(stars) + overlap - 1)
        row |= int(source == target) << variable_count(k)
        rows.append(row)
        intersections.append(sum(1 << i for i, coordinate in enumerate(coordinates)
                                 if coordinate in source))
    return family, target, rows, intersections


def cell_size(p, k, j):
    remaining = k - j
    return sum(comb(remaining, u) * comb(p - k, u) * 2 ** u
               for u in range(min(remaining, p - k) + 1))


def full_intersections(intersections, k):
    return set(intersections) == set(range(1 << k))


def verify(seed, negative_controls):
    full_results, actual_results, problems = [], [], {}
    for k in range(2, 11):
        rows = [intersection_row(j, k) for j in range(1 << k)]
        n = variable_count(k)
        proper_rank, _, proper_basis = solve(rows[:-1], n)
        require(n - proper_rank == k - 1, f"proper-equation dimension: k={k}")
        require(all(satisfies(rows[:-1], n, v) for v in proper_basis), "homogeneous solutions")
        require(all(symmetric(v, k) for v in proper_basis), f"symmetry: k={k}")
        rank, witness, basis = solve(rows, n)
        feasible = bool(k & (k - 1))
        require((witness is not None) == feasible, f"feasibility: k={k}")
        if feasible:
            require(len(basis) == k - 2, f"affine dimension: k={k}")
            require(satisfies(rows, n, witness), f"solution: k={k}")
            require(symmetric(witness, k), f"affine symmetry: k={k}")
        full_results.append(dict(k=k, variables=n, rank=rank, feasible=feasible,
                                 solution_count=2 ** len(basis) if feasible else 0,
                                 affine_dimension=len(basis) if feasible else None))

    cases = [(2, 2), (3, 2), (4, 3), (4, 4), (5, 4), (6, 4),
             (6, 5), (7, 6), (7, 7), (8, 8), (9, 8)]  # (p, k)
    for p, k in cases:
        family, target, rows, intersections = actual_problem(p, k, seed)
        problems[p, k] = family, target, rows, intersections
        counts = Counter(intersections)
        require(len(family) == 2 ** k * comb(p, k), "port count")
        require(full_intersections(intersections, k), "full-family assumption")
        require(all(row == intersection_row(j, k) for row, j in zip(rows, intersections)),
                "physical incidence disagrees with compressed rows")
        require(all(counts[j] == cell_size(p, k, j.bit_count())
                    for j in range(1 << k)), "intersection cell cardinality")
        rank, witness, _ = solve(rows, variable_count(k))
        require((witness is not None) == bool(k & (k - 1)), "physical feasibility")
        actual_results.append(dict(p=p, k=k, ports=len(family), rank=rank,
                                   target=sorted(target),
                                   cell_sizes_by_overlap=[cell_size(p, k, j)
                                                          for j in range(k + 1)]))

    coefficient_exhaustion = []
    for p, k in [(2, 2), (4, 3), (4, 4)]:
        rows, n = problems[p, k][2], variable_count(k)
        count = sum(satisfies(rows, n, candidate) for candidate in range(1 << n))
        require(count == (0 if k & (k - 1) == 0 else 2 ** (k - 2)),
                "brute-force coefficient count")
        coefficient_exhaustion.append(dict(p=p, k=k, coefficient_vectors=1 << n,
                                           solution_count=count))

    puncture_results = []
    for p, k in [(2, 2), (3, 2), (4, 4), (5, 4), (6, 4), (8, 8), (9, 8)]:
        family, target, rows, intersections = problems[p, k]
        full, n = (1 << k) - 1, variable_count(k)
        threshold = 2 * (p - k) + 1
        counts = Counter(intersections)
        require(min(counts[j] for j in range(1, full)) == threshold, "cell minimum")
        require(solve(set(rows), n)[1] is None, "all-cell obstruction")
        missing = full ^ 1  # One fixed (k-1)-subset of the selected target.
        deleted = [i for i, j in enumerate(intersections) if j == missing]
        remaining = [row for i, row in enumerate(rows) if i not in deleted]
        witness = 1 << (missing - 1)
        require(len(deleted) == threshold, "sharp deletion count")
        require(all(family[i] != target for i in deleted), "target retained")
        require(satisfies(remaining, n, witness), "sharp star witness")
        require(solve(remaining, n)[1] is not None, "punctured feasibility")
        puncture_results.append(dict(p=p, k=k, threshold=threshold,
                                     star=sorted(target - {min(target)}),
                                     deleted_ports=[sorted(family[i]) for i in deleted]))

    exhaustive_results = []
    for p, k, budget in [(2, 2, 1), (3, 2, 3), (4, 4, 1), (5, 4, 2)]:
        family, target, rows, intersections = problems[p, k]
        counts, cache, examined, feasible = Counter(intersections), {}, 0, 0
        deletable = [i for i, source in enumerate(family) if source != target]
        for size in range(budget + 1):
            for deleted in combinations(deletable, size):
                removed = Counter(intersections[i] for i in deleted)
                surviving = tuple(j for j in sorted(counts) if removed[j] < counts[j])
                if surviving not in cache:
                    cache[surviving] = solve([intersection_row(j, k) for j in surviving],
                                             variable_count(k))[1] is not None
                possible = cache[surviving]
                expected = any(removed[j] == counts[j] for j in range(1, (1 << k) - 1))
                require(possible == expected, "exhaustive puncture feasibility")
                require(not possible or size >= 2 * (p - k) + 1, "threshold lower bound")
                examined += 1
                feasible += possible
        exhaustive_results.append(dict(p=p, k=k, max_deletions=budget,
                                       deletion_sets=examined, feasible_sets=feasible,
                                       distinct_equation_systems=len(cache)))

    dual_results = []
    for p, k in [(5, 4), (8, 8)]:
        target = problems[p, k][1]
        target_pairs = sorted(coordinate // 2 for coordinate in target)
        cube = [frozenset(2 * pair + sign for pair, sign in zip(target_pairs, signs))
                for signs in product(range(2), repeat=k)]
        global_stars = [star for degree in range(k) for star in ports(p, degree)]
        parities = [sum(star <= source for source in cube) % 2 for star in global_stars]
        correction_parities = [sum(len(source & target) == j for source in cube) % 2
                               for j in range(1, k)]
        require(not any(parities + correction_parities), "dual column XOR")
        require(sum(source == target for source in cube) == 1, "dual RHS XOR")
        dual_results.append(dict(p=p, k=k, cube_rows=len(cube),
                                 global_star_columns=len(global_stars),
                                 correction_columns=k - 1, coefficient_xor=0, rhs_xor=1))

    controls = []
    if negative_controls:
        rows = [intersection_row(j, 4) for j in range(16)]
        n = variable_count(4)
        omitted = solve(rows[:-1], n)[1]
        require(omitted is not None and not satisfies(problems[4, 4][2], n, omitted),
                "omitted target control")
        controls.append("omitted target equation admits zero; physical target rejects it")
        rows3 = problems[4, 3][2]
        witness3 = solve(rows3, variable_count(3))[1]
        require(not satisfies(rows3, variable_count(3), witness3 ^ (1 << 6)),
                "corrupted correction coefficient control")
        controls.append("flipped b_1 coefficient is rejected on physical ports")
        _, _, rows4, intersections4 = problems[4, 4]
        punctured = [row for row, j in zip(rows4, intersections4) if j != 14]
        require(not satisfies(punctured, n, 0), "corrupted sharp witness control")
        controls.append("zeroed sharp star witness is rejected at the retained target")
        altered = [j for j in intersections4 if j != 14]
        require(not full_intersections(altered, 4), "missing intersection control")
        escaped = solve(punctured, n)[1]
        require(escaped is not None and not satisfies(rows4, n, escaped), "false full-family control")
        controls.append("missing proper intersection breaks full-family premise and permits decoding")
        cube = ports(4, 4)
        target = cube[0]
        require(sum(target <= source for source in cube) % 2 == 1, "full-degree star control")
        require(sum(len(source & target) == 0 for source in cube) % 2 == 1, "disjoint correction control")
        controls.append("degree-k star and overlap-zero correction each break the dual certificate")

    return dict(status="PASS", assignment_seed=seed, arithmetic="exact F2 integer bitsets",
                scope="Finite verification only; see README.md for general proofs. No kappa claim.",
                full_intersection_systems=full_results, actual_port_systems=actual_results,
                exhaustive_coefficient_vectors=coefficient_exhaustion,
                sharp_puncture_witnesses=puncture_results,
                exhaustive_target_retaining_punctures=exhaustive_results,
                global_star_dual_certificates=dual_results, negative_controls=controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write deterministic receipt to this path")
    parser.add_argument("--negative-controls", action="store_true", help="exercise invalid certificates")
    args = parser.parse_args()
    claim = json.loads((HERE / "CLAIM.json").read_text())
    result = verify(claim["assignment_seed"], args.negative_controls)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(output)
    print(f"PASS: {len(result['full_intersection_systems'])} compressed systems; "
          f"{len(result['actual_port_systems'])} physical port systems; "
          f"{sum(case['coefficient_vectors'] for case in result['exhaustive_coefficient_vectors'])} "
          f"coefficient vectors; "
          f"{sum(case['deletion_sets'] for case in result['exhaustive_target_retaining_punctures'])} "
          f"puncture sets; {len(result['negative_controls'])} negative controls")


if __name__ == "__main__":
    main()
