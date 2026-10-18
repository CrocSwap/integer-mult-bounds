#!/usr/bin/env python3
"""Exact replay of the scoped Hurwitz asymmetric copy-floor certificate.

Standard library only; no SAT solver or predecessor implementation is executed.
Prepared by Douglas R. Colkitt with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent
UNITS = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def left(q, vector):
    """Hamilton multiplication q * v on each of the two four-coordinate blocks."""
    a, b, c, d = q
    out = []
    for offset in (0, 4):
        e, f, g, h = vector[offset:offset + 4]
        out.extend((a*e-b*f-c*g-d*h, a*f+b*e+c*h-d*g,
                    a*g-b*h+c*e+d*f, a*h+b*g-c*f+d*e))
    return tuple(out)


def e8_roots():
    """All 240 E8 roots in doubled standard coordinates, squared norm eight."""
    roots = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            roots.append(tuple(row))
    roots.extend(row for row in product((-1, 1), repeat=8)
                 if sum(x < 0 for x in row) % 2 == 0)
    return sorted(roots)


def rank_q(rows):
    """Fraction-free row reduction, with gcd normalization after each step."""
    pivots = {}
    for source in rows:
        row = list(source)
        for column, basis in sorted(pivots.items()):
            if row[column]:
                a, b = basis[column], row[column]
                row = [a*x-b*y for x, y in zip(row, basis)]
                divisor = gcd(*row)
                if divisor:
                    row = [x // divisor for x in row]
        if any(row):
            column = next(i for i, x in enumerate(row) if x)
            divisor = gcd(*row)
            row = [x // divisor for x in row]
            if row[column] < 0:
                row = [-x for x in row]
            pivots[column] = row
    return len(pivots)


def rank_fraction(rows):
    """Separate rational implementation: column pivoting on a dense matrix."""
    matrix = [[Fraction(x) for x in row] for row in rows]
    if not matrix:
        return 0
    pivot = 0
    for column in range(len(matrix[0])):
        choice = next((i for i in range(pivot, len(matrix))
                       if matrix[i][column]), None)
        if choice is None:
            continue
        matrix[pivot], matrix[choice] = matrix[choice], matrix[pivot]
        scale = matrix[pivot][column]
        matrix[pivot] = [x / scale for x in matrix[pivot]]
        for i in range(pivot + 1, len(matrix)):
            scale = matrix[i][column]
            matrix[i] = [x-scale*y for x, y in zip(matrix[i], matrix[pivot])]
        pivot += 1
    return pivot


def rank_f2(rows):
    basis = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in basis:
                row ^= basis[bit]
            else:
                basis[bit] = row
                break
    return len(basis)


def indices(mask):
    return [i for i in range(10) if mask >> i & 1]


def mask_of(items):
    return sum(1 << i for i in items)


def geometry(roots):
    require(len(roots) == len(set(roots)) == 240, "root cardinality")
    root_set = set(roots)
    groups = {}
    for root in roots:
        require(len(root) == 8 and dot(root, root) == 8, "root norm")
        basis = [left(q, root) for q in UNITS]
        require(all(row in root_set for row in basis), "quaternion root closure")
        require([[dot(x, y) for y in basis] for x in basis]
                == [[8 * (i == j) for j in range(4)] for i in range(4)],
                "line basis Gram matrix")
        require(left(UNITS[1], left(UNITS[2], root)) == left(UNITS[3], root),
                "ij = k")
        require(left(UNITS[2], left(UNITS[1], root))
                == tuple(-x for x in left(UNITS[3], root)), "ji = -k")
        # Eight times the orthogonal projector: equal keys mean equal Q-spans.
        projector = tuple(sum(b[i]*b[j] for b in basis)
                          for i in range(8) for j in range(8))
        groups.setdefault(projector, []).append(root)
    require(len(groups) == 10 and set(map(len, groups.values())) == {24},
            "ten quaternionic lines of 24 roots")
    representatives = [min(groups[key]) for key in sorted(groups)]
    bases = [[left(q, root) for q in UNITS] for root in representatives]
    for i, j in combinations(range(10), 2):
        require(rank_q(bases[i] + bases[j]) == 8, "distinct lines span Q^8")
    mates = []
    for i in range(10):
        orthogonal = [j for j in range(10)
                      if all(dot(x, y) == 0 for x in bases[i] for y in bases[j])]
        require(len(orthogonal) == 1, "unique orthogonal mate")
        mates.append(orthogonal[0])
    validate_mates(mates)
    pairs = [(i, mates[i]) for i in range(10) if i < mates[i]]
    return representatives, bases, mates, pairs


def validate_mates(mates):
    require(len(mates) == 10 and all(isinstance(j, int) and 0 <= j < 10
                                   for j in mates), "mate indices")
    require(all(j != i and mates[j] == i for i, j in enumerate(mates)),
            "orthogonality must be a perfect matching")


def formula_cost(readers, sources, mates):
    if not readers or not sources:
        return 0
    if len(readers) >= 2 and len(sources) >= 2:
        return 2
    if len(readers) == len(sources) == 1 and mates[readers[0]] == sources[0]:
        return 0
    return 1


def gram_cost_table(bases, mates):
    # Every set with >=2 lines spans Q^8; its first two lines give a basis.
    small = [(i,) for i in range(10)] + list(combinations(range(10), 2))
    costs = {}
    histogram = Counter()
    for readers in small:
        rb = [row for i in readers for row in bases[i]]
        for sources in small:
            sb = [row for i in sources for row in bases[i]]
            matrix = [[dot(x, y) for y in sb] for x in rb]
            rank = rank_q(matrix)
            require(rank == rank_fraction(matrix), "independent Q-rank mismatch")
            require(rank % 4 == 0, "Gram rank is divisible by four")
            cost = rank // 4
            require(cost == formula_cost(readers, sources, mates),
                    "Gram rank formula")
            costs[readers, sources] = cost
            histogram[rank] += 1
    return costs, histogram


def support_data(costs, pairs):
    supports = [indices(mask) for mask in range(1024)]
    reduced = [tuple(items[:2]) for items in supports]
    transversals = [mask_of(items) for items in product(*pairs)]
    require(len(set(transversals)) == 32, "32 distinct transversals")
    hit = [sum(1 << t for t, transversal in enumerate(transversals)
               if mask & transversal) for mask in range(1024)]
    table = []
    histogram, slacks = Counter(), Counter()
    for readers in range(1024):
        row = []
        for sources in range(1024):
            cost = (costs[reduced[readers], reduced[sources]]
                    if readers and sources else 0)
            active = (hit[readers] & hit[sources]).bit_count()
            require(2 * active <= 32 * cost, "dual rectangle inequality")
            row.append(cost)
            histogram[cost] += 1
            slacks[32 * cost - 2 * active] += 1
        table.append(row)
    return table, transversals, histogram, slacks


def validate_pattern(rows, mates):
    require(len(rows) == 10, "decoder row count")
    for i, row in enumerate(rows):
        require(isinstance(row, int) and 0 <= row < 1024, "decoder row domain")
        require(row >> i & 1, "decoder diagonal")
        require(row & ~((1 << i) | (1 << mates[i])) == 0,
                "decoder forbidden nonorthogonal entry")


def rectangle_sum(totals):
    rows = [0] * 10
    for readers, sources in totals:
        require(0 <= readers < 1024 and 0 <= sources < 1024, "total domain")
        for i in indices(readers):
            rows[i] ^= sources
    return rows


def validate_witness(totals, mates, table, reported_cost):
    rows = rectangle_sum(totals)
    validate_pattern(rows, mates)
    actual_cost = sum(table[r][a] for r, a in totals)
    require(actual_cost == reported_cost, "witness copy invoice")
    return rows


def all_fitting_decoders(mates, pairs, table, transversals):
    ranks, symmetric = Counter(), 0
    for free_bits in range(1024):
        rows = [(1 << i) | (((free_bits >> i) & 1) << mates[i])
                for i in range(10)]
        validate_pattern(rows, mates)
        for transversal in transversals:
            require(all(rows[i] & transversal == 1 << i
                        for i in indices(transversal)), "principal identity")
            require(rank_f2([rows[i] & transversal
                             for i in indices(transversal)]) == 5,
                    "transversal identity rank")
        ranks[rank_f2(rows)] += 1
        symmetric += all(((free_bits >> i) & 1) == ((free_bits >> j) & 1)
                         for i, j in pairs)
        # Each row supplies an attaining cost-one total, for EVERY completion.
        totals = [(1 << i, rows[i]) for i in range(10)]
        require(validate_witness(totals, mates, table, 10) == rows,
                "row decomposition")
    pair_totals = [(mask_of(pair), mask_of(pair)) for pair in pairs]
    pair_rows = validate_witness(pair_totals, mates, table, 10)
    require(rank_f2(pair_rows) == 5, "five-total witness rank")
    require(ranks == {5: 1, 6: 15, 7: 90, 8: 270, 9: 405, 10: 243},
            "fitting-matrix rank distribution")
    require(symmetric == 32, "symmetric completion count")
    return ranks, symmetric, pair_totals


def reject(name, callback):
    try:
        callback()
    except ValueError:
        return name
    raise ValueError("negative control accepted: " + name)


def validate_dual_sample(transversals, table, readers, sources):
    active = sum(bool(readers & t) and bool(sources & t) for t in transversals)
    require(2 * active <= len(transversals) * table[readers][sources],
            "dual rectangle inequality")


def negative_controls(roots, mates, pairs, table, transversals, pair_totals):
    controls = []
    controls.append(reject("missing root", lambda: geometry(roots[:-1])))
    bad_mates = mates.copy()
    bad_mates[0] = 0
    controls.append(reject("invalid orthogonality matching",
                           lambda: validate_mates(bad_mates)))
    rows = rectangle_sum(pair_totals)
    bad = rows.copy()
    bad[0] ^= 1
    controls.append(reject("missing diagonal", lambda: validate_pattern(bad, mates)))
    bad = rows.copy()
    j = next(i for i in range(10) if i not in (0, mates[0]))
    bad[0] ^= 1 << j
    controls.append(reject("forbidden nonorthogonal coefficient",
                           lambda: validate_pattern(bad, mates)))
    controls.append(reject("omitted orthogonal-pair total",
                           lambda: validate_witness(pair_totals[:-1], mates, table, 8)))
    controls.append(reject("undercharged copy invoice",
                           lambda: validate_witness(pair_totals, mates, table, 9)))
    cheap = [row.copy() for row in table]
    pair = mask_of(pairs[0])
    cheap[pair][pair] = 1
    controls.append(reject("full-span rectangle priced at one",
                           lambda: validate_dual_sample(transversals, cheap, pair, pair)))
    incomplete = transversals[1:]
    vertex = next(i for i in range(10) if not transversals[0] >> i & 1)
    controls.append(reject("biased 31-transversal certificate",
                           lambda: validate_dual_sample(incomplete, table,
                                                        1 << vertex, 1 << vertex)))
    # A nonsymmetric fitting decoder must be ACCEPTED, not filtered away.
    asymmetric = [1 << i for i in range(10)]
    asymmetric[0] |= 1 << mates[0]
    require(asymmetric[mates[0]] & 1 == 0, "asymmetric positive control")
    require(validate_witness([(1 << i, asymmetric[i]) for i in range(10)],
                             mates, table, 10) == asymmetric,
            "asymmetric attaining decoder")
    # A zero-charge mate rectangle changes a free entry and stays invisible
    # on every transversal; do not incorrectly force every total to cost >0.
    free = (1, 1 << mates[0])
    require(table[free[0]][free[1]] == 0, "zero-charge rectangle")
    validate_witness(pair_totals + [free], mates, table, 10)
    return controls


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    root = HERE.parents[1]
    for entry in manifest["files"]:
        path = root / entry["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == entry["sha256"], "source pin: " + entry["path"])
    return manifest


def compute():
    manifest = source_pins()
    roots = e8_roots()
    representatives, bases, mates, pairs = geometry(roots)
    costs, gram_histogram = gram_cost_table(bases, mates)
    table, transversals, histogram, slacks = support_data(costs, pairs)
    ranks, symmetric, totals = all_fitting_decoders(mates, pairs, table, transversals)
    controls = negative_controls(roots, mates, pairs, table, transversals, totals)
    require(histogram == {0: 2057, 1: 20350, 2: 1026169}, "support census")
    # Rational-rank normalization: ten rank-four ports, copy floor forty.
    deficits = {str(s): (s-1)*10*4-s*10*4 for s in range(1, 33)}
    require(set(deficits.values()) == {-40}, "optimistic deficit accounting")
    return {
        "schema": 1, "base_commit": manifest["base_commit"], "assignment_seed": 49,
        "domain": "all binary asymmetric scalar-total decoders on ten Hurwitz E8 lines",
        "geometry": {"roots": len(roots), "lines": 10, "roots_per_line": 24,
                     "rational_ambient_dimension": 8, "rational_line_dimension": 4,
                     "representatives": representatives, "orthogonal_pairs": pairs,
                     "independent_gram_rank_checks": len(costs),
                     "gram_rational_rank_histogram": dict(sorted(gram_histogram.items()))},
        "dual": {"transversals": transversals, "weight_per_transversal": "1/16",
                 "all_reader_source_support_pairs": 1024**2,
                 "cost_histogram": dict(sorted(histogram.items())),
                 "scaled_dual_slack_histogram": dict(sorted(slacks.items())),
                 "proved_copy_floor_quaternionic_units": 10,
                 "proved_copy_floor_rational_units": 40},
        "decoders": {"completions": 1024, "symmetric": symmetric,
                     "asymmetric": 1024-symmetric,
                     "f2_rank_histogram": dict(sorted(ranks.items())),
                     "all_row_decompositions_cost": 10,
                     "five_total_attaining_witness": totals},
        "accounting": {"v": 10, "k": 4, "cst_lower_bound": 40,
                       "D_per_stage_copy_at_floor": "(s-1)*40-s*40 = -40",
                       "finite_arithmetic_controls_s_1_to_32": deficits},
        "negative_controls": controls,
        "positive_controls": ["nonsymmetric cost-ten decoder",
                              "zero-charge orthogonal-mate rectangle"],
        "scope": "Written finite-model proof with exact replay; no new supplier or kappa; no full theorem formalization.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a fully checked deterministic receipt")
    args = parser.parse_args()
    receipt = compute()
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.write.write_text(encoded)
    else:
        require(encoded == (HERE / "RESULTS.json").read_text(), "receipt mismatch")
    print("PASS_HURWITZ_ASYMMETRIC_COPY_FLOOR: cost 10; "
          "1048576 support pairs; 1024 decoders; 8 negative controls")


if __name__ == "__main__":
    main()
