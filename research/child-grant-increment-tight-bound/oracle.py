#!/usr/bin/env python3
"""Independent dense-list execution of the authenticated increment microtable."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CASE_SHA = "56065d4fc3a98c411cb068714eebc2c06d330976873093a28791193096b74cba"
SCHEMA_SHA = "ff29b35fef8e469938c6f0c7cbd0b17228e75e46fad6bdbab5e2ca2d262abed7"
SOURCE_SHA = "e08bed306ef62f5f05c5ae22969857c348b508cb0037f5310c01aaf9af145e73"
BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
FAR = 4096
INPUTS = {"producer.py", "machine.py", "counters.py", "SHAPE-PROOF.md",
          "CANONICAL-COUNTER-PROOF.md", "NOTICE"}
CONTROL_IDS = {"wrong_zero_write", "wrong_carry_write", "wrong_return_move",
               "wrong_default_guard", "per_call_18_false", "duplicate_key",
               "float_token", "boolean_integer"}


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
    need(len(data) <= 8 * 1024 * 1024, "JSON exceeds8MiB")
    return json.loads(data, object_pairs_hook=unique_pairs,
                      parse_float=forbidden_number, parse_constant=forbidden_number)


def load(path):
    return decode(path.read_bytes())


def authenticate():
    for name, expected in (("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA),
                           ("SOURCE-PINS.json", SOURCE_SHA)):
        need(digest((HERE / name).read_bytes()) == expected, "frozen metadata drift: " + name)
    expected_paths = {"primary.py", "oracle.py", "emitter.py", "CASES.json", "SCHEMA.json", "SOURCE-PINS.json"}
    expected_paths |= {"inputs/" + name for name in INPUTS}
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
    need(len(pins["sources"]) == 6, "six source objects required")
    for row in pins["sources"]:
        need(row["local_path"] in expected_paths, "source input path")
        need(digest((HERE / row["local_path"]).read_bytes()) == row["sha256"], "source byte drift")


def emit_candidate():
    spec = importlib.util.spec_from_file_location("s7_dense_shared_emitter", HERE / "emitter.py")
    need(spec is not None and spec.loader is not None, "shared emitter loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.emit_table()


def validate_table(table):
    need(type(table) is dict and set(table) == {"schema_version", "tapes", "entry", "stop_pc", "fail_pc", "instructions"}, "table exact keys")
    need(integer(table["schema_version"]) == 1 and integer(table["tapes"]) == 2, "table version/tapes")
    rows = table["instructions"]
    need(type(rows) is list and 0 < len(rows) <= 10000, "finite instruction list")
    target = lambda value: type(value) is int and 0 <= value < len(rows)
    for key in ("entry", "stop_pc", "fail_pc"):
        need(target(table[key]), "table control target")
    for pc, row in enumerate(rows):
        need(type(row) is list and row, "instruction list")
        op = row[0]
        if op == "branch":
            need(len(row) == 4 and integer(row[1]) == 0 and type(row[2]) is list, "branch schema")
            need(all(type(pair) is list and len(pair) == 2 and type(pair[0]) is int
                     and 0 <= pair[0] < 7 and target(pair[1]) for pair in row[2]), "branch pairs")
            need(len({pair[0] for pair in row[2]}) == len(row[2]) and target(row[3]), "branch uniqueness/default")
        elif op in ("write", "move"):
            need(len(row) == 3 and integer(row[1]) == 0 and pc + 1 < len(rows), "local action schema")
            need(type(row[2]) is int and (0 <= row[2] < 7 if op == "write" else row[2] in (-1, 1)), "local action value")
        elif op == "goto":
            need(len(row) == 2 and target(row[1]), "goto target")
        else:
            need((op == "halt" and len(row) == 1) or (op == "reject" and len(row) == 2 and type(row[1]) is str), "terminal instruction")
    need(rows[table["stop_pc"]] == ["halt"] and rows[table["fail_pc"]][0] == "reject", "wrapper boundaries")


class Rejected(Exception):
    def __init__(self, pc, reason):
        super().__init__(reason)
        self.pc = pc


class DenseTape:
    def __init__(self, head=1):
        self.origin = 16
        self.cells = [BLANK] * (FAR + 33)
        self.head = head

    def at(self, position):
        index = position + self.origin
        need(0 <= index < len(self.cells), "dense observer extent exceeded")
        return self.cells[index]

    def put(self, position, symbol):
        index = position + self.origin
        need(0 <= index < len(self.cells), "dense observer extent exceeded")
        self.cells[index] = symbol


def fixture(value, malformed=False):
    active, spectator = DenseTape(), DenseTape(-7)
    active.put(-1, MARK)
    active.put(FAR, UNIT)
    active.put(0, LEFT)
    digits = [] if value == 0 else [(value >> j) & 1 for j in range(value.bit_length())]
    for j, bit in enumerate(digits, 1):
        active.put(j, ONE if bit else ZERO)
    active.put(len(digits) + 1, RIGHT)
    if malformed:
        active.put(1, UNIT)
        active.put(2, RIGHT)
    spectator.put(-11, MARK)
    spectator.put(-7, ZERO)
    spectator.put(5, UNIT)
    return [active, spectator]


def execute(table, tapes):
    pc, steps, visited = table["entry"], 0, {1}
    rows = table["instructions"]
    while pc != table["stop_pc"]:
        need(steps < 100000, "macro step cap exceeded")
        row = rows[pc]
        op = row[0]
        steps += 1
        if op == "branch":
            tape = tapes[row[1]]
            visited.add(tape.head)
            choices = {symbol: target for symbol, target in row[2]}
            pc = choices.get(tape.at(tape.head), row[3])
        elif op == "write":
            tape = tapes[row[1]]
            visited.add(tape.head)
            tape.put(tape.head, row[2])
            pc += 1
        elif op == "move":
            tape = tapes[row[1]]
            visited.add(tape.head)
            tape.head += row[2]
            tape.at(tape.head)
            visited.add(tape.head)
            pc += 1
        elif op == "goto":
            pc = row[1]
        elif op == "reject":
            raise Rejected(pc, row[1])
        else:
            raise ValueError("premature halt or unsupported dispatch")
    return steps, min(visited), max(visited)


def observed_value(tape):
    need(tape.head == 1, "counter head1 required")
    need(tape.at(0) == LEFT, "counter LEFT marker")
    bits, position = [], 1
    while tape.at(position) in (ZERO, ONE):
        bits.append(int(tape.at(position) == ONE))
        position += 1
        need(position < FAR, "unterminated counter")
    need(tape.at(position) == RIGHT and bits and bits[-1] == 1, "positive canonical counter/RIGHT")
    need(tape.at(-1) == MARK and tape.at(FAR) == UNIT, "active sentinels changed")
    permitted = {-1, FAR, *range(position + 1)}
    need(all(symbol == BLANK or index - tape.origin in permitted
             for index, symbol in enumerate(tape.cells)), "unexpected counter backing")
    return sum(bit << j for j, bit in enumerate(bits))


def spectator_snapshot(tapes):
    return tapes[1].head, tuple(tapes[1].cells)


def one_call(table, tapes):
    before = spectator_snapshot(tapes)
    steps, low, high = execute(table, tapes)
    value = observed_value(tapes[0])
    need(spectator_snapshot(tapes) == before, "spectator tape changed")
    return value, steps, tapes[0].head, low, high


def sequential(table, count):
    tapes, rows, cumulative = fixture(0), [], 0
    for expected in range(1, count + 1):
        value, steps, head, low, high = one_call(table, tapes)
        need(value == expected, "sequential increment endpoint")
        cumulative += steps
        need(cumulative <= 15 * expected, "actual finite cumulative15 bound")
        rows.append([value, steps, cumulative, head, low, high])
    return rows


def carries(table, bits_cases):
    rows = []
    for bits in bits_cases:
        integer(bits)
        need(1 <= bits <= 256, "long-carry fixture bound")
        value, steps, head, low, high = one_call(table, fixture((1 << bits) - 1))
        need(value == 1 << bits, "long-carry increment endpoint")
        need(steps == 7 * bits + 11, "actual long-carry step count")
        rows.append([bits, value, steps, head, low, high])
    return rows


def rejected_value(function, diagnostic):
    try:
        function()
    except ValueError as error:
        need(diagnostic in str(error), "unintended rejection: " + str(error))
        return True
    raise ValueError("control accepted: " + diagnostic)


def controls(table):
    rows, entry = table["instructions"], table["entry"]
    need(rows[entry][0] == "branch", "macro entry branch")
    branches = dict(rows[entry][2])
    zero_pc, one_pc = branches[ZERO], branches[ONE]
    need(rows[zero_pc] == ["write", 0, ONE] and rows[one_pc] == ["write", 0, ZERO], "actual mutation sites")
    outcomes = {}
    for label, pc, symbol, start, expected_wrong in (("wrong_zero_write", zero_pc, ZERO, 2, 2),
                                                   ("wrong_carry_write", one_pc, ONE, 1, 3)):
        mutant = copy.deepcopy(table)
        mutant["instructions"][pc][2] = symbol
        validate_table(mutant)
        actual = one_call(mutant, fixture(start))[0]
        need(actual == expected_wrong and actual != start + 1, "semantic write mutant not detected")
        outcomes[label] = True
    mutant = copy.deepcopy(table)
    pc = table["stop_pc"] - 1
    need(rows[pc] == ["move", 0, 1], "last return movement")
    mutant["instructions"][pc][2] = -1
    tapes = fixture(0)
    execute(mutant, tapes)
    need(tapes[0].head == -1, "return mutant raw head")
    outcomes["wrong_return_move"] = rejected_value(lambda: observed_value(tapes[0]), "counter head1")
    outcomes["wrong_default_guard"] = default_guard_control(table, zero_pc)
    steps = one_call(table, fixture(3))[1]
    need(steps == 25 and steps > 18, "actual per-call18 scope control")
    outcomes["per_call_18_false"] = True
    outcomes["duplicate_key"] = rejected_value(lambda: decode(b'{"x":1,"x":2}'), "duplicate JSON")
    outcomes["float_token"] = rejected_value(lambda: decode(b'{"x":0.5}'), "float or nonfinite")
    outcomes["boolean_integer"] = rejected_value(lambda: integer(True), "proof integer excludes Boolean")
    return outcomes


def default_guard_control(table, zero_pc):
    try:
        execute(table, fixture(0, malformed=True))
    except Rejected as error:
        need(error.pc == table["fail_pc"], "wrong baseline guard rejection")
    else:
        raise ValueError("baseline accepted malformed UNIT")
    mutant = copy.deepcopy(table)
    mutant["instructions"][table["entry"]][3] = zero_pc
    validate_table(mutant)
    value = one_call(mutant, fixture(0, malformed=True))[0]
    need(value == 1, "raw default mutant did not accept/rewrite malformed input")
    return True


def certificate(cases):
    table = emit_candidate()
    validate_table(table)
    rows = sequential(table, cases["sequential_from_zero"])
    carry_rows = carries(table, cases["long_carry_bits"])
    outcomes = controls(table)
    need(set(outcomes) == CONTROL_IDS and all(outcomes.values()), "eight actual controls")
    need(rows[3][0] == 4 and rows[3][2] == 60, "actual sharp witness")
    return {"schema_version": 1, "source_head": cases["source_head"],
            "cases_sha256": CASE_SHA, "source_pins_sha256": SOURCE_SHA,
            "table": table, "table_sha256": digest(canonical(table)),
            "sequential_rows": rows, "carry_rows": carry_rows,
            "controls": outcomes,
            "sharp_witness": {"k": 4, "cost": 60, "uniform_coefficient": 15}}


def validate_certificate(value, cases):
    schema = load(HERE / "SCHEMA.json")
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(integer(value["schema_version"]) == 1, "certificate version")
    validate_table(value["table"])
    need(type(value["table_sha256"]) is str and value["table_sha256"] == digest(canonical(value["table"])), "table canonical hash")
    for name, count in (("sequential_rows", cases["sequential_from_zero"]),
                        ("carry_rows", len(cases["long_carry_bits"]))):
        rows = value[name]
        need(type(rows) is list and len(rows) == count, "complete row count: " + name)
        for row in rows:
            need(type(row) is list and len(row) == 6, "six-field actual execution row")
            for item in row:
                integer(item)
    need(type(value["controls"]) is dict and set(value["controls"]) == CONTROL_IDS, "control exact keys")
    need(all(type(flag) is bool and flag for flag in value["controls"].values()), "Boolean executed controls")
    witness = value["sharp_witness"]
    need(type(witness) is dict and set(witness) == {"k", "cost", "uniform_coefficient"}, "sharp witness keys")
    for item in witness.values():
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
    print("PASS_INCREMENT_DENSE_ORACLE sequential1024 carry10 controls8 actual_table no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, Rejected) as error:
        print("FAIL_INCREMENT_DENSE_ORACLE: " + str(error), file=sys.stderr)
        raise SystemExit(1)
