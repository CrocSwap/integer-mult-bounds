#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Execute the new carry-two tables against a separate coordinate oracle."""

import copy
import hashlib
import itertools
import json
import random
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, expected):
    require(hashlib.sha256(raw).hexdigest() == expected, "source SHA256 mismatch")


def source_module(name, path):
    """Execute the specified source bytes, bypassing any stale bytecode cache."""
    require(name not in sys.modules, "refuse preloaded source module " + name)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def load():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            authenticate((ROOT / row["path"]).read_bytes(), row["sha256"])
    base = ROOT / "research/fixed-tape-unit-carry/predecessor"
    modules = {}
    for name in ("machine", "counters", "shear", "independent_check"):
        modules[name] = source_module(name, base / (name + ".py"))
    modules["controller"] = source_module(
        "carry_two_controller", HERE / "controller.py"
    )
    return modules


def serialize(program):
    return json.loads(
        json.dumps(
            {
                "tapes": program.tapes,
                "entry": program.entry,
                "instructions": program.instructions,
            }
        )
    )


def oracle(shape, bits, direction):
    """Gather each output preimage directly, without split traversal or counters."""
    _, q, g, s = shape
    answer = []
    for destination in range(len(bits)):
        rest, z = divmod(destination, s)
        rest, y = divmod(rest, q)
        rest, gap = divmod(rest, g)
        prefix, x = divmod(rest, q)
        old_y = (y - direction * (x + 2)) % q
        source = (((prefix * q + x) * g + gap) * q + old_y) * s + z
        answer.append(bits[source])
    return answer


def exact_steps(shape):
    p, q, g, s = shape
    v = p * q * q * g * s
    conversion = sum(
        24 * n - 7 * n.bit_count() + 15 * n.bit_length() + 12 for n in shape
    )
    return (
        conversion
        + 36 * v
        + 20 * p * q * q * g
        + 28 * p * q * g
        + 62 * p * q
        + 27 * p
        + 13 * q
        + g
        + s
        + 127
        + 13 * (q == 1)
    )


def exact_span(shape):
    p, q, g, s = shape
    lengths = [n.bit_length() for n in shape]
    return (
        3 * p * q * q * g * s + p + g + s + 2 * q + max(q, *lengths) + sum(lengths) + 28
    )


def check_case(dense, table, shape, bits, direction, origins=None):
    bank = dense.fixtures(shape, bits, origins)
    result = dense.execute(table, bank, 504 * len(bits))
    for tape in dense.INPUTS:
        require(result["tapes"][tape].snapshot() == bank[tape][0], "input contents")
        require(result["tapes"][tape].head == bank[tape][1], "input head return")
    answer = oracle(shape, bits, direction)
    expected, head = dense.marked(
        [dense.ONE if bit else dense.ZERO for bit in answer], bank[1][1]
    )
    require(result["tapes"][1].snapshot() == expected, "coordinate endpoint")
    require(result["tapes"][1].head == head, "output head return")
    for tape in dense.WORK:
        require(not result["tapes"][tape].snapshot(), "scratch erasure")
        require(result["tapes"][tape].head == bank[tape][1], "scratch head return")
    require(result["steps"] == exact_steps(shape), "exact transition ledger")
    require(
        sum(t.high - t.low + 1 for t in result["tapes"]) == exact_span(shape),
        "exact visited-span ledger",
    )
    require(exact_span(shape) <= 41 * len(bits), "visited-span majorant")
    return result, answer


def fixtures():
    rng = random.Random(2829)
    shapes = set(itertools.product((1, 2), range(1, 10), (1, 2), (1, 2)))
    shapes.update((1, q, 1, 1) for q in (15, 16, 31))
    for axis in (0, 2, 3):
        for n in (15, 16, 31, 32, 63, 64):
            shape = [1, 1, 1, 1]
            shape[axis] = n
            shapes.add(tuple(shape))
    cases = []
    for shape in sorted(shapes):
        p, q, g, s = shape
        cases.append((shape, [rng.randrange(2) for _ in range(p * q * q * g * s)]))
    for bits in itertools.product((0, 1), repeat=4):
        cases.append(((1, 2, 1, 1), list(bits)))
    for shape in ((1, 3, 1, 1), (2, 3, 2, 1)):
        p, q, g, s = shape
        volume = p * q * q * g * s
        for column in range(volume):
            cases.append((shape, [int(i == column) for i in range(volume)]))
    return cases, len(shapes)


def sparse_check(machine, program, dense, shape, bits, origins, reference):
    bank = dense.fixtures(shape, bits, origins)
    executor = machine.Machine(
        program, [machine.Tape(cells, head) for cells, head in bank]
    )
    executor.run(max_steps=504 * len(bits))
    require(executor.steps == reference["steps"], "sparse/dense transition count")
    for left, right in zip(executor.tapes, reference["tapes"], strict=True):
        require(
            left.cells == right.snapshot() and left.head == right.head,
            "sparse/dense entire bank",
        )


def reject_case(dense, table, shape, bits, direction, expected):
    try:
        check_case(dense, table, shape, bits, direction)
    except ValueError as error:
        require(expected in str(error), "wrong rejection: " + str(error))
    else:
        raise ValueError("control was accepted: " + expected)


