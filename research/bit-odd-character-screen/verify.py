#!/usr/bin/env python3
"""Decide every odd-order cyclic character counting cut, with exact indices."""

import argparse
import json
import re
import sys
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import gcd, lcm
from pathlib import Path

MAX_BYTES = 65536
MAX_PAID = 9
MAX_TARGETS = 3
MAX_ENTRY = 65535
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pivot_columns(rows):
    """Exact rational rank and a coordinate projection injective on the span."""
    if not rows:
        return ()
    work = [list(map(Fraction, row)) for row in rows]
    pivots = []
    for col in range(len(work[0])):
        candidates = [i for i in range(len(pivots), len(work)) if work[i][col]]
        if not candidates:
            continue
        pos = len(pivots)
        other = candidates[0]
        work[pos], work[other] = work[other], work[pos]
        scale = work[pos][col]
        work[pos] = [v / scale for v in work[pos]]
        for i in range(pos + 1, len(work)):
            scale = work[i][col]
            work[i] = [a - scale * b for a, b in zip(work[i], work[pos], strict=True)]
        pivots.append(col)
    return tuple(pivots)


def determinant(rows):
    """Bareiss elimination. Every division is checked before it is used."""
    size = len(rows)
    if size == 0:
        return 1
    work = [list(row) for row in rows]
    previous, sign = 1, 1
    for k in range(size - 1):
        candidates = [i for i in range(k, size) if work[i][k]]
        if not candidates:
            return 0
        other = candidates[0]
        if other != k:
            work[k], work[other] = work[other], work[k]
            sign = -sign
        pivot = work[k][k]
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                numerator = work[i][j] * pivot - work[i][k] * work[k][j]
                require(numerator % previous == 0, "nonexact Bareiss division")
                work[i][j] = numerator // previous
            work[i][k] = 0
        previous = pivot
    return sign * work[-1][-1]


def lattice_divisor(rows, columns):
    """GCD of full-rank row minors in a fixed injective projection."""
    rank = len(columns)
    value = 0
    for selected in combinations(rows, rank):
        minor = tuple(tuple(row[c] for c in columns) for row in selected)
        value = gcd(value, abs(determinant(minor)))
    require(value > 0, "zero lattice divisor for declared rank")
    return value


def finite_index(base, extra):
    """Return [base+extra:base], or None when this index is infinite."""
    columns = pivot_columns(base)
    combined = tuple(base) + tuple(extra)
    if len(pivot_columns(combined)) != len(columns):
        return None
    numerator = lattice_divisor(base, columns)
    denominator = lattice_divisor(combined, columns)
    require(numerator % denominator == 0, "nonintegral subgroup index")
    return numerator // denominator


def odd_part(value):
    require(value > 0, "nonpositive index")
    return value // (value & -value)


def kernel_measure(base, extra):
    """Limiting fraction of odd characters vanishing on extra, given base=0."""
    index = finite_index(base, extra)
    if index is None:
        return Fraction(0)
    return Fraction(1, odd_part(index))


def avoidance_density(base, targets):
    """Positive exactly when some odd character kills base and avoids targets."""
    density = Fraction(0)
    for mask in range(1 << len(targets)):
        extra = tuple(row for i, row in enumerate(targets) if mask & (1 << i))
        sign = -1 if mask.bit_count() % 2 else 1
        density += sign * kernel_measure(base, extra)
    require(0 <= density <= 1, "avoidance density outside [0,1]")
    return density


def membership_failure(paid, targets):
    for i, target in enumerate(targets):
        if finite_index(paid, (target,)) != 1:
            return {"status": "REJECT_TARGET_OUTSIDE_GENERATED_LATTICE",
                    "target_index": i}
    return None


def screen(paid, targets):
    """Inputs are validated integer address vectors. No ambient saturation."""
    failure = membership_failure(paid, targets)
    if failure is not None:
        return failure
    tests = 0
    paid_subsets = 0
    for mask in range(1 << len(paid)):
        survivors = len(paid) - mask.bit_count()
        if survivors >= len(targets):
            continue
        paid_subsets += 1
        base = tuple(row for i, row in enumerate(paid) if mask & (1 << i))
        for indices in combinations(range(len(targets)), survivors + 1):
            tests += 1
            chosen = tuple(targets[i] for i in indices)
            density = avoidance_density(base, chosen)
            if density > 0:
                return {"status": "REJECT_ODD_CHARACTER_CUT",
                        "zero_paid_indices": [i for i in range(len(paid))
                                              if mask & (1 << i)],
                        "nonzero_target_indices": list(indices),
                        "paid_nonzero_upper_bound": survivors,
                        "target_nonzero_lower_bound": len(indices),
                        "avoidance_density": str(density),
                        "paid_subsets_checked": paid_subsets,
                        "avoidance_tests": tests}
    return {"status": "PASS_ALL_ODD_CHARACTER_CUTS_ONLY",
            "paid_subsets_checked": paid_subsets, "avoidance_tests": tests}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "input exceeds byte capacity")
    return json.loads(raw, object_pairs_hook=unique_object)


