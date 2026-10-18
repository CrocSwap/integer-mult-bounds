"""Delimited binary records with sequential reads and relative stack origins.

Host integers decode local words and implement arithmetic macros; this module
counts tape symbol operations, not the unimplemented arithmetic lowering.
"""
from collections import Counter


def need(test, message):
    if not test:
        raise ValueError(message)


class Tape:
    alphabet = (0, 1, "|", "#", "^", None)

    def __init__(self, ancestor=(), origin=0):
        self.cells = {origin - len(ancestor) + i: x for i, x in enumerate(ancestor)}
        self.cells[origin] = "^"
        self.head = origin + 1
        self.meter = Counter()
        self.low_seen = self.high_seen = self.head

    def observe(self):
        self.low_seen = min(self.low_seen, self.head)
        self.high_seen = max(self.high_seen, self.head)

    def read(self):
        self.meter["reads"] += 1
        self.observe()
        return self.cells.get(self.head)

    def write(self, value):
        need(value in self.alphabet, "finite tape alphabet")
        self.meter["writes"] += 1
        self.observe()
        if value is None:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = value

    def move(self, direction):
        need(direction in (-1, 1), "unit head movement")
        self.head += direction
        self.meter["moves"] += 1

    def append(self, value):
        need(self.read() is None, "append at local blank")
        self.write(value)
        self.move(1)

    def rewind(self):
        self.move(-1)
        while self.read() != "^":
            self.move(-1)
        self.move(1)

    def clear(self):
        self.rewind()
        while self.read() is not None:
            self.write(None)
            self.move(1)
        self.rewind()


def encode(values):
    for value in values:
        need(isinstance(value, int) and value >= 0, "nonnegative binary operand")
        for bit in range(max(1, value.bit_length())):
            yield (value >> bit) & 1
        yield "|"


def decode(symbols):
    out, value, shift = [], 0, 0
    for symbol in symbols:
        if symbol == "|":
            need(shift > 0, "nonempty operand")
            out.append(value)
            value, shift = 0, 0
        else:
            need(symbol in (0, 1), "binary operand symbol")
            value |= symbol << shift
            shift += 1
    need(shift == 0, "terminated operand")
    return tuple(out)


class Records:
    def __init__(self, records=(), ancestor=(), origin=0):
        self.tape = Tape(ancestor, origin)
        for record in records:
            for symbol in encode(record):
                self.tape.append(symbol)
            self.tape.append("#")
        self.tape.rewind()

    def get(self, index):
        need(index >= 0, "nonnegative record index")
        tape = self.tape
        tape.rewind()
        for _ in range(index):
            while tape.read() != "#":
                need(tape.read() is not None, "record index within local band")
                tape.move(1)
            tape.move(1)
        data = []
        while tape.read() != "#":
            need(tape.read() is not None, "complete local record")
            data.append(tape.read())
            tape.move(1)
        tape.rewind()
        return decode(data)


class Stack:
    def __init__(self, ancestor=(), origin=0):
        self.tape = Tape(ancestor, origin)
        self.reverse = Tape()

    def empty(self):
        self.tape.move(-1)
        result = self.tape.read() == "^"
        self.tape.move(1)
        return result

    def push(self, values):
        for symbol in encode(values):
            self.tape.append(symbol)
        self.tape.append("#")

    def pop(self):
        need(not self.empty(), "pop a nonempty local stack")
        tape, reverse = self.tape, self.reverse
        tape.move(-1)
        need(tape.read() == "#", "top record delimiter")
        tape.write(None)
        tape.move(-1)
        while tape.read() not in ("#", "^"):
            reverse.append(tape.read())
            tape.write(None)
            tape.move(-1)
        tape.move(1)
        reverse.move(-1)
        data = []
        while reverse.read() != "^":
            data.append(reverse.read())
            reverse.write(None)
            reverse.move(-1)
        reverse.move(1)
        return decode(data)


class FieldBand:
    """Fixed-width high entries in global-slot order; no spectator storage.

    A full caller initializes zero and advances the odometer. set_digits is
    only a bounded-fixture entry hook; production order uses advance().
    """
    def __init__(self, cap, dimensions, codes, ancestor=(), origin=0):
        need(cap >= 1 and len(dimensions) == len(codes), "canonical field schema")
        self.cap, self.dimensions, self.codes = cap, tuple(dimensions), tuple(codes)
        self.bits = max(1, (cap - 1).bit_length())
        self.schema = Records(((cap, len(dimensions), self.bits),) + tuple(zip(dimensions, codes)))
        self.tape = Tape(ancestor, origin)
        for dim in dimensions:
            for _ in range(dim * dim * self.bits):
                self.tape.append(0)
        self.tape.rewind()

    def set_digits(self, fields):
        need(len(fields) == len(self.dimensions), "complete fixture prefix")
        self.tape.rewind()
        for dim, values in zip(self.dimensions, fields):
            need(len(values) == dim * dim, "matrix entry count")
            for value in values:
                need(0 <= value < self.cap, "high digit extent")
                for bit in range(self.bits):
                    self.tape.write((value >> bit) & 1)
                    self.tape.move(1)
        need(self.tape.read() is None, "exact generated band length")
        self.tape.rewind()

    def read_field(self, slot, code, live_depth):
        cap, count, bits = self.schema.get(0)
        need(0 <= slot < live_depth <= count, "frozen slot excludes current field")
        dimension, expected_code = self.schema.get(slot+1)
        need(expected_code == code, "exact raw field specification")
        tape = self.tape
        tape.rewind()
        for earlier in range(slot):
            dim, _ = self.schema.get(earlier+1)
            for _ in range(dim*dim*bits):
                tape.move(1)
        values = []
        for _ in range(dimension ** 2):
            value = 0
            for bit in range(bits):
                symbol = tape.read()
                need(symbol in (0, 1), "complete generated digit")
                value |= symbol << bit
                tape.move(1)
            need(value < cap, "canonical high digit")
            values.append(value)
        tape.rewind()
        return tuple(values)

    def advance(self):
        cap, _count, bits = self.schema.get(0)
        tape = self.tape
        tape.rewind()
        while tape.read() is not None:
            tape.move(1)
        carry = True
        while carry:
            tape.move(-1)
            if tape.read() == "^":
                tape.move(1)
                return False
            value = 0
            for bit in range(bits - 1, -1, -1):
                value |= tape.read() << bit
                if bit:
                    tape.move(-1)
            updated = value + 1
            carry = updated == cap
            if carry:
                updated = 0
            for bit in range(bits):
                tape.write((updated >> bit) & 1)
                tape.move(1)
            if carry:
                for _ in range(bits):
                    tape.move(-1)
        tape.rewind()
        return True
