#!/usr/bin/env python3
"""Independent exact checker for the frame-zero JP8 compensation substitution.

This file reads serialized inputs; it never imports the construction or its
replay. Rows have integer coefficients and a common power-of-two denominator.
All 716 L inputs and the single private W input are algebraically independent.
Prepared for Varun-Mittal-1001 with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
INHERITED = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8"
PINS = {
    "CANONICAL-WORD.json.gz": "fb4a8d14ed2a8048698bea6ae16f86163a1aa6c80f2eb622222eee5cdbce9b3b",
    "LOCAL-PROGRAMS.json.gz": "efe45ce7fb025a6f53cc9eb54e951ac2211a5ed927e689a049e4f68ca680654b",
}
DIMENSION = 716
PRIVATE = ("W", 0)
ORIENTATIONS = ("forward", "backward")


class CheckError(ValueError):
    """A source, instruction, endpoint, or claimed bound failed verification."""


def require(condition, message):
    if not condition:
        raise CheckError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def reduced(row, exponent):
    """Canonical sparse integer row divided by 2**exponent."""
    row = {column: value for column, value in row.items() if value}
    if not row:
        return {}, 0
    if exponent:
        common = min((abs(value) & -abs(value)).bit_length() - 1 for value in row.values())
        common = min(common, exponent)
        if common:
            row = {column: value >> common for column, value in row.items()}
            exponent -= common
    return row, exponent


def scaled(row, numerator, denominator):
    require(type(numerator) is int and type(denominator) is int, "coefficient must have integer numerator and denominator")
    require(denominator > 0 and denominator & (denominator - 1) == 0, "coefficient denominator is not a positive power of two")
    coefficients, exponent = row
    return reduced({column: value * numerator for column, value in coefficients.items()}, exponent + denominator.bit_length() - 1)


def plus(left, right):
    left_row, left_exp = left
    right_row, right_exp = right
    exponent = max(left_exp, right_exp)
    result = {column: value << (exponent - left_exp) for column, value in left_row.items()}
    for column, value in right_row.items():
        result[column] = result.get(column, 0) + (value << (exponent - right_exp))
    return reduced(result, exponent)


def norm(row):
    return sum(abs(value) for value in row[0].values()), row[1]


def greater(left, right):
    return left[0] << right[1] > right[0] << left[1]


def rational(value):
    numerator, exponent = value
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    return {"numerator": numerator, "denominator": 1 << exponent}


def register(value):
    require(isinstance(value, list) and len(value) == 2, "register must be [namespace,index]")
    name, index = value
    require(type(index) is int, "register index must be an integer")
    require((name == "L" and 0 <= index < DIMENSION) or (name == "W" and index == 0), "only L[0:716] and W[0] are permitted")
    return name, index


def initial_rows():
    rows = {("L", index): ({index: 1}, 0) for index in range(DIMENSION)}
    rows[PRIVATE] = ({DIMENSION: 1}, 0)
    return rows


def source_panel():
    """Bind the panel to the pinned canonical word and both emitted programs."""
    loaded = {}
    for name, expected in PINS.items():
        payload = gzip.decompress((INHERITED / name).read_bytes())
        require(sha256(payload) == expected, "inherited payload hash mismatch: " + name)
        loaded[name] = json.loads(payload)
    canonical = loaded["CANONICAL-WORD.json.gz"]
    programs = loaded["LOCAL-PROGRAMS.json.gz"]
    panel = canonical["compensation"]
    require(canonical["v"] == 112 and canonical["R"] == 492, "unexpected supplier dimensions")
    require(len(panel) == 8800 and len(canonical["precondition"]) == 168, "unexpected compensation boundary")
    require(len(canonical["start"]) == DIMENSION, "unexpected entry dimension")
    for gate in panel:
        require(isinstance(gate, list) and len(gate) == 6 and gate[0] == "add" and gate[5] == 0, "compensation is not an all-frame-zero additive panel")
        _, target, source, numerator, denominator, _ = gate
        register(["L", target])
        register(["L", source])
        require(type(numerator) is int and numerator != 0 and denominator in (1, 2, 4), "unexpected compensation coefficient")
        require(canonical["start"][target] == canonical["start"][source] == 0, "panel register does not enter at frame zero")
    targets = {gate[1] for gate in panel}
    sources = {gate[2] for gate in panel}
    require(targets == set(range(112, 224)) and len(sources) == 266 and not targets & sources, "panel lacks the pinned disjoint rectangular support")
    for orientation in ORIENTATIONS:
        program = programs[orientation]
        expected = []
        for _, target, source, numerator, denominator, _ in panel:
            if orientation == "backward":
                target, source, numerator = source, target, -numerator
            expected.append(["scalar", ["add", ["L", target], ["L", source], numerator, denominator], 0])
        require(program[0] == ["phase", "zero_frame_precondition"], "unexpected first phase")
        require(program[169:8969] == expected, "canonical/local compensation binding failed for " + orientation)
        require(program[8969] == ["phase", "entry_adapters"], "compensation end moved")
    return panel


def expected_map(panel, orientation):
    # The disjoint support implies K**2 = 0, hence (I+K)**(-T) = I-K**T.
    rows = initial_rows()
    rows[PRIVATE] = ({}, 0)
    targets, sources = set(), set()
    for _, target, source, numerator, denominator, _ in panel:
        if orientation == "backward":
            target, source, numerator = source, target, -numerator
        targets.add(("L", target))
        sources.add(("L", source))
        rows["L", target] = plus(rows["L", target], scaled(({source: 1}, 0), numerator, denominator))
    require(not targets & sources, "expected map is not rectangular")
    return rows, targets, sources


def execute(operations, targets, sources):
    require(isinstance(operations, list) and operations, "candidate program must be a nonempty list")
    rows = initial_rows()
    peak = (1, 0)
    peak_at = {"primitive_index": -1, "register": ["L", 0]}
    histogram = {}
    for index, operation in enumerate(operations):
        require(isinstance(operation, list) and len(operation) >= 2, "malformed primitive at " + str(index))
        tag = operation[0]
        target = register(operation[1])
        require(target == PRIVATE or target in targets, "write outside compensation targets at " + str(index))
        histogram[tag] = histogram.get(tag, 0) + 1
        if tag == "clear":
            require(len(operation) == 2 and target == PRIVATE, "only private W can be cleared")
            rows[target] = ({}, 0)
        elif tag == "copy":
            require(len(operation) == 3 and target == PRIVATE, "copy must target private W")
            source = register(operation[2])
            require(source in sources, "copy must read an unchanged panel source")
            rows[target] = (dict(rows[source][0]), rows[source][1])
        elif tag == "scale":
            require(len(operation) == 4 and target == PRIVATE, "only private W can be scaled")
            numerator, denominator = operation[2:]
            require(type(numerator) is int and type(denominator) is int and (numerator, denominator) in ((-1, 1), (1, 1), (2, 1), (1, 2)), "scale is not one allowed primitive")
            rows[target] = scaled(rows[target], numerator, denominator)
        elif tag == "add":
            require(len(operation) == 5, "add must have five fields")
            source = register(operation[2])
            numerator, denominator = operation[3:]
            require(type(numerator) is int and type(denominator) is int and numerator in (-1, 1) and denominator == 1, "add is not a unit signed primitive")
            require(source != target, "add must use distinct registers")
            require(source in sources or source == PRIVATE, "add read outside unchanged sources/private W")
            rows[target] = plus(rows[target], scaled(rows[source], numerator, denominator))
        else:
            raise CheckError("unsupported primitive: " + str(tag))
        current = norm(rows[target])
        if greater(current, peak):
            peak = current
            peak_at = {"primitive_index": index, "register": list(target)}
    return rows, peak, peak_at, histogram


def equal_endpoint(actual, expected):
    for reference in expected:
        if actual[reference] != expected[reference]:
            left, right = actual[reference], expected[reference]
            columns = sorted(set(left[0]) | set(right[0]))
            column = next(column for column in columns if (left[0].get(column, 0) << right[1]) != (right[0].get(column, 0) << left[1]))
            raise CheckError("endpoint mismatch at " + str(reference) + ", independent input column " + str(column))


def digest_matrix(rows):
    serial = [[list(reference), row[1], sorted(row[0].items())] for reference, row in sorted(rows.items())]
    return sha256(json.dumps(serial, separators=(",", ":")).encode())


def verify_orientation(operations, panel, orientation, prefix_cap=None):
    expected, targets, sources = expected_map(panel, orientation)
    actual, peak, peak_at, histogram = execute(operations, targets, sources)
    equal_endpoint(actual, expected)
    if prefix_cap is not None:
        require(not greater(peak, prefix_cap), "exact primitive prefix exceeds declared cap")
    for reference in sources:
        require(actual[reference] == ({reference[1]: 1}, 0), "an arbitrary source input was not preserved")
    require(not actual[PRIVATE][0], "private W does not exit at zero")
    return {
        "single_coordinate_primitives": len(operations),
        "real_component_primitives": 2 * len(operations),
        "primitive_histogram": histogram,
        "exact_columns": DIMENSION + 1,
        "arbitrary_L_inputs": DIMENSION,
        "arbitrary_destination_input_preserved": True,
        "unchanged_source_rows": len(sources),
        "unchanged_spectator_rows": DIMENSION - len(targets),
        "private_input_column_removed": True,
        "private_exit_zero": True,
        "endpoint_matrix_sha256": digest_matrix(actual),
        "exact_prefix_l1": rational(peak),
        "prefix_witness": peak_at,
    }, peak


def negative_controls(candidate, panel, peaks):
    rejected = []

    def reject(label, orientation, operations, cap=None):
        try:
            verify_orientation(operations, panel, orientation, cap)
        except CheckError as error:
            rejected.append({"name": label, "rejection": str(error)})
        else:
            raise CheckError("negative control accepted: " + label)

    for orientation in ORIENTATIONS:
        operations = candidate[orientation]
        changed = copy.deepcopy(operations)
        index = next(i for i, op in enumerate(changed) if op[0] == "add" and op[1][0] == "L")
        changed[index][3] *= -1
        reject(orientation + ":changed_accumulation_sign", orientation, changed)

        changed = copy.deepcopy(operations)
        changed.pop(index)
        reject(orientation + ":omitted_accumulation", orientation, changed)

        changed = copy.deepcopy(operations)
        first_clear = next(i for i, op in enumerate(changed) if op[0] == "clear")
        changed.pop(first_clear)
        reject(orientation + ":missing_initial_clear", orientation, changed)

        changed = copy.deepcopy(operations)
        final_clear = max(i for i, op in enumerate(changed) if op[0] == "clear")
        changed.pop(final_clear)
        reject(orientation + ":missing_final_clear", orientation, changed)

        _, _, sources = expected_map(panel, orientation)
        source = list(min(sources))
        changed = copy.deepcopy(operations)
        changed.append(["add", source, ["W", 0], 1, 1])
        reject(orientation + ":write_to_unchanged_source", orientation, changed)

        # Double then halve private work: unchanged endpoint, strictly larger
        # exact prefix. The separate prefix check must detect this mutation.
        cap = peaks[orientation]
        doublings = max(2, cap[0].bit_length() + 2)
        excursion = [["clear", ["W", 0]], ["copy", ["W", 0], source]]
        excursion += [["scale", ["W", 0], 2, 1] for _ in range(doublings)]
        excursion += [["scale", ["W", 0], 1, 2] for _ in range(doublings)]
        excursion += [["clear", ["W", 0]]]
        changed = copy.deepcopy(operations) + excursion
        verify_orientation(changed, panel, orientation)
        reject(orientation + ":same_endpoint_excessive_prefix", orientation, changed, cap)
    return rejected


def check_candidate(candidate, controls=True):
    require(isinstance(candidate, dict) and all(key in candidate for key in ORIENTATIONS), "candidate must contain forward and backward arrays")
    panel = source_panel()
    receipts, peaks = {}, {}
    for orientation in ORIENTATIONS:
        receipts[orientation], peaks[orientation] = verify_orientation(candidate[orientation], panel, orientation)
    return {
        "status": "PASS_INDEPENDENT_INTEGER_DYADIC_COMPENSATION_CHECK",
        "inherited_payload_sha256": PINS,
        "canonical_compensation_gates": len(panel),
        "local_event_slice": {"start_inclusive": 169, "stop_exclusive": 8969},
        "both_pinned_local_program_slices_match_canonical": True,
        "source_target_disjointness": True,
        "orientations": receipts,
        "negative_controls_rejected": negative_controls(candidate, panel, peaks) if controls else [],
        "scope": "Exact frame-zero compensation substitution on arbitrary L inputs and arbitrary private W entry; W exits zero. The backward panel is I-K^T. Remaining local phases, recursive costs, routing and kappa are outside this checker.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=HERE / "CANDIDATE.json")
    parser.add_argument("--output", type=Path, help="write an independently generated receipt")
    args = parser.parse_args()
    receipt = check_candidate(read_json(args.candidate))
    receipt["candidate_sha256"] = sha256(args.candidate.read_bytes())
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
