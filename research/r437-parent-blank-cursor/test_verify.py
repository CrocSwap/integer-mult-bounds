#!/usr/bin/env python3
"""Rejection controls for the parent blank-return cursor meter."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("blank_cursor", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def transcribed(n: int):
    """Success-path rewind, then clear, counted without records.Tape.

    clear always opens with its own rewind, including when the head is
    already on the first payload cell.
    """
    reads = writes = moves = 0
    head = n + 1

    def step(direction):
        nonlocal head, moves
        head += direction
        if head < 0:
            raise AssertionError(head)
        moves += 1

    def rewind():
        nonlocal reads
        step(-1)
        while head != 0:
            reads += 1
            step(-1)
        reads += 1
        step(1)

    rewind()
    rewind()
    while head != n + 1:
        reads += 1
        writes += 1
        step(1)
    reads += 1
    rewind()
    return reads, writes, moves


def reject(name, bad_model_matches):
    if bad_model_matches:
        raise AssertionError(name + " matched the measured meter")


def main():
    tape_type, words = verify.load_tape()
    for n in range(0, 41):
        for bit in (0, 1):
            _, _, total = verify.success_path(tape_type, words.BLANK, n, bit)
            if total != transcribed(n):
                raise AssertionError((n, bit, total, transcribed(n)))
            if n:
                reject("payload-only moves", total[2] == n)
                reject("clear-without-opening-rewind", total[2] == 3 * n + 4)

    parent = verify.parent_payload()
    reject("executed fibre pays the parent", parent == verify.EXECUTED_BITS)
    reject("dropped omitted coordinates", parent == 9475 * 12 * 3 ** (128 - 124))
    reject("one visit is the whole meter", verify.success_moves(parent) == parent)
    result = verify.certify()
    if result["writes"] != parent or result["moves"] != verify.success_moves(parent):
        raise AssertionError(result)
    if result["reads"] != verify.success_reads(parent):
        raise AssertionError(result)
    print(
        "PASS_R437_PARENT_BLANK_CURSOR_CONTROLS"
        f" checked_n=0..40"
        f" parent_moves_minus_writes={result['moves'] - result['writes']}"
        " rejected=payload_only,fibre_only,gap_omitted,clear_without_opening_rewind"
    )


if __name__ == "__main__":
    main()
