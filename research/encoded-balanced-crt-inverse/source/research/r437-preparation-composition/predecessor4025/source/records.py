"""Sequential binary program/field records and typed continuation stacks.

Runtime numerical words copy between tapes. Only tags, source codes, ranks
and row labels enter fixed finite control. Fixture encoding is separate.
"""
from words import BLANK, LEFT, ONE, RIGHT, ZERO, Meter, Unsigned, need

WORD_END, RECORD_END = 5, 6
ROOT, STEP, VALUE, CONSTANT, MULTIPLY, PAIR, RETURN = range(7, 14)
FINITE_BITS = 16  # Fixed vocabulary width for this compiled source instance.


class Tape:
    def __init__(self):
        self.cells = bytearray([LEFT])
        self.head = 1
        self.meter = Meter()

    def read(self):
        self.meter.reads += 1
        return self.cells[self.head] if self.head < len(self.cells) else BLANK

    def write(self, symbol):
        need(ZERO <= symbol <= RETURN, "fixed record alphabet")
        self.meter.writes += 1
        if self.head >= len(self.cells):
            self.cells.extend([BLANK]*(self.head+1-len(self.cells)))
        self.cells[self.head] = symbol

    def step(self, direction):
        need(direction in (-1, 1), "unit record-head move")
        self.head += direction
        need(self.head >= 0, "local record boundary")
        self.meter.moves += 1

    def append(self, symbol):
        need(self.read() == BLANK, "append at record blank")
        self.write(symbol)
        self.step(1)

    def rewind(self):
        self.step(-1)
        while self.read() != LEFT:
            self.step(-1)
        self.step(1)

    def clear(self):
        self.rewind()
        while self.read() != BLANK:
            self.write(BLANK)
            self.step(1)
        self.rewind()


def append_word(tape, word):
    word.rewind()
    while word.read() != RIGHT:
        tape.append(word.read())
        word.step(1)
    tape.append(WORD_END)
    word.rewind()


def read_word(tape, arena):
    out = arena.zero()
    while tape.read() != WORD_END:
        bit = tape.read()
        need(bit in (ZERO, ONE) and out.read() != RIGHT, "encoded word extent")
        out.write(bit)
        out.step(1)
        tape.step(1)
    need(out.read() == RIGHT, "complete encoded word")
    tape.step(1)
    out.rewind()
    return out


def append_finite(tape, value, bits=FINITE_BITS):
    """Compile-time finite source/operation tag encoding."""
    need(0 <= value < 1 << bits, "compiled finite vocabulary")
    for bit in range(bits):
        tape.append((value >> bit) & 1)
    tape.append(WORD_END)


def read_finite(tape, bits=FINITE_BITS):
    # The accumulator ranges over a fixed finite set, independent of e/w/h.
    state = 0
    for bit in range(bits):
        value = tape.read()
        need(value in (ZERO, ONE), "finite label bit")
        state |= value << bit
        tape.step(1)
    need(tape.read() == WORD_END, "finite label delimiter")
    tape.step(1)
    return state


def seek_record(tape, index):
    machine, arena = Unsigned(index.arena), index.arena
    remaining, one = arena.copy(index), arena.literal(1)
    tape.rewind()
    while not remaining.zero():
        while tape.read() != RECORD_END:
            need(tape.read() != BLANK, "record exists at global slot")
            tape.step(1)
        tape.step(1)
        after = machine.subtract_exact(remaining, one)
        arena.free(remaining)
        remaining = after
    arena.free_many(remaining, one)


class Stack:
    def __init__(self, index_arena, residue_arena):
        self.index_arena, self.residue_arena = index_arena, residue_arena
        self.tape, self.reverse = Tape(), Tape()

    def empty(self):
        self.tape.step(-1)
        result = self.tape.read() == LEFT
        self.tape.step(1)
        return result

    def push(self, tag, *words):
        need(tag in (VALUE, CONSTANT, MULTIPLY, PAIR, RETURN), "continuation kind")
        need(len(words) == (2 if tag == VALUE else 1), "continuation arity")
        self.tape.append(tag)
        for word in words:
            append_word(self.tape, word)
        self.tape.append(RECORD_END)

    def pop(self):
        need(not self.empty(), "nonempty continuation stack")
        tape, reverse = self.tape, self.reverse
        tape.step(-1)
        need(tape.read() == RECORD_END, "continuation top delimiter")
        tape.write(BLANK)
        tape.step(-1)
        while tape.read() not in (LEFT, RECORD_END):
            reverse.append(tape.read())
            tape.write(BLANK)
            tape.step(-1)
        tape.step(1)
        reverse.step(-1)
        tag = reverse.read()
        need(tag in (VALUE, CONSTANT, MULTIPLY, PAIR, RETURN), "encoded continuation kind")
        reverse.write(BLANK)
        reverse.step(-1)
        arenas = (self.index_arena, self.index_arena) if tag == VALUE else (self.residue_arena,)
        words = []
        for arena in arenas:
            out = arena.zero()
            while reverse.read() != WORD_END:
                bit = reverse.read()
                need(bit in (ZERO, ONE) and out.read() != RIGHT, "continuation binary word")
                out.write(bit)
                out.step(1)
                reverse.write(BLANK)
                reverse.step(-1)
            need(out.read() == RIGHT, "complete continuation operand")
            reverse.write(BLANK)
            reverse.step(-1)
            out.rewind()
            words.append(out)
        need(reverse.read() == LEFT, "complete continuation record")
        reverse.step(1)
        return tag, tuple(words)


