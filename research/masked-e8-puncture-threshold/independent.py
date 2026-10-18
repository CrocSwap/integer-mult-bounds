#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact check of the E7 flat bound and sharp 27-puncture witness.

This implementation uses seven fundamental-normal Weyl orbits, rational
linear algebra and fraction-free integer ranks. It imports neither the
primary checker nor any predecessor executable. Completeness of the seven
parabolic types uses the standard root-flat conjugacy theorem; enumeration
within each type is exhaustive, and the primary check supplies a separate
closure-lattice completeness argument.

Default execution is read-only. Python 3.10+, standard library only.
"""
import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, deque
from fractions import Fraction
from functools import reduce
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Failure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def positive(vector):
    return next((value for value in vector if value), 0) > 0


def primitive(vector):
    divisor = reduce(math.gcd, vector)
    require(divisor != 0, "zero projective normal")
    answer = tuple(value // divisor for value in vector)
    return answer if positive(answer) else tuple(-value for value in answer)


def root_line(vector):
    return vector if positive(vector) else tuple(-value for value in vector)


def e8_lines():
    roots = []
    for a, b in itertools.combinations(range(8), 2):
        for sa, sb in itertools.product((-1, 1), repeat=2):
            vector = [0] * 8
            vector[a], vector[b] = 2 * sa, 2 * sb
            roots.append(tuple(vector))
    roots.extend(signs for signs in itertools.product((-1, 1), repeat=8)
                 if signs.count(-1) % 2 == 0)
    require(len(roots) == len(set(roots)) == 240, "E8 roots are not 240 distinct vectors")
    lines = sorted({root_line(root) for root in roots})
    require(len(lines) == 120, "E8 line count differs from 120")
    require(all(dot(root, root) == 8 for root in roots), "incorrect doubled-root norm")
    return roots, lines


def simple_roots(roots):
    positive_roots = {root for root in roots if positive(root)}
    return sorted(root for root in positive_roots
                  if not any(tuple(a - b for a, b in zip(root, other)) in positive_roots
                             for other in positive_roots))


def solve_rational(matrix, rhs):
    rows = [[Fraction(value) for value in row] + [Fraction(value)]
            for row, value in zip(matrix, rhs)]
    order = len(rows)
    require(all(len(row) == order + 1 for row in rows), "nonsquare rational system")
    for column in range(order):
        pivot = next((row for row in range(column, order) if rows[row][column]), None)
        require(pivot is not None, "singular fundamental-normal system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for row in range(order):
            if row != column:
                multiplier = rows[row][column]
                rows[row] = [left - multiplier * right
                             for left, right in zip(rows[row], rows[column])]
    return [row[-1] for row in rows]


def integer_rank(matrix):
    """Rectangular Bareiss elimination; no modular or floating rank inference."""
    if not matrix:
        return 0
    rows = [list(row) for row in matrix]
    width = len(rows[0])
    require(all(len(row) == width for row in rows), "ragged rank matrix")
    rank, previous = 0, 1
    for column in range(width):
        pivot_row = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot_row is None:
            continue
        rows[rank], rows[pivot_row] = rows[pivot_row], rows[rank]
        pivot = rows[rank][column]
        for row in range(rank + 1, len(rows)):
            multiplier = rows[row][column]
            for later in range(column + 1, width):
                numerator = pivot * rows[row][later] - multiplier * rows[rank][later]
                require(numerator % previous == 0, "Bareiss division is not exact")
                rows[row][later] = numerator // previous
            rows[row][column] = 0
        previous = pivot
        rank += 1
        if rank == len(rows):
            break
    return rank


def root_reflection(root, simple):
    numerator = dot(root, simple)
    require(numerator % 4 == 0, "nonintegral root reflection")
    return tuple(value - numerator // 4 * coefficient
                 for value, coefficient in zip(root, simple))


def normal_reflection(normal, simple):
    # Four times the reflected vector avoids rational intermediate values.
    scalar = dot(normal, simple)
    return primitive(tuple(4 * value - scalar * coefficient
                           for value, coefficient in zip(normal, simple)))


def root_transitivity(roots, lines, target):
    simples = simple_roots(roots)
    require(len(simples) == 8 and integer_rank(simples) == 8, "incorrect E8 simple system")
    line_set = set(lines)
    for simple in simples:
        image = {root_line(root_reflection(root, simple)) for root in lines}
        require(image == line_set, "E8 simple reflection does not permute all lines")
    seen, queue = {target}, deque([target])
    while queue:
        root = queue.popleft()
        for simple in simples:
            image = root_line(root_reflection(root, simple))
            if image not in seen:
                seen.add(image)
                queue.append(image)
    require(seen == line_set, "target Weyl orbit does not cover all 120 lines")
    return len(seen)


def flat_census(roots, lines, target):
    orthogonal_roots = [root for root in roots if dot(root, target) == 0]
    orthogonal_lines = [root for root in lines if dot(root, target) == 0]
    require(len(orthogonal_roots) == 126 and len(orthogonal_lines) == 63, "incorrect E7 section")
    simples = simple_roots(orthogonal_roots)
    require(len(simples) == 7 and integer_rank(simples) == 7, "incorrect E7 simple system")
    for simple in simples:
        require({root_line(root_reflection(root, simple)) for root in orthogonal_lines}
                == set(orthogonal_lines), "E7 reflection does not preserve its lines")
    gram = [[dot(left, right) for right in simples] for left in simples]
    require(all(gram[i][i] == 8 and all(gram[i][j] in (-4, 0) for j in range(7) if j != i)
                for i in range(7)), "E7 simple roots have an invalid Cartan form")
    for root in orthogonal_lines:
        coefficients = solve_rational(gram, [dot(root, simple) for simple in simples])
        require(all(value.denominator == 1 and value >= 0 for value in coefficients),
                "positive E7 root lacks nonnegative integer simple coordinates")
        require(tuple(sum(coefficients[j] * simples[j][axis] for j in range(7))
                      for axis in range(8)) == root, "simple coordinates do not reconstruct the root")
    all_normals, all_masks, histogram, orbits = set(), set(), Counter(), []
    transcript = hashlib.sha256()
    for coordinate in range(7):
        coefficients = solve_rational(gram, [4 * (j == coordinate) for j in range(7)])
        rational_normal = [sum(coefficients[j] * simples[j][axis] for j in range(7))
                           for axis in range(8)]
        denominator = math.lcm(*(value.denominator for value in rational_normal))
        seed = primitive(tuple(int(value * denominator) for value in rational_normal))
        require(dot(seed, target) == 0, "fundamental normal leaves the E7 space")
        seen, queue = {seed}, deque([seed])
        while queue:
            normal = queue.popleft()
            for simple in simples:
                image = normal_reflection(normal, simple)
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
        require(not (seen & all_normals), "two fundamental-normal orbits overlap")
        orbit_sizes = Counter()
        for normal in sorted(seen):
            require(dot(normal, target) == 0, "orbit normal leaves the E7 space")
            mask = sum(1 << j for j, root in enumerate(orthogonal_lines) if dot(root, normal) == 0)
            flat = [root for j, root in enumerate(orthogonal_lines) if (mask >> j) & 1]
            require(integer_rank(flat) == 6, "normal does not define a rank-six E7 root flat")
            require(mask not in all_masks, "two projective normals define the same rank-six flat")
            all_masks.add(mask)
            orbit_sizes[len(flat)] += 1
            transcript.update((str(normal) + ":" + str(mask) + "\n").encode("ascii"))
        require(len(orbit_sizes) == 1, "flat cardinality changes inside a Weyl orbit")
        histogram.update(orbit_sizes)
        all_normals.update(seen)
        orbits.append({"seed": list(seed), "normal_count": len(seen),
                       "flat_size": next(iter(orbit_sizes))})
    expected = {10: 5040, 13: 2016, 16: 1008, 21: 666, 30: 63, 36: 28}
    require(dict(histogram) == expected and len(all_masks) == 8821,
            "E7 flat census differs from the exact predecessor census")
    supports = sorted(tuple(i for i in range(63) if (mask >> i) & 1) for mask in all_masks)
    supports_digest = hashlib.sha256(json.dumps(supports, sort_keys=True,
                                               separators=(",", ":")).encode()).hexdigest()
    return {"method": "seven rational fundamental-normal Weyl orbits; Bareiss ranks",
            "completeness_premise": "standard conjugacy of maximal root-spanned flats to parabolic flats",
            "flat_count": len(all_masks), "flat_sizes": {str(k): v for k, v in sorted(histogram.items())},
            "max_flat_size": max(histogram), "orbits": orbits,
            "rank6_supports_sha256": supports_digest,
            "normal_incidence_transcript_sha256": transcript.hexdigest()}


def binary_rank(rows):
    # Least-significant-bit pivots differ from the primary high-pivot implementation.
    basis = {}
    for row in rows:
        while row:
            pivot = row & -row
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def pairing(left, right):
    numerator = dot(left, right)
    require(numerator % 4 == 0, "root Gram entry is not integral")
    return (1 + numerator // 4) % 2


def copy_cost(lines, live, target_index, normal, perturb):
    costs = []
    for coordinate in range(8):
        row_support = [i for i in live if lines[i][coordinate] != 0]
        column_support = [i for i in live if lines[i][coordinate]
                          + (normal[coordinate] if perturb and i == target_index else 0) != 0]
        rows = [sum(pairing(lines[i], lines[j]) << k for k, j in enumerate(column_support))
                for i in row_support]
        costs.append(binary_rank(rows))
    return costs


def identity_counts(lines, live, target_index, normal):
    """D=Z/2 and T=Z+e_target normal^T; compare twice DT^T to Z Z^T."""
    masked_failures, all_failures, masked_entries = [], [], 0
    for i in live:
        for j in live:
            source = tuple(value + (normal[k] if j == target_index else 0)
                           for k, value in enumerate(lines[j]))
            residual_twice = dot(lines[i], source) - dot(lines[i], lines[j])
            is_masked = pairing(lines[i], lines[j]) == 1
            masked_entries += is_masked
            if residual_twice != 0:
                all_failures.append((i, j, residual_twice))
                if is_masked:
                    masked_failures.append((i, j, residual_twice))
    return masked_entries, masked_failures, all_failures


def witness_check(lines):
    target = (2, 2, 0, 0, 0, 0, 0, 0)
    normal = (1, -1, 2, 0, 0, 0, 0, 0)
    target_index = lines.index(target)
    deleted = [i for i, root in enumerate(lines)
               if dot(root, target) == 0 and dot(root, normal) != 0]
    live = [i for i in range(120) if i not in deleted]
    neighborhood = [i for i in live if pairing(lines[i], target)]
    require(len(deleted) == 27 and len(live) == 93 and target_index in live, "invalid puncture witness")
    require(integer_rank([lines[i] for i in live]) == 8, "live witness loses global rank")
    require(len(neighborhood) == 37 and integer_rank([lines[i] for i in neighborhood]) == 7,
            "bad target neighborhood is not rank seven")
    require(dot(target, normal) == 0 and all(dot(lines[i], normal) == 0 for i in neighborhood),
            "perturbation does not annihilate the masked neighborhood")
    _, baseline_mask, baseline_all = identity_counts(lines, live, target_index, (0,) * 8)
    require(not baseline_mask and not baseline_all, "baseline is not all-pairs exact")
    masked_entries, mask_failures, all_failures = identity_counts(lines, live, target_index, normal)
    require(not mask_failures and len(all_failures) == 56, "sharp witness does not separate the identities")
    require(all(j == target_index for _, j, _ in all_failures), "witness changes an unintended target")
    residual_census = Counter(residual for _, _, residual in all_failures)
    require(dict(residual_census) == {-6: 1, -2: 27, 2: 27, 6: 1}, "incorrect exact witness residuals")
    baseline_cost = copy_cost(lines, live, target_index, normal, False)
    masked_cost = copy_cost(lines, live, target_index, normal, True)
    require(baseline_cost == masked_cost == [9] * 8, "incorrect witness copy-rank invoice")

    # All 27 ways to undo one deletion must restore local rigidity and reject this witness.
    for restored in deleted:
        restored_live = sorted(live + [restored])
        restored_neighborhood = [i for i in restored_live if pairing(lines[i], target)]
        require(integer_rank([lines[i] for i in restored_neighborhood]) == 8,
                "a 26-puncture restoration fails to recover neighborhood rank eight")
        _, failures, _ = identity_counts(lines, restored_live, target_index, normal)
        require(failures, "restoring a deleted root failed to reject the mask-only witness")

    # Diagonal inclusion is essential: alpha itself is orthogonal to every off-diagonal E-neighbor.
    _, diagonal_failures, _ = identity_counts(lines, live, target_index, target)
    require(diagonal_failures and all(i == j == target_index for i, j, _ in diagonal_failures),
            "diagonal corruption was not detected at exactly the target diagonal")
    require(pairing(target, target) == 1, "mask omits the diagonal")
    full_pairing = [sum(pairing(left, right) << j for j, right in enumerate(lines)) for left in lines]
    without_affine = [sum((dot(left, right) // 4 % 2) << j for j, right in enumerate(lines))
                      for left in lines]
    require(binary_rank(full_pairing) == 9 and binary_rank(without_affine) == 8,
            "affine-label negative control does not distinguish the two pairings")
    nonzero = next((i, j, value) for i, j, value in all_failures)
    return {"target": list(target), "target_index": target_index, "normal": list(normal),
            "deleted_indices": deleted, "live_count": len(live), "live_rank": 8,
            "bad_neighborhood_size": len(neighborhood), "bad_neighborhood_rank": 7,
            "entrywise_checks_per_identity": len(live) ** 2, "masked_entries": masked_entries,
            "masked_failures": 0, "all_pairs_failures": len(all_failures),
            "twice_residual_census": {str(k): v for k, v in sorted(residual_census.items())},
            "first_unmasked_failure": list(nonzero),
            "baseline_copy_ranks": baseline_cost, "masked_copy_ranks": masked_cost,
            "copy_rank_total": sum(masked_cost), "restoration_controls": len(deleted),
            "other_controls": ["diagonal mutation rejected", "omitted affine label changes rank"]}


def build_receipt():
    roots, lines = e8_lines()
    target = (2, 2, 0, 0, 0, 0, 0, 0)
    transitivity = root_transitivity(roots, lines, target)
    census = flat_census(roots, lines, target)
    witness = witness_check(lines)
    require(63 - census["max_flat_size"] == 27, "minimum deletion threshold differs from 27")
    return {"schema_version": 1, "checker": "independent fundamental-normal Weyl orbits",
            "root_order": "lexicographically sorted sign-positive doubled E8 roots",
            "e8_target_orbit_size": transitivity, "e7": census,
            "rigidity_through_deletions": 26, "first_failure_deletions": 27,
            "witness": witness,
            "scope": "finite geometry and explicit masked identity; no supplier or moment improvement"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="compare every receipt field against this JSON")
    parser.add_argument("--write", type=Path, help="write a new receipt; existing files are not overwritten")
    args = parser.parse_args()
    try:
        here = Path(__file__).resolve().parent
        pins = json.loads((here / "SOURCES.json").read_text())
        for name, expected in {**pins["implementation_sha256"], **pins["receipt_sha256"]}.items():
            require(hashlib.sha256((here / name).read_bytes()).hexdigest() == expected,
                    "package source/receipt drift: " + name)
        if args.write:
            require(not args.write.exists(), "refusing to overwrite an existing receipt")
        receipt = build_receipt()
        check_path = args.check or (HERE / "INDEPENDENT.json" if not args.write else None)
        if check_path:
            require(json.loads(check_path.read_text()) == receipt, "independent receipt differs")
        if args.write:
            with args.write.open("x") as stream:
                json.dump(receipt, stream, indent=2, sort_keys=True)
                stream.write("\n")
    except (Failure, OSError, ValueError) as error:
        parser.exit(1, "FAIL_MASKED_E8_PUNCTURE_THRESHOLD_INDEPENDENT: " + str(error) + "\n")
    print("PASS_MASKED_E8_PUNCTURE_THRESHOLD_INDEPENDENT "
          "flats=8821 max_flat=36 targets=120 threshold=27 "
          "witness_entries=8649 changed=56 copy_rank=72 restoration_controls=27 other_controls=2")


if __name__ == "__main__":
    main()
