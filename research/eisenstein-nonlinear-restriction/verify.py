"""Finite corroboration of the nonlinear coordinate-restriction lemma.

New work produced by Nick Petalas. Apache-2.0. Predecessor theorems are
cited premises, never imported or replayed by this checker.
"""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from random import Random

from restrictions import (evaluate, from_truth_table, is_affine,
                          minimum_affine_face, minimum_zero_cut, require,
                          restrict, validate)


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def source_hashes():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            digest = sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "changed input: " + row["path"])
            hashes[row["path"]] = digest
    for name in ("verify.py", "restrictions.py", "PROOF.md", "SOURCES.json"):
        hashes[name] = sha256((PACKAGE / name).read_bytes()).hexdigest()
    return hashes


def truth_affine(n, outputs, fixed, ones):
    """Independent oracle from values at a base point and its neighbors."""
    free = tuple(i for i in range(n) if not fixed & (1 << i))
    for terms in outputs:
        constant = evaluate(terms, ones)
        slopes = tuple(evaluate(terms, ones | 1 << i) ^ constant for i in free)
        for word in range(1 << len(free)):
            point = ones | sum(((word >> j) & 1) << i
                               for j, i in enumerate(free))
            expected = constant ^ (sum(slopes[j] * ((word >> j) & 1)
                                       for j in range(len(free))) & 1)
            if evaluate(terms, point) != expected:
                return False
    return True


def face_census(n, outputs):
    validate(n, outputs)
    require(n <= 5, "census bound")
    best, zero_best, faces, points = n + 1, n + 1, 0, 0
    for fixed in range(1 << n):
        for ones in range(1 << n):
            if ones & ~fixed:
                continue
            restricted = tuple(restrict(terms, fixed, ones) for terms in outputs)
            affine = truth_affine(n, outputs, fixed, ones)
            require(affine == is_affine(restricted), "affine oracle disagreement")
            for point in range(1 << n):
                if point & fixed == ones:
                    for original, reduced in zip(outputs, restricted):
                        require(evaluate(original, point) == evaluate(reduced, point),
                                "substitution disagreement")
                        points += 1
            if affine:
                best = min(best, fixed.bit_count())
                if ones == 0:
                    zero_best = min(zero_best, fixed.bit_count())
            faces += 1
    fixed, ones = minimum_affine_face(n, outputs)
    cut = minimum_zero_cut(n, outputs)
    require(fixed.bit_count() == best, "minimum face disagreement")
    require(cut.bit_count() == zero_best, "transversal disagreement")
    require(best <= zero_best, "zero face is an allowed face")
    return faces, points


def polynomial_census():
    maps, faces, points = 0, 0, 0
    for n in range(4):
        for word in range(1 << (1 << n)):
            table = tuple((word >> x) & 1 for x in range(1 << n))
            terms = from_truth_table(table)
            require(tuple(evaluate(terms, x) for x in range(1 << n)) == table,
                    "Mobius inversion")
            f, p = face_census(n, (terms,))
            maps, faces, points = maps + 1, faces + f, points + p
    rng = Random(2017814)
    for n, count, width in ((4, 64, 3), (5, 24, 4)):
        for _ in range(count):
            outputs = tuple(tuple(t for t in range(1 << n) if rng.randrange(2))
                            for _ in range(width))
            f, p = face_census(n, outputs)
            maps, faces, points = maps + 1, faces + f, points + p
    triangle = ((3, 5, 6, 7),)
    cut = minimum_zero_cut(3, triangle)
    fixed, ones = minimum_affine_face(3, triangle)
    require(cut.bit_count() == 2 and fixed.bit_count() == 1,
            "nonzero-face strict improvement")
    return {"maps": maps, "faces": faces, "point_output_checks": points,
            "strict_example": {"zero_cut": cut, "fixed": fixed, "ones": ones,
                               "restricted": restrict(triangle[0], fixed, ones)}}


