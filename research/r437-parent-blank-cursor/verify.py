#!/usr/bin/env python3
"""Exact success-path blank-return meter for the R437 parent payload.

The tape is the pinned predecessor records.Tape. The call is packet_engine's
success-path rewind followed by clear, starting from the trailing blank.
This checker does not allocate the parent and does not run physical.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor"
ENGINE = ROOT / "research/selected-bit-physical-caller/inputs/pr2753/packet_engine.py"

UNUSED_ROWS = 9475
OMITTED_COORDINATES = 124
EXECUTED_BITS = 972


def success_reads(n: int) -> int:
    return 3 * n + 4


def success_writes(n: int) -> int:
    return n


def success_moves(n: int) -> int:
    return 3 * n + 6


def load_tape():
    sys.path.insert(0, str(VENDOR))
    spec = importlib.util.spec_from_file_location("r437_blank_records", VENDOR / "records.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    words = importlib.import_module("words")
    return module.Tape, words


def parent_payload() -> int:
    return UNUSED_ROWS * 12 * 3**128


def meter(tape):
    counted = tape.meter
    return (counted.reads, counted.writes, counted.moves)


def delta(before, after):
    return tuple(after[i] - before[i] for i in range(3))


def success_path(tape_type, blank, n: int, bit: int, left: int = 2):
    """n appends, completeness read, then rewind and clear."""
    tape = tape_type()
    for _ in range(n):
        tape.append(bit)
    if tape.head != n + 1 or tape.read() != blank or tape.head != n + 1:
        raise AssertionError((n, tape.head))
    start = meter(tape)
    tape.rewind()
    middle = meter(tape)
    tape.clear()
    end = meter(tape)
    if tape.head != 1 or list(tape.cells) != [left] + [blank] * n:
        raise AssertionError((n, tape.head, list(tape.cells[:4]), len(tape.cells)))
    return delta(start, middle), delta(middle, end), delta(start, end)


def certify():
    tape_type, words = load_tape()
    if (words.ZERO, words.ONE, words.LEFT, words.RIGHT, words.BLANK) != (0, 1, 2, 3, 4):
        raise AssertionError("alphabet moved")
    blank = words.BLANK
    source = ENGINE.read_text(encoding="utf-8")
    call = (
        'need(current.read()==directory.read()==BLANK,"complete shared packet and directory")\n'
        "                current.rewind();directory.rewind()\n"
        "                if current is not source:current.clear()\n"
    )
    if call not in source:
        raise AssertionError("success-path blank-return call site moved")
    clear_source = (VENDOR / "records.py").read_text(encoding="utf-8")
    if "def clear(self):\n        self.rewind()\n        while self.read() != BLANK:\n" not in clear_source:
        raise AssertionError("Tape.clear control flow moved")

    for n in list(range(0, 49)) + [EXECUTED_BITS]:
        for bit in (0, 1):
            rewind, clear, total = success_path(tape_type, blank, n, bit, words.LEFT)
            if rewind != (n + 1, 0, n + 2):
                raise AssertionError((n, bit, rewind))
            if clear != (2 * n + 3, n, 2 * n + 4):
                raise AssertionError((n, bit, clear))
            if total != (success_reads(n), success_writes(n), success_moves(n)):
                raise AssertionError((n, bit, total))

    # The omitted-coordinate factor is inside the length. A miniature parent
    # with 3^k in place of 3^128 still writes every cell, including that factor.
    for exponent in (0, 1):
        miniature = UNUSED_ROWS * 12 * 3**exponent
        _, _, total = success_path(tape_type, blank, miniature, 1, words.LEFT)
        if total[1] != miniature or total != (
            success_reads(miniature),
            miniature,
            success_moves(miniature),
        ):
            raise AssertionError((exponent, total))
        skipped = miniature // 3**exponent
        if exponent and total[1] == skipped:
            raise AssertionError("gap cells were not written")

    child = 2 * 3 * 2 * 3**4
    if child != EXECUTED_BITS:
        raise AssertionError(child)
    parent = parent_payload()
    if parent != UNUSED_ROWS * EXECUTED_BITS * 3**OMITTED_COORDINATES:
        raise AssertionError(parent)
    if parent != UNUSED_ROWS * 2 * (3 * 3**OMITTED_COORDINATES) * 2 * 3**4:
        raise AssertionError(parent)
    executed = (success_reads(EXECUTED_BITS), EXECUTED_BITS, success_moves(EXECUTED_BITS))
    full = (success_reads(parent), parent, success_moves(parent))
    if executed[1] >= full[1] or executed[2] >= full[2]:
        raise AssertionError((executed, full))
    return {
        "rows": UNUSED_ROWS,
        "omitted_coordinates": OMITTED_COORDINATES,
        "executed_bits": EXECUTED_BITS,
        "parent_payload": parent,
        "reads": full[0],
        "writes": full[1],
        "moves": full[2],
        "executed_moves": executed[2],
    }


def main():
    result = certify()
    print(
        "PASS_R437_PARENT_BLANK_CURSOR"
        f" rows={result['rows']}"
        f" omitted_coordinates={result['omitted_coordinates']}"
        f" executed_bits={result['executed_bits']}"
        f" parent_payload={result['parent_payload']}"
        f" reads={result['reads']}"
        f" writes={result['writes']}"
        f" moves={result['moves']}"
        f" executed_fibre_moves={result['executed_moves']}"
        " call=rewind_then_clear"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
