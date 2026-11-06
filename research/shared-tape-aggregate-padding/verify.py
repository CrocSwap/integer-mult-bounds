"""Literal eight-tape checks and a separate rectangle oracle. Apache-2.0."""

import ast
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def machine_module():
    spec = importlib.util.spec_from_file_location("shared_tape_machine", PACKAGE / "machine.py")
    require(spec is not None and spec.loader is not None, "missing machine")
    machine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(machine)
    return machine


class Meter:
    def __init__(self, cap):
        self.cap = cap
        self.count = 0

    def tick(self, _action):
        self.count += 1
        require(self.count <= self.cap, "action budget exhausted")


class Tape:
    """One actual head, with immutable sentinels outside the owned interval."""

    def __init__(self, contents, meter, origin=0, writable=True):
        self.cells = ["!"] + list(contents) + ["!"]
        self.origin = origin
        self.head = origin + 2
        self.initial_head = self.head
        self.meter = meter
        self.writable = writable

    def index(self):
        index = self.head - self.origin
        require(1 <= index < len(self.cells) - 1, "crossed protected boundary")
        return index

    def read(self):
        self.meter.tick("read")
        return self.cells[self.index()]

    def write(self, value):
        self.meter.tick("write")
        require(self.writable, "write to immutable tape")
        require(value in ("0", "1", "$"), "invalid written symbol")
        self.cells[self.index()] = value

    def move(self, step):
        self.meter.tick("move")
        require(type(step) is int and step in (-1, 1), "nonunit head move")
        self.head += step
        self.index()


def descriptor(q):
    return "" if q == 1 else bin(q - 1)[2:][::-1]


def oracle(shape, payload, restrict):
    padded = [1 << (q - 1).bit_length() for q in shape]
    rows = itertools.product(*(range(r) for r in padded))
    live = [all(x < q for x, q in zip(row, shape)) for row in rows]
    if restrict:
        return "".join(bit for bit, keep in zip(payload, live) if keep)
    source = iter(payload)
    return "".join(next(source) if keep else "0" for keep in live)


def fixture(machine, shape, payload, restrict=False, origin=0, repeats=1):
    require(len(shape) == 5 and all(type(q) is int and 1 <= q <= 257 for q in shape),
            "fixture shape outside bounded domain")
    widths = [(q - 1).bit_length() for q in reversed(shape)]
    n = 1 << sum(widths)
    require(n <= 4096 and repeats in (1, 2), "fixture capacity exceeded")
    m = math.prod(shape)
    bound = 256 * n + 32 * sum(widths) + 256
    meter = Meter(repeats * bound)
    descriptors = [Tape("^" + descriptor(q) + "$", meter, origin + 17 * i, False)
                   for i, q in enumerate(reversed(shape))]
    work_word = "".join("^" + "0" * width + "$" for width in widths)
    work = Tape(work_word, meter, origin - 37)
    immutable = [(t, tuple(t.cells)) for t in descriptors]
    observations = []
    for _ in range(repeats):
        start = meter.count
        source = Tape("^" + payload + "$", meter, origin + 97, False)
        output_size = m if restrict else n
        target = Tape("^" + "_" * (output_size + 1), meter, origin - 101)
        source_before = tuple(source.cells)
        machine.scan(descriptors, work, source, target, meter.tick, restrict)
        require("".join(target.cells[2:2 + output_size]) == oracle(shape, payload, restrict),
                "wrong rectangle output")
        require(target.cells[2 + output_size] == "$", "missing output delimiter")
        require(tuple(source.cells) == source_before, "source changed")
        require("".join(work.cells[1:-1]) == work_word, "work or delimiters not restored")
        require(all(tuple(t.cells) == before for t, before in immutable), "descriptor changed")
        tapes = descriptors + [work, source, target]
        require(len(tapes) == len({id(t) for t in tapes}) == 8, "eight physical tapes required")
        require(all(t.head == t.initial_head for t in tapes), "head not returned")
        require(all(t.cells[0] == t.cells[-1] == "!" for t in tapes), "sentinel changed")
        require(meter.count - start <= bound, "complete bound exceeded")
        observations.append(meter.count - start)
    require(len(set(observations)) == 1, "reused work changed execution")
    return observations[0], bound


def payload(size, seed):
    return "".join(str(((i * 13 + seed) ^ (i >> 1)) & 1) for i in range(size))


