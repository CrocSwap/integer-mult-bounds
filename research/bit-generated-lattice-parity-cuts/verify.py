#!/usr/bin/env python3
# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Exact generated-lattice parity cuts; a pass is only a necessary condition."""

import argparse
import itertools
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_BYTES = 65536
MAX_CALLS = 12
MAX_ROLES = 12
MAX_DIM = 4
MAX_BITS = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded(row):
    require(all(abs(x).bit_length() <= MAX_BITS for x in row), "integer capacity")
    return row


def lattice_basis(rows, width):
    """Euclidean unimodular row operations. Never saturate the rational span."""
    work = [bounded(list(row)) for row in rows]
    pivot = 0
    for column in range(width):
        for _ in range((2 * MAX_BITS + 1) * MAX_CALLS):
            candidates = [i for i in range(pivot, len(work)) if work[i][column]]
            if not candidates:
                break
            found = min(candidates, key=lambda i: abs(work[i][column]))
            work[pivot], work[found] = work[found], work[pivot]
            if work[pivot][column] < 0:
                work[pivot] = [-x for x in work[pivot]]
            for i in range(pivot + 1, len(work)):
                q = work[i][column] // work[pivot][column]
                work[i] = bounded([x - q * y for x, y in zip(work[i], work[pivot], strict=True)])
            if all(work[i][column] == 0 for i in range(pivot + 1, len(work))):
                for i in range(pivot):
                    q = work[i][column] // work[pivot][column]
                    work[i] = bounded([x - q * y for x, y in zip(work[i], work[pivot], strict=True)])
                pivot += 1
                break
        else:
            raise ValueError("Euclidean iteration capacity")
    require(not any(any(row) for row in work[pivot:]), "echelon invariant")
    return tuple(tuple(row) for row in work[:pivot])


def coordinates(basis, row):
    remaining = list(row)
    result = []
    for vector in basis:
        pivot = next(i for i, x in enumerate(vector) if x)
        q, remainder = divmod(remaining[pivot], vector[pivot])
        if remainder:
            return None
        result.append(q)
        remaining = bounded([x - q * y for x, y in zip(remaining, vector, strict=True)])
    if any(remaining):
        return None
    bounded(result)
    require(all(sum(c * b[i] for c, b in zip(result, basis, strict=True)) == x
                for i, x in enumerate(row)), "coordinate reconstruction")
    return tuple(result)


def rational(value):
    require(type(value) in (int, str), "entry must be an integer or rational string")
    if isinstance(value, str):
        require(len(value) <= 13 and re.fullmatch(r"-?[0-9]+(?:/[0-9]+)?", value),
                "invalid rational string")
    result = Fraction(value)
    require(abs(result.numerator) <= 65535 and result.denominator <= 65535,
            "rational entry capacity")
    return result


def rational_rank(rows):
    work = [list(map(Fraction, row)) for row in rows]
    rank = 0
    width = len(work[0]) if work else 0
    for column in range(width):
        found = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[rank], work[found] = work[found], work[rank]
        divisor = work[rank][column]
        work[rank] = [x / divisor for x in work[rank]]
        for i in range(rank + 1, len(work)):
            coefficient = work[i][column]
            work[i] = [x - coefficient * y for x, y in zip(work[i], work[rank], strict=True)]
        rank += 1
    return rank


def parse(value):
    require(type(value) is dict and set(value) == {
        "address_dimension", "paid_frames", "target_frames"}, "wrong instance keys")
    dimension = value["address_dimension"]
    require(type(dimension) is int and 1 <= dimension <= MAX_DIM, "dimension capacity")
    paid, targets = value["paid_frames"], value["target_frames"]
    require(type(paid) is list and len(paid) <= MAX_CALLS, "paid count capacity")
    require(type(targets) is list and 1 <= len(targets) <= MAX_ROLES, "target count capacity")
    parsed = []
    for matrix in paid + targets:
        require(type(matrix) is list and len(matrix) == dimension, "matrix row count")
        require(all(type(row) is list and len(row) == dimension for row in matrix),
                "matrix column count")
        parsed.append(tuple(rational(x) for row in matrix for x in row))
    for row in parsed[:len(paid)]:
        require(rational_rank([row[i:i + dimension] for i in range(0, dimension**2, dimension)]) == 1,
                "paid frame must have rational rank one")
    return dimension, tuple(parsed[:len(paid)]), tuple(parsed[len(paid):])