def rational_rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        divisor = rows[pivot][col]
        rows[pivot] = [x / divisor for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            multiplier = rows[i][col]
            rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def fixture_geometry():
    data = json.loads((ROOT / "research/eisenstein-message-copy-bound/certificate.json")
                      .read_text())["geometry"]
    reps, rotation = data["representatives"], data["rotation4"]
    images = [tuple(sum(Fraction(rotation[i][j], 4) * r[j] for j in range(8))
                    for i in range(8)) for r in reps]
    frame = next(f for f in combinations(range(40), 4)
                 if all(dot(reps[i], reps[j]) == dot(reps[i], images[j]) == 0
                        for i, j in combinations(f, 2)))
    prices = []
    for reader in range(40):
        sources = frame if reader == frame[-1] else (reader,)
        vectors = [v for a in sources for v in (reps[a], images[a])]
        matrix = [[dot(v, w) for w in vectors]
                  for v in (reps[reader], images[reader])]
        rank = rational_rank(matrix)
        require(rank == 2, "new fixture singleton pairing price")
        prices.append(rank // 2)
    return frame, prices


def observation_check(outputs, side):
    """A receiver sees its own message and declared side-information bits."""
    seen = [dict() for _ in range(4)]
    count = 0
    for point in range(16):
        for t in range(4):
            key = (evaluate(outputs[t], point), point & side[t])
            demanded = (point >> t) & 1
            require(key not in seen[t] or seen[t][key] == demanded,
                    "receiver observation conflict")
            seen[t][key] = demanded
            count += 1
    return count


def nonlinear_fixture():
    frame, prices = fixture_geometry()
    outputs = ((1,), (2,), (4,), (7, 8))
    observations = observation_check(outputs, (0, 0, 0, 7))
    cut = minimum_zero_cut(4, outputs)
    fixed, ones = minimum_affine_face(4, outputs)
    require(cut.bit_count() == fixed.bit_count() == 1, "cubic restriction")
    # Product embedding; no 2^40-input enumeration is claimed.
    full = tuple((1 << i,) if i != frame[-1]
                 else tuple(sorted((1 << i, sum(1 << j for j in frame[:3]))))
                 for i in range(40))
    validate(40, full)
    require(not is_affine(full), "full code is genuinely nonlinear")
    restricted = tuple(restrict(t, 1 << frame[0], 0) for t in full)
    require(is_affine(restricted), "one fixed bit linearizes the full code")
    direct_checks = sum(evaluate((1,), bit) == bit
                        for _ in range(36) for bit in range(2))
    require(direct_checks == 72, "padded direct messages")
    return {"frame": frame, "pairing_prices": prices, "charge": sum(prices),
            "frame_inputs": 16, "receiver_observations": observations,
            "direct_bit_checks": direct_checks, "total_demand": len(full),
            "minimum_fixing": fixed.bit_count(),
            "new_lower_bound": len(full) - fixed.bit_count()}


def controls():
    rejected = []
    cases = (("negative variables", lambda: validate(-1, ((1,),))),
             ("boolean monomial", lambda: validate(1, ((True,),))),
             ("duplicate monomial", lambda: validate(1, ((1, 1),))),
             ("out-of-range monomial", lambda: validate(2, ((4,),))),
             ("invalid face", lambda: restrict((3,), 1, 2)),
             ("unbounded cut search", lambda: minimum_zero_cut(13, ((1,),))),
             ("unbounded face search", lambda: minimum_affine_face(9, ((1,),))),
             ("nonbinary truth table", lambda: from_truth_table((0, 2))),
             ("missing side information",
              lambda: observation_check(((1,), (2,), (4,), (7, 8)), (0, 0, 0, 6))))
    for name, action in cases:
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)
    require(not is_affine((restrict((3,), 0, 0),)), "empty cut leaves a product")
    require(restrict((3, 5, 6, 7), 4, 4) == (1, 2), "XOR cancellation control")
    require(evaluate((7, 8), 7) != evaluate((8,), 7), "omitted cubic detected")
    return {"rejections": rejected, "semantic_controls": 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new generated receipt")
    args = parser.parse_args()
    hashes = source_hashes()
    result = {"schema": "eisenstein-nonlinear-restriction/v1", "sources": hashes,
              "polynomial_census": polynomial_census(),
              "nonlinear_fixture": nonlinear_fixture(), "controls": controls()}
    if args.output:
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("PASS_EISENSTEIN_NONLINEAR_RESTRICTION " + canonical({
        "maps": result["polynomial_census"]["maps"],
        "faces": result["polynomial_census"]["faces"],
        "new_fixture_lower_bound": result["nonlinear_fixture"]["new_lower_bound"],
        "rejections": len(result["controls"]["rejections"]),
        "semantic_controls": result["controls"]["semantic_controls"]}))


if __name__ == "__main__":
    main()
