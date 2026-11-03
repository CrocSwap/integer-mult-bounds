#!/usr/bin/env python3
"""Finite exact corroboration of the signed-permutation frame radius theorem.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is replayed.
"""

import argparse
import ast
from fractions import Fraction as F
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import sys

# -I removes the script directory; restore only this local package.
PACKAGE = Path(__file__).resolve().parent
SOURCE_FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                "VERIFY.json", "orbit_oracle.py", "rounding.py", "verify.py")
sys.path.insert(0, str(PACKAGE))
import orbit_oracle
import rounding


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    dimension = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(dimension))
                       for j in range(dimension)) for i in range(dimension))


def signed_permutations(dimension):
    require(1 <= dimension <= 3, "complete group fixture cap exceeded")
    return tuple(tuple(tuple(signs[i] if j == perm[i] else 0
                             for j in range(dimension)) for i in range(dimension))
                 for perm in permutations(range(dimension))
                 for signs in product((-1, 1), repeat=dimension))


def error(output, point):
    return max(abs(a - b) for a, b in zip(output, point))


def two_dimensional():
    counts = dict(frames=0, grid_points=0, equivariance_checks=0,
                  integer_candidates=0, attaining_orbits=0)
    digest = hashlib.sha256()
    for entries in product(range(-2, 3), repeat=4):
        a, b, c, d = entries
        if abs(a * d - b * c) != 1:
            continue
        frame = ((a, b), (c, d))
        inverse = rounding.matrix(frame)
        group = orbit_oracle.frames(frame)
        expected_group = {multiply(multiply(frame, s), inverse)
                          for s in signed_permutations(2)}
        require(set(group) == expected_group, "independent group mismatch")
        counts["frames"] += 1
        for m in range(2, 10):
            largest = 0
            for residues in product(range(m), repeat=2):
                point = rounding.apply(frame, tuple(F(v, m) for v in residues))
                output = rounding.round_point(frame, inverse, point)
                require(error(output, point) <= rounding.radius(frame, m),
                        "quantizer exceeds grid radius")
                for g in group:
                    transported = rounding.apply(g, point)
                    require(rounding.round_point(frame, inverse, transported) ==
                            rounding.apply(g, output), "equivariance failure")
                    counts["equivariance_checks"] += 1
                numerator = tuple(int(v * m) for v in point)
                best, candidates = orbit_oracle.optimize(group, numerator, m, output)
                require(best <= m * rounding.radius(frame, m), "orbit exceeds bound")
                largest = max(largest, best)
                counts["integer_candidates"] += candidates
                counts["grid_points"] += 1
                digest.update((repr((entries, m, residues, best)) + "\n").encode())
            require(largest == m * rounding.radius(frame, m), "grid optimum mismatch")
            point, _ = rounding.extremizer(frame, m)
            output = rounding.round_point(frame, inverse, point)
            best, candidates = orbit_oracle.optimize(
                group, tuple(int(v * m) for v in point), m, output)
            require(best == m * rounding.radius(frame, m), "extremizer not sharp")
            counts["integer_candidates"] += candidates
            counts["attaining_orbits"] += 1
    return dict(counts, orbit_optima_sha256=digest.hexdigest())


def check_generators(frame, inverse, data, output):
    dimension = len(frame)
    count = 0
    integer_coordinates = rounding.apply(inverse, output)
    for i in range(dimension):
        sign = tuple(-v if k == i else v for k, v in enumerate(data))
        signed_output = tuple(-v if k == i else v
                              for k, v in enumerate(integer_coordinates))
        require(rounding.round_point(frame, inverse, rounding.apply(frame, sign)) ==
                rounding.apply(frame, signed_output), "sign generator failure")
        count += 1
    for i in range(dimension - 1):
        permutation = list(range(dimension))
        permutation[i], permutation[i + 1] = permutation[i + 1], permutation[i]
        swapped = tuple(data[j] for j in permutation)
        swapped_output = tuple(integer_coordinates[j] for j in permutation)
        require(rounding.round_point(frame, inverse, rounding.apply(frame, swapped)) ==
                rounding.apply(frame, swapped_output), "swap generator failure")
        count += 1
    return count


