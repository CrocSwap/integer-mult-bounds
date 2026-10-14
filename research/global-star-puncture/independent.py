#!/usr/bin/env python3
"""Independent parity-check replay for the finite proper-star puncture cases.

Ports and incidence are regenerated locally.  The parity-check matrix H is
the full kernel of the proper-star incidence matrix G, found by list-valued
GF2 RREF, rather than packed-integer row-space membership.  No other verifier
or prototype is imported.  Exact completeness follows from checked ranks
and G H^T = 0.  The replay concerns only (p, k) = (5, 4), (6, 4); it is not a
formal proof of a general puncture theorem or the multiplication theorem.

Copyright 2026 Luke Mansoor.  Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
"""
import argparse
from itertools import combinations, product
import json
from math import comb


EXPECTED = {
    5: {"ports": 80, "stars": 131, "rank": 65, "check_rank": 15,
        "pair_syndromes": 1345, "minimum_weight": 4},
    6: {"ports": 240, "stars": 233, "rank": 155, "check_rank": 85,
        "pair_syndromes": 28680, "minimum_weight": 6},
}


class VerificationError(RuntimeError):
    """A proof-relevant obligation failed, also under python -O."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def enumerate_ports(pair_count, size):
    """Sorted-coordinate tuples, one coordinate per selected pair."""
    return [tuple(2 * pair + sign for pair, sign in zip(pair_ids, signs))
            for pair_ids in combinations(range(pair_count), size)
            for signs in product((0, 1), repeat=size)]


def incidence(stars, ports):
    return [[int(all(coordinate in port for coordinate in star))
             for port in ports] for star in stars]


def rref(matrix):
    """Exact GF2 RREF, mutating a copy; no packed integer arithmetic."""
    rows = [list(row) for row in matrix]
    if not rows:
        return [], []
    require(all(len(row) == len(rows[0]) for row in rows),
            "RREF matrix is not rectangular")
    require(all(value in (0, 1) for row in rows for value in row),
            "RREF matrix has a nonbinary entry")
    pivot_columns = []
    next_row = 0
    for column in range(len(rows[0])):
        source = next((r for r in range(next_row, len(rows))
                       if rows[r][column]), None)
        if source is None:
            continue
        rows[next_row], rows[source] = rows[source], rows[next_row]
        for r in range(len(rows)):
            if r != next_row and rows[r][column]:
                rows[r] = [a ^ b for a, b in zip(rows[r], rows[next_row])]
        pivot_columns.append(column)
        next_row += 1
        if next_row == len(rows):
            break
    return rows[:next_row], pivot_columns


def parity_check(generator):
    """Construct H: free entry 1 and pivot entries from corresponding G rows."""
    reduced, pivots = rref(generator)
    port_count = len(generator[0])
    free = [column for column in range(port_count) if column not in pivots]
    result = []
    for column in free:
        equation = [0] * port_count
        equation[column] = 1
        for row, pivot in zip(reduced, pivots):
            equation[pivot] = row[column]
        result.append(equation)
    return result, pivots, free


def dot(a, b):
    require(len(a) == len(b), "dot product dimension mismatch")
    return sum(x * y for x, y in zip(a, b)) % 2


def orthogonal(generator, check):
    return all(dot(row, equation) == 0
               for row in generator for equation in check)


def add_columns(a, b):
    require(len(a) == len(b), "syndrome dimension mismatch")
    return tuple(x ^ y for x, y in zip(a, b))


def verify(pair_count):
    """Return a deterministic finite receipt; raise on every failed obligation."""
    require(pair_count in EXPECTED, "only p=5 or p=6 is certified")
    expected_case = EXPECTED[pair_count]
    size = 4
    ports = enumerate_ports(pair_count, size)
    stars = [star for level in range(size)
             for star in enumerate_ports(pair_count, level)]
    generator = incidence(stars, ports)
    check, pivots, free = parity_check(generator)
    port_count = len(ports)
    require(port_count == (2 ** size) * comb(pair_count, size)
            == expected_case["ports"], "port count changed")
    require(len(stars) == sum((2 ** level) * comb(pair_count, level)
                              for level in range(size))
            == expected_case["stars"], "proper-star count changed")
    require(len(pivots) == expected_case["rank"], "generator rank changed")
    require(orthogonal(generator, check), "G H^T is nonzero")
    h_reduced, h_pivots = rref(check)
    require(len(h_reduced) == len(free) == port_count - len(pivots)
            == expected_case["check_rank"], "nullspace completeness failed")
    require(all(sum(row) % 2 == 0 for row in generator),
            "a proper star has odd weight")

    columns = [tuple(row[column] for row in check)
               for column in range(port_count)]
    zero = (0,) * len(check)
    require(all(column != zero for column in columns),
            "weight-one codeword detected")
    require(len(set(columns)) == port_count,
            "weight-two codeword detected")

    pair_syndromes = {}
    first_collision = None
    for left, right in combinations(range(port_count), 2):
        syndrome = add_columns(columns[left], columns[right])
        require(syndrome != zero, "zero pair syndrome detected")
        if syndrome in pair_syndromes and first_collision is None:
            first_collision = [list(pair_syndromes[syndrome]), [left, right]]
        pair_syndromes.setdefault(syndrome, (left, right))
    require(len(pair_syndromes) == expected_case["pair_syndromes"],
            "distinct pair-syndrome count changed")

    # Attaining witness: a single 3-star with its complete port support.
    witness_star = (0, 2, 4)
    witness = generator[stars.index(witness_star)]
    witness_support = [i for i, value in enumerate(witness) if value]
    require(all(dot(witness, equation) == 0 for equation in check),
            "attaining witness has nonzero syndrome")
    require(len(witness_support) == 2 * (pair_count - 3)
            == expected_case["minimum_weight"], "witness weight changed")
    if pair_count == 5:
        # Nonzero distinct H columns exclude weight 1/2; parity excludes 3.
        require(first_collision is not None, "expected weight-four collision absent")
        minimum_distance = 4
    else:
        # Unique pair sums exclude weight 4; row parity excludes odd weights.
        require(first_collision is None, "weight-four codeword detected")
        require(len(pair_syndromes) == comb(port_count, 2),
                "pair-syndrome enumeration is incomplete")
        minimum_distance = 6

    # Every target and overlap correction: C_j = sum_{l=j}^3 C(l,j) B_l,
    # where B_l is the sum of l-stars contained in the target.
    star_indices = {star: index for index, star in enumerate(stars)}
    overlap_rows_checked = 0
    for target in ports:
        b_rows = {}
        for level in range(1, size):
            rows = [generator[star_indices[subset]]
                    for subset in combinations(target, level)]
            b_rows[level] = [sum(row[s] for row in rows) % 2
                             for s in range(port_count)]
        for overlap in range(1, size):
            supplied = [sum(comb(level, overlap) * b_rows[level][s]
                            for level in range(overlap, size)) % 2
                        for s in range(port_count)]
            expected = [int(sum(c in source for c in target) == overlap)
                        for source in ports]
            require(supplied == expected, "overlap/star identity failed")
            require(all(dot(expected, equation) == 0 for equation in check),
                    "overlap correction lies outside proper-star span")
            overlap_rows_checked += 1
    require(overlap_rows_checked == 3 * port_count,
            "overlap-row enumeration is incomplete")

    # Retain the independently derived H while corrupting G.  Two flips in
    # the same row preserve even parity, so orthogonality must detect them.
    damaged_single = [row[:] for row in generator]
    damaged_single[0][0] ^= 1
    require(not orthogonal(damaged_single, check),
            "single-entry incidence corruption escaped detection")
    require(sum(damaged_single[0]) % 2 == 1, "single-flip parity control failed")
    damaged_pair = [row[:] for row in generator]
    damaged_pair[0][0] ^= 1
    damaged_pair[0][1] ^= 1
    require(sum(damaged_pair[0]) % 2 == 0, "pair-flip parity control failed")
    require(not orthogonal(damaged_pair, check),
            "even-parity incidence corruption escaped detection")

    return {
        "p": pair_count, "k": size, "ports": port_count,
        "proper_stars_including_empty": len(stars),
        "generator_rank": len(pivots), "check_rank": len(h_pivots),
        "all_generator_rows_even": True,
        "nonzero_distinct_syndrome_columns": port_count,
        "pair_count": comb(port_count, 2),
        "distinct_pair_syndromes": len(pair_syndromes),
        "first_pair_collision": first_collision,
        "minimum_nonzero_weight": minimum_distance,
        "three_star_witness": list(witness_star),
        "witness_port_indices": witness_support,
        "witness_ports": [list(ports[i]) for i in witness_support],
        "overlap_rows_checked": overlap_rows_checked,
        "incidence_single_flip_rejected": True,
        "incidence_parity_preserving_pair_flip_rejected": True,
        "nullspace_free_columns": free,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the full deterministic receipt")
    args = parser.parse_args()
    results = [verify(p) for p in (5, 6)]
    if args.json:
        print(json.dumps({"status": "PASS", "method": "list-RREF-nullspace",
                          "results": results}, indent=2))
    else:
        for result in results:
            print("PASS independent p={p} k={k}: rank={generator_rank}/{ports}, "
                  "check-rank={check_rank}, minimum-weight={minimum_nonzero_weight}, "
                  "overlap-rows={overlap_rows_checked}, incidence-controls=2/2".format(**result))


if __name__ == "__main__":
    main()
