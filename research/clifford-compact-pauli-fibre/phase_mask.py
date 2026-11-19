"""Single-scan full-fibre decoder for the coupled phase-mask family of #7801."""
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fibre import MASK48, pack, parity, plan, split_address, walsh


def read_mask(tape):
    """Consume exactly 104 least-significant-first bits, then restore the read head."""
    word = 0
    for j in range(104):
        bit = tape.read()
        if bit not in (0,1):
            raise ValueError("Expected one binary input symbol")
        word |= bit << j
        if j < 103:
            tape.move(1)
    for _ in range(103):
        tape.move(-1)
    return word


def numerators(mask):
    """Return all 256 exact numerators, each with denominator 2^36."""
    row, col = map(split_address, divmod(mask, 1 << 52))
    firsts = pack(row[:-1:2] + col[:-1:2])
    alpha, beta = (pack([s ^ t for s,t in zip(side[:-1:2], side[1:-1:2], strict=True)])
                   for side in (row, col))
    bins = [[0]*16 for _ in range(16)]
    for labels, move, sign, weight in plan():
        shifts = (labels >> 8) & MASK48
        wave = labels >> 56
        out, inp = wave & ((1 << 24)-1), wave >> 24
        zout, zin = sign & 15, sign >> 4
        k = zout ^ row[-1]
        z = k ^ zin ^ col[-1]
        neg = parity((firsts & shifts) ^ ((out ^ alpha) & (inp ^ beta)) ^ (z & move & 15))
        bins[z][k] += -weight if neg else weight
    for values in bins:
        walsh(values)
    return tuple(bins[z][x] for x in range(16) for z in range(16))


def decode(tape):
    return [Fraction(v, 1 << 36) for v in numerators(read_mask(tape))]


class Tape:
    """Finite read-only binary input followed by the end position, with a move counter."""
    def __init__(self, word):
        self.bits = tuple((word >> j) & 1 for j in range(104))
        self.head = self.reads = self.moves = 0

    def read(self):
        self.reads += 1
        return self.bits[self.head]

    def move(self, delta):
        self.head += delta
        self.moves += abs(delta)
        if not 0 <= self.head <= 104:
            raise ValueError("Moved outside the input track")