def physical_controls(dense, table, shape, bits):
    mutant = copy.deepcopy(table)
    sites = [
        i for i, row in enumerate(mutant["instructions"]) if row == ["write", 11, 0]
    ]
    require(len(sites) >= 4, "four transfer sites")
    mutant["instructions"][sites[1]] = ["goto", sites[1] + 7]
    reject_case(dense, mutant, shape, bits, 1, "coordinate endpoint")
    mutant = copy.deepcopy(table)
    for row in mutant["instructions"]:
        if row[0] == "goto":
            row[1] += 2
        elif row[0] == "branch":
            row[3] += 2
            for pair in row[2]:
                pair[1] += 2
    mutant["instructions"] = [["move", 13, 1], ["move", 13, -1]] + mutant[
        "instructions"
    ]
    reject_case(dense, mutant, shape, bits, 1, "exact transition ledger")
    bank = dense.fixtures(shape, bits)
    cells, _ = bank[5]
    cells[max(cells) - 1] = dense.ZERO
    try:
        dense.execute(table, bank, 504 * len(bits))
    except ValueError as error:
        require("table rejected" in str(error), "canonical descriptor rejection")
    else:
        raise ValueError("noncanonical Q descriptor accepted")
    return [
        "missing second carry transfer",
        "unbilled endpoint-preserving moves",
        "noncanonical Q descriptor",
    ]


def controls(modules, tables):
    dense = modules["independent_check"]
    shape = (2, 3, 2, 1)
    bits = [int(i == 2) for i in range(36)]
    reject_case(dense, tables["inverse"], shape, bits, 1, "coordinate endpoint")
    old = serialize(modules["shear"].build_program())
    reject_case(dense, old, shape, bits, 1, "coordinate endpoint")
    mutant = copy.deepcopy(tables["forward"])
    site = next(
        i for i, row in enumerate(mutant["instructions"]) if row == ["move", 13, 1]
    )
    mutant["instructions"][site][2] = 2
    reject_case(dense, mutant, shape, bits, 1, "unit head movement")
    mutant = copy.deepcopy(tables["forward"])
    site = max(
        i for i, row in enumerate(mutant["instructions"]) if row == ["write", 13, 0]
    )
    mutant["instructions"][site][2] = 1
    reject_case(dense, mutant, shape, bits, 1, "scratch erasure")
    mutant = copy.deepcopy(tables["forward"])
    for row in mutant["instructions"]:
        if row == ["write", 1, 4]:
            row[2] = 3
    reject_case(dense, mutant, shape, bits, 1, "coordinate endpoint")
    for bad in (None, 0, 1, "false"):
        try:
            modules["controller"].build_program(
                (modules["shear"], modules["machine"], modules["counters"]), bad
            )
        except ValueError:
            pass
        else:
            raise ValueError("non-Boolean direction accepted")
    try:
        authenticate(b"changed source", hashlib.sha256(b"source").hexdigest())
    except ValueError:
        pass
    else:
        raise ValueError("changed source accepted")
    return [
        "wrong direction",
        "zero-carry endpoint",
        "nonlocal move",
        "retained scratch",
        "changed payload",
        "None direction",
        "integer-zero direction",
        "integer-one direction",
        "string direction",
        "source hash corruption",
    ] + physical_controls(dense, tables["forward"], shape, bits)


def run(modules, programs, tables):
    cases, shape_count = fixtures()
    dense = modules["independent_check"]
    total_steps = sparse_cases = roundtrips = payload_bits = 0
    for index, (shape, bits) in enumerate(cases):
        origins = [(17 * i - 3 * index) % 43 - 21 for i in range(14)]
        for name, direction in (("forward", 1), ("inverse", -1)):
            result, answer = check_case(
                dense, tables[name], shape, bits, direction, origins
            )
            total_steps += result["steps"]
            payload_bits += len(bits)
            if sparse_cases < 18:
                sparse_check(
                    modules["machine"],
                    programs[name],
                    dense,
                    shape,
                    bits,
                    origins,
                    result,
                )
                sparse_cases += 1
            if direction == 1 and shape[1] > 2 and roundtrips < 12:
                _, restored = check_case(
                    dense, tables["inverse"], shape, answer, -1, origins
                )
                require(restored == bits, "physical inverse round trip")
                roundtrips += 1
    return {
        "directional_executions": 2 * len(cases),
        "shapes": shape_count,
        "sparse_cases": sparse_cases,
        "roundtrips": roundtrips,
        "payload_bits": payload_bits,
        "total_transitions": total_steps,
        "controls": controls(modules, tables),
    }


def main():
    modules = load()
    compiler = modules["controller"]
    libraries = (modules["shear"], modules["machine"], modules["counters"])
    programs = {
        name: compiler.build_program(libraries, inverse)
        for name, inverse in (("forward", False), ("inverse", True))
    }
    tables = {name: serialize(program) for name, program in programs.items()}
    for table in tables.values():
        require(
            table["tapes"] == 14 and len(table["instructions"]) == 598,
            "fixed table size",
        )
        require(
            all(
                row[1] not in modules["independent_check"].INPUTS
                for row in table["instructions"]
                if row[0] == "write"
            ),
            "static input immutability",
        )
    result = run(modules, programs, tables)
    result["table_sha256"] = {
        name: hashlib.sha256(json.dumps(table, sort_keys=True).encode()).hexdigest()
        for name, table in tables.items()
    }
    result["package_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(HERE.iterdir())
        if path.is_file()
    }
    print("PASS_CARRY_TWO_FOURTEEN_TAPES")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
