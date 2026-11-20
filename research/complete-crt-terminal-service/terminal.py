"""Literal terminal service on the frozen union's owners plus three records.

Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
Compilation receives no precision, data, extent, free list or head position.
"""
from collections import Counter
from hashlib import sha256
import json

SYMBOLS = ("0", "1", "L", "R", "_", *map(str, range(5, 14)))


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Builder:
    def __init__(self):
        self.code, self.labels, self.serial = [], {}, 0

    def mark(self, name):
        need(name not in self.labels, "duplicate state")
        self.labels[name] = len(self.code)

    def op(self, *row):
        self.code.append(row)

    def read(self, role, branches):
        self.op("R", role, {s: branches.get(s, "FAIL") for s in SYMBOLS})

    def expect(self, role, symbol):
        self.serial += 1
        label = "expected_" + str(self.serial)
        self.read(role, {symbol: label})
        self.mark(label)

    def finish(self):
        result = []
        for op, *args in self.code:
            if op == "R":
                result.append((op, args[0], {s: self.labels[q] for s, q in args[1].items()}))
            elif op == "J":
                result.append((op, self.labels[args[0]]))
            else:
                result.append((op, *args))
        return tuple(result), dict(self.labels)


def blank_frame(b, role):
    for i in range(8):
        b.expect(role, "_")
        if i != 7:
            b.op("M", role, 1)
    for _ in range(7):
        b.op("M", role, -1)


def rewind(b, role, prefix):
    b.op("M", role, -1)
    b.mark(prefix + "_read")
    b.read(role, {"L": prefix + "_done", "_": prefix + "_back"})
    b.mark(prefix + "_back")
    b.op("M", role, -1)
    b.op("J", prefix + "_read")
    b.mark(prefix + "_done")
    b.op("M", role, 1)


def compile_terminal(include_records=True):
    b = Builder()
    b.mark("TERMINAL")
    # Under the inherited distinct-owned-stack invariant, exactly 56 records
    # are equivalent to live = {0,...,7}. This is a physical, read-only guard.
    for role in range(64, 68):
        blank_frame(b, role)
    b.expect(69, "L")
    b.op("M", 69, 1)
    for i in range(336):
        name = "stack_digit_" + str(i)
        b.read(69, {"0": name, "1": name})
        b.mark(name)
        b.op("M", 69, 1)
    b.expect(69, "R")
    for _ in range(337):
        b.op("M", 69, -1)
    b.mark("NUMERICAL_MARKERS")
    for role in range(8, 64):
        # The exact seven native actions, with ready head 1.
        b.op("M", role, -1)
        b.expect(role, "L")
        b.op("M", role, 1)
        b.expect(role, "_")
        b.op("M", role, -1)
        b.op("W", role, "_")
        b.op("M", role, 1)
    b.mark("TEMPLATE")
    b.op("M", 68, -1)
    b.expect(68, "L")
    b.op("M", 68, 1)
    b.mark("template_scan")
    b.read(68, {"0": "template_digit", "R": "template_end"})
    b.mark("template_digit")
    b.op("W", 68, "_")
    b.op("M", 68, 1)
    b.op("J", "template_scan")
    b.mark("template_end")
    b.op("W", 68, "_")
    rewind(b, 68, "template_rewind")
    b.op("M", 68, -1)
    b.op("W", 68, "_")
    b.op("M", 68, 1)
    if include_records:
        for role in range(70, 73):
            prefix = "record_" + str(role)
            b.mark(prefix)
            b.op("M", role, -1)
            b.expect(role, "L")
            b.op("M", role, 1)
            b.mark(prefix + "_scan")
            b.read(role, {**{s: prefix + "_digit" for s in SYMBOLS if s not in ("L", "_")},
                          "_": prefix + "_end"})
            b.mark(prefix + "_digit")
            b.op("W", role, "_")
            b.op("M", role, 1)
            b.op("J", prefix + "_scan")
            b.mark(prefix + "_end")
            rewind(b, role, prefix + "_rewind")
            b.op("M", role, -1)
            b.op("W", role, "_")
            b.op("M", role, 1)
    # Same 1395-instruction metadata close path as the frozen lifecycle.
    b.mark("METADATA_CLOSE")
    for role in (64, 65):
        blank_frame(b, role)
    b.expect(69, "L")
    b.op("W", 69, "_")
    b.op("M", 69, 1)
    for i in range(336):
        label = "erase_stack_digit_" + str(i)
        b.read(69, {"0": label, "1": label})
        b.mark(label)
        b.op("W", 69, "_")
        b.op("M", 69, 1)
    b.expect(69, "R")
    b.op("W", 69, "_")
    for _ in range(337):
        b.op("M", 69, -1)
    b.op("H", "CLOSED" if include_records else "NUMERICAL_CLOSED")
    b.mark("FAIL")
    b.op("H", "REJECTED")
    code, labels = b.finish()
    return code, {"roles": 73 if include_records else 70, "labels": labels,
                  "states": len(code), "sha256": digest(code)}