def parity_mask(row):
    return sum((x % 2) << i for i, x in enumerate(row))


def character_cut(paid, targets, rank):
    best = (0, 0, [], [])
    for character in range(1 << rank):
        p = [i for i, row in enumerate(paid) if (character & parity_mask(row)).bit_count() % 2]
        t = [i for i, row in enumerate(targets) if (character & parity_mask(row)).bit_count() % 2]
        if len(p) - len(t) < best[0]:
            best = (len(p) - len(t), character, p, t)
    margin, character, p, t = best
    return {"minimum_margin": margin, "characters_checked": 1 << rank,
            "witness": {"basis_values": [(character >> i) & 1 for i in range(rank)],
                        "paid_indices": p, "target_indices": t}}


def screen(value):
    dimension, paid, targets = parse(value)
    scale = math.lcm(*(x.denominator for row in paid + targets for x in row))
    require(scale.bit_length() <= 128, "common denominator capacity")
    integer_paid = [tuple(int(x * scale) for x in row) for row in paid]
    integer_targets = [tuple(int(x * scale) for x in row) for row in targets]
    basis = lattice_basis(integer_paid, dimension**2)
    p = [coordinates(basis, row) for row in integer_paid]
    require(all(row is not None for row in p), "paid lattice reconstruction")
    t = [coordinates(basis, row) for row in integer_targets]
    determinant = all(sum(row[i] for row in paid) == sum(row[i] for row in targets)
                      for i in range(dimension**2))
    result = {"lattice_rank": len(basis), "scale": scale, "basis": basis,
              "paid_coordinates": p, "target_coordinates": t,
              "determinant_matches": determinant}
    outside = [i for i, row in enumerate(t) if row is None]
    if outside:
        return dict(result, status="REJECT_TARGET_OUTSIDE_LATTICE", outside_targets=outside)
    result.update(character_cut(p, t, len(basis)))
    result["target_classes"] = [[x % 2 for x in row] for row in t]
    if result["minimum_margin"] < 0:
        result["status"] = "REJECT_GENERATED_LATTICE_PARITY_CUT"
    elif not determinant:
        result["status"] = "REJECT_DETERMINANT"
    else:
        result["status"] = "PASS_NECESSARY_PARITY_AND_DETERMINANT_ONLY"
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "file capacity")
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except RecursionError as error:
        raise ValueError("JSON nesting capacity") from error


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def instance(paid, targets):
    return {"address_dimension": 2, "paid_frames": [[[a, b], [0, 0]] for a, b in paid],
            "target_frames": [[[a, b], [0, 0]] for a, b in targets]}


