"""Fixed CRT key tape-action experiment, not a uniform bit-time compiler.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
The inverse word and CRT coefficients retain the predecessors credited in README.
Data words live on tapes; Python controls only fixed scan positions and bit flags.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Tape:
    def __init__(self, name, cells, events, readonly=False):
        need(all(type(x) is int and x in (0, 1) for x in cells), "binary tape")
        self.name, self.cells, self.events = name, list(cells), events
        self.head, self.readonly = 0, readonly
        self.phase = "copy-input"

    def seek(self, position):
        need(0 <= position < len(self.cells), "bounded tape position")
        while self.head != position:
            direction = 1 if self.head < position else -1
            self.events.append((self.phase, self.name, "M", self.head, direction))
            self.head += direction

    def read(self, position):
        self.seek(position)
        value = self.cells[self.head]
        self.events.append((self.phase, self.name, "R", self.head, value))
        return value

    def write(self, position, value):
        need(not self.readonly and type(value) is int and value in (0, 1), "legal write")
        self.seek(position)
        self.events.append((self.phase, self.name, "W", self.head, value))
        self.cells[self.head] = value


class Register:
    """A statically assigned region of one shared scratch tape, little endian."""
    def __init__(self, tape, start, width):
        self.tape, self.start, self.width = tape, start, width

    def read(self, bit):
        return self.tape.read(self.start + bit)

    def write(self, bit, value):
        self.tape.write(self.start + bit, value)

    def clear(self):
        for bit in range(self.width):
            self.write(bit, 0)


def add_constant(register, constant):
    """Ripple a fixed signed constant modulo the declared power of two."""
    carry = 0
    for bit in range(register.width):
        a, b = register.read(bit), (constant >> bit) & 1
        register.write(bit, a ^ b ^ carry)
        carry = (a & b) | (a & carry) | (b & carry)


def less_constant(register, constant):
    less, equal = 0, 1
    for bit in reversed(range(register.width)):
        a, b = register.read(bit), (constant >> bit) & 1
        less |= equal & (1 - a) & b
        equal &= 1 - (a ^ b)
    return less


def multiply_constant(source, constant, destination):
    destination.clear()
    for bit in range(source.width):
        if source.read(bit):
            add_constant(destination, constant << bit)


def remainder(source, modulus, destination):
    """Binary long division with one bit of slack: 2*remainder+bit fits."""
    need(2 * modulus <= 1 << destination.width, "remainder register slack")
    destination.clear()
    for bit in reversed(range(source.width)):
        for j in reversed(range(1, destination.width)):
            destination.write(j, destination.read(j - 1))
        destination.write(0, source.read(bit))
        if not less_constant(destination, modulus):
            add_constant(destination, -modulus)


def copy_register(source, destination):
    need(source.width == destination.width, "equal copy widths")
    for bit in range(source.width):
        destination.write(bit, source.read(bit))


class KeyMachine:
    """Fixed 18-bit interface: u,t,y[14..0],back; all five tapes are reused.

    Input and ROM are borrowed, output must initially be clean, and work/scratch
    are clean private regions. The back bit is a copied spectator. ROM consists
    of 17 rows of 32 bits for the fixed Beneš layer. Its compilation is setup.
    """
    def __init__(self, address_bits, rom, coordinate_bits, mode="correct"):
        need(len(address_bits) == 18 and len(rom) == 544, "fixed fixture interface")
        need(tuple(map(len, coordinate_bits)) == (4, 4, 5), "complete descriptors")
        need(all(0 <= p < 15 for row in coordinate_bits for p in row), "y-only descriptors")
        need(mode in ("correct", "stale_second", "stale_third", "drop_high",
                      "omit_clear", "omit_return", "bad_weight", "invalid_left_enabled"),
             "known fault mode")
        self.events, self.snapshots = [], []
        self.input = Tape("input", address_bits, self.events, True)
        self.rom = Tape("rom", rom, self.events, True)
        self.output = Tape("output", [0] * 18, self.events)
        self.work = Tape("work", [0] * 18, self.events)
        self.scratch = Tape("scratch", [0] * 64, self.events)
        self.tapes = (self.input, self.rom, self.output, self.work, self.scratch)
        self.coordinate_bits, self.mode = coordinate_bits, mode
        self.a = Register(self.scratch, 0, 4)
        self.b = Register(self.scratch, 4, 4)
        self.target = Register(self.scratch, 8, 5)
        self.acc = Register(self.scratch, 13, 12)
        self.rem = Register(self.scratch, 25, 9)
        self.product = Register(self.scratch, 34, 12)
        self.offset = Register(self.scratch, 46, 6)
        self.saved = Register(self.scratch, 52, 6)
        self.query_count = 0

    def phase(self, name):
        for tape in self.tapes:
            tape.phase = name

    def query(self):
        self.query_count += 1
        epoch = self.query_count
        self.phase("query-%d-descriptors" % epoch)
        for register, positions in zip((self.a, self.b, self.target), self.coordinate_bits):
            for bit, ybit in enumerate(positions):
                register.write(bit, self.work.read(16 - ybit))
        self.phase("query-%d-arithmetic" % epoch)
        valid = less_constant(self.a, 11) & less_constant(self.b, 13)
        self.acc.clear()
        if valid or self.mode == "invalid_left_enabled":
            for bit in range(4):
                if self.a.read(bit):
                    add_constant(self.acc, (77 if self.mode == "bad_weight" else 78) << bit)
                if self.b.read(bit):
                    add_constant(self.acc, 11 << bit)
        remainder(self.acc, 143, self.rem)
        multiply_constant(self.rem, 5, self.product)
        remainder(self.product, 17, self.offset)
        if self.mode in ("stale_second", "stale_third"):
            if epoch == 1:
                copy_register(self.offset, self.saved)
            elif (self.mode == "stale_second" and epoch == 2
                  or self.mode == "stale_third" and epoch == 3):
                copy_register(self.saved, self.offset)
        self.phase("query-%d-rom-scan" % epoch)
        answer, seen = 0, 0
        # Both loops are fixed control; no data word becomes a Python index.
        for fixed_offset in range(17):
            for fixed_target in range(32):
                match = 1
                for bit in range(6):
                    match &= 1 - (self.offset.read(bit) ^ ((fixed_offset >> bit) & 1))
                for bit in range(5):
                    match &= 1 - (self.target.read(bit) ^ ((fixed_target >> bit) & 1))
                need(not (seen & match), "unique ROM match")
                seen |= match
                answer |= match & self.rom.read(32 * fixed_offset + fixed_target)
        need(seen == 1, "complete ROM match")
        # Observer-only snapshots are never consulted by the tape program.
        self.snapshots.append((tuple(self.work.cells), tuple(self.scratch.cells), answer))
        self.phase("query-%d-cleanup" % epoch)
        for register in (self.a, self.b, self.target, self.acc, self.rem, self.product, self.offset):
            register.clear()
        self.rom.seek(0)
        self.scratch.seek(0)
        self.work.seek(0)
        return answer

    def change_y(self, start, enabled, negative):
        carry = enabled
        stop = 10 if self.mode == "drop_high" else 15
        for bit in range(start, stop):
            previous = self.work.read(16 - bit)
            self.work.write(16 - bit, previous ^ carry)
            carry &= previous ^ negative

    def run(self):
        for bit in range(18):
            self.work.write(bit, self.input.read(bit))
        for step in reversed(range(10)):
            self.phase("inverse-step-%d" % step)
            if step in (9, 4):
                value = self.query()
                self.phase("inverse-step-%d" % step)
                self.work.write(0, self.work.read(0) ^ value)
            elif step in (8, 3):
                self.work.write(1, self.work.read(1) ^ self.work.read(7) ^ self.work.read(0))
            elif step in (7, 2):
                self.change_y(9, self.work.read(0), 1 - self.work.read(1))
            elif step in (6, 1):
                self.work.write(1, self.work.read(1) ^ self.work.read(7))
            else:
                self.change_y(10, self.work.read(0) & self.work.read(1), 1)
        value = self.query()
        self.phase("ideal-switch")
        self.work.write(7, self.work.read(7) ^ value)
        self.phase("copy-output")
        for bit in range(18):
            self.output.write(bit, self.work.read(bit))
        self.phase("final-cleanup")
        if self.mode != "omit_clear":
            for tape in (self.work, self.scratch):
                for bit in range(len(tape.cells)):
                    tape.write(bit, 0)
        if self.mode != "omit_return":
            for tape in self.tapes:
                tape.seek(0)
        return tuple(self.output.cells)
