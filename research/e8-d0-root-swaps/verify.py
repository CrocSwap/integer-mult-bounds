#!/usr/bin/env python3
"""Exact coordinate replay of the E8 d=0 root-swap proof inputs.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
See PROOF.md and SOURCES.json for predecessor credit and exact scope.

This implementation enumerates Euclidean coordinate patterns. The separate
geometry_audit.py uses Cartan coordinates, reflections and Weyl orbits instead.
Neither imports predecessor code or reads a predecessor PASS receipt.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)
EXPECTED_PROFILES = {
    "norm4": [[70, 14, 8, 128], [73, 13, 8, 896], [76, 12, 7, 56]],
    "norm6": [[77, 25, None, 2688], [79, 24, None, 448], [80, 24, None, 224]],
    "norm8": [[84, 28, None, 1024]],
    "a2_plane": [[78, 26, None, 896], [80, 24, None, 224]],
    "a1_squared_plane": [[82, 26, None, 448], [84, 24, None, 2688]],
}


class VerificationError(ValueError):
    """A mathematical or receipt condition failed."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def canonical(vector):
    return vector if next(x for x in vector if x) > 0 else tuple(-x for x in vector)


def binary_rank(values):
    pivots = {}
    for value in values:
        while value:
            position = value.bit_length() - 1
            if position in pivots:
                value ^= pivots[position]
            else:
                pivots[position] = value
                break
    return len(pivots)


def rational_rank(rows):
    matrix = [[Fraction(x) for x in row] for row in rows]
    if not matrix:
        return 0
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            scale = matrix[i][column]
            if scale:
                matrix[i] = [x - scale * y for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def inverse(matrix):
    size = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        require(pivot is not None, "singular E8 coordinate basis")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(size):
            if i != column and rows[i][column]:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[column])]
    return [row[size:] for row in rows]


def integer_lines(twos, ones):
    """Doubled integral E8 vectors with twos entries +/-4 and ones +/-2."""
    result = set()
    for larger in combinations(range(8), twos):
        remaining = [i for i in range(8) if i not in larger]
        for smaller in combinations(remaining, ones):
            positions = larger + smaller
            for signs in product((-1, 1), repeat=len(positions)):
                vector = [0] * 8
                for i, sign in zip(positions, signs):
                    vector[i] = sign * (4 if i in larger else 2)
                if sum(vector) % 4 == 0:
                    result.add(canonical(tuple(vector)))
    return result


def half_lines(larger_count=0, larger=3):
    result = set()
    for positions in combinations(range(8), larger_count):
        for signs in product((-1, 1), repeat=8):
            vector = tuple(sign * (larger if i in positions else 1)
                           for i, sign in enumerate(signs))
            if sum(vector) % 4 == 0:
                result.add(canonical(vector))
    return result


def frame_roots():
    result = []
    for sign in (1, -1):
        for pair in range(4):
            vector = [0] * 8
            vector[2 * pair], vector[2 * pair + 1] = 2, 2 * sign
            result.append(tuple(vector))
    return result


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def support_mask(normal, roots):
    return sum(1 << i for i, root in enumerate(roots) if dot(normal, root))


def partitions(total, minimum=1):
    if total == 0:
        yield ()
    for part in range(minimum, total + 1):
        for rest in partitions(total - part, part):
            yield (part,) + rest


def partition_checks(caps):
    profiles = [p for total in range(1, 8) for p in partitions(total)]
    require(len(profiles) == 44, "incomplete low-cost partition enumeration")
    require(max(sum(caps[x] for x in p) for p in profiles if sum(p) <= 6) == 20,
            "restricted union-support bound is not 20")
    require(max(sum(caps[x] for x in p) for p in profiles if len(p) >= 2) == 21,
            "full union-support bound is not 21")
    require({p for p in profiles if sum(x >= 3 for x in p) >= 2}
            == {(3, 3), (3, 4), (1, 3, 3)}, "missing exceptional basis profile")


