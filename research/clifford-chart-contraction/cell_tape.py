"""A fixed active cell on a compact, phase-modulated observation; Apache-2.0."""
from fractions import Fraction
from contract import apply, parity

SHIFTS = (0, 0, 0, 0, 0, 4) * 2
MASKS = (0x48210048210, 0x1048210148210, 0x2048210248210)
SIGNATURE = 2


def compile_cell():
    frequencies = [apply(MASKS, w) for w in range(8)]
    initial = sum((parity(w & SIGNATURE) ^ parity((f & ((1 << 24)-1)) & (f >> 24))) << w
                  for w, f in enumerate(frequencies))
    lookup = []
    for j in range(24):
        output_shift = (SHIFTS[j//4] >> (j%4)) & 1
        input_shift = (SHIFTS[6+j//4] >> (j%4)) & 1
        row = []
        for quad in range(16):
            a, b, c, d = ((quad >> k) & 1 for k in range(4))
            r, s = a ^ b, c ^ d
            common = (a & output_shift) ^ (c & input_shift) ^ (r & s)
            row.append(sum((common ^ (r & (f >> (24+j))) ^ (s & (f >> j))) << w
                           for w, f in enumerate(frequencies)))
        lookup.append(row)
    eligible = [sum((f >> 48 == s) << w for w, f in enumerate(frequencies)) for s in range(16)]
    return initial, lookup, eligible


TABLE = compile_cell()


def phase_mask_symbols(mask):
    """Input encoder used in tests; the consumer itself reads only the tape."""
    tape = []
    for j in range(24):
        right = 4*(11 - 2*(j//4)) + j%4
        for bit in (52+right+4, 52+right, right+4, right):
            tape.append((mask >> bit) & 1)
    for bit in range(4):
        tape.extend(((mask >> (52+bit)) & 1, (mask >> bit) & 1))
    return bytes(tape)


class Tape:
    """One read-only binary input track, a movable head, and counted motion."""
    def __init__(self, symbols):
        if len(symbols) != 104:
            raise ValueError("A phase mask has 104 bits")
        self.symbols = symbols
        self.position = self.reads = self.moves = 0

    def take(self):
        symbol = self.symbols[self.position]
        if symbol not in (0, 1):
            raise ValueError("Expected a binary symbol")
        self.reads += 1
        self.moves += 1
        self.position += 1
        return symbol

    def restore(self):
        self.moves += self.position
        self.position = 0


def evaluate(tape):
    phase, blocks, eligible = TABLE
    for table in blocks:
        quad = sum(tape.take() << j for j in range(4))
        phase ^= table[quad]
    singleton = 0
    for j in range(4):
        singleton |= (tape.take() ^ tape.take()) << j
    active = eligible[singleton]
    value = active.bit_count() - 2 * (phase & active).bit_count()
    tape.restore()
    return Fraction(value, 1 << 32)
