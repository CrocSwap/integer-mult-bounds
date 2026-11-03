#!/usr/bin/env python3
"""Independent numerical-first, actual-gate-data-second pair oracle.

Credit Ali Romman6509/6511, ToikY6523, Nick Petalas3152/3081,
Cuccaro-Draper-Kutin-Moulton, Clear1nsight4017 and the retained lineage.
No source or primary implementation is imported. Substantial OpenAI Codex
assistance. Apache-2.0. A blind arithmetic receipt is not circuit evidence.
"""

import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PIN_SHA = "771b2147ada0ebcbb0db1525f2db67a3c31814e88fccdd00983466e9c216b469"
CASE_SHA = "432b6579917eee977f995fd942507cd1d82cc0d7b967562db9fe00297eb15877"
SCHEMA_SHA = "c2de37d9fabafbd516ce84f1347f398799a18206f40927995657ff6fc302781a"
WIDTHS = (6, 7, 8, 16, 32, 64, 128, 256)
SIGNS = (-1, 1)
COMMON = {"schema_version", "source_manifest_sha256", "case_manifest_sha256", "logical_inventory", "case_groups"}
INVENTORY_KEYS = {"width", "sign", "data_bits", "clean_bits", "wires", "cx", "ccx", "x", "gates",
                  "selector_bits", "address_occurrences", "control_incidences", "encoded_bits"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_value(value):
    return sha((canonical(value) + "\n").encode())


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON key: " + key)
        value[key] = item
    return value


def reject_number(token):
    raise ValueError("noninteger JSON number forbidden: " + token)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_float=reject_number, parse_constant=reject_number)


def integer(value, name):
    require(type(value) is int, name + " must be integer, not bool")
    return value


def digest_text(value):
    return type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def checked_hash(raw, expected):
    require(sha(raw) == expected, "source/case/schema digest changed")


def parameters(width, sign):
    require(type(width) is int and 6 <= width <= 256, "supported width is6..256")
    require(type(sign) is int and sign in SIGNS, "compiled sign must be integer±1")


def case_input(width, sign, values):
    parameters(width, sign)
    require(type(values) is list and len(values) == 4, "case needs four input integers")
    bound = 1 << (width - 6)
    require(all(type(value) is int and abs(value) <= bound for value in values),
            "input outside promised headroom box")


