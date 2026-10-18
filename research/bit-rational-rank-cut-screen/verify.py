#!/usr/bin/env python3
"""Complete rational projection/rank screen; passing is only necessary."""

import argparse
import json
import re
import sys
from fractions import Fraction
from itertools import combinations_with_replacement, product
from math import gcd, lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_BYTES = 65536
MAX_PAID = 12
MAX_TARGETS = 12
MAX_DIMENSION = 4
MAX_ENTRY = 65535


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    return decode_json(data)


def decode_json(data):
    require(len(data) <= MAX_BYTES, "input exceeds 65536 bytes")
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except RecursionError as error:
        raise ValueError("JSON nesting too deep") from error


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def rational(value):
    require(type(value) in (int, str), "entries must be integers or rational strings")
    if isinstance(value, str):
        require(
            len(value) <= 13 and re.fullmatch(r"-?[0-9]+(?:/[0-9]+)?", value),
            "invalid rational entry",
        )
    result = Fraction(value)
    require(
        abs(result.numerator) <= MAX_ENTRY and result.denominator <= MAX_ENTRY,
        "reduced entry numerator/denominator exceeds 65535",
    )
    return result


def extend(basis, vector):
    """Canonical reduced row basis after adding one vector."""
    row = list(vector)
    for old in basis:
        pivot = next(i for i, x in enumerate(old) if x)
        coefficient = row[pivot]
        row = [x - coefficient * y for x, y in zip(row, old, strict=True)]
    pivot = next((i for i, x in enumerate(row) if x), None)
    if pivot is None:
        return basis
    divisor = row[pivot]
    row = tuple(x / divisor for x in row)
    rows = [
        tuple(x - old[pivot] * y for x, y in zip(old, row, strict=True))
        for old in basis
    ]
    rows.append(row)
    rows.sort(key=lambda old: next(i for i, x in enumerate(old) if x))
    return tuple(rows)


def matrix(value, dimension):
    require(type(value) is list and len(value) == dimension, "wrong matrix row count")
    require(
        all(type(row) is list and len(row) == dimension for row in value),
        "wrong matrix column count",
    )
    return tuple(rational(x) for row in value for x in row)


def parse_instance(value):
    require(
        type(value) is dict
        and set(value) == {"address_dimension", "paid_frames", "target_frames"},
        "wrong instance keys",
    )
    dimension = value["address_dimension"]
    require(
        type(dimension) is int and 1 <= dimension <= MAX_DIMENSION,
        "address_dimension must be an integer from 1 through 4",
    )
    paid, targets = value["paid_frames"], value["target_frames"]
    require(type(paid) is list and len(paid) <= MAX_PAID, "at most 12 paid frames")
    require(
        type(targets) is list and 1 <= len(targets) <= MAX_TARGETS,
        "from 1 through 12 target frames required",
    )
    paid = tuple(matrix(item, dimension) for item in paid)
    targets = tuple(matrix(item, dimension) for item in targets)
    for item in paid:
        rows = [item[i : i + dimension] for i in range(0, dimension**2, dimension)]
        basis = ()
        for row in rows:
            basis = extend(basis, row)
        require(len(basis) == 1, "each paid frame must have rational rank one")
    return dimension, paid, targets


def dot(left, right):
    return sum((x * y for x, y in zip(left, right, strict=True)), Fraction(0))