def run_geometry():
    root_set = integer_lines(0, 2) | half_lines()
    frame = frame_roots()
    require(len(root_set) == 120 and set(frame) <= root_set, "E8 root/frame inventory")
    roots = sorted(root_set - set(frame)) + frame
    require(all(dot(x, x) == 8 for x in roots), "root norm is not two")
    require(all(dot(a, b) == 0 for a, b in combinations(frame, 2)), "frame is not orthogonal")
    basis_inverse = inverse(list(zip(*SIMPLE)))
    coordinates = [tuple(dot(row, root) for row in basis_inverse) for root in roots]
    require(all(x.denominator == 1 for row in coordinates for x in row),
            "a root is outside the integral E8 lattice basis")
    labels = [1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
              for row in coordinates]
    require(len(set(labels)) == 120 and binary_rank(labels) == 9, "root-class labels")
    require(binary_rank(labels[-8:]) == 4, "frame label rank is not four")
    gram = [[Fraction(dot(a, b), 4) for b in SIMPLE] for a in SIMPLE]
    require(all(x.denominator == 1 for row in gram for x in row), "nonintegral lattice Gram form")
    quadratic = []
    for value in range(256):
        vector = [(value >> i) & 1 for i in range(8)]
        norm = sum(vector[i] * gram[i][j] * vector[j] for i in range(8) for j in range(8))
        require(norm.denominator == 1 and norm % 2 == 0, "lattice is not even")
        quadratic.append(int(norm // 2) % 2)
    require({label >> 1 for label in labels} == {i for i, q in enumerate(quadratic) if q},
            "root classes are not exactly the nonsingular points")
    require(sum(1 - 2 * q for q in quadratic) == 16, "quadratic Gauss sum is not 16")
    require(binary_rank(sum((int(gram[i][j]) % 2) << j for j in range(8))
                        for i in range(8)) == 8, "quadratic polar form is degenerate")
    outside = [sum(1 << i for i, label in enumerate(labels) if (normal & label).bit_count() % 2)
               for normal in range(1, 512)]
    for cut in outside:
        require(rational_rank(roots[i] for i in indices(cut)) == 8,
                "a full codeword can have weight at most eight")
    off_masks = [support_mask(root, roots) for root in roots]
    remainder_profile = Counter({0: 1, 24: 126, 28: 256, 32: 126, 56: 2})
    for i, off in enumerate(off_masks):
        remainder = off ^ (1 << i)
        require(remainder.bit_count() == 56, "root remainder does not have 56 lines")
        require(binary_rank(labels[j] for j in indices(remainder)) == 8,
                "root remainder label rank is not eight")
        require(Counter((remainder & cut).bit_count() for cut in outside) == remainder_profile,
                "root-remainder deletion profile differs")

    large = {}
    for subset in range(256):
        selected = [i for i, row in enumerate(coordinates)
                    if all(not x or subset >> j & 1 for j, x in enumerate(row))]
        rank = subset.bit_count()
        require(rational_rank(roots[i] for i in selected) == rank, "parabolic root rank")
        if rank <= 5:
            require(len(selected) <= 20, "small parabolic has too many roots")
        if rank <= 7 and len(selected) >= 28:
            key = (rank, len(selected))
            require(key not in large, "repeated large parabolic seed")
            large[key] = subset
    require(set(large) == {(6, 30), (6, 36), (7, 28), (7, 37), (7, 42), (7, 63)},
            "large proper parabolic inventory differs")
    for (rank, count), subset in large.items():
        if rank == 7:
            omitted = next(i for i in range(8) if not subset >> i & 1)
            normal = basis_inverse[omitted]
            require(4 * dot(normal, normal) == {63: 2, 42: 4, 37: 6, 28: 8}[count],
                    "fundamental normal norm differs")
        else:
            perpendicular = [root for root in roots
                             if all(not subset >> i & 1 or dot(root, SIMPLE[i]) == 0
                                    for i in range(8))]
            require(len(perpendicular) == {36: 3, 30: 2}[count]
                    and rational_rank(perpendicular) == 2, "normal-plane root system")

    normal_sets = {
        "norm4": integer_lines(1, 0) | integer_lines(0, 4) | half_lines(1),
        "norm6": integer_lines(1, 2) | integer_lines(0, 6) | half_lines(2),
        "norm8": (integer_lines(2, 0) | integer_lines(1, 4) | integer_lines(0, 8)
                  | half_lines(3) | half_lines(1, 5)) - {tuple(2 * x for x in r) for r in roots},
    }
    expected_sizes = {"norm4": 1080, "norm6": 3360, "norm8": 8640}
    family_masks = {}
    p112 = (1 << 112) - 1
    for name, normals in normal_sets.items():
        require(len(normals) == expected_sizes[name], "normal coordinate inventory: " + name)
        require(all(dot(x, x) == 4 * int(name[4:]) for x in normals), "normal coordinate norm")
        family_masks[name] = [support_mask(x, roots) & p112 for x in normals]
    for name, nonorthogonal, expected in (("a2_plane", True, 1120),
                                         ("a1_squared_plane", False, 3780)):
        planes = {off_masks[i] | off_masks[j] for i, j in combinations(range(120), 2)
                  if bool(dot(roots[i], roots[j])) == nonorthogonal}
        require(len(planes) == expected, "root-pair normal-plane inventory: " + name)
        family_masks[name] = [off & p112 for off in planes]
    normal_filter = {}
    for name, masks in family_masks.items():
        counts = Counter()
        for off in masks:
            size = off.bit_count()
            if size > 84:
                continue
            deletions = [off & cut for cut in outside]
            minimum = min(mask.bit_count() for mask in deletions)
            small = [mask for mask in deletions if mask.bit_count() <= 20]
            minimum_rank = min((binary_rank(labels[i] for i in indices(mask)) for mask in small),
                               default=None)
            if small:
                require(minimum_rank >= 7, "non-root normal passes the binary-rank filter")
            else:
                require(minimum > 20, "non-root normal passes the support-size filter")
            counts[(size, minimum, minimum_rank)] += 1
        profiles = [list(key) + [count] for key, count in sorted(counts.items())]
        require(profiles == EXPECTED_PROFILES[name], "normal deletion profile differs: " + name)
        normal_filter[name] = {"orbit_size": len(masks), "profiles": profiles}
    cap8 = max(120 - cut.bit_count() for cut in outside)
    require(cap8 == 64, "dimension-eight full-E8 cap is not 64")
    caps = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36, 8: cap8}
    # PROOF.md gives the uniform Fourier bound; the Cartan checker independently
    # checks that Fourier identity and exhausts the required small quadratics.
    partition_checks(caps)
    return {
        "schema_version": 1,
        "model": {"root_lines": 120, "frame_lines": 8, "frame_label_rank": 4,
                  "quadratic_gauss_sum": 16},
        "full_cap_bounds": {str(k): v for k, v in caps.items()},
        "full_code": {"hyperplanes_checked": 511, "minimum_complement_real_rank": 8},
        "root_remainders": {"directions_checked": 120, "size": 56, "minimum_nonzero_deletion": 24},
        "parabolics": {"subsets_checked": 256,
                       "large_proper_types": [list(key) for key in sorted(large)]},
        "normal_filter": normal_filter,
    }


def compare_geometry(primary, independent):
    for key, value in primary.items():
        require(independent.get(key) == value, "independent geometry mismatch: " + key)


def scientific_hashes():
    return {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in ("PROOF.md", "EXTENSION.md", "verify.py", "geometry_audit.py",
                         "algebra_check.py", "extension_check.py",
                         "formal/RootSwapOneExceptional.lean", "formal/RootSwapQuartet.lean",
                         "formal/RootSwapConnectedCover.lean")}


def run_all():
    primary = run_geometry()
    # Explicitly select package-local source even for isolated (-I) execution.
    sys.path.insert(0, str(PACKAGE))
    import geometry_audit
    import algebra_check
    import extension_check

    independent = geometry_audit.run_audit()
    compare_geometry(primary, independent)
    algebra = algebra_check.run_checks()
    extension = extension_check.run_checks()
    return {"schema_version": 1, "geometry": primary,
            "independent_geometry_controls": independent["rejection_controls"],
            "algebra": algebra, "cost_seven_extension": extension,
            "scientific_sha256": scientific_hashes()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="create a new receipt; refuse to overwrite")
    args = parser.parse_args()
    try:
        result = run_all()
        if args.emit:
            with args.emit.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, indent=2, sort_keys=True)
                stream.write("\n")
        else:
            expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
            require(result == expected, "recomputed mathematics or scientific source hashes differ from RESULT.json")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_E8_D0_ROOT_SWAPS: " + str(error), file=sys.stderr)
        return 1
    print("PASS_E8_D0_ROOT_SWAPS geometry=two-exact-methods normal_families=5 "
          "root_remainders=120 parabolics=256 "
          "extension_models=2 f1_support=24 frame_plane_cases=57120")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