def authenticate():
    raw = (ROOT / "SOURCE-PINS.json").read_bytes()
    checked_hash(raw, PIN_SHA)
    manifest = parse(raw)
    require(len(manifest["files"]) == 10, "ten immutable source objects required")
    for entry in manifest["files"]:
        raw = (ROOT / entry["local_path"]).read_bytes()
        require(len(raw) == entry["bytes"], "source byte count changed")
        checked_hash(raw, entry["sha256"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == entry["git_blob"], "source Git blob changed")
    raw = (ROOT / "SCHEMA.json").read_bytes()
    checked_hash(raw, SCHEMA_SHA)
    parse(raw)
    raw = (ROOT / "CASES.json").read_bytes()
    checked_hash(raw, CASE_SHA)
    cases = parse(raw)["cases"]
    require(type(cases) is list and len(cases) == 14814, "case count changed")
    groups = defaultdict(list)
    for row in cases:
        require(type(row) is list and len(row) == 3, "case row shape invalid")
        width, sign, values = row
        case_input(width, sign, values)
        require(width in WIDTHS, "case width not retained")
        groups[(width, sign)].append(values)
    require(list(groups) == [(w, sign) for w in WIDTHS for sign in SIGNS], "case group order invalid")
    for key, values in groups.items():
        expected = {6: 81, 7: 625, 8: 6561}.get(key[0], 28)
        require(len(values) == expected and values == sorted(values), "case group size/order invalid")
        require(len(values) == len({tuple(item) for item in values}), "duplicate case input")
    return dict(groups)


def forecast(width, sign):
    parameters(width, sign)
    cx, ccx = 276 * width - 104, 96 * width - 80
    wires = 18 * width + 6
    selector = (wires - 1).bit_length()
    gates = cx + ccx
    addresses = 2 * cx + 3 * ccx
    return {"width": width, "sign": sign, "data_bits": 4 * width, "clean_bits": 14 * width + 6,
            "wires": wires, "cx": cx, "ccx": ccx, "x": 0, "gates": gates,
            "selector_bits": selector, "address_occurrences": addresses,
            "control_incidences": cx + 2 * ccx, "encoded_bits": 9 + 2 * gates + selector * addresses}


def word(value, width):
    limit = 1 << (width - 1)
    require(type(value) is int and -limit <= value < limit, "signed intermediate overflow")
    return value


def numerical_pair(values, width, sign):
    parameters(width, sign)
    require(type(values) in (list, tuple) and len(values) == 4, "pair needs four components")
    a, b, c, d = [word(value, width) for value in values]
    sr, si = word(a + c, width), word(b + d, width)
    dr, di = word(a - c, width), word(b - d, width)
    cr, ci = 0, 0
    if (sr % 2) != (si % 2):
        if sr % 2:
            cr = 1 if sr > 0 else -1
        else:
            ci = 1 if si > 0 else -1
    shifted_real, shifted_imag = word(dr - cr, width), word(di - ci, width)
    rotated_real = word(-sign * shifted_imag, width)
    rotated_imag = word(sign * shifted_real, width)
    new_real, new_imag = word(rotated_real + cr, width), word(rotated_imag + ci, width)
    numerators = [word(sr + new_real, width), word(si + new_imag, width),
                  word(sr - new_real, width), word(si - new_imag, width)]
    require(all(value % 2 == 0 for value in numerators), "pair half numerator not even")
    return [word(value // 2, width) for value in numerators]


def numerical_profile(groups):
    result = []
    for (width, sign), inputs in groups.items():
        records = []
        for values in inputs:
            output = numerical_pair(values, width, sign)
            require(numerical_pair(output, width, -sign) == values, "numerical inverse failed")
            require(output[0] + output[2] == values[0] + values[2]
                    and output[1] + output[3] == values[1] + values[3], "conserved sum failed")
            records.append([values, output])
        result.append({"width": width, "sign": sign, "cases": len(inputs), "io_sha256": digest_value(records)})
    return result


def validate_receipt(receipt, groups):
    require(type(receipt) is dict and set(receipt) == COMMON, "receipt keys must match schema v1")
    require(type(receipt["schema_version"]) is int and receipt["schema_version"] == 1,
            "receipt schema_version must be integer1")
    require(digest_text(receipt["source_manifest_sha256"]) and digest_text(receipt["case_manifest_sha256"]),
            "receipt source/case digest malformed")
    require(receipt["source_manifest_sha256"] == PIN_SHA and receipt["case_manifest_sha256"] == CASE_SHA,
            "receipt source/case binding differs")
    rows = receipt["logical_inventory"]
    order = [(width, sign) for width in range(6, 257) for sign in SIGNS]
    require(type(rows) is list and len(rows) == len(order), "inventory row count invalid")
    for row, (width, sign) in zip(rows, order):
        require(type(row) is dict and set(row) == INVENTORY_KEYS, "inventory keys invalid")
        require(all(type(value) is int for value in row.values()), "inventory values must be integers")
        require(row == forecast(width, sign), "logical inventory differs from derived block bill")
    rows = receipt["case_groups"]
    require(type(rows) is list and len(rows) == len(groups), "case profile group count invalid")
    for row, ((width, sign), inputs) in zip(rows, groups.items()):
        require(type(row) is dict and set(row) == {"width", "sign", "cases", "io_sha256"},
                "case profile keys invalid")
        require(all(type(row[key]) is int for key in ("width", "sign", "cases")), "case profile integers required")
        require((row["width"], row["sign"], row["cases"]) == (width, sign, len(inputs)),
                "case profile order/domain invalid")
        require(digest_text(row["io_sha256"]), "case profile digest invalid")


def validate_gate(gate, width):
    require(type(gate) is list and len(gate) in (2, 3), "gate must be CNOT or Toffoli")
    require(all(type(wire) is int for wire in gate), "gate wires must be integers, not bool")
    require(len(set(gate)) == len(gate), "aliased gate wires")
    require(all(0 <= wire < 18 * width + 6 for wire in gate), "gate wire outside declared layout")


def load_artifact(path):
    with gzip.open(path, "rb") as stream:
        raw = stream.read(16777217)
    require(len(raw) <= 16777216, "expanded gate artifact exceeds16MiB")
    data = parse(raw)
    require(type(data) is dict and set(data) == {"schema_version", "circuits"}, "gate artifact keys invalid")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "gate artifact version invalid")
    records = data["circuits"]
    order = [(width, sign) for width in WIDTHS for sign in SIGNS]
    require(type(records) is list and len(records) == len(order), "gate artifact circuit count invalid")
    for record, (width, sign) in zip(records, order):
        require(type(record) is dict and set(record) == {"width", "sign", "gates"}, "gate record keys invalid")
        require(type(record["width"]) is int and type(record["sign"]) is int,
                "gate width/sign must be integers")
        require((record["width"], record["sign"]) == (width, sign), "gate artifact order invalid")
        gates = record["gates"]
        require(type(gates) is list and len(gates) <= 100000, "gate word size invalid")
        cx, ccx = 0, 0
        for gate in gates:
            validate_gate(gate, width)
            cx += len(gate) == 2
            ccx += len(gate) == 3
        expected = forecast(width, sign)
        require((cx, ccx, len(gates)) == (expected["cx"], expected["ccx"], expected["gates"]),
                "actual gate inventory differs from forecast")
    return records, digest_value(data), len(raw)


def pack(values, width):
    mask = (1 << width) - 1
    return sum((value & mask) << (index * width) for index, value in enumerate(values))


def unpack(state, width):
    mask, sign = (1 << width) - 1, 1 << (width - 1)
    values = [(state >> (index * width)) & mask for index in range(4)]
    return [value - (1 << width) if value & sign else value for value in values]


def masks(gates):
    return [(sum(1 << wire for wire in gate[:-1]), 1 << gate[-1]) for gate in gates]


def apply(state, program, inverse=False):
    sequence = reversed(program) if inverse else program
    for control, target in sequence:
        if state & control == control:
            state ^= target
    return state


def verify_state(width, state, expected):
    require(state >> (4 * width) == 0, "actual circuit leaves nonzero owned bits")
    require(unpack(state, width) == expected, "actual circuit public output differs")


def execute_artifact(records, groups):
    visits, cases = 0, 0
    observed_groups = []
    for record in records:
        width, sign, gates = record["width"], record["sign"], record["gates"]
        program = masks(gates)
        outputs = []
        for values in groups[(width, sign)]:
            initial = pack(values, width)
            final = apply(initial, program)
            expected = numerical_pair(values, width, sign)
            verify_state(width, final, expected)
            require(apply(final, program, True) == initial, "actual literal inverse differs")
            outputs.append([values, unpack(final, width)])
            cases += 1
            visits += 2 * len(gates)
        observed_groups.append({"width": width, "sign": sign, "cases": len(outputs), "io_sha256": digest_value(outputs)})
    return observed_groups, {"actual_circuit_checked": True, "expanded_programs": len(records),
                             "complete_case_outputs_and_owned_zero": cases, "literal_inverse_cases": cases,
                             "literal_elementary_gate_visits": visits}


def rejected(function, argument):
    try:
        function(argument)
    except ValueError:
        return True
    return False


def controls(receipt, groups):
    bad_version = dict(receipt)
    bad_version["schema_version"] = True
    missing = dict(receipt)
    del missing["logical_inventory"]
    result = {"unsupported_width_rejected": rejected(lambda width: forecast(width, 1), 5),
              "boolean_width_rejected": rejected(lambda width: forecast(width, 1), True),
              "boolean_sign_rejected": rejected(lambda sign: forecast(6, sign), True),
              "headroom_violation_rejected": rejected(lambda values: case_input(6, 1, values), [2, 0, 0, 0]),
              "aliased_gate_rejected": rejected(lambda gate: validate_gate(gate, 6), [0, 0]),
              "boolean_gate_wire_rejected": rejected(lambda gate: validate_gate(gate, 6), [False, 1]),
              "outside_gate_wire_rejected": rejected(lambda gate: validate_gate(gate, 6), [0, 114]),
              "wrong_gate_arity_rejected": rejected(lambda gate: validate_gate(gate, 6), [0]),
              "nonzero_owned_bits_rejected": rejected(lambda state: verify_state(6, state, [0] * 4), 1 << 24),
              "generic_cnot_inverse": apply(apply(1, masks([[0, 1]])), masks([[0, 1]]), True) == 1,
              "generic_toffoli_inverse": apply(apply(3, masks([[0, 1, 2]])), masks([[0, 1, 2]]), True) == 3,
              "source_digest_drift_rejected": rejected(lambda raw: checked_hash(raw, sha(b"source")), b"drift"),
              "boolean_schema_rejected": rejected(lambda value: validate_receipt(value, groups), bad_version),
              "missing_profile_rejected": rejected(lambda value: validate_receipt(value, groups), missing),
              "duplicate_json_rejected": rejected(parse, '{"x":1,"x":2}'),
              "nonfinite_json_rejected": rejected(parse, '{"x":NaN}'),
              "float_json_rejected": rejected(parse, '{"x":1.0}')}
    require(all(type(value) is bool and value for value in result.values()), "oracle control failed")
    return result


def generate(groups):
    receipt = {"schema_version": 1, "source_manifest_sha256": PIN_SHA, "case_manifest_sha256": CASE_SHA,
               "logical_inventory": [forecast(width, sign) for width in range(6, 257) for sign in SIGNS],
               "case_groups": numerical_profile(groups)}
    validate_receipt(receipt, groups)
    diagnostic = {"stage": "arithmetic_forecast_only", "actual_circuit_checked": False,
                  "numerical_cases_and_inverses": sum(len(values) for values in groups.values()),
                  "forecast_inventory_rows": len(receipt["logical_inventory"]), "controls": controls(receipt, groups),
                  "code_sha256": sha(Path(__file__).read_bytes())}
    return receipt, diagnostic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", "--write-first", dest="emit", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    require(not (args.emit and args.check_primary), "blind arithmetic emission must not read primary data")
    groups = authenticate()
    frozen, primary, artifact = None, None, None
    if not args.emit:
        frozen = parse((ROOT / "ORACLE.json").read_bytes())
        validate_receipt(frozen, groups)
    if args.check_primary:
        primary = parse(args.check_primary.read_bytes())
        validate_receipt(primary, groups)
        artifact = load_artifact(args.check_primary.parent / "GATES.json.gz")
    receipt, diagnostic = generate(groups)
    if args.emit:
        with args.emit.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(canonical(receipt) == canonical(frozen), "retained arithmetic profile differs")
    print("ORACLE_FIRST_STAGE " + canonical(diagnostic), flush=True)
    if args.check_primary:
        require(canonical(receipt) == canonical(primary), "actual primary common profile differs")
        records, artifact_hash, artifact_bytes = artifact
        actual_groups, report = execute_artifact(records, groups)
        require(canonical(actual_groups) == canonical(receipt["case_groups"]), "actual gate case profile differs")
        report.update({"actual_artifact_canonical_sha256": artifact_hash, "decompressed_artifact_bytes": artifact_bytes})
        print("PASS_ACTUAL_PRIMARY_GATE_DATA " + canonical(report), flush=True)
    print("PASS_CONSERVATIVE_PAIR_ORACLE " + ("actual_gate_data_checked" if args.check_primary else "arithmetic_forecast_only"))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_CONSERVATIVE_PAIR_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
