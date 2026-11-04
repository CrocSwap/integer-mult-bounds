#!/usr/bin/env python3
"""Dense-list independent execution of the full nine-tape child-shape producer."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASE_SHA = "ac4c74bbc6d96f7c1e66b54f1769b709e36ea7c03279393797c7cecc38ff4013"
SCHEMA_SHA = "24b7f960118facfb26dc0b014fcdfcf45d2fca041bde877eb768ed619e787618"
SOURCE_SHA = "fbc9dd89ee46a6b5e2da89a8b291c93f8b9b92c0feadd43957fdd385abcfa155"
BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
FAR = 8192
SOURCE_PATHS = {"source/producer.py", "source/inputs/PR6719/machine.py",
                "source/inputs/PR6719/counters.py", "source/inputs/PR6719/router.py",
                "inputs/SHAPE-PROOF.md", "inputs/CANONICAL-COUNTER-PROOF.md", "inputs/NOTICE"}
CONTROL_IDS = {"quotient_write_mutant", "product_write_mutant", "workspace_erase_mutant",
               "input_return_mutant", "nondivisible_rejected", "noncanonical_rejected",
               "occupied_origin_rejected", "duplicate_key", "float_token", "boolean_integer"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    need(type(value) is int, "proof integer excludes Boolean")
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def forbidden_number(_):
    raise ValueError("float or nonfinite JSON token")


def decode(data):
    need(len(data) <= 16 * 1024 * 1024, "JSON exceeds16MiB")
    return json.loads(data, object_pairs_hook=unique_pairs,
                      parse_float=forbidden_number, parse_constant=forbidden_number)


def load(path):
    return decode(path.read_bytes())


def authenticate():
    for name, expected in (("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA),
                           ("SOURCE-PINS.json", SOURCE_SHA)):
        need(digest((HERE / name).read_bytes()) == expected, "frozen metadata drift: " + name)
    expected_paths = SOURCE_PATHS | {"primary.py", "oracle.py", "emitter.py",
                                    "CASES.json", "SCHEMA.json", "SOURCE-PINS.json"}
    manifest = load(HERE / "FILES.json")
    need(type(manifest) is dict and set(manifest) == {"schema_version", "files"}, "FILES schema")
    need(integer(manifest["schema_version"]) == 1, "FILES version")
    seen = set()
    for row in manifest["files"]:
        need(type(row) is dict and set(row) == {"path", "sha256"}, "FILES row schema")
        name = row["path"]
        need(type(name) is str and name in expected_paths and name not in seen, "FILES exact path set")
        need(digest((HERE / name).read_bytes()) == row["sha256"], "FILES byte drift: " + name)
        seen.add(name)
    need(seen == expected_paths, "FILES missing required input")
    pins = load(HERE / "SOURCE-PINS.json")
    need(len(pins["sources"]) == 7, "seven source objects required")
    for row in pins["sources"]:
        need(row["local_path"] in SOURCE_PATHS, "source input path")
        need(digest((HERE / row["local_path"]).read_bytes()) == row["sha256"], "source byte drift")


def emit_candidates():
    spec = importlib.util.spec_from_file_location("s8_dense_shared_emitter", HERE / "emitter.py")
    need(spec is not None and spec.loader is not None, "shared emitter loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.emit_tables()


def validate_table(table):
    need(type(table) is dict and set(table) == {"low_types", "tapes", "entry", "instructions"}, "table exact keys")
    need(integer(table["low_types"]) >= 2 and integer(table["tapes"]) == 9, "fixed table types/tapes")
    rows = table["instructions"]
    need(type(rows) is list and 0 < len(rows) <= 20000, "finite instruction list")
    target = lambda value: type(value) is int and 0 <= value < len(rows)
    tape = lambda value: type(value) is int and 0 <= value < 9
    need(target(table["entry"]), "entry target")
    for pc, row in enumerate(rows):
        need(type(row) is list and row, "instruction list")
        op = row[0]
        if op == "branch":
            need(len(row) == 4 and tape(row[1]) and type(row[2]) is list, "branch schema")
            need(all(type(pair) is list and len(pair) == 2 and type(pair[0]) is int
                     and 0 <= pair[0] < 7 and target(pair[1]) for pair in row[2]), "branch pairs")
            need(len({pair[0] for pair in row[2]}) == len(row[2]) and target(row[3]), "branch uniqueness/default")
        elif op in ("write", "move"):
            need(len(row) == 3 and tape(row[1]) and pc + 1 < len(rows), "local action schema")
            need(type(row[2]) is int and (0 <= row[2] < 7 if op == "write" else row[2] in (-1, 1)), "local action value")
        elif op == "goto":
            need(len(row) == 2 and target(row[1]), "goto target")
        else:
            need((op == "halt" and len(row) == 1) or (op == "reject" and len(row) == 2 and type(row[1]) is str), "terminal instruction")


class Rejected(Exception):
    def __init__(self, pc, reason):
        super().__init__(reason)
        self.pc = pc


class DenseTape:
    def __init__(self, head):
        self.origin = 16
        self.cells = [BLANK] * (FAR + 33)
        self.head = head
        self.put(-1, MARK)
        self.put(FAR, UNIT)

    def at(self, position):
        index = position + self.origin
        need(0 <= index < len(self.cells), "dense observer extent exceeded")
        return self.cells[index]

    def put(self, position, symbol):
        index = position + self.origin
        need(0 <= index < len(self.cells), "dense observer extent exceeded")
        self.cells[index] = symbol

    def nonblank(self):
        return [[index - self.origin, symbol] for index, symbol in enumerate(self.cells)
                if symbol != BLANK]


def fixture(case):
    _, a, h, r = case
    tapes = [DenseTape(1 if role < 3 else 0) for role in range(9)]
    for role, value in enumerate((a, h, r)):
        need(type(value) is int and value > 0, "positive raw fixture header")
        tapes[role].put(0, LEFT)
        for bit in range(value.bit_length()):
            tapes[role].put(bit + 1, ONE if (value >> bit) & 1 else ZERO)
        tapes[role].put(value.bit_length() + 1, RIGHT)
    return tapes


def execute(table, tapes):
    pc, steps = table["entry"], 0
    visits = [{tape.head} for tape in tapes]
    rows = table["instructions"]
    while True:
        need(steps < 2000000, "producer step cap exceeded")
        row = rows[pc]
        op = row[0]
        steps += 1
        if op == "halt":
            return steps, visits
        if op == "reject":
            raise Rejected(pc, row[1])
        if op == "goto":
            pc = row[1]
            continue
        role, tape = row[1], tapes[row[1]]
        visits[role].add(tape.head)
        if op == "branch":
            pc = dict(row[2]).get(tape.at(tape.head), row[3])
        elif op == "write":
            tape.put(tape.head, row[2])
            pc += 1
        elif op == "move":
            tape.head += row[2]
            tape.at(tape.head)
            visits[role].add(tape.head)
            pc += 1
        else:
            raise ValueError("unsupported independent dispatch")


def binary_output(tape):
    need(tape.head == 1 and tape.at(0) == LEFT, "output head/LEFT restoration")
    bits, pos = [], 1
    while tape.at(pos) in (ZERO, ONE):
        bits.append(int(tape.at(pos) == ONE))
        pos += 1
        need(pos < FAR, "unterminated output")
    need(tape.at(pos) == RIGHT and bits and bits[-1] == 1, "positive canonical output")
    allowed = {-1, FAR, *range(pos + 1)}
    need(all(position in allowed for position, _ in tape.nonblank()), "extra output backing")
    return sum(bit << index for index, bit in enumerate(bits))


def endpoint(tapes, original_inputs):
    for tape in tapes:
        need(tape.at(-1) == MARK and tape.at(FAR) == UNIT, "guard changed")
    for role in range(3):
        need(tapes[role].head == 1, "input head restoration")
        need(tuple(tapes[role].cells) == original_inputs[role], "input bytes changed")
    outputs = [binary_output(tapes[role]) for role in (3, 4)]
    for role in range(5, 9):
        need(tapes[role].head == 0, "scratch head restoration")
        need(tapes[role].nonblank() == [[-1, MARK], [FAR, UNIT]], "scratch fully blank required")
    return outputs


def run_case(table, case):
    low, a, h, r = case
    need(all(type(value) is int and value > 0 for value in case), "integer positive case")
    need(low == table["low_types"], "case/table low-type binding")
    tapes = fixture(case)
    original = [tuple(tapes[role].cells) for role in range(3)]
    steps, visits = execute(table, tapes)
    outputs = endpoint(tapes, original)
    need(a % (low * h) == 0 and outputs == [a // (low * h), h * r], "actual output values")
    scale = a + h + r + h * r
    space = sum(len(visited) for visited in visits)
    need(steps <= 60 * scale, "actual60 step envelope")
    need(space <= 10 * scale, "actual10 visited envelope")
    state = [{"head": tape.head, "cells": tape.nonblank()} for tape in tapes]
    return {"case": case[:], "outputs": outputs, "steps": steps, "space": space,
            "heads": [tape.head for tape in tapes],
            "visits": [[min(v), max(v), len(v)] for v in visits],
            "endpoint_sha256": digest(canonical(state))}


def expect_value_rejection(function, diagnostic):
    try:
        function()
    except ValueError as error:
        need(diagnostic in str(error), "unintended rejection: " + str(error))
        return True
    raise ValueError("control accepted: " + diagnostic)


def expect_program_reject(table, tapes):
    try:
        execute(table, tapes)
    except Rejected as error:
        need(table["instructions"][error.pc][0] == "reject", "not source REJECT")
        return True
    raise ValueError("invalid fixture did not reach source REJECT")


def changed_output_control(table, role, case):
    mutant = copy.deepcopy(table)
    pc = next(index for index, row in enumerate(mutant["instructions"])
              if row == ["write", role, ONE])
    mutant["instructions"][pc][2] = ZERO
    validate_table(mutant)
    tapes = fixture(case)
    original = [tuple(tapes[index].cells) for index in range(3)]
    execute(mutant, tapes)
    values = endpoint(tapes, original)
    expected = [case[1] // (case[0] * case[2]), case[2] * case[3]]
    need(values[role - 3] == 2 and values[role - 3] != expected[role - 3], "write mutant wrong value")
    return True


def restoration_controls(table):
    outcomes = {}
    for role, symbol, replacement, name, diagnostic in (
            (8, BLANK, LEFT, "workspace_erase_mutant", "scratch fully blank"),
            (0, 1, -1, "input_return_mutant", "input head restoration")):
        mutant = copy.deepcopy(table)
        op = "write" if role == 8 else "move"
        pc = max(index for index, row in enumerate(mutant["instructions"])
                 if row == [op, role, symbol])
        mutant["instructions"][pc][2] = replacement
        validate_table(mutant)
        tapes = fixture([2, 2, 1, 1])
        original = [tuple(tapes[index].cells) for index in range(3)]
        execute(mutant, tapes)
        need(tapes[8].at(0) == LEFT if role == 8 else tapes[0].head == -1,
             "restoration mutant raw witness")
        outcomes[name] = expect_value_rejection(lambda: endpoint(tapes, original), diagnostic)
    return outcomes


def controls(table):
    outcomes = {
        "quotient_write_mutant": changed_output_control(table, 3, [2, 6, 1, 1]),
        "product_write_mutant": changed_output_control(table, 4, [2, 2, 1, 3])}
    outcomes.update(restoration_controls(table))
    outcomes["nondivisible_rejected"] = expect_program_reject(table, fixture([2, 3, 2, 1]))
    noncanonical = fixture([2, 2, 1, 1])
    noncanonical[0].put(3, ZERO)
    noncanonical[0].put(4, RIGHT)
    outcomes["noncanonical_rejected"] = expect_program_reject(table, noncanonical)
    occupied = fixture([2, 2, 1, 1])
    occupied[8].put(0, MARK)
    outcomes["occupied_origin_rejected"] = expect_program_reject(table, occupied)
    outcomes["duplicate_key"] = expect_value_rejection(lambda: decode(b'{"x":1,"x":2}'), "duplicate JSON")
    outcomes["float_token"] = expect_value_rejection(lambda: decode(b'{"x":0.5}'), "float or nonfinite")
    outcomes["boolean_integer"] = expect_value_rejection(lambda: integer(True), "proof integer excludes Boolean")
    need(set(outcomes) == CONTROL_IDS and all(outcomes.values()), "ten executed controls")
    return outcomes


def certificate(cases):
    tables = emit_candidates()
    need(type(tables) is list and [table["low_types"] for table in tables] == cases["low_types"], "four ordered source tables")
    for table in tables:
        validate_table(table)
    lookup = {table["low_types"]: table for table in tables}
    rows = [run_case(lookup[case[0]], case) for case in cases["valid_cases"]]
    outcomes = controls(lookup[2])
    small = cases["small_witness"]
    witness = next(row for row in rows if row["case"] == small["case"])
    need({name: witness[name] for name in small} == small, "actual small witness")
    return {"schema_version": 1, "source_head": cases["source_head"],
            "cases_sha256": CASE_SHA, "source_pins_sha256": SOURCE_SHA,
            "tables": tables, "tables_sha256": digest(canonical(tables)),
            "case_rows": rows, "controls": outcomes, "small_witness": small,
            "bounds": {"steps_per_S_plus_K": 60, "space_per_S_plus_K": 10}}


def validate_certificate(value, cases):
    schema = load(HERE / "SCHEMA.json")
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(integer(value["schema_version"]) == 1, "certificate version")
    need(type(value["tables"]) is list and len(value["tables"]) == 4, "four tables")
    for table in value["tables"]:
        validate_table(table)
    need(type(value["tables_sha256"]) is str and value["tables_sha256"] == digest(canonical(value["tables"])), "tables canonical hash")
    need(type(value["case_rows"]) is list and len(value["case_rows"]) == len(cases["valid_cases"]), "all actual case rows")
    for row in value["case_rows"]:
        need(type(row) is dict and set(row) == set(schema["case_row_keys"]), "case row exact keys")
        for name, length in (("case", 4), ("outputs", 2), ("heads", 9)):
            need(type(row[name]) is list and len(row[name]) == length, "case row vector")
            for item in row[name]:
                integer(item)
        integer(row["steps"])
        integer(row["space"])
        need(type(row["visits"]) is list and len(row["visits"]) == 9, "nine visit triples")
        for triple in row["visits"]:
            need(type(triple) is list and len(triple) == 3, "visit triple shape")
            for item in triple:
                integer(item)
        need(type(row["endpoint_sha256"]) is str, "endpoint digest string")
    need(type(value["controls"]) is dict and set(value["controls"]) == CONTROL_IDS, "control exact keys")
    need(all(type(flag) is bool and flag for flag in value["controls"].values()), "true Boolean controls")
    need(type(value["bounds"]) is dict and set(value["bounds"]) == set(schema["bounds"]), "bounds keys")
    for item in value["bounds"].values():
        integer(item)
    need(type(value["small_witness"]) is dict and set(value["small_witness"]) == set(cases["small_witness"]), "witness keys")
    for name in ("steps", "space"):
        integer(value["small_witness"][name])
    for name in ("case", "outputs"):
        need(type(value["small_witness"][name]) is list, "witness list")
        for item in value["small_witness"][name]:
            integer(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.certificate), "choose emit or retained certificate")
    authenticate()
    cases = load(HERE / "CASES.json")
    result = certificate(cases)
    validate_certificate(result, cases)
    if args.emit:
        args.emit.write_bytes(canonical(result) + b"\n")
    else:
        actual = load(args.certificate or HERE / "ORACLE.json")
        validate_certificate(actual, cases)
        need(canonical(actual) == canonical(result), "whole actual oracle certificate differs")
    print("PASS_FULL_CHILD_SHAPE_DENSE_ORACLE cases261 controls10 full_HALT actual_source no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, Rejected) as error:
        print("FAIL_FULL_CHILD_SHAPE_DENSE_ORACLE: " + str(error), file=sys.stderr)
        raise SystemExit(1)
