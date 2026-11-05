#!/usr/bin/env python3
"""Sparse-tape execution of the authenticated full nine-tape producer."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    "CASES.json": "ac4c74bbc6d96f7c1e66b54f1769b709e36ea7c03279393797c7cecc38ff4013",
    "SCHEMA.json": "24b7f960118facfb26dc0b014fcdfcf45d2fca041bde877eb768ed619e787618",
    "SOURCE-PINS.json": "fbc9dd89ee46a6b5e2da89a8b291c93f8b9b92c0feadd43957fdd385abcfa155",
}
SOURCE = "3bad39ffd4faf7e8cb1bc5b47769cbb28511f797"
BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
FAR = 8192
SOURCE_PATHS = {
    "source/producer.py", "source/inputs/PR6719/machine.py",
    "source/inputs/PR6719/counters.py", "source/inputs/PR6719/router.py",
    "inputs/SHAPE-PROOF.md", "inputs/CANONICAL-COUNTER-PROOF.md", "inputs/NOTICE",
}
CONTROL_IDS = {
    "quotient_write_mutant", "product_write_mutant", "workspace_erase_mutant",
    "input_return_mutant", "nondivisible_rejected", "noncanonical_rejected",
    "occupied_origin_rejected", "duplicate_key", "float_token", "boolean_integer",
}


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
    need(len(raw) <= 8 * 1024 * 1024, "JSON byte budget")
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_float=bad_number, parse_constant=bad_number)


def load(path):
    return decode(path.read_bytes())


def integer(value, label):
    need(type(value) is int, label + ": proof integer required")
    return value


def proof_integers(value):
    if type(value) is list:
        for item in value:
            proof_integers(item)
    else:
        integer(value, "certificate numeric data")


def hex_digest(value):
    need(type(value) is str and len(value) == 64 and
         all(c in "0123456789abcdef" for c in value), "SHA256 hex string")


def authenticate():
    for name, expected in PINS.items():
        need(digest((HERE / name).read_bytes()) == expected,
             "frozen metadata drift: " + name)
    sources = load(HERE / "SOURCE-PINS.json")
    need(type(sources) is dict and len(sources["sources"]) == 7, "seven source inputs")
    source_names = set()
    for entry in sources["sources"]:
        name = entry["local_path"]
        need(type(name) is str and name in SOURCE_PATHS and
             name not in source_names, "unique exact source path")
        source_names.add(name)
        need(digest((HERE / name).read_bytes()) == entry["sha256"],
             "source byte drift: " + name)
    need(source_names == SOURCE_PATHS, "complete source closure")
    paths = {"primary.py", "oracle.py", "emitter.py", *PINS, *SOURCE_PATHS}
    manifest = load(HERE / "FILES.json")
    need(type(manifest) is dict and set(manifest) == {"schema_version", "files"}, "FILES keys")
    need(integer(manifest["schema_version"], "FILES version") == 1, "FILES version one")
    need(type(manifest["files"]) is list, "FILES row list")
    seen = set()
    for entry in manifest["files"]:
        need(type(entry) is dict and set(entry) == {"path", "sha256"}, "FILES row")
        name = entry["path"]
        need(type(name) is str and name in paths and name not in seen, "FILES exact unique paths")
        seen.add(name)
        need(digest((HERE / name).read_bytes()) == entry["sha256"], "FILES byte drift: " + name)
    need(seen == paths and len(paths) == 13, "FILES thirteen core inputs")
    return load(HERE / "CASES.json"), load(HERE / "SCHEMA.json")


def actual_tables():
    spec = importlib.util.spec_from_file_location("full_producer_emitter", HERE / "emitter.py")
    need(spec is not None and spec.loader is not None, "emitter loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.emit_tables()


def validate_instruction(row, pc, count):
    need(type(row) is list and row and type(row[0]) is str, "instruction row")
    op = row[0]
    arity = {"branch": 4, "write": 3, "move": 3, "goto": 2, "halt": 1, "reject": 2}
    need(op in arity and len(row) == arity[op], "instruction arity")
    if op in ("branch", "write", "move"):
        need(0 <= integer(row[1], "tape index") < 9, "tape index range")
    if op == "branch":
        need(type(row[2]) is list and len(row[2]) <= 7, "finite branch cases")
        seen = set()
        for pair in row[2]:
            need(type(pair) is list and len(pair) == 2, "branch pair")
            symbol, target = pair
            need(0 <= integer(symbol, "branch symbol") < 7 and symbol not in seen,
                 "unique alphabet case")
            need(0 <= integer(target, "branch target") < count, "branch target range")
            seen.add(symbol)
        need(0 <= integer(row[3], "branch default") < count, "default target range")
    elif op == "goto":
        need(0 <= integer(row[1], "goto target") < count, "goto target range")
    elif op == "write":
        need(0 <= integer(row[2], "write symbol") < 7 and pc + 1 < count,
             "write alphabet/successor")
    elif op == "move":
        need(integer(row[2], "move direction") in (-1, 1) and pc + 1 < count,
             "unit move/successor")
    elif op == "reject":
        need(type(row[1]) is str, "reject reason")


def validate_tables(tables, cases, schema):
    need(type(tables) is list and len(tables) == 4, "four emitted tables")
    for table, low in zip(tables, cases["low_types"]):
        need(type(table) is dict and set(table) == set(schema["table_keys"]), "table exact keys")
        need(integer(table["low_types"], "table L") == low, "table fixed L order")
        need(integer(table["tapes"], "table tape count") == 9, "nine physical roles")
        rows = table["instructions"]
        need(type(rows) is list and 1 <= len(rows) <= 16384, "bounded instructions")
        need(0 <= integer(table["entry"], "table entry") < len(rows), "table entry range")
        for pc, row in enumerate(rows):
            validate_instruction(row, pc, len(rows))
        need(sum(row[0] == "halt" for row in rows) == 1, "one success HALT")


def guarded_blank():
    return {-1: MARK, FAR: UNIT}


def packet(value):
    need(integer(value, "fixture positive input") > 0, "positive fixture input")
    cells = guarded_blank()
    cells[0] = LEFT
    for bit in range(value.bit_length()):
        cells[bit + 1] = ONE if value >> bit & 1 else ZERO
    cells[value.bit_length() + 1] = RIGHT
    return cells


def state(case):
    tapes = [packet(value) for value in case[1:]]
    tapes.extend(guarded_blank() for _ in range(6))
    return {"cells": tapes, "heads": [1, 1, 1, 0, 0, 0, 0, 0, 0]}


class ProgramRejected(ValueError):
    def __init__(self, pc, reason):
        super().__init__(reason)
        self.pc = pc


class EndpointMismatch(ValueError):
    pass


def endpoint_need(condition, message):
    if not condition:
        raise EndpointMismatch(message)


def execute(table, machine):
    rows, heads, tapes = table["instructions"], machine["heads"], machine["cells"]
    pc, steps = table["entry"], 0
    visited = [{head} for head in heads]
    while True:
        need(steps < 1000000 and 0 <= pc < len(rows), "producer step/PC budget")
        row = rows[pc]
        op = row[0]
        steps += 1
        if op in ("branch", "write", "move"):
            tape = row[1]
            visited[tape].add(heads[tape])
        if op == "branch":
            pc = dict(row[2]).get(tapes[tape].get(heads[tape], BLANK), row[3])
        elif op == "write":
            if row[2] == BLANK:
                tapes[tape].pop(heads[tape], None)
            else:
                tapes[tape][heads[tape]] = row[2]
            pc += 1
        elif op == "move":
            heads[tape] += row[2]
            visited[tape].add(heads[tape])
            pc += 1
        elif op == "goto":
            pc = row[1]
        elif op == "halt":
            return steps, visited
        elif op == "reject":
            raise ProgramRejected(pc, row[1])
        else:
            raise ValueError("unsupported actual opcode")


def observed_positive(cells):
    value = 0
    for position in range(1, FAR):
        symbol = cells.get(position, BLANK)
        if symbol == RIGHT:
            endpoint_need(position > 1 and cells.get(position - 1) == ONE,
                          "output is not positive canonical binary")
            return value
        endpoint_need(symbol in (ZERO, ONE), "output has invalid body symbol")
        if symbol == ONE:
            value += 1 << (position - 1)
    raise EndpointMismatch("output has no bounded RIGHT")


def endpoint(machine, case):
    low, a_value, h_value, r_value = case
    cells, heads = machine["cells"], machine["heads"]
    for tape, original in enumerate((a_value, h_value, r_value)):
        endpoint_need(heads[tape] == 1 and cells[tape] == packet(original),
                      "input restoration/head mismatch")
    outputs = [observed_positive(cells[tape]) for tape in (3, 4)]
    expected = [a_value // (low * h_value), h_value * r_value]
    for tape, value in zip((3, 4), expected):
        endpoint_need(heads[tape] == 1 and cells[tape] == packet(value),
                      "output quotient/product/marker mismatch")
    endpoint_need(outputs == expected, "output values mismatch")
    for tape in range(5, 9):
        endpoint_need(heads[tape] == 0 and cells[tape] == guarded_blank(),
                      "scratch retirement/head mismatch")
    return outputs


def state_digest(machine):
    rows = [{"head": head, "cells": [[p, v] for p, v in sorted(cells.items())]}
            for head, cells in zip(machine["heads"], machine["cells"])]
    return digest(canonical(rows))


def exact_steps(case):
    low, a_value, h_value, r_value = case
    quotient, product = a_value // (low * h_value), h_value * r_value
    convert = lambda x: 24 * x - 7 * x.bit_count() + 15 * x.bit_length() + 12
    increment = lambda x: 13 * x - 7 * x.bit_count() + 5 * x.bit_length()
    return (sum(convert(x) for x in (a_value, h_value, r_value)) +
            increment(quotient) + increment(product) + 12 * a_value +
            11 * h_value + r_value + 6 * product + 4 * quotient * low +
            2 * quotient + 46)


def run_case(table, case, cases):
    machine = state(case)
    steps, visited = execute(table, machine)
    outputs = endpoint(machine, case)
    span = sum(len(points) for points in visited)
    _, a_value, h_value, r_value = case
    scale = a_value + h_value + r_value + h_value * r_value
    need(steps == exact_steps(case), "actual full-producer exact step formula")
    need(steps <= cases["step_factor_S_plus_K"] * scale, "producer time bound")
    need(span <= cases["space_factor_S_plus_K"] * scale, "producer visited-space bound")
    return {"case": list(case), "outputs": outputs, "steps": steps,
            "space": span, "heads": list(machine["heads"]),
            "visits": [[min(v), max(v), len(v)] for v in visited],
            "endpoint_sha256": state_digest(machine)}


def copied_table(table):
    return decode(canonical(table))


def selected_site(table, wanted, last=False):
    matches = [pc for pc, row in enumerate(table["instructions"]) if row == wanted]
    need(bool(matches), "actual mutation site missing")
    return matches[-1] if last else matches[0]


def endpoint_failure(table, case, word):
    machine = state(case)
    execute(table, machine)
    try:
        endpoint(machine, case)
    except EndpointMismatch as error:
        need(word in str(error), "unintended semantic control diagnostic")
        return True
    raise ValueError("semantic mutant was accepted")


def rejected(table, machine, reason):
    try:
        execute(table, machine)
    except ProgramRejected as error:
        need(table["instructions"][error.pc] == ["reject", reason] and
             str(error) == reason, "unintended source rejection diagnostic")
        return True
    raise ValueError("raw malformed fixture was accepted")


def parser_failure(function, word):
    try:
        function()
    except ValueError as error:
        need(word in str(error), "unintended parser control diagnostic")
        return True
    raise ValueError("parser mutation was accepted")


def semantic_controls(table):
    q_bad, p_bad, work_bad, input_bad = [copied_table(table) for _ in range(4)]
    for mutant, tape in ((q_bad, 3), (p_bad, 4)):
        index = selected_site(mutant, ["write", tape, ONE])
        mutant["instructions"][index][2] = ZERO
    index = selected_site(work_bad, ["write", 8, BLANK], last=True)
    work_bad["instructions"][index][2] = LEFT
    index = selected_site(input_bad, ["move", 0, 1], last=True)
    input_bad["instructions"][index][2] = -1
    return {"quotient_write_mutant": endpoint_failure(q_bad, [2, 6, 1, 1], "output"),
            "product_write_mutant": endpoint_failure(p_bad, [2, 2, 1, 3], "output"),
            "workspace_erase_mutant": endpoint_failure(work_bad, [2, 2, 1, 1], "scratch"),
            "input_return_mutant": endpoint_failure(input_bad, [2, 2, 1, 1], "input")}


def controls(table):
    result = semantic_controls(table)
    source_reason = "positive canonical inputs, exact L*H divisor, blank owned work"
    counter_reason = "positive canonical binary extent and empty conversion workspace"
    noncanonical = state([2, 2, 1, 1])
    noncanonical["cells"][0][3] = ZERO
    noncanonical["cells"][0][4] = RIGHT
    occupied = state([2, 2, 1, 1])
    occupied["cells"][8][0] = MARK
    result["nondivisible_rejected"] = rejected(table, state([2, 3, 2, 1]), source_reason)
    result["noncanonical_rejected"] = rejected(table, noncanonical, counter_reason)
    result["occupied_origin_rejected"] = rejected(table, occupied, source_reason)
    result["duplicate_key"] = parser_failure(lambda: decode(b'{"x":1,"x":2}'), "duplicate")
    result["float_token"] = parser_failure(lambda: decode(b'{"x":1.0}'), "float")
    result["boolean_integer"] = parser_failure(lambda: integer(True, "control"), "proof integer")
    need(set(result) == CONTROL_IDS, "complete ten controls")
    return result


def certificate(cases, schema):
    need(cases["source_head"] == SOURCE and cases["low_types"] == [2, 3, 4, 7],
         "frozen source/template domain")
    need(cases["far_guard"] == FAR and len(cases["valid_cases"]) == 261, "frozen cases")
    tables = actual_tables()
    validate_tables(tables, cases, schema)
    lookup = {table["low_types"]: table for table in tables}
    rows = [run_case(lookup[case[0]], case, cases) for case in cases["valid_cases"]]
    witness = {key: rows[0][key] for key in ("case", "outputs", "steps", "space")}
    need(witness == cases["small_witness"], "actual small witness")
    return {"schema_version": 1, "source_head": SOURCE,
            "cases_sha256": PINS["CASES.json"], "source_pins_sha256": PINS["SOURCE-PINS.json"],
            "tables": tables, "tables_sha256": digest(canonical(tables)),
            "case_rows": rows, "controls": controls(lookup[2]),
            "small_witness": witness, "bounds": dict(schema["bounds"])}


def validate_case_row(row, case, schema):
    need(type(row) is dict and set(row) == set(schema["case_row_keys"]), "case row exact keys")
    need(type(row["case"]) is list and len(row["case"]) == 4, "case input tuple")
    proof_integers(row["case"])
    need(row["case"] == case, "actual case order/domain")
    need(type(row["outputs"]) is list and len(row["outputs"]) == 2, "two output values")
    proof_integers(row["outputs"])
    need(integer(row["steps"], "actual steps") > 0, "positive step count")
    need(integer(row["space"], "actual space") > 0, "positive visited count")
    need(type(row["heads"]) is list and len(row["heads"]) == 9, "nine endpoint heads")
    proof_integers(row["heads"])
    need(type(row["visits"]) is list and len(row["visits"]) == 9, "nine visited sets")
    for visit in row["visits"]:
        need(type(visit) is list and len(visit) == 3, "visit triple")
        proof_integers(visit)
        need(visit[0] <= visit[1] and visit[2] > 0, "visit range/count")
    hex_digest(row["endpoint_sha256"])


def validate_certificate(value, cases, schema):
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(integer(value["schema_version"], "certificate version") == 1, "certificate version one")
    need(type(value["source_head"]) is str and value["source_head"] == SOURCE, "certificate source")
    for key in ("cases_sha256", "source_pins_sha256", "tables_sha256"):
        hex_digest(value[key])
    validate_tables(value["tables"], cases, schema)
    need(value["tables_sha256"] == digest(canonical(value["tables"])), "actual table digest")
    rows = value["case_rows"]
    need(type(rows) is list and len(rows) == 261, "certificate 261 cases")
    for row, case in zip(rows, cases["valid_cases"]):
        validate_case_row(row, case, schema)
    outcomes = value["controls"]
    need(type(outcomes) is dict and set(outcomes) == CONTROL_IDS, "certificate control keys")
    need(all(type(x) is bool and x for x in outcomes.values()), "true Boolean controls")
    small = value["small_witness"]
    need(type(small) is dict and set(small) == {"case", "outputs", "steps", "space"}, "small witness keys")
    for item in small.values():
        proof_integers(item)
    need(canonical(small) == canonical(cases["small_witness"]), "small witness values")
    bounds = value["bounds"]
    need(type(bounds) is dict and set(bounds) == set(schema["bounds"]), "bounds exact keys")
    for item in bounds.values():
        integer(item, "bound coefficient")
    need(bounds == schema["bounds"], "bound coefficients")


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
    print("PASS_FULL_PRODUCER_SPARSE tables4 cases261 controls10 bounds60_10 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_FULL_PRODUCER_SPARSE: " + str(error), file=sys.stderr)
        raise SystemExit(1)
