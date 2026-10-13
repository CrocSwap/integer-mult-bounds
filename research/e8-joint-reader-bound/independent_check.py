#!/usr/bin/env python3
"""Independent finite checks for the E8 joint-reader lower bound.

Uses Fraction RREF and direct root-span membership, not simple-root support
masks. Imports no primary verifier or predecessor implementation. The default
run compares only CERTIFICATE.json's independent_summary: capacities, reader
thresholds, weight histogram, pair-union minimum and the twenty invoice minima.
It does not verify other certificate fields or formally prove the parabolic
reduction. --write-summary instead writes its own detailed finite-check report.
Python 3.10+, standard library. Checks remain enabled with python -O.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def canonical(vector):
    first = next(x for x in vector if x)
    return tuple(vector) if first > 0 else tuple(-x for x in vector)


def make_roots():
    # Construct all 240 signed roots, then quotient by sign. This order differs
    # from the predecessor; certificate comparisons contain no root indices.
    signed = set()
    for i, j in combinations(range(8), 2):
        for si, sj in product((-2, 2), repeat=2):
            root = [0] * 8
            root[i], root[j] = si, sj
            signed.add(tuple(root))
    signed.update(signs for signs in product((-1, 1), repeat=8)
                  if sum(x < 0 for x in signs) % 2 == 0)
    require(len(signed) == 240, "signed root count")
    require(all(dot(root, root) == 8 for root in signed), "root norms")
    roots = sorted({canonical(root) for root in signed})
    require(len(roots) == 120, "root-line count")
    simple = [(1, -1, -1, -1, -1, -1, -1, 1),
              (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        row = [0] * 8
        row[i], row[i + 1] = -2, 2
        simple.append(tuple(row))
    require(all(root in signed for root in simple), "simple roots")
    return roots, simple


def rref(rows):
    """Normalized rational Gauss-Jordan elimination, scanning columns."""
    matrix = [[Fraction(x) for x in row] for row in rows]
    if not matrix:
        return [], []
    pivots = []
    next_row = 0
    for column in range(len(matrix[0])):
        selected = next((i for i in range(next_row, len(matrix))
                         if matrix[i][column]), None)
        if selected is None:
            continue
        matrix[next_row], matrix[selected] = matrix[selected], matrix[next_row]
        divisor = matrix[next_row][column]
        matrix[next_row] = [x / divisor for x in matrix[next_row]]
        for i in range(len(matrix)):
            if i != next_row and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = [x - factor * y
                             for x, y in zip(matrix[i], matrix[next_row])]
        pivots.append(column)
        next_row += 1
        if next_row == len(matrix):
            break
    return matrix[:next_row], pivots


def in_span(vector, reduced, pivots):
    remainder = [Fraction(x) for x in vector]
    for row, pivot in zip(reduced, pivots):
        factor = remainder[pivot]
        remainder = [x - factor * y for x, y in zip(remainder, row)]
    return not any(remainder)


def check_flat_dimension(roots, flat, dimension):
    actual = len(rref([root for i, root in enumerate(roots)
                       if flat >> i & 1])[1])
    require(actual == dimension, "root-section dimension")


def make_code(roots):
    rows = []
    for left in roots:
        bits = 0
        for i, right in enumerate(roots):
            inner = dot(left, right)
            require(inner % 4 == 0, "decoder integrality")
            bits |= ((1 + inner // 4) % 2) << i
        rows.append(bits)
    # Low-pivot binary elimination, independently of physical Fraction ranks.
    pivots = {}
    for original in rows:
        row = original
        while row:
            low = row & -row
            if low in pivots:
                row ^= pivots[low]
            else:
                pivots[low] = row
                break
    require(len(pivots) == 9, "binary reader dimension")
    words = {0}
    for row in pivots.values():
        words.update([word ^ row for word in words])
    require(len(words) == 512 and set(rows) <= words, "reader-space closure")
    return sorted(words - {0})


def pair_union(c, d, code):
    require(c != 0 and d != 0 and c != d, "pair requires distinct nonzero readers")
    require(c ^ d in code, "pair XOR must be a codeword")
    numerator = c.bit_count() + d.bit_count() + (c ^ d).bit_count()
    require(numerator % 2 == 0, "pair union identity parity")
    return numerator // 2


def validate_invoice(punctures, ranks, cost, capacities, thresholds):
    require(len(ranks) == 9 and list(ranks) == sorted(ranks), "nine sorted ranks")
    require(all(0 <= d <= 8 for d in ranks), "rank domain")
    require(all(thresholds[d] <= punctures for d in ranks), "single-reader threshold")
    require(capacities[ranks[0]] + capacities[ranks[1]] >= 84 - punctures,
            "shared-puncture pair constraint")
    require(sum(ranks) == cost, "invoice sum")


def reject(call, message):
    try:
        call()
    except VerificationError as error:
        require(str(error) == message, "negative control failed at wrong obligation")
    else:
        raise VerificationError("negative control was accepted: " + message)


def reconstruct():
    roots, simple = make_roots()
    require(len(rref(simple)[1]) == 8, "simple-system rank")
    code = make_code(roots)
    weights = dict(sorted(Counter(word.bit_count() for word in code).items()))
    require(weights == {56: 255, 64: 255, 120: 1}, "nonzero weight distribution")
    word_set = set(code)
    union_min = min(pair_union(c, d, word_set) for c, d in combinations(code, 2))
    require(union_min == 84, "minimum pair support union")

    capacities = []
    thresholds = []
    flat_counts = []
    threshold_witness_ranks = []
    for dimension in range(9):
        largest_flat = 0
        smallest_deletion = 121
        best_survivors = None
        count = 0
        for indices in combinations(range(8), dimension):
            reduced, pivots = rref([simple[i] for i in indices])
            require(len(pivots) == dimension, "standard-flat dimension")
            flat = sum(1 << i for i, root in enumerate(roots)
                       if in_span(root, reduced, pivots))
            check_flat_dimension(roots, flat, dimension)
            largest_flat = max(largest_flat, flat.bit_count())
            deletions, reader = min(((word & ~flat).bit_count(), word) for word in code)
            if deletions < smallest_deletion:
                smallest_deletion = deletions
                best_survivors = reader & flat
            count += 1
        capacities.append(largest_flat)
        thresholds.append(smallest_deletion)
        flat_counts.append(count)
        witness_rank = len(rref([root for i, root in enumerate(roots)
                                if best_survivors >> i & 1])[1])
        require(witness_rank == dimension, "sharp threshold witness rank")
        threshold_witness_ranks.append(witness_rank)
    require(capacities == [0, 1, 3, 6, 12, 20, 36, 63, 120], "flat capacities")
    require(thresholds == [56, 55, 53, 50, 44, 36, 26, 1, 0], "reader thresholds")

    # Exhaust all 24,310 sorted nine-rank profiles instead of reducing the
    # optimization to the cheapest pair a+8*b. These are relaxation invoices,
    # not purportedly realizable geometries or puncture sets.
    profiles = list(combinations_with_replacement(range(9), 9))
    require(len(profiles) == 24310, "profile enumeration cardinality")
    bounds = []
    for punctures in range(36, 56):
        feasible = []
        for ranks in profiles:
            if any(thresholds[d] > punctures for d in ranks):
                continue
            if any(capacities[a] + capacities[b] < 84 - punctures
                   for a, b in combinations(ranks, 2)):
                continue
            feasible.append(ranks)
        minimum = min(map(sum, feasible))
        expected = 53 if punctures < 44 else 45 if punctures < 52 else 44
        require(minimum == expected, "rank-invoice optimum")
        witness = min(ranks for ranks in feasible if sum(ranks) == minimum)
        validate_invoice(punctures, witness, minimum, capacities, thresholds)
        require(Fraction(minimum, 120 - punctures) > Fraction(63, 111),
                "copy-ratio exclusion")
        bounds.append({"punctures": punctures, "minimum_relaxed_cost": minimum,
                       "minimizing_rank_profile": list(witness),
                       "feasible_sorted_profiles": len(feasible)})

    # The first control is the tempting but incompatible nine rank-five invoice
    # at p=36: it passes all individual thresholds and fails only jointly.
    reject(lambda: validate_invoice(36, [5] * 9, 45, capacities, thresholds),
           "shared-puncture pair constraint")
    reject(lambda: validate_invoice(36, [5] + [6] * 8, 52, capacities, thresholds),
           "invoice sum")
    reject(lambda: pair_union(code[0], code[0], word_set),
           "pair requires distinct nonzero readers")
    # Adding an independent root to a rank-one section must fail the same
    # dimension check used in the census, rather than merely testing an error.
    require(len(rref(roots[:2])[1]) == 2, "independent root control fixture")
    reject(lambda: check_flat_dimension(roots, 3, 1), "root-section dimension")
    # Physical rational rank and label binary rank are separate obligations.
    require(len(rref([[1, 1], [1, -1]])[1]) == 2,
            "wrong-characteristic physical-rank control")

    return {"root_lines": len(roots), "binary_reader_dimension": 9,
            "nonzero_reader_weight_histogram": {str(k): v for k, v in weights.items()},
            "distinct_reader_pairs_checked": len(code) * (len(code) - 1) // 2,
            "minimum_pair_support_union": union_min,
            "standard_flat_counts_by_dimension": flat_counts,
            "maximum_root_lines_by_dimension": capacities,
            "minimum_deletions_by_reader_rank": thresholds,
            "threshold_witness_ranks": threshold_witness_ranks,
            "sorted_profiles_per_puncture_count": len(profiles),
            "rank_invoice_bounds": bounds, "negative_controls": 4}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path,
                        default=Path(__file__).with_name("CERTIFICATE.json"))
    parser.add_argument("--write-summary", type=Path,
                        help="write regenerated summary instead of reading a certificate")
    args = parser.parse_args()
    summary = reconstruct()
    if args.write_summary:
        args.write_summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    else:
        certificate = json.loads(args.check.read_text())
        projection = {
            "flat_capacities": summary["maximum_root_lines_by_dimension"],
            "single_reader_thresholds": summary["minimum_deletions_by_reader_rank"],
            "reader_weight_histogram": {"0": 1, **summary["nonzero_reader_weight_histogram"]},
            "pair_union_minimum": summary["minimum_pair_support_union"],
            "rank_invoice_minima_36_through_55": [row["minimum_relaxed_cost"]
                                                  for row in summary["rank_invoice_bounds"]],
        }
        require(certificate.get("independent_summary") == projection,
                "certificate independent_summary mismatch")
    print("PASS_E8_JOINT_INDEPENDENT: 256 rational root flats; 130305 reader pairs; "
          "486200 sorted rank profiles; 4 negative controls; no new kappa")


if __name__ == "__main__":
    main()
