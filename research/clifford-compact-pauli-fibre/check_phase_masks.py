"""Independent literal nibble contraction for the phase-mask producer.

On each of the 4,265 Bell reads, form its 16 x 16 singleton matrix using
ordinary Weyl matrix actions. Trace against every output Weyl explicitly.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from functools import cache
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fibre import fibre
from phase_mask import Tape, decode, numerators
from contract import Q, iter_reads, label_sum, RAW_DENOMINATOR


def sign(number):
    return -1 if number.bit_count() & 1 else 1


@cache
def literal_pair(a, b):
    return sum(sign((r & s) ^ (a & r) ^ (b & s)) for r in range(16) for s in range(16))


def producer(mask):
    gates = [('C', 1 << j, 1) for j in range(104)]
    rows = [1 << j for j in range(104)]
    for first in range(4, 52, 8):
        for j in range(first, first + 4):
            rows[j] |= 1 << (j + 52)
            rows[j + 52] |= 1 << j
    gates.append(('D', rows, [1+2*((mask >> j) & 1) for j in range(104)]))
    return Q.signature(104, gates)


def literal(mask):
    # The 52-bit row and column addresses both end at their singleton nibble.
    rowmask, colmask = mask >> 52, mask & ((1 << 52)-1)
    matrix = [[0]*16 for _ in range(16)]
    for read in iter_reads():
        if read.correction_i:
            raise ValueError("Unexpected identity-fibre transport phase")
        weight = read.numerator
        for j, (out, inp) in enumerate(zip(read.output_labels, read.input_labels, strict=True)):
            pos = 4*(11-2*j)
            row_second, row_first = (rowmask >> pos) & 15, (rowmask >> (pos+4)) & 15
            col_second, col_first = (colmask >> pos) & 15, (colmask >> (pos+4)) & 15
            weight *= sign((row_first & (out >> 4)) ^ (col_first & (inp >> 4)))
            weight *= literal_pair((out & 15) ^ row_first ^ row_second,
                                   (inp & 15) ^ col_first ^ col_second)
        left, right = label_sum(read.output_labels), label_sum(read.input_labels)
        left_scale = [sign(((left ^ rowmask) & 15) & r) for r in range(16)]
        right_scale = [sign(((right ^ colmask) & 15) & c) for c in range(16)]
        for r, a in enumerate(left_scale):
            dest = matrix[r ^ (left >> 4)]
            for c, b in enumerate(right_scale):
                dest[c ^ (right >> 4)] += weight*a*b
    denominator = RAW_DENOMINATOR << 52
    return [(Fraction(sum(sign(z & c)*matrix[c ^ x][c] for c in range(16)), denominator), 0)
            for x in range(16) for z in range(16)]


def main():
    rng = Random(104)
    witness = 0xe90447f9b4d1553cfdce84821d
    masks = [witness, 0, 1, 1 << 52, *[rng.getrandbits(104) for _ in range(7)]]
    outputs = set()
    for mask in masks:
        reference = literal(mask)
        actual, _ = fibre(producer(mask))
        if list(actual) != reference:
            raise ValueError("Literal Bell contractions disagree with shared-fibre calculation")
        tape = Tape(mask)
        streamed = decode(tape)
        if [(a, 0) for a in streamed] != reference or (tape.head,tape.reads,tape.moves) != (0,104,206):
            raise ValueError("Tape answers, access or head restoration")
        outputs.add(tuple(reference))
        if mask == 0 and reference[0] != (Fraction(1, 1 << 29), 0):
            raise ValueError("Incorrect reference normalization")
    expect = numerators(witness)
    for j in range(104):
        if numerators(witness ^ (1 << j)) == expect:
            raise ValueError("Input symbol is invisible on the sharp probe witness")
    print("PASS all 104 single-bit flips change the output on the common witness; 206 moves with head restoration")
    if len(outputs) < 4:
        raise ValueError("Insufficient distinct phase-mask controls")
    print(f"PASS literal 16-by-16 singleton matrices on {len(masks)} masks, {256*len(masks)} exact outputs")


if __name__ == "__main__":
    main()
