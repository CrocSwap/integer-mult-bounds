#!/usr/bin/env python3
"""Exact finite corroboration of the new rank-three obstruction.

Standard library only. No predecessor executable or receipt is consumed.
"""

import argparse
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def span(basis):
    require(len(basis) <= 8, "bounded binary basis")
    values = [0]
    for vector in basis:
        values += [old ^ vector for old in values]
    return frozenset(values)


def basis_of(vectors):
    require(len(vectors) <= 256, "bounded binary vector set")
    basis = []
    occupied = {0}
    for vector in sorted(vectors):
        if vector not in occupied:
            require(len(basis) < 8, "binary dimension limit")
            basis.append(vector)
            occupied = set(span(basis))
    return tuple(basis)


def rank(vectors):
    return len(basis_of(vectors))


def pairing(left, right):
    return parity((left & 15) & (right >> 4)) ^ parity((right & 15) & (left >> 4))


def word_image(value, axes):
    require(len(axes) <= 4 and all(0 < a < 256 for a in axes), "word bound")
    for axis in axes:
        if pairing(value, axis):
            value ^= axis
    return value


def combine(coordinates, axes):
    value = 0
    for index, axis in enumerate(axes):
        if coordinates & (1 << index):
            value ^= axis
    return value


def bilinear(left, right, rows):
    image = sum(parity(row & right) << i for i, row in enumerate(rows))
    return parity(image & left)


def quadratic_table(code):
    diagonal = code & 15
    edges = tuple((i, j) for i in range(4) for j in range(i + 1, 4))
    table = []
    for value in range(16):
        result = parity(value & diagonal)
        for bit, (i, j) in enumerate(edges):
            result ^= ((code >> (bit + 4)) & 1) & (value >> i) & (value >> j) & 1
        table.append(result)
    return tuple(table)


def quadratic_census():
    totals = {"quadratic_forms": 1024, "hyperplanes_per_form": 15,
              "totally_singular_pairs": 0, "nonzero_polar_pairs": 0}
    for code in range(1024):
        q = quadratic_table(code)
        polar = tuple(sum((q[(1 << i) ^ (1 << j)] ^ q[1 << i] ^ q[1 << j]) << j
                          for j in range(4)) for i in range(4))
        for mask in range(1, 16):
            plane = tuple(x for x in range(16) if not parity(x & mask))
            if any(q[x] for x in plane):
                continue
            totals["totally_singular_pairs"] += 1
            if rank(polar):
                totals["nonzero_polar_pairs"] += 1
                radical = tuple(x for x in range(16)
                                 if all(not parity(row & x) for row in polar))
                anisotropic = tuple(x for x in range(16) if q[x])
                require(rank(polar) == 2, "nonzero polar rank")
                require(set(radical) <= set(plane), "radical lies in hyperplane")
                require(all(not q[x] for x in radical), "quadratic radical vanishes")
                require(len(anisotropic) == 4 and rank(anisotropic) == 3,
                        "anisotropic vectors cannot span four dimensions")
    require(totals["nonzero_polar_pairs"] > 0, "nonvacuous quadratic control")
    return totals


def topology(code):
    axes = [1 << i for i in range(4)]
    rows = [1 << i for i in range(4)]
    bit = 0
    for i in range(4):
        for j in range(i + 1, 4):
            if code & (1 << bit):
                axes[j] ^= 1 << (i + 4)
                rows[i] ^= 1 << j
            bit += 1
    require(rank(axes) == 4, "independent chronological axes")
    return tuple(axes), tuple(rows)


def literal_wall(axes, rows):
    images = tuple(word_image(v, axes) for v in range(256))
    for value in range(256):
        displacement = images[value] ^ value
        coordinates = displacement & 15
        require(combine(coordinates, axes) == displacement, "literal displacement")
        for i, axis in enumerate(axes):
            require(bilinear(coordinates, 1 << i, rows) == pairing(value, axis),
                    "triangular Wall form matches literal chronological word")
        require(word_image(images[value], tuple(reversed(axes))) == value,
                "literal inverse")
    for i in range(8):
        for j in range(i + 1, 8):
            require(pairing(images[1 << i], images[1 << j]) == pairing(1 << i, 1 << j),
                    "whole symplectic endpoint")
    return images


