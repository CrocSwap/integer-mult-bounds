#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only independent replay of the fixed ordered-shear transition tables.

This file imports neither the producer nor its machine/counter implementation.
The dense interpreter executes only TABLE.json; the coordinate oracle knows no
transition-table labels.  The predecessor is separately byte-authenticated and
is used only as an additional endpoint comparison, never as the oracle.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
SOURCE_PATH = "research/selected-bit-stream-routes/qadic_streams.py"
BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK = range(7)
INPUTS = (0, 4, 5, 6, 7)
WORK = (2, 3, 8, 9, 10, 11, 12, 13)
TAPES = 14


class CheckFailure(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def integer(value):
    return type(value) is int


def validate_program(program):
    require(type(program) is dict and set(program) == {"tapes", "entry", "instructions"},
            "exact program schema")
    require(integer(program["tapes"]) and program["tapes"] == TAPES, "fourteen physical tapes")
    code = program["instructions"]
    require(type(code) is list and len(code) > 0, "nonempty finite instruction list")
    target = lambda pc: integer(pc) and 0 <= pc < len(code)
    tape = lambda i: integer(i) and 0 <= i < TAPES
    symbol = lambda s: integer(s) and 0 <= s < 7
    require(target(program["entry"]), "finite entry")
    for pc, row in enumerate(code):
        require(type(row) is list and len(row) > 0, "instruction array")
        op = row[0]
        if op == "branch":
            require(len(row) == 4 and tape(row[1]) and type(row[2]) is list and target(row[3]),
                    "local branch schema")
            seen = set()
            for pair in row[2]:
                require(type(pair) is list and len(pair) == 2 and symbol(pair[0]) and target(pair[1]),
                        "finite branch pair")
                require(pair[0] not in seen, "unique branch symbol")
                seen.add(pair[0])
        elif op == "write":
            require(len(row) == 3 and tape(row[1]) and symbol(row[2]) and target(pc + 1),
                    "single-cell write")
        elif op == "move":
            require(len(row) == 3 and tape(row[1]) and integer(row[2]) and row[2] in (-1, 1)
                    and target(pc + 1), "unit head movement")
        elif op == "goto":
            require(len(row) == 2 and target(row[1]), "finite jump")
        elif op == "halt":
            require(len(row) == 1, "halt schema")
        elif op == "reject":
            require(len(row) == 2 and type(row[1]) is str, "finite reject schema")
        else:
            raise CheckFailure("unknown finite instruction")


class DenseTape:
    """A list-backed bilateral tape; absolute positions are simulator data only."""
    def __init__(self, cells, head):
        self.base = min(cells, default=head)
        last = max(cells, default=head)
        self.cells = [BLANK] * (last - self.base + 1)
        for position, value in cells.items():
            self.cells[position - self.base] = value
        self.head = head
        self.low = self.high = head

    def read(self):
        index = self.head - self.base
        return self.cells[index] if 0 <= index < len(self.cells) else BLANK

    def write(self, value):
        index = self.head - self.base
        if index < 0:
            self.cells[:0] = [BLANK] * -index
            self.base = self.head
            index = 0
        elif index >= len(self.cells):
            self.cells.extend([BLANK] * (index - len(self.cells) + 1))
        self.cells[index] = value

    def move(self, delta):
        self.head += delta
        self.low = min(self.low, self.head)
        self.high = max(self.high, self.head)

    def snapshot(self):
        return {self.base + i: value for i, value in enumerate(self.cells) if value != BLANK}


def execute(program, fixtures, max_steps, trace=False):
    """Execute each branch/write/move/goto/halt as one charged transition."""
    validate_program(program)
    tapes = [DenseTape(cells, head) for cells, head in fixtures]
    require(len(tapes) == TAPES, "complete physical bank")
    code, pc = program["instructions"], program["entry"]
    steps = reads = writes = moves = 0
    support = sum(len(t.snapshot()) for t in tapes)
    peak_support = support
    visited = set()
    history = [] if trace else None
    while True:
        require(steps < max_steps, "independent execution limit")
        row = code[pc]
        steps += 1
        visited.add(pc)
        if history is not None:
            history.append(pc)
        op = row[0]
        if op == "halt":
            break
        if op == "reject":
            raise CheckFailure("table rejected: " + row[1])
        if op == "goto":
            pc = row[1]
            continue
        tape = tapes[row[1]]
        if op == "branch":
            value = tape.read()
            reads += 1
            next_pc = row[3]
            for symbol, destination in row[2]:
                if symbol == value:
                    next_pc = destination
                    break
            pc = next_pc
            continue
        if op == "write":
            old = tape.read()
            tape.write(row[2])
            support += int(row[2] != BLANK) - int(old != BLANK)
            peak_support = max(peak_support, support)
            writes += 1
        else:
            tape.move(row[2])
            moves += 1
        pc += 1
    return {"tapes": tapes, "steps": steps, "reads": reads, "writes": writes,
            "moves": moves, "peak_nonblank": peak_support, "visited": visited,
            "history": history}


def marked(values, origin):
    return {origin: LEFT, **{origin + i + 1: value for i, value in enumerate(values)},
            origin + len(values) + 1: RIGHT}, origin + 1


def fixtures(shape, payload, origins=None):
    require(len(shape) == 4 and all(integer(x) and x > 0 for x in shape), "positive shape")
    p, q, g, s = shape
    require(len(payload) == p * q * g * q * s and all(type(b) is int and b in (0, 1) for b in payload),
            "Boolean payload of full volume")
    origins = [0] * TAPES if origins is None else list(origins)
    require(len(origins) == TAPES and all(integer(x) for x in origins), "physical origins")
    bank = [({}, origin) for origin in origins]
    bank[0] = marked([ONE if b else ZERO for b in payload], origins[0])
    for tape, value in zip((4, 5, 6, 7), shape):
        bank[tape] = marked([ONE if (value >> j) & 1 else ZERO for j in range(value.bit_length())],
                            origins[tape])
    return bank


def oracle(shape, payload, inverse=False):
    """Scatter individual coordinates, independently of the split/merge algorithm."""
    p, q, g, s = shape
    result = [None] * len(payload)
    delta = -1 if inverse else 1
    for prefix, x, gap, y, suffix in itertools.product(range(p), range(q), range(g), range(q), range(s)):
        source = ((((prefix * q + x) * g + gap) * q + y) * s + suffix)
        destination = ((((prefix * q + x) * g + gap) * q + (y + delta * x) % q) * s + suffix)
        require(result[destination] is None, "oracle permutation is injective")
        result[destination] = payload[source]
    require(all(b is not None for b in result), "oracle permutation is onto")
    return result


def check_case(program, shape, payload, inverse=False, origins=None, trace=False, max_steps=None):
    bank = fixtures(shape, payload, origins)
    expected = oracle(shape, payload, inverse)
    # This guard is an experimental stopping rule, not the all-size proof.
    cap = 10000 * (len(payload) + 1) if max_steps is None else max_steps
    result = execute(program, bank, cap, trace=trace)
    tapes = result["tapes"]
    for i in INPUTS:
        require(tapes[i].snapshot() == bank[i][0], "source/descriptor preservation on tape " + str(i))
        require(tapes[i].head == bank[i][1], "source/descriptor head return on tape " + str(i))
    output_origin = bank[1][1]
    output_cells, output_head = marked([ONE if b else ZERO for b in expected], output_origin)
    require(tapes[1].snapshot() == output_cells, "ordered-shear output differs from coordinate oracle")
    require(tapes[1].head == output_head, "output head return")
    for i in WORK:
        require(not tapes[i].snapshot(), "scratch must be wholly blank on tape " + str(i))
        require(tapes[i].head == bank[i][1], "scratch head return on tape " + str(i))
    p, q, g, s = shape
    volume = len(payload)
    setup = sum(24 * n - 7 * n.bit_count() + 15 * n.bit_length() + 12 for n in shape)
    expected_steps = (setup + 36 * volume + 20 * p * q * q * g + 28 * p * q * g
                      + 50 * p * q + 19 * p + 7 * q + g + s + 104)
    require(result["steps"] == expected_steps, "exact transition ledger")
    require(result["steps"] <= 442 * volume, "universal transition bound on fixture")
    span = sum(tape.high - tape.low + 1 for tape in tapes)
    expected_span = (3 * volume + p + g + s + 2 * q + max(n.bit_length() for n in shape)
                     + sum(n.bit_length() for n in shape) + 28)
    require(span == expected_span, "exact visited-cell span ledger")
    require(span <= 41 * volume, "universal visited-cell bound on fixture")
    result["visited_cell_span"] = span
    return result


def authenticate(raw, record):
    require(hashlib.sha256(raw).hexdigest() == record["sha256"], "predecessor SHA256 mismatch")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(blob == record["git_blob"], "predecessor Git blob mismatch")


def predecessor(sources_path):
    manifest = json.loads(sources_path.read_text())
    matches = [row for row in manifest["files"] if row["path"] == SOURCE_PATH and row["usage"] == "input"]
    require(len(matches) == 1, "one exact live predecessor source pin")
    path = HERE.parents[1] / SOURCE_PATH
    raw = path.read_bytes()
    authenticate(raw, matches[0])
    name = "_ordered_shear_authenticated_predecessor"
    require(name not in sys.modules, "fresh predecessor module name")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    try:
        # Compile the bytes just authenticated, avoiding any stale .pyc cache.
        exec(compile(raw, str(path), "exec"), module.__dict__)
    finally:
        del sys.modules[name]
    return module, raw, matches[0]


def pattern(size, seed):
    value = seed & 0xFFFFFFFF
    bits = []
    for _ in range(size):
        value = (1664525 * value + 1013904223) & 0xFFFFFFFF
        bits.append((value >> 30) & 1)
    return bits


def cases():
    # Exhaust every Boolean payload on the smallest nontrivial Q=2 rectangle.
    for mask in range(16):
        yield (1, 2, 1, 1), [(mask >> j) & 1 for j in range(4)], False
    # One-hot bases distinguish every moved coordinate in several spectator layouts.
    for shape in ((1, 3, 1, 1), (2, 3, 1, 1), (1, 2, 3, 2)):
        p, q, g, s = shape
        volume = p * q * g * q * s
        for position in range(volume):
            yield shape, [int(j == position) for j in range(volume)], False
    shapes = ((1, 1, 1, 1), (3, 1, 5, 2), (2, 3, 2, 3), (2, 5, 3, 2),
              (1, 8, 1, 3), (2, 7, 1, 1), (1, 17, 1, 2), (1, 31, 1, 1),
              (128, 1, 1, 1), (1, 1, 128, 1), (1, 1, 1, 128),
              (1024, 1, 1, 1), (1, 1, 1024, 1), (1, 1, 1, 1024), (1, 32, 1, 1))
    for i, shape in enumerate(shapes):
        p, q, g, s = shape
        yield shape, pattern(p * q * g * q * s, 57 + i), True


def must_detect(action, label):
    try:
        action()
    except (CheckFailure, KeyError, TypeError, IndexError) as exc:
        return {"name": label, "detected": True, "reason": str(exc)}
    raise CheckFailure("negative control accepted: " + label)


def mutation_controls(table, raw, source_record):
    shape = (2, 3, 2, 2)
    volume = 72
    payload = pattern(volume, 703)
    baseline = check_case(table["forward"], shape, payload, trace=True)
    code = table["forward"]["instructions"]
    used = baseline["history"]
    controls = []

    def mutate_one(pc, replacement, label):
        modified = json.loads(json.dumps(table["forward"]))
        modified["instructions"][pc] = replacement
        outcome = must_detect(lambda: check_case(modified, shape, payload, max_steps=4 * baseline["steps"]), label)
        outcome["instruction"] = pc
        return outcome

    pc = next(pc for pc in used if code[pc][:2] == ["write", 1] and code[pc][2] in (ZERO, ONE))
    controls.append(mutate_one(pc, ["write", 1, ONE if code[pc][2] == ZERO else ZERO], "payload-bit-corruption"))
    pc = next(pc for pc in reversed(used) if code[pc][0] == "write" and code[pc][1] in WORK
              and code[pc][2] == BLANK)
    controls.append(mutate_one(pc, ["goto", pc + 1], "omitted-scratch-erasure"))
    pc = next(pc for pc in reversed(used) if code[pc] == ["move", 0, -1])
    controls.append(mutate_one(pc, ["goto", pc + 1], "omitted-source-head-reset-move"))
    controls.append(must_detect(lambda: check_case(table["inverse"], shape, payload), "reversed-shear-orientation"))
    pc = next(pc for pc in used if code[pc][0] == "move")
    controls.append(mutate_one(pc, ["move", code[pc][1], 2], "nonlocal-two-cell-movement"))
    controls.append(must_detect(lambda: authenticate(raw + b"\n", source_record), "unauthenticated-predecessor-bytes"))
    return controls


def run_checks(table_path=None, sources_path=None):
    table_path = HERE / "TABLE.json" if table_path is None else Path(table_path)
    sources_path = HERE / "SOURCES.json" if sources_path is None else Path(sources_path)
    table_raw = table_path.read_bytes()
    table = json.loads(table_raw)
    require(set(table) == {"forward", "inverse"}, "exact forward/inverse table bank")
    for program in table.values():
        validate_program(program)
    legacy, raw, source_record = predecessor(sources_path)
    count = comparisons = translated = total_steps = 0
    coverage = {"forward": set(), "inverse": set()}
    max_steps_ratio = (0, 1)
    max_support_ratio = (0, 1)
    for index, (shape, payload, use_translation) in enumerate(cases()):
        origins = [(i * 11 - 31) * (-1 if i % 2 else 1) for i in range(TAPES)] if use_translation else None
        for inverse, direction in ((False, "forward"), (True, "inverse")):
            result = check_case(table[direction], shape, payload, inverse, origins)
            count += 1
            translated += int(use_translation)
            total_steps += result["steps"]
            coverage[direction].update(result["visited"])
            volume = len(payload)
            if result["steps"] * max_steps_ratio[1] > max_steps_ratio[0] * volume:
                max_steps_ratio = result["steps"], volume
            if result["peak_nonblank"] * max_support_ratio[1] > max_support_ratio[0] * volume:
                max_support_ratio = result["peak_nonblank"], volume
            if use_translation or index < 2:
                p, q, g, s = shape
                meter = legacy.Meter()
                source = legacy.Tape(meter, payload)
                output = legacy.add_high(source, q, -1 if inverse else 1, lambda _: 0, p, g, s)
                require(output.bits == oracle(shape, payload, inverse), "authenticated predecessor endpoint mismatch")
                require(source.bits == payload, "predecessor source preservation")
                require(meter.ordinary == [], "ordered shear must not invoke ordinary interchange oracle")
                comparisons += 1
        if use_translation:
            image = oracle(shape, payload)
            check_case(table["inverse"], shape, image, True, origins)
            require(oracle(shape, image, True) == payload, "forward/inverse composition")
    controls = mutation_controls(table, raw, source_record)
    return {"schema_version": 1, "status": "pass", "table_sha256": hashlib.sha256(table_raw).hexdigest(),
            "source_sha256": source_record["sha256"], "physical_tapes": TAPES,
            "cases_both_directions": count, "translated_origin_cases": translated,
            "roundtrip_cases": sum(1 for _, _, translated in cases() if translated),
            "predecessor_endpoint_comparisons": comparisons, "total_transitions": total_steps,
            "max_observed_steps_per_payload_bit": list(max_steps_ratio),
            "max_observed_nonblank_per_payload_bit": list(max_support_ratio),
            "executed_instruction_counts": {key: len(value) for key, value in coverage.items()},
            "program_instruction_counts": {key: len(value["instructions"]) for key, value in table.items()},
            "exact_transition_and_visited_span_ledgers": "checked on every successful execution",
            "negative_controls": controls,
            "scope": "finite physical executions; universal linear bounds require PROOF.md"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=HERE / "TABLE.json")
    parser.add_argument("--sources", type=Path, default=HERE / "SOURCES.json")
    parser.add_argument("--result", type=Path, default=HERE / "INDEPENDENT-RESULT.json")
    parser.add_argument("--write", action="store_true", help="write the deterministic INDEPENDENT-RESULT.json receipt")
    args = parser.parse_args()
    result = run_checks(args.table, args.sources)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.result.write_text(text)
    else:
        require(args.result.read_bytes() == text.encode("utf-8"), "independent receipt differs from exact replay")
    print(text, end="")


if __name__ == "__main__":
    main()