def higher_dimensions():
    checks = dict(frames=0, points=0, generator_checks=0, fixed_point_checks=0)
    for dimension in range(1, 9):
        frame = tuple(tuple(int(i == j) + (i + 1 if j == i + 1 else 0)
                            for j in range(dimension)) for i in range(dimension))
        inverse = rounding.matrix(frame)
        checks["frames"] += 1
        for m in (2, 3, 7, 10, 101):
            point, signs = rounding.extremizer(frame, m)
            output = rounding.round_point(frame, inverse, point)
            require(error(output, point) == rounding.radius(frame, m),
                    "higher-dimensional sharpness failure")
            for i in range(dimension - 1):
                permutation = list(range(dimension))
                permutation[i], permutation[i + 1] = permutation[i + 1], permutation[i]
                s = tuple(tuple(signs[j] * signs[permutation[j]]
                                if k == permutation[j] else 0
                                for k in range(dimension)) for j in range(dimension))
                g = multiply(multiply(frame, s), inverse)
                require(rounding.apply(g, point) == point, "witness stabilizer failure")
                require(rounding.apply(g, output) == output, "output stabilizer failure")
                checks["fixed_point_checks"] += 1
            for j in range(17):
                data = tuple(F(((i + 3) * (j + 5)) % 37 - 18, m)
                             for i in range(dimension))
                x = rounding.apply(frame, data)
                z = rounding.round_point(frame, inverse, x)
                require(error(z, x) <= rounding.radius(frame, m), "data radius failure")
                checks["generator_checks"] += check_generators(frame, inverse, data, z)
                checks["points"] += 1
    return checks


def semantic_controls():
    frame = ((1, 2), (0, 1))
    inverse = rounding.matrix(frame)
    point = (F(3, 2), F(1, 2))
    output = rounding.round_point(frame, inverse, point)
    require(error(output, point) == F(3, 2), "sheared D8 fixture changed")
    require(error(output, point) > 1, "understated radius escaped")
    require(rounding.radius(frame, 3) == 1, "odd-grid correction missing")
    swap = multiply(multiply(frame, ((0, 1), (1, 0))), inverse)
    bad = rounding.apply(frame, (0, 1))
    require(rounding.apply(swap, point) == point and
            rounding.apply(swap, bad) != bad, "stabilizer omission escaped")
    reflection = ((1, -4), (0, -1))
    require(reflection in orbit_oracle.frames(frame), "reflection missing")
    witness = (F(0), F(1, 2))
    plain = tuple(rounding.nearest(v) for v in witness)
    require(tuple(rounding.nearest(v) for v in rounding.apply(reflection, witness)) !=
            rounding.apply(reflection, plain), "physical-coordinate rounding control failed")
    original = rounding.nearest
    try:
        rounding.nearest = lambda v: (2 * v.numerator + v.denominator) // (2 * v.denominator)
        negative = rounding.round_point(frame, inverse, tuple(-v for v in point))
        require(negative != tuple(-v for v in output), "nonodd tie mutation escaped")
    finally:
        rounding.nearest = original
    require(rounding.round_point(frame, inverse, (2**256, -(2**256))) ==
            (2**256, -(2**256)), "integer fixing failure")
    return {"semantic_controls": 5, "sheared_dihedral_radius": "3/2",
            "odd_grid_m3_radius": "1", "large_integer_bits": 257}


def invalid_controls():
    frame = ((1, 2), (0, 1))
    inverse = rounding.matrix(frame)
    bad_frames = ((), ((1, 2),), ((1, 2), (2, 4)),
                  ((2, 0), (0, 1)), ((True, 0), (0, 1)), ((2**17,),))
    rejected = 0
    for candidate in bad_frames:
        try:
            rounding.matrix(candidate)
        except ValueError:
            rejected += 1
    for candidate in ((), (0.5, 0), (True, 0), (2**4097, 0)):
        try:
            rounding.round_point(frame, inverse, candidate)
        except ValueError:
            rejected += 1
    for m in (0, -1, True, F(3, 2), 2**17):
        try:
            rounding.radius(frame, m)
        except ValueError:
            rejected += 1
    require(rejected == 15, "input rejection coverage failure")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="exclusively create an external receipt")
    args = parser.parse_args()
    sources = {}
    for name in SOURCE_FILES:
        payload = (PACKAGE / name).read_bytes()
        sources[name] = hashlib.sha256(payload).hexdigest()
        if name.endswith(".py"):
            ast.parse(payload, filename=name)
    receipt = {"status": "PASS_SIGNED_PERMUTATION_FRAME_RADIUS",
               "claim_type": "scoped written proof with exact finite corroboration",
               "two_dimensional": two_dimensional(),
               "higher_dimensions": higher_dimensions(),
               "controls": semantic_controls(),
               "invalid_input_rejections": invalid_controls(),
               "source_sha256": sources}
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            require(stream.write(encoded) == len(encoded), "short receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
