"""Iterative generated-weight control with sequential frozen-table access.

Tables represent completed fixed-size full-ring preparation. Their producer
cost is a separate part of PROOF.md, not measured by this finite interpreter.
"""
from dataclasses import dataclass, field
from math import gcd


def need(test, message):
    if not test:
        raise ValueError(message)


@dataclass(frozen=True)
class Step:
    kind: str
    tag: int
    rank: int = 7
    field: int = 1
    reverse: bool = False
    half: bool = False


@dataclass(frozen=True)
class Program:
    q: int
    width: int
    root_size: int
    unit: int
    steps: tuple

    def extents(self):
        need(self.q >= 3 and self.q % 2 and self.width >= 1, "odd atom ring")
        need(gcd(self.unit, self.q) == 1 and self.root_size > 0, "root unit and extent")
        out = [self.root_size]
        for step in self.steps:
            f = out[-1] // 64
            need(f >= 1 and step.tag >= 0 and
                 step.tag.bit_length() <= 4096 * (self.q**self.width).bit_length() + 64,
                 "internal descriptor extent")
            if step.kind == "good":
                need(1 <= step.rank <= 42, "selected good rank")
                size = step.rank * f
            elif step.kind == "pair":
                need(0 <= step.field < 127, "diagonal pair field")
                size = f
            else:
                need(step.kind == "unit", "generated descriptor kind")
                size = f // 2 if step.half else f
            need(0 < size <= 42 * f < out[-1], "proper generated child")
            out.append(size)
        return out


@dataclass(frozen=True)
class Table:
    tag: int
    pivots: tuple
    diagonal: tuple
    permutation: tuple


@dataclass
class Meter:
    requests: int = 0
    combines: int = 0
    field_reads: list = field(default_factory=list)
    bit_reads: int = 0
    head_moves: int = 0
    ring_operations: int = 0
    maximum_stack_items: int = 0


class FrozenTape:
    """Read-only, fixed-size pages with charged head motion and word decoding."""
    def __init__(self, tables, modulus, meter):
        self.modulus = modulus
        self.word_bits = (modulus - 1).bit_length()
        self.tag_bits = max(16, max((t.tag.bit_length() for t in tables), default=0))
        need(self.tag_bits <= 4096 * modulus.bit_length() + 64, "bounded low/request metadata")
        self.page_bits = self.tag_bits + 192 * self.word_bits + 128 * 7
        self.count = len(tables)
        self.meter = meter
        self.head = 0
        data = []
        def emit(value, width):
            need(0 <= value < 1 << width, "encoded field extent")
            data.extend((value >> j) & 1 for j in range(width))
        for table in tables:
            need(len(table.pivots) == 64 and len(table.diagonal) == 128,
                 "fixed preparation table dimensions")
            need(sorted(table.permutation) == list(range(128)), "row permutation")
            need(all(0 <= x < modulus and gcd(x, modulus) == 1
                     for x in table.pivots + table.diagonal), "prepared units")
            emit(table.tag, self.tag_bits)
            for value in table.pivots + table.diagonal:
                emit(value, self.word_bits)
            for value in table.permutation:
                emit(value, 7)
        self.data = tuple(data)

    @property
    def unused_stock(self):
        raise ValueError("unused stock is outside coefficient control")

    def move(self, destination):
        need(0 <= destination <= len(self.data), "local frozen-tape boundary")
        self.meter.head_moves += abs(destination - self.head)
        self.head = destination

    def word(self, width):
        value = 0
        for j in range(width):
            need(self.head < len(self.data), "complete control word")
            value |= self.data[self.head] << j
            self.head += 1
            self.meter.bit_reads += 1
            self.meter.head_moves += 1
        return value

    def read(self, slot, tag):
        need(0 <= slot < self.count, "frozen field excludes current fresh matrix")
        self.move(slot * self.page_bits)
        observed = self.word(self.tag_bits)
        pivots = tuple(self.word(self.word_bits) for _ in range(64))
        diagonal = tuple(self.word(self.word_bits) for _ in range(128))
        permutation = tuple(self.word(7) for _ in range(128))
        self.move(0)
        need(observed == tag, "frozen low/request binding")
        self.meter.field_reads.append(slot)
        return Table(observed, pivots, diagonal, permutation)


def evaluate(program, tape, index):
    sizes = program.extents()
    depth = len(program.steps)
    need(tape.count == depth, "retain the global frozen-field prefix")
    need(0 <= index < sizes[-1], "requested weight extent")
    modulus = program.q**program.width
    need(tape.modulus == modulus and tape.head == 0, "one local ring and head origin")
    pending, values = [("value", depth, index)], []
    meter = tape.meter
    while pending:
        meter.maximum_stack_items = max(meter.maximum_stack_items, len(pending) + len(values))
        event = pending.pop()
        if event[0] == "constant":
            values.append(event[1])
        elif event[0] == "multiply":
            values[-1] = values[-1] * event[1] % modulus
            meter.ring_operations += 1
            meter.combines += 1
        elif event[0] == "pair":
            denominator, numerator = values.pop(), values.pop()
            need(gcd(denominator, modulus) == 1, "generated denominator unit")
            values.append(event[1] * numerator * pow(denominator, -1, modulus) % modulus)
            meter.ring_operations += 3
            meter.combines += 1
        else:
            _, level, coordinate = event
            meter.requests += 1
            need(0 <= coordinate < sizes[level], "recursive index extent")
            if level == 0:
                values.append(program.unit % modulus)
                continue
            step = program.steps[level - 1]
            if step.kind == "unit":
                values.append(1)
                continue
            table = tape.read(level - 1, step.tag)
            f = sizes[level - 1] // 64
            if step.kind == "good":
                pending.extend((("multiply", table.pivots[coordinate // f]),
                                ("value", level - 1, coordinate)))
            else:
                j = f - 1 - coordinate if step.reverse else coordinate
                def bank(row):
                    return ("value", level - 1, row * f + j) if row < 64 else ("constant", 1)
                pending.extend((("pair", table.diagonal[step.field]),
                                bank(step.field), bank(table.permutation[step.field])))
    need(len(values) == 1 and gcd(values[0], modulus) == 1, "one completed unit value")
    result = values.pop()
    need(not pending and not values and tape.head == 0, "local stack and head restoration")
    return result


def header_offsets(before, radix, middle, coefficient, carry, meter):
    """Active-source counter stays separate from arbitrary spectator counters."""
    need(before >= 1 and middle >= 1 and radix >= 1, "complete header rectangle")
    for _before in range(before):
        for source in range(radix):
            if radix == 1:
                offset = 0
            else:
                offset = (coefficient * source + carry) % radix
                meter["active_preparations"] += 1
                meter["active_bits_read"] += max(1, source.bit_length())
            for _middle in range(middle):
                meter["fibres"] += 1
                yield offset