class Program:
    """Encoded root and admitted chronological steps; numerical fields are words."""
    def __init__(self, index_arena, residue_arena, code_bits=FINITE_BITS):
        self.index_arena, self.residue_arena = index_arena, residue_arena
        self.code_bits = code_bits
        self.tape = Tape()

    def root(self):
        self.tape.rewind()
        need(self.tape.read() == ROOT, "root record")
        self.tape.step(1)
        size = read_word(self.tape, self.index_arena)
        unit = read_word(self.tape, self.residue_arena)
        depth = read_word(self.tape, self.index_arena)
        need(self.tape.read() == RECORD_END, "root record end")
        self.tape.rewind()
        return size, unit, depth

    def step(self, level):
        need(not level.zero(), "positive step level")
        seek_record(self.tape, level)
        need(self.tape.read() == STEP, "step record")
        self.tape.step(1)
        metadata = tuple(read_finite(self.tape, self.code_bits if field == 1 else FINITE_BITS)
                         for field in range(6))
        parent = read_word(self.tape, self.index_arena)
        child = read_word(self.tape, self.index_arena)
        need(self.tape.read() == RECORD_END, "step record end")
        self.tape.rewind()
        return metadata, parent, child

    @classmethod
    def fixture(cls, index_arena, residue_arena, root_size, root_unit, events, code_bits=FINITE_BITS):
        """Fixture-only serialization; runtime computes and validates extents."""
        out = cls(index_arena, residue_arena, code_bits)
        out.tape.append(ROOT)
        for arena, value in ((index_arena, root_size), (residue_arena, root_unit), (index_arena, len(events))):
            word = arena.input(value)
            append_word(out.tape, word)
            arena.free(word)
        out.tape.append(RECORD_END)
        size = root_size
        for kind, code, rank, field, reverse, half in events:
            f = size//64
            child = rank*f if kind == 0 else f//2 if half else f
            out.tape.append(STEP)
            for field_index, label in enumerate((kind, code, rank, field, int(reverse), int(half))):
                append_finite(out.tape, label, code_bits if field_index == 1 else FINITE_BITS)
            for value in (size, child):
                word = index_arena.input(value)
                append_word(out.tape, word)
                index_arena.free(word)
            out.tape.append(RECORD_END)
            size = child
        out.tape.rewind()
        return out


class Fields:
    def __init__(self, index_arena, residue_arena, code_bits=FINITE_BITS):
        self.index_arena, self.residue_arena = index_arena, residue_arena
        self.code_bits = code_bits
        self.tape = Tape()

    def check_code(self, slot, code):
        seek_record(self.tape, slot)
        observed = read_finite(self.tape, self.code_bits)
        self.tape.rewind()
        need(observed == code, "original global raw-field code")

    def end(self, after):
        seek_record(self.tape, after)
        complete = self.tape.read() == BLANK
        self.tape.rewind()
        need(complete, "exact frozen/current field prefix")

    def read(self, slot, code, depth):
        need(Unsigned(self.index_arena).compare(slot, depth) < 0, "frozen field excludes current/future slot")
        seek_record(self.tape, slot)
        observed = read_finite(self.tape, self.code_bits)
        need(observed == code, "exact encoded raw-field specification")
        out = [[read_word(self.tape, self.residue_arena) for _ in range(64)] for _ in range(64)]
        need(self.tape.read() == RECORD_END, "complete 64-dimensional raw high field")
        self.tape.rewind()
        return out

    @classmethod
    def fixture(cls, index_arena, residue_arena, fields, code_bits=FINITE_BITS):
        """Load canonical raw-field fixture data before measured execution."""
        out = cls(index_arena, residue_arena, code_bits)
        for code, high in fields:
            append_finite(out.tape, code, code_bits)
            need(len(high) == 64 and all(len(row) == 64 for row in high), "field fixture shape")
            for row in high:
                for value in row:
                    word = residue_arena.input(value)
                    append_word(out.tape, word)
                    residue_arena.free(word)
            out.tape.append(RECORD_END)
        out.tape.rewind()
        return out