def separating_functional(basis, outside, width):
    pivots = [next(i for i, x in enumerate(row) if x) for row in basis]
    free = [i for i in range(width) if i not in pivots]
    annihilator = []
    for column in free:
        vector = [Fraction(0)] * width
        vector[column] = Fraction(1)
        for pivot, row in zip(pivots, basis, strict=True):
            vector[pivot] = -row[column]
        annihilator.append(tuple(vector))
    require(annihilator, "a rejecting flat must have a nonzero annihilator")
    bound = len(outside) * (len(annihilator) - 1)
    for t in range(bound + 1):
        candidate = tuple(
            sum((t**j * row[i] for j, row in enumerate(annihilator)), Fraction(0))
            for i in range(width)
        )
        if all(dot(candidate, vector) for vector in outside):
            denominator = lcm(*(x.denominator for x in candidate))
            integers = tuple(int(x * denominator) for x in candidate)
            divisor = gcd(*integers)
            sign = 1 if next(x for x in integers if x) > 0 else -1
            return tuple(sign * x // divisor for x in integers)
    raise ValueError("internal error: polynomial root bound exhausted")


def screen(value):
    dimension, paid, targets = parse_instance(value)
    flats = {()}
    for vector in paid:
        flats |= {extend(basis, vector) for basis in flats}
    require(len(flats) <= 2 ** len(paid), "internal error: flat count")
    best = (0, ())
    for basis in sorted(flats):
        paid_out = sum(extend(basis, vector) != basis for vector in paid)
        target_out = sum(extend(basis, vector) != basis for vector in targets)
        if paid_out - target_out < best[0]:
            best = (paid_out - target_out, basis)
    margin, basis = best
    result = {
        "status": "REJECT_RATIONAL_RANK_CUT"
        if margin < 0
        else "PASS_NECESSARY_CUTS_ONLY",
        "minimum_margin": margin,
        "flats_checked": len(flats),
        "paid_count": len(paid),
        "target_count": len(targets),
    }
    if margin < 0:
        outside = tuple(v for v in paid + targets if extend(basis, v) != basis)
        functional = separating_functional(basis, outside, dimension**2)
        paid_values = tuple(dot(functional, v) for v in paid)
        target_values = tuple(dot(functional, v) for v in targets)
        actual_margin = sum(bool(x) for x in paid_values) - sum(
            bool(x) for x in target_values
        )
        require(actual_margin == margin, "internal error: witness margin")
        require(
            all(dot(functional, row) == 0 for row in basis),
            "internal error: functional does not annihilate flat",
        )
        result["witness"] = {
            "functional": [
                list(functional[i : i + dimension])
                for i in range(0, dimension**2, dimension)
            ],
            "paid_values": [str(x) for x in paid_values],
            "target_values": [str(x) for x in target_values],
            "paid_nonzero": sum(bool(x) for x in paid_values),
            "target_nonzero": sum(bool(x) for x in target_values),
        }
    return result


def frame(dimension, entries):
    result = [[0] * dimension for _ in range(dimension)]
    for row, column, value in entries:
        result[row][column] = value
    return result


def instance(dimension, paid, targets):
    return {
        "address_dimension": dimension,
        "paid_frames": paid,
        "target_frames": targets,
    }


def check_witness(value, result):
    """Separate literal dot-product check, without the row-space implementation."""
    weights = result["witness"]["functional"]
    counts = []
    for key in ("paid_frames", "target_frames"):
        values = [
            sum(
                Fraction(x) * weights[i][j]
                for i, row in enumerate(item)
                for j, x in enumerate(row)
            )
            for item in value[key]
        ]
        require(
            [str(x) for x in values]
            == result["witness"][key.replace("frames", "values")],
            "witness values differ",
        )
        counts.append(sum(x != 0 for x in values))
    require(counts[0] < counts[1], "witness must violate the cut")
    return counts


def independent_small_oracle():
    """Exhaust actual integer functionals on all bounded 2D vector fixtures."""
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    target_directions = [(0, 0)] + directions
    functionals = tuple(product(range(-6, 7), repeat=2))
    cases = 0
    for count in range(4):
        for paid in combinations_with_replacement(directions, count):
            for targets in combinations_with_replacement(target_directions, 2):
                expected = min(
                    sum(a * x + b * y != 0 for a, b in paid)
                    - sum(a * x + b * y != 0 for a, b in targets)
                    for x, y in functionals
                )
                value = instance(
                    2,
                    [[[a, b], [0, 0]] for a, b in paid],
                    [[[a, b], [0, 0]] for a, b in targets],
                )
                result = screen(value)
                require(
                    result["minimum_margin"] == expected, "independent oracle mismatch"
                )
                if expected < 0:
                    check_witness(value, result)
                cases += 1
    return cases


def semantic_controls(example, direct, rejection):
    for i, j in product(range(3), repeat=2):
        counts = [
            sum(Fraction(item[i][j]) != 0 for item in example[key])
            for key in ("paid_frames", "target_frames")
        ]
        require(counts[0] >= counts[1], "example must pass every coordinate cut")
    removed = instance(3, direct["paid_frames"][1:], direct["target_frames"])
    require(screen(removed)["minimum_margin"] == -1, "missing direct call must reject")
    corrupted = json.loads(json.dumps(rejection))
    corrupted["witness"]["functional"] = [[0] * 3 for _ in range(3)]
    try:
        check_witness(example, corrupted)
    except ValueError:
        pass
    else:
        raise ValueError("corrupted witness accepted")
    limit = instance(
        4,
        [frame(4, [(0, 0, "65535/65534")])] * 12,
        [frame(4, [(0, 0, "65535/65534")])] * 12,
    )
    require(screen(limit)["status"] == "PASS_NECESSARY_CUTS_ONLY", "capacity boundary")
    rational_a = [["1/2", "1/3"], [0, 0]]
    rational_b = [["1/3", "1/2"], [0, 0]]
    rational_value = instance(2, [rational_a, rational_b], [rational_a, rational_a])
    require(
        check_witness(rational_value, screen(rational_value)) == [1, 2],
        "noncoordinate rational basis",
    )
    for mutant in (False, 0.0):
        require(
            canonical_json({"margin": mutant}) != canonical_json({"margin": 0}),
            "receipt type mutation accepted",
        )
    return {
        "coordinate_cuts": 9,
        "missing_call_rejected": True,
        "corrupt_witness_rejected": True,
        "maximum_shape_accepted": True,
        "receipt_type_mutants_rejected": 2,
        "rational_basis_rejection": True,
    }


def verify():
    example = read_json(HERE / "EXAMPLE.json")
    rejection = screen(example)
    require(check_witness(example, rejection) == [2, 3], "eight-frame example")
    reference = dict(rejection)
    reference["witness"] = {
        "functional": [[1, -1, 0], [0, 0, 0], [0, 0, 0]],
        "paid_values": ["1", "2", "0", "0", "0", "0", "0", "0"],
        "target_values": ["1", "1", "1", "0"],
    }
    require(check_witness(example, reference) == [2, 3], "discussion reference cut")
    identity = frame(3, [(i, i, 1) for i in range(3)])
    direct = instance(
        3,
        [frame(3, [(i, i, 1)]) for i in range(3) for _ in range(3)],
        [identity] * 3 + [frame(3, [])],
    )
    require(screen(direct)["status"] == "PASS_NECESSARY_CUTS_ONLY", "direct word")
    incomplete = instance(1, [[[1]], [[1]]], [[[3]]])
    require(
        screen(incomplete)["status"] == "PASS_NECESSARY_CUTS_ONLY", "necessary only"
    )
    rational_case = instance(1, [[["1/2"]]], [[["-3/5"]], [["-3/5"]]])
    require(
        check_witness(rational_case, screen(rational_case)) == [1, 2],
        "rational values and duplicate targets",
    )
    require(screen(instance(1, [], [[[1]]]))["minimum_margin"] == -1, "empty paid list")
    require(
        screen(instance(1, [[[2]]], [[[2]]]))["minimum_margin"] == 0,
        "even formal exponent is nonzero",
    )
    semantic = semantic_controls(example, direct, rejection)
    controls = invalid_controls()
    cases = independent_small_oracle()
    units = [frame(4, [(i // 4, i % 4, 1)]) for i in range(12)]
    identity4 = frame(4, [(i, i, 1) for i in range(4)])
    capacity = screen(instance(4, units, [identity4] * 3))
    require(
        (capacity["flats_checked"], capacity["minimum_margin"]) == (4096, -3),
        "maximum flat-count control",
    )
    return {
        "example": rejection,
        "direct_word": screen(direct),
        "necessary_only_control": screen(incomplete),
        "oracle_cases": cases,
        "invalid_controls": controls,
        "semantic_controls": semantic,
        "capacity_control": capacity,
        "scope": "necessary rational rank cuts only",
    }


def invalid_controls():
    fixtures = [
        instance(True, [], [[[1]]]),
        instance(5, [], []),
        instance(1, [[[0]]], [[[1]]]),
        instance(2, [[[1, 0], [0, 1]]], [[[1, 0], [0, 1]]]),
        instance(1, [[[1.0]]], [[[1]]]),
        instance(1, [[[True]]], [[[1]]]),
        instance(1, [[["1/0"]]], [[[1]]]),
        instance(1, [[["1/65536"]]], [[[1]]]),
        instance(1, [[[1]]] * 13, [[[1]]]),
        instance(1, [], [[[1]]] * 13),
        instance(1, [], [[[65536]]]),
        instance(1, [], [[["NaN"]]]),
        instance(1, [], [[[1], [2]]]),
        {"paid_frames": []},
    ]
    for value in fixtures:
        try:
            screen(value)
        except (ValueError, ZeroDivisionError):
            continue
        raise ValueError("invalid instance accepted")
    for data in (
        b'{"a":1,"a":2}',
        b"[" * 2000 + b"0" + b"]" * 2000,
        b" " * (MAX_BYTES + 1),
    ):
        try:
            parse_instance(decode_json(data))
        except ValueError:
            continue
        raise ValueError("malformed JSON accepted")
    return len(fixtures) + 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="screen an instance; exit 0 passes, 1 rejects, 2 invalid",
    )
    parser.add_argument(
        "--write", action="store_true", help="write this package's verification receipt"
    )
    args = parser.parse_args()
    try:
        require(
            not (args.input and args.write),
            "--input and --write are mutually exclusive",
        )
        if args.input:
            result = screen(read_json(args.input))
            print(json.dumps(result, indent=2, sort_keys=True))
            return 1 if result["status"].startswith("REJECT") else 0
        result = verify()
        if args.write:
            (HERE / "RESULT.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n"
            )
        else:
            require(
                canonical_json(result)
                == canonical_json(read_json(HERE / "RESULT.json")),
                "receipt mismatch",
            )
        print(
            f"PASS_RATIONAL_RANK_CUT_SCREEN oracle_cases={result['oracle_cases']} "
            f"invalid_controls={result['invalid_controls']} example=2<3 no_new_kappa"
        )
        return 0
    except (ValueError, ZeroDivisionError, OSError) as error:
        print(f"INVALID_OR_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