def scan_cases(machine):
    shapes = list(itertools.product((1, 2, 3), repeat=5))
    shapes += sorted(set(itertools.permutations((1, 1, 3, 5, 9))))
    for q in (4, 7, 8, 17, 31, 32, 65, 129, 257):
        for position in range(5):
            shapes.append(tuple(q if i == position else 1 for i in range(5)))
    shapes += [(2, 3, 5, 7, 2), (1, 2, 3, 5, 17)]
    records = []
    for index, shape in enumerate(shapes):
        n = 1 << sum((q - 1).bit_length() for q in shape)
        for restrict in (False, True):
            size = n if restrict else math.prod(shape)
            steps, bound = fixture(machine, shape, payload(size, index), restrict,
                                   index - 173, 2 if index % 29 == 0 else 1)
            records.append((shape, restrict, steps, bound))
    return records


def all_payloads(machine):
    count = 0
    for shape in ((1, 1, 1, 1, 1), (3, 1, 1, 1, 1), (3, 2, 1, 1, 1)):
        for restrict in (False, True):
            size = (1 << sum((q - 1).bit_length() for q in shape)) if restrict else math.prod(shape)
            for bits in itertools.product("01", repeat=size):
                fixture(machine, shape, "".join(bits), restrict)
                count += 1
    return count


def navigation_cases(machine):
    records = []
    for left in range(258):
        for right in (0, 1, 7, 257):
            meter = Meter(4 * left + 8)
            word = "^" + "01" * (left // 2) + "0" * (left % 2) + "$^" + "0" * right + "$"
            work = Tape(word, meter, -513)
            before = tuple(work.cells)
            machine.next_block(work)
            require(work.head == work.initial_head + left + 2, "wrong next-block head")
            machine.previous_block(work)
            require(work.head == work.initial_head and tuple(work.cells) == before,
                    "navigation changed work")
            require(meter.count == 4 * left + 8, "crossing action identity")
            records.append((left, right, meter.count))
    return records


def rejected(action):
    try:
        action()
    except (ValueError, RuntimeError):
        return 1
    raise ValueError("control was accepted")


def boundary_escape(meter):
    tape = Tape("^$", meter)
    tape.move(-1)
    tape.move(-1)


def controls(machine):
    count = 0
    for word in ("", "00", "x"):
        count += rejected(lambda word=word: fixture(machine, (1,) * 5, word))
    meter = Meter(10000)
    count += rejected(lambda: machine.scan([], None, None, None, meter.tick))
    count += rejected(lambda: machine.borrow(Tape("^x$", meter)))
    count += rejected(lambda: machine.load(Tape("^x$", meter), Tape("^0$", meter)))
    count += rejected(lambda: machine.load(Tape("^1$", meter), Tape("^00$", meter)))
    count += rejected(lambda: Tape("^0$", meter, writable=False).write("1"))
    count += rejected(lambda: Tape("^0$", meter).move(2))
    count += rejected(lambda: boundary_escape(meter))
    count += rejected(lambda: Meter(0).tick("exhaustion"))
    count += rejected(lambda: fixture(machine, (258, 1, 1, 1, 1), ""))
    return count


def mutation_controls(machine):
    count = 0
    original_load, original_finish = machine.load, machine.finish
    original_previous = machine.previous_block

    def wrong_complement(descriptor_tape, work, complement=False):
        return original_load(descriptor_tape, work, False)

    for name, replacement, original in (
        ("load", wrong_complement, original_load),
        ("finish", lambda work: None, original_finish),
        ("previous_block", lambda work: None, original_previous),
    ):
        try:
            setattr(machine, name, replacement)
            count += rejected(lambda: fixture(machine, (1, 1, 1, 2, 3), "101011"))
        finally:
            setattr(machine, name, original)
    return count


def source_diagnostics():
    lengths = {}
    for name in ("machine.py", "verify.py"):
        tree = ast.parse((PACKAGE / name).read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = node.end_lineno - node.lineno + 1
                require(length <= 60, "function exceeds review ceiling")
                lengths[name + ":" + node.name] = length
    return max(lengths.values())


def main():
    machine = machine_module()
    records = scan_cases(machine)
    navigation = navigation_cases(machine)
    result = {"status": "PASS_SHARED_TAPE_AGGREGATE_PADDING", "claim_type": "scoped construction",
              "tapes": 8, "counter_cells": "D", "action_bound": "256N+32D+256",
              "full_scan_cases": len(records), "exhaustive_payload_scans": all_payloads(machine),
              "navigation_pairs": len(navigation),
              "controls": controls(machine) + mutation_controls(machine),
              "maximum_function_lines": source_diagnostics(),
              "scan_sha256": hashlib.sha256(json.dumps(records).encode()).hexdigest(),
              "navigation_sha256": hashlib.sha256(json.dumps(navigation).encode()).hexdigest()}
    result["file_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