def contract_classification(axes, rows, images, plane):
    vectors = tuple(combine(x, axes) for x in plane)
    radical = tuple(x for x in plane
                     if all(not bilinear(x, y, rows) for y in plane))
    require(len(radical) == 2, "rank-two restriction has one-dimensional radical")
    z = combine(next(x for x in radical if x), axes)
    kernel = tuple(v for v in range(256) if images[v] == v)
    kernel_plus_d = {k ^ d for k in kernel for d in vectors}
    lifts = tuple(v for v in range(256) if images[v] ^ v == z)
    require(len(lifts) > 0, "nonzero radical has a source lift")
    closed = all(v in kernel_plus_d for v in lifts)
    return closed, len(lifts)


def word_census():
    totals = {"gram_topologies": 64, "literal_input_vectors": 0,
              "wall_basis_equalities": 0, "hyperplane_restrictions": 0,
              "alternating_rank_two_contracts": 0, "escaping_radical_lifts": 0,
              "nonalternating_closed_controls": 0, "omitted_turn_controls": 0}
    control = None
    for code in range(64):
        axes, rows = topology(code)
        images = literal_wall(axes, rows)
        totals["literal_input_vectors"] += 256
        totals["wall_basis_equalities"] += 256 * 4
        for omitted in range(4):
            damaged = axes[:omitted] + axes[omitted + 1:]
            require(any(word_image(v, damaged) != images[v] for v in range(256)),
                    "omitting a turn must damage the whole endpoint")
            totals["omitted_turn_controls"] += 1
        for mask in range(1, 16):
            totals["hyperplane_restrictions"] += 1
            plane = tuple(x for x in range(16) if not parity(mask & x))
            basis = basis_of(plane)
            restricted = tuple(sum(bilinear(x, y, rows) << j for j, y in enumerate(basis))
                               for x in basis)
            if rank(restricted) != 2:
                continue
            closed, lift_count = contract_classification(axes, rows, images, plane)
            alternating = all(not bilinear(x, x, rows) for x in plane)
            if alternating:
                totals["alternating_rank_two_contracts"] += 1
                require(code == 0 and not closed, "four turns force commuting axes and escape")
                totals["escaping_radical_lifts"] += lift_count
            elif closed:
                totals["nonalternating_closed_controls"] += 1
                if control is None:
                    control = {"gram_code": code, "hyperplane_mask": mask,
                               "axes": list(axes), "restricted_rows": list(restricted)}
    require(totals["alternating_rank_two_contracts"] == 1, "nonvacuous sharp four-turn case")
    require(totals["nonalternating_closed_controls"] > 0, "alternation is necessary")
    return {"counts": totals, "nonalternating_control": control}


def failure_controls():
    axes, rows = topology(0)
    wrong_rows = (rows[0] ^ 1,) + rows[1:]
    rejected = 0
    try:
        literal_wall(axes, wrong_rows)
    except ValueError as error:
        require(str(error) == "triangular Wall form matches literal chronological word",
                "diagonal mutation rejects for the intended reason")
        rejected += 1
    try:
        word_image(0, (0,))
    except ValueError as error:
        require(str(error) == "word bound", "zero axis rejects at the boundary")
        rejected += 1
    require(rejected == 2, "both failure controls reject")
    return rejected


def receipt():
    package = Path(__file__).resolve().parent
    source_names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                    "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in source_names}
    return {"schema_version": 1,
            "claim_type": "scoped written proof with exact finite corroboration",
            "source_sha256": hashes, "quadratic_census": quadratic_census(),
            "word_census": word_census(), "failure_controls": failure_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = receipt()
    path = Path(__file__).resolve().with_name("RESULT.json")
    if args.write_report:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(path.read_text()) == report, "receipt differs from exact replay")
    print(json.dumps(report, sort_keys=True))
    print("PASS_RANK_THREE_CLOSED_COMPLETION")


if __name__ == "__main__":
    main()
