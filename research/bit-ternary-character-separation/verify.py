#!/usr/bin/env python3
# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Replay one exact separation of ternary cuts from rational and binary cuts."""

import argparse
from collections import Counter
from fractions import Fraction
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MAX_BYTES = 65536
F4 = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    with path.open("rb") as source:
        data = source.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "JSON byte capacity")
    return json.loads(data, object_pairs_hook=unique_object)


def matrix(value, rows, columns):
    require(type(value) is list and len(value) == rows, "matrix row count")
    require(all(type(row) is list and len(row) == columns for row in value),
            "matrix column count")
    require(all(type(x) is int and abs(x).bit_length() <= 64
                for row in value for x in row), "integer entry capacity")
    return tuple(tuple(row) for row in value)


def parse(example, lattice):
    require(type(example) is dict and set(example) == {
        "address_dimension", "paid_frames", "target_frames"}, "example keys")
    require(type(example["address_dimension"]) is int
            and example["address_dimension"] == 3, "fixed address dimension")
    paid, targets = example["paid_frames"], example["target_frames"]
    require(type(paid) is list and len(paid) == 8, "fixed paid count")
    require(type(targets) is list and len(targets) == 3, "fixed target count")
    frames = [matrix(frame, 3, 3) for frame in paid + targets]
    flat = [tuple(x for row in frame for x in row) for frame in frames]
    require(type(lattice) is dict and set(lattice) == {
        "basis", "basis_from_paid", "paid_coordinates", "target_coordinates",
        "three_e11_from_other_paid"},
        "lattice keys")
    basis = matrix(lattice["basis"], 6, 9)
    combinations = matrix(lattice["basis_from_paid"], 6, 8)
    pc = matrix(lattice["paid_coordinates"], 8, 6)
    tc = matrix(lattice["target_coordinates"], 3, 6)
    three_e11 = matrix(lattice["three_e11_from_other_paid"], 1, 7)[0]
    return frames, flat[:8], flat[8:], basis, combinations, pc, tc, three_e11


def rational_rank(rows):
    work = [list(map(Fraction, row)) for row in rows]
    rank = 0
    for column in range(len(work[0])):
        found = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[rank], work[found] = work[found], work[rank]
        pivot = work[rank][column]
        work[rank] = [x / pivot for x in work[rank]]
        for i in range(rank + 1, len(work)):
            coefficient = work[i][column]
            work[i] = [x - coefficient * y
                       for x, y in zip(work[i], work[rank], strict=True)]
        rank += 1
    return rank


def combination(coefficients, rows):
    return tuple(sum(c * row[i] for c, row in zip(coefficients, rows, strict=True))
                 for i in range(len(rows[0])))


def determinant3(frame):
    a, b, c = frame
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def character_summary(paid, targets, modulus):
    require(modulus in (2, 3, 4), "character modulus")
    histogram = Counter()
    best = None
    for values in itertools.product(range(modulus), repeat=6):
        p = [sum(a * b for a, b in zip(values, row, strict=True)) % modulus
             for row in paid]
        t = [sum(a * b for a, b in zip(values, row, strict=True)) % modulus
             for row in targets]
        margin = sum(x != 0 for x in p) - sum(x != 0 for x in t)
        histogram[margin] += 1
        if best is None or margin < best[0]:
            best = (margin, values, p, t)
    require(best is not None and sum(histogram.values()) == modulus**6,
            "complete character coverage")
    return {"characters_checked": modulus**6, "minimum_margin": best[0],
            "margin_histogram": {str(k): histogram[k] for k in sorted(histogram)},
            "witness": {"basis_values": best[1], "paid_residues": best[2],
                        "target_residues": best[3]}}


def binary_rank(rows):
    pivots = {}
    for row in rows:
        for bit in range(7, -1, -1):
            if not row & (1 << bit):
                continue
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def restriction_of_scalars(frame):
    """F4-linear multiplication becomes an 8-by-8 binary map on four roles."""
    rows = []
    for row in frame:
        for bit in range(2):
            rows.append(sum(((F4[x][1 << b] >> bit) & 1) << (2 * j + b)
                            for j, x in enumerate(row) for b in range(2)))
    return rows


def f4_product(left, right):
    result = [[0] * 4 for _ in range(4)]
    for i, j, k in itertools.product(range(4), repeat=3):
        result[i][j] ^= F4[left[i][k]][right[k][j]]
    return result


def field_controls():
    identity = [[int(i == j) for j in range(4)] for i in range(4)]
    target_difference = [[(3, 3, 2, 0)[i] if i == j else 0
                          for j in range(4)] for i in range(4)]
    require(binary_rank(restriction_of_scalars(target_difference)) == 6,
            "three nonidentity F4 target roles")
    projectors = 0
    for x, y in itertools.product(range(1, 16), repeat=2):
        if (x & y).bit_count() % 2 != 1:
            continue
        increment = [[3 * (((x >> i) & 1) & ((y >> j) & 1))
                      for j in range(4)] for i in range(4)]
        require(binary_rank(restriction_of_scalars(increment)) == 2,
                "single surviving rank-one F4 increment")
        projectors += 1
    require(projectors == 120, "four-role idempotent coverage")
    # Three E_ii calls on each data role give I3; the fourth role stays dirty.
    for order in (tuple(range(9)), tuple(reversed(range(9)))):
        product = identity
        sums = [[0] * 9 for _ in range(4)]
        for index in order:
            role, coordinate = divmod(index, 3)
            factor = [row.copy() for row in identity]
            factor[role][role] = 2 if coordinate == 0 else 1
            product = f4_product(product, factor)
            sums[role][4 * coordinate] += 1
        require(sums == [[1, 0, 0, 0, 1, 0, 0, 0, 1]] * 3 + [[0] * 9],
                "nine-call exact formal diagonal endpoint")
        require(product == [[2 if i == j and i < 3 else identity[i][j]
                             for j in range(4)] for i in range(4)],
                "nine-call F4 positive endpoint")
    return {"four_role_projectors": projectors, "single_increment_binary_rank": 2,
            "target_difference_binary_rank": 6, "positive_word_orders": 2}


