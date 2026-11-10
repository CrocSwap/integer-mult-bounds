#!/usr/bin/env python3
"""Sparse-tape interpretation of the authenticated source increment macro."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    "CASES.json": "56065d4fc3a98c411cb068714eebc2c06d330976873093a28791193096b74cba",
    "SCHEMA.json": "ff29b35fef8e469938c6f0c7cbd0b17228e75e46fad6bdbab5e2ca2d262abed7",
    "SOURCE-PINS.json": "e08bed306ef62f5f05c5ae22969857c348b508cb0037f5310c01aaf9af145e73",
}
SOURCE = "3bad39ffd4faf7e8cb1bc5b47769cbb28511f797"
BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
FAR = 4096
SPECTATOR = {-8: LEFT, -7: ONE, -6: RIGHT, 9: MARK}
CONTROLS = {"wrong_zero_write", "wrong_carry_write", "wrong_return_move",
            "wrong_default_guard", "per_call_18_false", "duplicate_key",
            "float_token", "boolean_integer"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def bad_number(_):
    raise ValueError("float or nonfinite JSON token")


def decode(raw):
    need(len(raw) <= 4 * 1024 * 1024, "JSON byte budget")
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_float=bad_number, parse_constant=bad_number)


def load(path):
    return decode(path.read_bytes())


def integer(value, label):
    need(type(value) is int, label + ": proof integer required")
    return value


def authenticate():
    for name, expected in PINS.items():
        need(digest((HERE / name).read_bytes()) == expected, "frozen metadata drift: " + name)
    sources = load(HERE / "SOURCE-PINS.json")
    paths = {"primary.py", "oracle.py", "emitter.py", *PINS}
    need(len(sources["sources"]) == 6, "six source inputs")
    for entry in sources["sources"]:
        name = entry["local_path"]
        need(type(name) is str and name.startswith("inputs/") and
             ".." not in Path(name).parts and name not in paths, "unique source path")
        paths.add(name)
        need(digest((HERE / name).read_bytes()) == entry["sha256"], "source byte drift")
    manifest = load(HERE / "FILES.json")
    need(type(manifest) is dict and set(manifest) == {"schema_version", "files"}, "FILES keys")
    need(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1, "FILES version")
    seen = set()
    for entry in manifest["files"]:
        need(type(entry) is dict and set(entry) == {"path", "sha256"}, "FILES row")
        name = entry["path"]
        need(type(name) is str and name in paths and name not in seen, "FILES exact unique paths")
        seen.add(name)
        need(digest((HERE / name).read_bytes()) == entry["sha256"], "FILES byte drift: " + name)
    need(seen == paths and len(paths) == 12, "FILES must cover twelve core inputs")
    return load(HERE / "CASES.json"), load(HERE / "SCHEMA.json")


def actual_table():
    spec = importlib.util.spec_from_file_location("increment_source_emitter", HERE / "emitter.py")
    need(spec is not None and spec.loader is not None, "emitter loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.emit_table()


def validate_table(table, schema):
    need(type(table) is dict and set(table) == set(schema["table_keys"]), "table exact keys")
    for key in ("schema_version", "tapes", "entry", "stop_pc", "fail_pc"):
        integer(table[key], "table " + key)
    need(table["schema_version"] == 1 and table["tapes"] == 2, "table version/tapes")
    rows = table["instructions"]
    need(type(rows) is list and 1 <= len(rows) <= 1024, "bounded instruction list")
    for key in ("entry", "stop_pc", "fail_pc"):
        need(0 <= table[key] < len(rows), "bounded table PC")
    for row in rows:
        validate_instruction(row, len(rows))
    need(rows[table["stop_pc"]] == ["halt"], "wrapper stop must be HALT")
    need(rows[table["fail_pc"]][0] == "reject", "failure row must reject")


def validate_instruction(row, count):
    need(type(row) is list and row and type(row[0]) is str, "instruction row")
    op = row[0]
    arity = {"branch": 4, "write": 3, "move": 3, "goto": 2, "halt": 1, "reject": 2}
    need(op in arity and len(row) == arity[op], "instruction arity")
    if op in ("branch", "write", "move"):
        need(0 <= integer(row[1], "tape index") < 2, "tape index range")
    if op == "branch":
        need(type(row[2]) is list, "branch cases")
        seen = set()
        for pair in row[2]:
            need(type(pair) is list and len(pair) == 2, "branch pair")
            symbol, target = pair
            need(0 <= integer(symbol, "branch symbol") < 7 and symbol not in seen, "unique alphabet case")
            need(0 <= integer(target, "branch target") < count, "branch target range")
            seen.add(symbol)
        need(0 <= integer(row[3], "branch default") < count, "default target range")
    elif op == "goto":
        need(0 <= integer(row[1], "goto target") < count, "goto target range")
    elif op == "write":
        need(0 <= integer(row[2], "write symbol") < 7, "write alphabet")
    elif op == "move":
        need(integer(row[2], "move direction") in (-1, 1), "unit move")
    elif op == "reject":
        need(type(row[1]) is str, "reject reason")


def counter_cells(value):
    integer(value, "fixture counter")
    need(value >= 0, "nonnegative fixture")
    cells = {-1: MARK, 0: LEFT, FAR: UNIT}
    for bit in range(value.bit_length()):
        cells[bit + 1] = ONE if value >> bit & 1 else ZERO
    cells[value.bit_length() + 1] = RIGHT
    return cells


def state(value):
    return {"cells": [counter_cells(value), dict(SPECTATOR)], "heads": [1, -7]}


class MacroRejected(ValueError):
    def __init__(self, pc, reason):
        super().__init__(reason)
        self.pc = pc


class EndpointMismatch(ValueError):
    pass


def execute(table, machine):
    rows, heads, tapes = table["instructions"], machine["heads"], machine["cells"]
    pc, steps, visited = table["entry"], 0, {heads[0]}
    while pc != table["stop_pc"]:
        need(steps < 100000 and 0 <= pc < len(rows), "macro step/PC budget")
        row = rows[pc]
        op = row[0]
        steps += 1
        if op == "branch":
            symbol = tapes[row[1]].get(heads[row[1]], BLANK)
            pc = dict(row[2]).get(symbol, row[3])
        elif op == "write":
            if row[2] == BLANK:
                tapes[row[1]].pop(heads[row[1]], None)
            else:
                tapes[row[1]][heads[row[1]]] = row[2]
            pc += 1
        elif op == "move":
            heads[row[1]] += row[2]
            pc += 1
        elif op == "goto":
            pc = row[1]
        elif op == "reject":
            raise MacroRejected(pc, row[1])
        else:
            raise ValueError("unexpected HALT before macro continuation")
        visited.add(heads[0])
    return steps, min(visited), max(visited)


def read_value(machine):
    cells, value, length = machine["cells"][0], 0, 0
    for position in range(1, FAR):
        symbol = cells.get(position, BLANK)
        if symbol == RIGHT:
            if length and cells[position - 1] != ONE:
                raise EndpointMismatch("counter is not canonical")
            return value
        if symbol not in (ZERO, ONE):
            raise EndpointMismatch("counter has invalid body")
        if symbol == ONE:
            value += 1 << length
        length += 1
    raise EndpointMismatch("counter has no bounded RIGHT marker")


def endpoint(machine, expected):
    if machine["heads"][0] != 1:
        raise EndpointMismatch("head did not return to one")
    actual = read_value(machine)
    if actual != expected or machine["cells"][0] != counter_cells(expected):
        raise EndpointMismatch("counter value/markers/guards differ")
    if machine["heads"][1] != -7 or machine["cells"][1] != SPECTATOR:
        raise EndpointMismatch("spectator changed")
    return actual


def run_positive(table, value):
    machine = state(value)
    steps, low, high = execute(table, machine)
    return machine, endpoint(machine, value + 1), steps, low, high


def sequential(table, cases):
    machine, total, rows = state(0), 0, []
    for expected in range(1, cases["sequential_from_zero"] + 1):
        steps, low, high = execute(table, machine)
        actual = endpoint(machine, expected)
        total += steps
        formula = 13 * expected - 7 * expected.bit_count() + 5 * expected.bit_length()
        need(total == formula and total <= 15 * expected, "from-zero exact/uniform cost")
        rows.append([actual, steps, total, machine["heads"][0], low, high])
    return rows


def carries(table, cases):
    rows = []
    for bits in cases["long_carry_bits"]:
        integer(bits, "carry width")
        need(1 <= bits <= 256, "carry width bound")
        machine, actual, steps, low, high = run_positive(table, (1 << bits) - 1)
        need(steps == 7 * bits + 11, "all-ones actual carry cost")
        rows.append([bits, actual, steps, machine["heads"][0], low, high])
    return rows


def copied_table(table):
    return decode(canonical(table))


def endpoint_failure(table, start, word):
    machine = state(start)
    execute(table, machine)
    try:
        endpoint(machine, start + 1)
    except EndpointMismatch as error:
        need(word in str(error), "unintended endpoint control diagnostic")
        return True
    raise ValueError("semantic mutation was accepted")


def parser_failure(function, word):
    try:
        function()
    except ValueError as error:
        need(word in str(error), "unintended parser control diagnostic")
        return True
    raise ValueError("parser mutation was accepted")


def invalid_unit_state():
    machine = state(0)
    machine["cells"][0][1] = UNIT
    machine["cells"][0][2] = RIGHT
    return machine


def default_control(table, zero_pc):
    try:
        execute(table, invalid_unit_state())
    except MacroRejected as error:
        need(error.pc == table["fail_pc"], "baseline invalid UNIT rejected elsewhere")
    else:
        raise ValueError("baseline invalid UNIT was accepted")
    mutant = copied_table(table)
    mutant["instructions"][table["entry"]][3] = zero_pc
    machine = invalid_unit_state()
    execute(mutant, machine)
    endpoint(machine, 1)
    return True


def controls(table, schema):
    entry = table["instructions"][table["entry"]]
    need(entry[0:2] == ["branch", 0], "source increment entry")
    targets = dict(entry[2])
    zero_pc, one_pc = targets[ZERO], targets[ONE]
    need(table["instructions"][zero_pc] == ["write", 0, ONE], "source ZERO write site")
    need(table["instructions"][one_pc] == ["write", 0, ZERO], "source carry write site")
    need(table["instructions"][table["stop_pc"] - 1] == ["move", 0, 1], "source return site")
    wrong_zero, wrong_carry, wrong_return = [copied_table(table) for _ in range(3)]
    wrong_zero["instructions"][zero_pc][2] = ZERO
    wrong_carry["instructions"][one_pc][2] = ONE
    wrong_return["instructions"][table["stop_pc"] - 1][2] = -1
    for mutant in (wrong_zero, wrong_carry, wrong_return):
        validate_table(mutant, schema)
    result = {"wrong_zero_write": endpoint_failure(wrong_zero, 2, "counter"),
              "wrong_carry_write": endpoint_failure(wrong_carry, 1, "counter"),
              "wrong_return_move": endpoint_failure(wrong_return, 0, "head"),
              "wrong_default_guard": default_control(table, zero_pc)}
    _, _, steps, _, _ = run_positive(table, 3)
    need(steps == 25 and steps > 18, "arbitrary-start per-call18 control")
    result["per_call_18_false"] = True
    result["duplicate_key"] = parser_failure(lambda: decode(b'{"x":1,"x":2}'), "duplicate")
    result["float_token"] = parser_failure(lambda: decode(b'{"x":1.0}'), "float")
    result["boolean_integer"] = parser_failure(lambda: integer(True, "control"), "proof integer")
    need(set(result) == CONTROLS, "complete eight controls")
    return result


def certificate(cases, schema):
    need(cases["source_head"] == SOURCE and cases["sequential_from_zero"] == 1024, "frozen source/domain")
    table = actual_table()
    validate_table(table, schema)
    rows, carry = sequential(table, cases), carries(table, cases)
    need(rows[3][2] == 60, "sharp actual C4 witness")
    result = {"schema_version": 1, "source_head": SOURCE,
              "cases_sha256": PINS["CASES.json"], "source_pins_sha256": PINS["SOURCE-PINS.json"],
              "table": table, "table_sha256": digest(canonical(table)),
              "sequential_rows": rows, "carry_rows": carry,
              "controls": controls(table, schema),
              "sharp_witness": {"k": 4, "cost": 60, "uniform_coefficient": 15}}
    return result


def validate_certificate(value, cases, schema):
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(integer(value["schema_version"], "certificate version") == 1, "certificate version one")
    validate_table(value["table"], schema)
    for key, count in (("sequential_rows", 1024), ("carry_rows", len(cases["long_carry_bits"]))):
        rows = value[key]
        need(type(rows) is list and len(rows) == count, "certificate row count")
        for row in rows:
            need(type(row) is list and len(row) == 6, "six proof integers per row")
            for item in row:
                integer(item, "certificate row")
    need(type(value["controls"]) is dict and set(value["controls"]) == CONTROLS, "certificate control keys")
    need(all(type(x) is bool and x for x in value["controls"].values()), "true Boolean control outcomes")
    sharp = value["sharp_witness"]
    need(type(sharp) is dict and set(sharp) == {"k", "cost", "uniform_coefficient"}, "sharp witness keys")
    for item in sharp.values():
        integer(item, "sharp witness")
    for key in ("source_head", "cases_sha256", "source_pins_sha256", "table_sha256"):
        need(type(value[key]) is str, "certificate provenance/hash string")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.certificate), "choose emission or retained certificate")
    cases, schema = authenticate()
    expected = certificate(cases, schema)
    validate_certificate(expected, cases, schema)
    if args.emit:
        args.emit.write_bytes(canonical(expected) + b"\n")
    else:
        actual = load(args.certificate or HERE / "CERTIFICATE.json")
        validate_certificate(actual, cases, schema)
        need(canonical(actual) == canonical(expected), "whole canonical certificate differs")
    print("PASS_SOURCE_INCREMENT_SPARSE actual_table rows1024 controls8 sharp15 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_SOURCE_INCREMENT_SPARSE: " + str(error), file=sys.stderr)
        raise SystemExit(1)