def entry(value):
    require(type(value) is int or type(value) is str, "entry must be int or rational string")
    if type(value) is str:
        require(len(value) <= 24 and re.fullmatch(r"-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?", value),
                "invalid rational string")
    number = Fraction(value)
    require(abs(number.numerator) <= MAX_ENTRY and number.denominator <= MAX_ENTRY,
            "entry exceeds rational capacity")
    return number


def parse_frames(data):
    require(type(data) is dict and set(data) == {
        "address_dimension", "paid_frames", "target_frames"}, "invalid input keys")
    dim = data["address_dimension"]
    require(type(dim) is int and 1 <= dim <= 3, "address dimension must be 1..3")
    groups = []
    for key, minimum, maximum in (("paid_frames", 0, MAX_PAID),
                                  ("target_frames", 1, MAX_TARGETS)):
        matrices = data[key]
        require(type(matrices) is list and minimum <= len(matrices) <= maximum,
                "frame count exceeds capacity")
        group = []
        for matrix in matrices:
            require(type(matrix) is list and len(matrix) == dim, "invalid matrix rows")
            require(all(type(row) is list and len(row) == dim for row in matrix),
                    "invalid matrix columns")
            rows = tuple(tuple(entry(value) for value in row) for row in matrix)
            if key == "paid_frames":
                require(len(pivot_columns(rows)) == 1, "paid frame must have rank one")
            group.append(tuple(value for row in rows for value in row))
        groups.append(tuple(group))
    scale = lcm(*(v.denominator for group in groups for row in group for v in row))
    integer_groups = tuple(tuple(tuple(int(v * scale) for v in row) for row in group)
                           for group in groups)
    return integer_groups


def run_input(data):
    paid, targets = parse_frames(data)
    return screen(paid, targets)


def direct_fixture():
    frames = []
    for _ in range(3):
        for col in range(3):
            frames.append([[int(i == col and j == col) for j in range(3)]
                           for i in range(3)])
    identity = [[int(i == j) for j in range(3)] for i in range(3)]
    return {"address_dimension": 3, "paid_frames": frames,
            "target_frames": [identity, identity, identity]}


def check_sources():
    sources = read_json(HERE / "SOURCES.json")
    root = HERE.parent.parent
    for source in sources["files"]:
        if source["usage"] == "input":
            raw = (root / source["path"]).read_bytes()
            require(sha256(raw).hexdigest() == source["sha256"], "source digest mismatch")


def self_check():
    check_sources()
    require(avoidance_density(((2,),), ((1,),)) == 0, "2-primary torsion is invisible")
    require(avoidance_density(((6,),), ((1,),)) == Fraction(2, 3),
            "mixed torsion odd part is wrong")
    require(avoidance_density((), ((1,),)) == 1, "free target avoidance is wrong")
    require(avoidance_density((), ((0,),)) == 0, "zero target cannot be avoided")
    composite = run_input(read_json(HERE / "EXAMPLE.json"))
    require(composite["status"] == "REJECT_ODD_CHARACTER_CUT", "composite cut missed")
    require(composite["zero_paid_indices"] == [0], "wrong composite zero subset")
    require(composite["avoidance_density"] == "8/15", "wrong composite density")
    direct = run_input(direct_fixture())
    require(direct["status"] == "PASS_ALL_ODD_CHARACTER_CUTS_ONLY", "direct word rejected")
    predecessor = HERE.parent / "bit-ternary-character-separation" / "EXAMPLE.json"
    ternary = run_input(read_json(predecessor))
    require(ternary["status"] == "REJECT_ODD_CHARACTER_CUT", "retained ternary cut missed")
    paid, targets = parse_frames(read_json(predecessor))
    require(avoidance_density(paid[1:], targets) == Fraction(2, 3),
            "wrong retained one-paid ternary density")
    return {"composite": composite, "direct": direct, "retained_ternary": ternary,
            "retained_one_paid_density": "2/3"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="screen rational square address matrices")
    parser.add_argument("--write", action="store_true", help="regenerate only RESULT.json")
    args = parser.parse_args()
    require(not (args.input and args.write), "--write cannot be combined with --input")
    if args.input:
        result = run_input(read_json(args.input))
        print(json.dumps(result, sort_keys=True, indent=2))
        return int(result["status"].startswith("REJECT"))
    result = self_check()
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        expected = read_json(HERE / "RESULT.json")
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "result receipt mismatch")
    print("PASS_ODD_CHARACTER_SCREEN composite=8/15 direct=pass retained_ternary=reject no_new_kappa")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RecursionError, OverflowError) as error:
        print(f"INVALID_OR_FAILED: {error}", file=sys.stderr)
        sys.exit(2)
