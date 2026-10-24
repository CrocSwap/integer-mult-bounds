#!/usr/bin/env python3
"""Sharp closed-return head-move bill for L546 -= L561 on six kernel tapes.

The tape object is research/qq16-gaussian-axis-tapes/tapes.py (Clear1nsight,
Apache-2.0). This file only schedules reads, writes and unit moves.
"""
import importlib.util
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAPE_PATH = ROOT / "research" / "qq16-gaussian-axis-tapes" / "tapes.py"


def load_tapes():
    spec = importlib.util.spec_from_file_location("qq16_axis_tapes", TAPE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned tape module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TAPES = load_tapes()
Tape = TAPES.Tape
need = TAPES.need


def encode(values, width):
    lo = -(1 << (width - 1))
    hi = (1 << (width - 1)) - 1
    need(all(type(v) is int and lo <= v <= hi for v in values), "signed input range")
    return [(v >> bit) & 1 for v in values for bit in range(width)]


def decode(cells, width):
    values = []
    for start in range(0, len(cells), width):
        word = sum(cells[start + bit] << bit for bit in range(width))
        values.append(word - ((word >> (width - 1)) << width))
    return values


def lengths(n, width):
    need(type(n) is int and n >= 2 and (n & (n - 1)) == 0, "N=2^n, n>=1")
    need(type(width) is int and width >= 1, "component width")
    length = n * width
    need(length % 2 == 0, "even bit length")
    return [length, length] + [length // 2] * 4


def lower_bound(n, width):
    """Closed origin-return tours that visit every cell of each tape."""
    return sum(2 * (length - 1) for length in lengths(n, width))


def subtract_segment(dst, src, nbits, width):
    """In-place two's-complement subtraction. Heads finish on the last cell."""
    need(nbits % width == 0 and nbits >= width, "whole coordinates")
    coords = nbits // width
    for coord in range(coords):
        borrow = 0
        for bit in range(width):
            incoming = src.read()
            resident = dst.read()
            diff = resident - incoming - borrow
            dst.write(diff & 1)
            borrow = 1 if diff < 0 else 0
            if bit != width - 1 or coord != coords - 1:
                dst.move(1)
                src.move(1)


def rewind(tape, steps):
    for _ in range(steps):
        tape.move(-1)


def place(real_a, imag_a, real_b, imag_b, width):
    n = len(real_a)
    half = n // 2
    bits = [
        encode(real_a, width),
        encode(imag_a, width),
        encode(real_b[:half], width),
        encode(imag_b[:half], width),
        encode(real_b[half:], width),
        encode(imag_b[half:], width),
    ]
    need([len(row) for row in bits] == lengths(n, width), "placement lengths")
    tapes = []
    for index, row in enumerate(bits):
        tapes.append(Tape(row, origin=0, trace=True, discardable=(index >= 2)))
    return tapes


def closed_subtraction(real_a, imag_a, real_b, imag_b, width):
    """L546 (a) -= L561 (b), then return every head to its origin.

    data0/data1 hold L546 real/imag for every coordinate.
    scratch0/scratch1 hold L561's first N/2 coordinates.
    scratch2/scratch3 hold L561's second N/2 coordinates.
    """
    n = len(real_a)
    need(len(imag_a) == len(real_b) == len(imag_b) == n, "equal lengths")
    tapes = place(real_a, imag_a, real_b, imag_b, width)
    data0, data1, s0, s1, s2, s3 = tapes
    half_bits = (n // 2) * width
    saved = [list(tape.cells) for tape in tapes[2:]]
    exteriors = [dict(tape.exterior) for tape in tapes]

    subtract_segment(data0, s0, half_bits, width)
    subtract_segment(data1, s1, half_bits, width)
    data0.move(1)
    data1.move(1)
    subtract_segment(data0, s2, half_bits, width)
    subtract_segment(data1, s3, half_bits, width)
    for tape in (data0, data1):
        rewind(tape, n * width - 1)
    for tape in (s0, s1, s2, s3):
        rewind(tape, half_bits - 1)

    for tape in tapes:
        need(tape.head == tape.origin, "head returned")
        need(tape.exterior == exteriors[tapes.index(tape)], "exterior untouched")
    for tape, before in zip(tapes[2:], saved):
        need(tape.cells == before, "L561 preserved")
    return tapes


def counts(tapes):
    read = write = move = 0
    for tape in tapes:
        traced = [action for action, _pos in tape.trace]
        need(sum(item == "read" for item in traced) == tape.count["read"], "trace reads")
        need(sum(item == "write" for item in traced) == tape.count["write"], "trace writes")
        need(sum(item == "move" for item in traced) == tape.count["move"], "trace moves")
        read += tape.count["read"]
        write += tape.count["write"]
        move += tape.count["move"]
    return read, write, move


def expect_bill(n, width, tapes):
    length = n * width
    read, write, move = counts(tapes)
    need(read == 4 * length, "read bill")
    need(write == 2 * length, "write bill")
    need(move == lower_bound(n, width) == 8 * length - 12, "sharp move bill")
    return read, write, move


def signed_range(width):
    return -(1 << (width - 1)), (1 << (width - 1)) - 1


def check_random(rng, n, width, trials):
    lo, hi = signed_range(width)
    # Both summands lie in [lo/2, hi/2], so minuend = result + source stays
    # inside the signed width. lo = -2^(W-1) is even for W>=2.
    need(width >= 2, "half-range fixture needs W>=2")
    span_lo, span_hi = lo // 2, hi // 2
    accepted = 0
    for _ in range(trials):
        result_r = [rng.randint(span_lo, span_hi) for _ in range(n)]
        result_i = [rng.randint(span_lo, span_hi) for _ in range(n)]
        source_r = [rng.randint(span_lo, span_hi) for _ in range(n)]
        source_i = [rng.randint(span_lo, span_hi) for _ in range(n)]
        real_a = [result_r[coord] + source_r[coord] for coord in range(n)]
        imag_a = [result_i[coord] + source_i[coord] for coord in range(n)]
        need(all(lo <= value <= hi for value in real_a + imag_a), "constructed overflow")
        tapes = closed_subtraction(real_a, imag_a, source_r, source_i, width)
        expect_bill(n, width, tapes)
        need(decode(tapes[0].cells, width) == result_r, "real difference")
        need(decode(tapes[1].cells, width) == result_i, "imag difference")
        accepted += 1
    need(accepted >= 1, "no in-range random fixture")


def check_sensitivity():
    """Every payload cell changes the difference for some one-bit flip."""
    n, width = 2, 2
    real_a, imag_a = [1, -2], [0, 1]
    real_b, imag_b = [1, 0], [-1, 1]
    base = closed_subtraction(real_a, imag_a, real_b, imag_b, width)
    base_r = decode(base[0].cells, width)
    base_i = decode(base[1].cells, width)
    placed = place(real_a, imag_a, real_b, imag_b, width)
    for tape_index, tape in enumerate(placed):
        for cell in range(len(tape.cells)):
            trial = place(real_a, imag_a, real_b, imag_b, width)
            trial[tape_index].cells[cell] ^= 1
            out = rerun_from_cells(trial, width)
            # Modulo 2^W the map is a translation in each component, so every
            # payload bit changes the written difference. Preservation of a
            # flipped L561 cell is not itself the signal.
            changed = (decode(out[0].cells, width) != base_r or
                       decode(out[1].cells, width) != base_i)
            need(changed, "silent payload cell")


def rerun_from_cells(tapes, width):
    """Subtract using cells already placed. Used only by the sensitivity control."""
    nbits = len(tapes[0].cells)
    half = nbits // 2
    need(len(tapes[2].cells) == half, "half scratch")
    data0, data1, s0, s1, s2, s3 = tapes
    subtract_segment(data0, s0, half, width)
    subtract_segment(data1, s1, half, width)
    data0.move(1)
    data1.move(1)
    subtract_segment(data0, s2, half, width)
    subtract_segment(data1, s3, half, width)
    for tape in (data0, data1):
        rewind(tape, nbits - 1)
    for tape in (s0, s1, s2, s3):
        rewind(tape, half - 1)
    return tapes


def check_machine_contract():
    """The pinned Tape charges unit moves and refuses a non-unit jump."""
    tape = Tape([0, 1, 0], origin=0, trace=False, discardable=False)
    need(tape.read() == 0, "read at origin")
    tape.move(1)
    need(tape.count["move"] == 1 and tape.head == 1, "unit move")
    try:
        tape.move(2)
    except ValueError:
        pass
    else:
        raise AssertionError("non-unit move was accepted")
    # One-past the last cell is allowed; reading it is not.
    tape.move(1)
    tape.move(1)
    need(tape.head == 3, "one-past")
    try:
        tape.read()
    except ValueError:
        pass
    else:
        raise AssertionError("read past the owned interval was accepted")


def check_formula_grid():
    for exponent in range(1, 8):
        n = 1 << exponent
        for width in range(1, 6):
            tapes = closed_subtraction([0] * n, [0] * n, [0] * n, [0] * n, width)
            expect_bill(n, width, tapes)
            need(decode(tapes[0].cells, width) == [0] * n, "zero real")
            need(decode(tapes[1].cells, width) == [0] * n, "zero imag")


def main():
    check_machine_contract()
    check_formula_grid()
    rng = random.Random(546561)
    check_random(rng, 2, 3, 40)
    check_random(rng, 4, 5, 20)
    check_random(rng, 8, 4, 10)
    check_random(rng, 512, 5, 1)
    # Hand example: 1 - (-1) = 2 on a signed 3-bit component, both coordinates.
    tapes = closed_subtraction([1, 1], [0, -1], [-1, 1], [1, 0], 3)
    expect_bill(2, 3, tapes)
    need(decode(tapes[0].cells, 3) == [2, 0], "hand real")
    need(decode(tapes[1].cells, 3) == [-1, -1], "hand imag")
    check_sensitivity()
    print(
        "PASS_QQ16_L546_HEAD_MOVE "
        "move=8*N*W-12 read=4*N*W write=2*N*W "
        "bound=sum_2(L_t-1) sharp=yes "
        "placement=data_full_scratch_halves heads=origin "
        "L561=preserved no_new_kappa"
    )


if __name__ == "__main__":
    main()