def family_controls(paid, targets, three_e11, pc):
    require(paid[0] == (4, 0, 0, 0, 0, 0, 0, 0, 0), "fixed family member")
    require(combination(three_e11, paid[1:]) == (3, 0, 0, 0, 0, 0, 0, 0, 0),
            "three E11 belongs to other-paid lattice")
    require(all(row[0] % 3 == 0 for row in paid[1:]), "other paid ternary residues")
    recipes = ((1, 1, 1, 0, 0, 0, 0, 0), (1, 0, 0, 1, 1, 0, 0, 0),
               (-1, 0, 0, 0, 0, 1, 1, 1))
    require(tuple(combination(c, paid) for c in recipes) == tuple(targets),
            "disjoint other-paid target recipes")
    require(all(x % 4 == 0 for x in pc[0]), "integral E11 coordinates")
    unit_coordinates = tuple(x // 4 for x in pc[0])
    roles = (0, 0, 0, 1, 1, 2, 2, 2)
    for s in range(1, 17):
        amount = 4**s
        require(amount - ((amount - 1) // 3) * 3 == 1,
                "family E11 lattice identity")
        modified = ((amount, 0, 0, 0, 0, 0, 0, 0, 0),) + tuple(paid[1:])
        new_targets = [combination(c, modified) for c in recipes]
        determinants = [determinant3([r[:3], r[3:6], r[6:]]) for r in new_targets]
        require(determinants == [1296 * amount, 144 * amount, 67500 - 10494 * amount]
                and all(determinants), "family target determinant formulas")
        coordinates = (tuple(amount * x for x in unit_coordinates),) + pc[1:]
        target_coordinates = [combination(c, coordinates) for c in recipes]
        for role in range(3):
            actual = combination(tuple(int(r == role) for r in roles), coordinates)
            require(all((a - b) % amount == 0
                        for a, b in zip(actual, target_coordinates[role], strict=True)),
                    "full projected diagonal word in H/(4^s H)")
    return {"exponents_checked": list(range(1, 17)),
            "target_determinant_slopes": [1296, 144, -10494],
            "target_determinant_constants": [0, 0, 67500],
            "projected_word_roles": roles, "quotient_group": "H/(4^s H)"}


def verify(example, lattice):
    (frames, paid, targets, basis, combinations,
     pc, tc, three_e11) = parse(example, lattice)
    require(all(rational_rank(frame) == 1 for frame in frames[:8]),
            "paid rational rank one")
    determinants = [determinant3(frame) for frame in frames[8:]]
    require(all(determinants), "invertible target frames")
    require(rational_rank(basis) == 6, "independent lattice basis")
    require(all(combination(c, paid) == row
                for c, row in zip(combinations, basis, strict=True)),
            "basis must belong to generated lattice")
    require(all(combination(c, basis) == row
                for c, row in zip(pc + tc, paid + targets, strict=True)),
            "integral coordinate reconstruction")
    require(all(sum(row[i] for row in paid) == sum(row[i] for row in targets)
                for i in range(9)), "determinant exponent equality")
    subsets = list(itertools.combinations(paid, 6))
    require(len(subsets) == 28 and all(rational_rank(rows) == 6 for rows in subsets),
            "all rational cuts pass via six-frame independence")
    parity = character_summary(pc, tc, 2)
    require(parity["minimum_margin"] == 0, "all generated-lattice parity cuts pass")
    order_four = character_summary(pc, tc, 4)
    require(order_four["minimum_margin"] == 0, "all order-four counting cuts pass")
    ternary = character_summary(pc, tc, 3)
    witness = ternary["witness"]
    require(ternary["minimum_margin"] == -2, "ternary separation")
    require(witness["paid_residues"] == [1, 0, 0, 0, 0, 0, 0, 0]
            and witness["target_residues"] == [1, 1, 2], "literal ternary witness")
    labels = zip(pc + tc, paid + targets, strict=True)
    require(all(sum(a * b for a, b in zip(witness["basis_values"], row, strict=True))
                % 3 == frame[0] % 3 for row, frame in labels),
            "witness is ambient X11 modulo three")
    return {"status": "REJECT_TERNARY_CHARACTER_ALL_ORDERS_AND_DIRTY_ROLE_COUNTS",
            "target_determinants": determinants, "independent_six_frame_subsets": 28,
            "lattice_rank": 6, "determinant_matches": True,
            "binary": parity, "order_four": order_four, "ternary": ternary,
            "family": family_controls(paid, targets, three_e11, pc),
            "field_controls": field_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="regenerate only RESULT.json")
    args = parser.parse_args()
    result = verify(read_json(HERE / "EXAMPLE.json"), read_json(HERE / "LATTICE.json"))
    payload = json.dumps(result, indent=2) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(payload, encoding="utf-8")
    else:
        require((HERE / "RESULT.json").read_text(encoding="utf-8") == payload,
                "receipt differs")
    print("PASS_TERNARY_CHARACTER_SEPARATION rational_subsets=28 binary=64 order4=4096 "
          "ternary=729 cut=1<3 projectors=120 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RecursionError) as error:
        print("FAIL_TERNARY_CHARACTER_SEPARATION: " + str(error), file=sys.stderr)
        sys.exit(2)