def digest(code):
    return sha256(json.dumps(code, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def relocate(code, base):
    """Offline suffix for appending to the exact frozen graph without edits."""
    need(type(base) is int and base >= 0, "fixed nonnegative state offset")
    return tuple((row[0], row[1], {s: q+base for s, q in row[2].items()}) if row[0] == "R"
                 else ("J", row[1]+base) if row[0] == "J" else row for row in code)


class Port:
    """Literal primitive bridge to an existing backing and head; no Word method.

    Bounds checks and counters are instrumentation. This never appends, slices,
    replaces a backing, decodes a word, queries arena.live or calls an Entry.
    """
    def __init__(self, backing, byte_symbols=True):
        self.backing, self.byte_symbols = backing, byte_symbols

    @property
    def cells(self):
        return self.backing.cells

    @property
    def head(self):
        return self.backing.head

    def read(self):
        need(0 <= self.head < len(self.cells), "supplied read window")
        symbol = self.cells[self.head]
        return SYMBOLS[symbol] if self.byte_symbols else symbol

    def write(self, symbol):
        need(0 <= self.head < len(self.cells), "supplied write window")
        self.cells[self.head] = SYMBOLS.index(symbol) if self.byte_symbols else symbol

    def move(self, direction):
        need(direction in (-1, 1) and 0 <= self.head + direction < len(self.cells), "supplied move window")
        self.backing.head += direction


def execute(code, metadata, ports, start="TERMINAL", limit=1000000):
    need(len(ports) == metadata["roles"] and len({id(t.cells) for t in ports}) == len(ports),
         "distinct fixed physical owners")
    pc = metadata["labels"][start]
    count, operations = 0, Counter()
    histories = [[t.head, t.head] for t in ports]
    old_ids = [id(t.cells) for t in ports]
    capacities = [len(t.cells) for t in ports]
    phase, phases = start, Counter()
    boundaries = {q: label for label, q in metadata["labels"].items()
                  if label in ("NUMERICAL_MARKERS", "TEMPLATE", "METADATA_CLOSE", "record_70", "record_71", "record_72")}
    while True:
        phase = boundaries.get(pc, phase)
        row = code[pc]
        op = row[0]
        count += 1
        phases[phase] += 1
        operations[op] += 1
        need(count <= limit, "replay watchdog")
        if op == "R":
            pc = row[2][ports[row[1]].read()]
        elif op == "W":
            ports[row[1]].write(row[2])
            pc += 1
        elif op == "M":
            port = ports[row[1]]
            port.move(row[2])
            histories[row[1]][0] = min(histories[row[1]][0], port.head)
            histories[row[1]][1] = max(histories[row[1]][1], port.head)
            pc += 1
        elif op == "J":
            pc = row[1]
        elif op == "H":
            need(old_ids == [id(t.cells) for t in ports], "preserved physical backing identity")
            need(capacities == [len(t.cells) for t in ports], "no grant or history refund")
            return {"status": row[1], "instructions": count, "operations": dict(operations),
                    "phases": dict(phases), "histories": histories, "capacities": capacities}
        else:
            raise ValueError("nonliteral opcode")