def independent_oracle():
    """Cramer's rule computes every character without the lattice algorithm."""
    pool = [(1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (1, -1), (2, 2)]
    cases = 0
    for (a, b), (c, d) in itertools.product(pool, repeat=2):
        determinant = a * d - b * c
        if not determinant:
            continue
        for x, y in itertools.product(range(-4, 5), repeat=2):
            numerators = (x * d - y * c, a * y - b * x)
            result = screen(instance([(a, b), (c, d)], [(x, y)] * 3))
            if any(n % determinant for n in numerators):
                require(result["status"] == "REJECT_TARGET_OUTSIDE_LATTICE", "Cramer membership")
            else:
                u, v = (n // determinant for n in numerators)
                expected = min(i + j - 3 * ((i * u + j * v) % 2)
                               for i, j in itertools.product(range(2), repeat=2))
                require(result["minimum_margin"] == expected, "independent character oracle")
            cases += 1
    for generators in itertools.product(range(1, 7), repeat=3):
        g = math.gcd(*generators)
        result = screen(instance([(a, 0) for a in generators], [(g, 0)] * 3))
        expected = min(0, sum((a // g) % 2 for a in generators) - 3)
        require(result["minimum_margin"] == expected, "gcd character oracle")
        cases += 1
    return cases


def relation_oracle():
    """A primitive cross-minor relation enumerates characters on three generators."""
    pool = [(1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (1, -1), (2, 2)]
    cases = 0
    for a, b, c in itertools.product(pool, repeat=3):
        relation = (b[0] * c[1] - b[1] * c[0],
                    c[0] * a[1] - c[1] * a[0],
                    a[0] * b[1] - a[1] * b[0])
        divisor = math.gcd(*relation)
        if not divisor:
            continue
        relation = tuple(x // divisor for x in relation)
        characters = [p for p in itertools.product(range(2), repeat=3)
                      if sum(x * y for x, y in zip(p, relation, strict=True)) % 2 == 0]
        require(len(characters) == 4, "primitive relation character count")
        for coefficients in itertools.product(range(2), repeat=3):
            target = tuple(sum(n * row[i] for n, row in zip(coefficients, (a, b, c), strict=True))
                           for i in range(2))
            expected = min(sum(p) - 3 * (sum(x * y for x, y in zip(p, coefficients, strict=True)) % 2)
                           for p in characters)
            result = screen(instance([a, b, c], [target] * 3))
            require(result["minimum_margin"] == expected, "primitive relation oracle")
            cases += 1
    return cases


def determinant3(row):
    a, b, c, d, e, f, g, h, i = row
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def evidence():
    example = read_json(HERE / "EXAMPLE.json")
    _, paid, targets = parse(example)
    require(len(paid) == 8 and len(targets) == 3, "example shape")
    require(rational_rank(paid) == 6, "paid span exactly six")
    expected = [tuple(sum(paid[j][i] for j in indices) for i in range(9))
                for indices in ((0, 1, 2), (0, 3, 4))]
    expected.append(tuple(-paid[0][i] + sum(paid[j][i] for j in (5, 6, 7)) for i in range(9)))
    require(tuple(expected) == targets, "displayed target decomposition")
    subsets = [rational_rank([paid[i] for i in indices])
               for indices in itertools.combinations(range(8), 6)]
    require(len(subsets) == 28 and set(subsets) == {6}, "all six-frame subsets independent")
    determinants = [determinant3(row) for row in targets]
    require(all(determinants), "targets invertible")
    result = screen(example)
    require(result["status"] == "REJECT_GENERATED_LATTICE_PARITY_CUT"
            and result["determinant_matches"] and result["minimum_margin"] == -2,
            "eight-call separation")
    require(len({tuple(row) for row in result["target_classes"]}) == 3, "unequal classes")
    require([i for i, row in enumerate(paid) if row[0] % 2] == [0]
            and all(row[0] % 2 for row in targets), "literal X11 character")
    direct = {"address_dimension": 3,
              "paid_frames": [[[int(i == j == k) for j in range(3)] for i in range(3)]
                              for k in range(3) for _ in range(3)],
              "target_frames": [[[int(i == j) for j in range(3)] for i in range(3)]] * 3}
    require(screen(direct)["status"].startswith("PASS_"), "nine-call direct word")
    for scale in (Fraction(1, 2), Fraction(2), Fraction(-1, 3)):
        variant = {"address_dimension": 3}
        for key in ("paid_frames", "target_frames"):
            variant[key] = [[[str(scale * x) for x in row] for row in matrix] for matrix in example[key]]
        require(screen(variant)["minimum_margin"] == -2, "rational scaling invariance")
    cramer_gcd, relations = independent_oracle(), relation_oracle()
    return {"example": result, "six_frame_subsets": len(subsets),
            "target_determinants": [str(x) for x in determinants],
            "literal_character": {"paid_indices": [0], "target_indices": [0, 1, 2]},
            "direct_nine_calls": screen(direct), "oracle_cases": cramer_gcd + relations,
            "cramer_gcd_cases": cramer_gcd, "primitive_relation_cases": relations,
            "scope": "all generated-lattice binary-character cuts and idempotent determinant only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="exit 0 passes necessary tests, 1 rejects, 2 invalid")
    parser.add_argument("--write", action="store_true", help="regenerate this package's receipt")
    args = parser.parse_args()
    try:
        require(not (args.input and args.write), "--input and --write are mutually exclusive")
        if args.input:
            result = screen(read_json(args.input))
            print(json.dumps(result, indent=2, sort_keys=True))
            return int(result["status"].startswith("REJECT_"))
        result = evidence()
        if args.write:
            (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            require(canonical(result) == canonical(read_json(HERE / "RESULT.json")), "receipt mismatch")
        print(f"PASS_GENERATED_LATTICE_PARITY_CUTS example=1<3 characters=64 "
              f"oracle_cases={result['oracle_cases']} no_new_kappa")
        return 0
    except (ValueError, ZeroDivisionError, OSError) as error:
        print(f"INVALID_OR_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
