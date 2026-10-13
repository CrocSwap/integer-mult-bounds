#!/usr/bin/env python3
"""Independent exact arithmetic check of the first E8 rank-five boundary.

Standard library only, Python >= 3.10. No project or predecessor imports.
Rational ranks use normalized Fraction RREF; binary ranks use low-column RREF.
The minimum basis cost is computed by the cumulative-rank identity, not greedy.
The finite census uses the parabolic/Weyl reduction explained in README.md.

Prepared by Philipp (@mightyOil), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    """Keep every check active under python -O."""
    if not condition:
        raise ValueError(message)


def rational_rref(rows):
    """Incremental, normalized RREF over Q, retaining all pivot eliminations."""
    basis = {}
    width = None
    for source in rows:
        row = [Fraction(value) for value in source]
        if width is None:
            width = len(row)
        require(len(row) == width, "ragged rational matrix")
        for pivot in sorted(basis):
            coefficient = row[pivot]
            if coefficient:
                row = [x - coefficient * y for x, y in zip(row, basis[pivot])]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        divisor = row[pivot]
        row = [value / divisor for value in row]
        for old_pivot, old_row in list(basis.items()):
            coefficient = old_row[pivot]
            if coefficient:
                basis[old_pivot] = [x - coefficient * y
                                    for x, y in zip(old_row, row)]
        basis[pivot] = row
        if len(basis) == width:
            break
    return [(pivot, basis[pivot]) for pivot in sorted(basis)]


def rational_rank(rows):
    return len(rational_rref(rows))


def lies_in_span(vector, rref):
    residual = [Fraction(value) for value in vector]
    for pivot, row in rref:
        coefficient = residual[pivot]
        residual = [x - coefficient * y for x, y in zip(residual, row)]
    return not any(residual)


def binary_rref(rows):
    """Eliminate the lowest nonzero bit and clear it from all retained rows."""
    basis = {}
    for source in rows:
        require(isinstance(source, int) and source >= 0, "invalid binary row")
        row = source
        for pivot in sorted(basis):
            if row & (1 << pivot):
                row ^= basis[pivot]
        if not row:
            continue
        pivot = (row & -row).bit_length() - 1
        for old_pivot in list(basis):
            if basis[old_pivot] & (1 << pivot):
                basis[old_pivot] ^= row
        basis[pivot] = row
    return [basis[pivot] for pivot in sorted(basis)]


def indices(mask, size=120):
    return [i for i in range(size) if mask & (1 << i)]


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def validate_roots(roots):
    require(len(roots) == 120 and len(set(roots)) == 120, "invalid root count")
    require(all(len(row) == 8 and dot(row, row) == 8 for row in roots),
            "invalid root geometry")
    require(all(next(x for x in row if x) > 0 for row in roots),
            "noncanonical root line representative")
    require(all(dot(left, right) % 4 == 0 for left in roots for right in roots),
            "nonintegral quarter Gram matrix")


def geometry():
    roots = []
    for left, right in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[left], row[right] = 2, 2 * sign
            roots.append(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if sum(value < 0 for value in tail) % 2 == 0:
            roots.append((1,) + tail)
    validate_roots(roots)

    simple = [(1, -1, -1, -1, -1, -1, -1, 1),
              (2, 2, 0, 0, 0, 0, 0, 0)]
    for coordinate in range(6):
        row = [0] * 8
        row[coordinate], row[coordinate + 1] = -2, 2
        simple.append(tuple(row))
    augmented = [list(row) + [int(i == j) for j in range(8)]
                 for i, row in enumerate(simple)]
    inverse_rows = rational_rref(augmented)
    require([pivot for pivot, _ in inverse_rows] == list(range(8)),
            "simple system is singular")
    inverse = [row[8:] for _, row in inverse_rows]
    for root in roots:
        coordinates = [sum(root[k] * inverse[k][j] for k in range(8))
                       for j in range(8)]
        require(all(value.denominator == 1 for value in coordinates),
                "nonintegral simple coordinates")
        require(all(value >= 0 for value in coordinates)
                or all(value <= 0 for value in coordinates),
                "mixed-sign simple coordinates")
    return roots, simple


def reader_code(roots):
    rows = [sum(((1 + dot(left, right) // 4) % 2) << j
                for j, right in enumerate(roots)) for left in roots]
    basis = binary_rref(rows)
    require(len(basis) == 9, "reader code does not have dimension nine")
    words = {0}
    for row in basis:
        words |= {word ^ row for word in words}
    words.remove(0)
    require(len(words) == 511, "incorrect nonzero reader count")
    require(Counter(word.bit_count() for word in words)
            == {56: 255, 64: 255, 120: 1}, "incorrect reader weight distribution")
    return sorted(words)


def census():
    roots, simple = geometry()
    words = reader_code(roots)
    all_roots = (1 << len(roots)) - 1
    minimum = len(roots)
    pairs = []
    flat_count = 0
    tested = 0
    for chosen in combinations(range(8), 5):
        flat_count += 1
        flat_rref = rational_rref(simple[i] for i in chosen)
        require(len(flat_rref) == 5, "incorrect parabolic dimension")
        section = sum(1 << i for i, root in enumerate(roots)
                      if lies_in_span(root, flat_rref))
        for word in words:
            tested += 1
            deleted = word & (all_roots ^ section)
            count = deleted.bit_count()
            minimum = min(minimum, count)
            if count == 36:
                require(rational_rank(roots[i] for i in indices(word & section)) == 5,
                        "equality reader does not retain rank five")
                pairs.append({"simple_indices": list(chosen),
                              "reader_root_indices": indices(word),
                              "deleted_root_indices": indices(deleted)})
    require(flat_count == 56 and tested == 28616, "incomplete rank-five census")
    require(minimum == 36 and len(pairs) == 2, "unexpected boundary equality census")
    pairs.sort(key=lambda item: (item["simple_indices"], item["reader_root_indices"]))

    punctures = []
    for deletion_tuple in sorted({tuple(pair["deleted_root_indices"]) for pair in pairs}):
        deleted = sum(1 << i for i in deletion_tuple)
        live = all_roots ^ deleted
        ranks = [(word, rational_rank(roots[i] for i in indices(word & live)))
                 for word in words]
        histogram = Counter(rank for _, rank in ranks)
        cheap_ranks = [len(binary_rref(word for word, rank in ranks if rank <= limit))
                       for limit in range(8)]
        # For a rank-nine matroid with weights in {0,...,8}, any minimum basis
        # contains rank({p: weight(p)<=k}) elements of weight <=k. Sum its
        # complementary counts over k=0,...,7 to obtain the total weight.
        cost = sum(9 - rank for rank in cheap_ranks)
        require(histogram == {5: 1, 7: 42, 8: 468}, "unexpected reader-rank histogram")
        require(cheap_ranks == [0, 0, 0, 0, 0, 1, 1, 8],
                "unexpected cumulative cheap-reader ranks")
        require(cost == 62, "unexpected minimum star-basis cost")
        punctures.append({"deleted_root_indices": list(deletion_tuple),
                          "reader_rank_histogram": {str(k): v for k, v in sorted(histogram.items())},
                          "cheap_rank_by_threshold": cheap_ranks,
                          "star_cost": cost})
    require(len(punctures) == 2, "unexpected number of distinct standard punctures")
    return {"binary_dimension": len(binary_rref(words)),
            "reader_weight_histogram": {str(k): v for k, v in sorted(
                Counter(word.bit_count() for word in words).items())},
            "flat_count": flat_count, "pairs_tested": tested,
            "minimum_deletions": minimum, "equality_pairs": pairs,
            "punctures": punctures}


def expect_rejection(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError("negative control was accepted: " + message)


def controls():
    require(rational_rank([[1, 2], [2, 4]]) == 1, "dependent rational rank control")
    require(rational_rank([[1, 1], [1, -1]]) == 2, "rational/binary distinction control")
    require(rational_rank([[1, 1], [1, 1 + Fraction(1, 10**40)]]) == 2,
            "small exact rational difference was lost")
    require(len(binary_rref([1, 2, 3])) == 2, "dependent binary rank control")
    require(len(binary_rref([3, 3])) == 1, "duplicate binary row control")
    roots, _ = geometry()
    corrupted = list(roots)
    corrupted[0] = (3,) + corrupted[0][1:]
    expect_rejection(lambda: validate_roots(corrupted), "corrupt root norm")
    expect_rejection(lambda: validate_roots([roots[1]] + roots[1:]), "duplicate root")
    expect_rejection(lambda: binary_rref([-1]), "negative binary row")
    plane = rational_rref([[1, 0, 1], [0, 1, 1]])
    require(lies_in_span([1, 1, 2], plane), "span membership control")
    require(not lies_in_span([1, 1, 3], plane), "extra independent vector accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path,
                        help="compare certificate's independent_summary with recomputed census")
    parser.add_argument("--json", action="store_true", help="print the complete independent summary")
    args = parser.parse_args()
    controls()
    summary = census()
    if args.check:
        certificate = json.loads(args.check.read_text(encoding="utf-8"))
        require(certificate.get("independent_summary") == summary,
                "certificate independent_summary differs from independent recomputation")
        print("Certificate independent_summary matches independent recomputation.")
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("Independent Fraction-RREF check passed (all checks active under -O).")
        print("Reader dimension: 9; weight histogram: {56: 255, 64: 255, 120: 1}.")
        print("56 flats x 511 readers = 28616 pairs; minimum deletions: 36; equality pairs: 2.")
        print("Both punctures: rank histogram {5: 1, 7: 42, 8: 468}; "
              "cumulative ranks [0, 0, 0, 0, 0, 1, 1, 8]; minimum star cost 62.")
        print("Exact arithmetic and rejection controls passed.")


if __name__ == "__main__":
    main()
