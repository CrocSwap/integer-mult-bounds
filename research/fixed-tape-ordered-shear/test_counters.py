#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Physical binary-to-unary checks against integer-valued specifications.

The fixture construction and cost oracle run outside the machine.  Every
conversion executes the same finite instruction table, including all source
rewinds, countdown carries, workspace erasure, and output-head restoration.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from counters import emit_binary_to_unary
from machine import Assembler, LEFT, RIGHT, ZERO, ONE, UNIT, Tape, Machine, Rejected, binary, marked


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def conversion_cost(value):
    """Proved macro cost, excluding the caller's final halt instruction."""
    return 24 * value - 7 * value.bit_count() + 15 * value.bit_length() + 12


def run_checks():
    assembler = Assembler(3)
    emit_binary_to_unary(assembler, 0, 1, 2)
    assembler.halt()
    program = assembler.finish()
    total_steps = 0
    largest_steps = 0
    # The contiguous range includes every carry pattern through ten bits;
    # further power boundaries exercise shrinking longer descriptors.
    extra = (1025, 2047, 2048, 4095, 4096)
    values = tuple(range(1, 1025)) + extra
    for value in values:
        source = binary(value)
        original = dict(source.cells)
        machine = Machine(program, [source, Tape({0: LEFT}, 1), Tape({0: LEFT}, 1)])
        expected_steps = conversion_cost(value) + 1
        machine.run(max_steps=expected_steps + 1)
        expected_unary = {0: LEFT, **{i: UNIT for i in range(1, value + 1)}, value + 1: RIGHT}
        require(machine.steps == expected_steps, f"exact charged transition count for {value}")
        require(machine.steps <= 44 * value + 1, f"uniform linear transition bound for {value}")
        require(source.cells == original, f"source descriptor preserved for {value}")
        require(not machine.write_positions[0], f"source descriptor is never written for {value}")
        require(machine.tapes[1].cells == {0: LEFT}, f"binary work erased for {value}")
        require(machine.tapes[2].cells == expected_unary, f"exact unary output for {value}")
        require([tape.head for tape in machine.tapes] == [1, 1, 1], f"physical heads restored for {value}")
        total_steps += machine.steps
        largest_steps = max(largest_steps, machine.steps)

    malformed = (
        ("empty", ()),
        ("zero", (ZERO,)),
        ("two_zeroes", (ZERO, ZERO)),
        ("redundant_top_zero", (ONE, ZERO)),
        ("long_redundant_top_zero", (ONE, ONE, ZERO)),
        ("nonbinary_digit", (UNIT,)),
        ("embedded_left_marker", (ONE, LEFT, ONE)),
    )
    rejected = []
    for label, symbols in malformed:
        source = marked(symbols)
        original = dict(source.cells)
        machine = Machine(program, [source, Tape({0: LEFT}, 1), Tape({0: LEFT}, 1)])
        try:
            machine.run(max_steps=1000)
        except Rejected:
            rejected.append(label)
        else:
            raise AssertionError("accepted malformed descriptor: " + label)
        require(source.cells == original and not machine.write_positions[0], "rejection preserves source: " + label)

    # Workspace emptiness is part of the subroutine interface.  The current
    # cell is checked before either the binary copy or unary append writes it.
    for dirty_tape in (1, 2):
        tapes = [binary(3), Tape({0: LEFT}, 1), Tape({0: LEFT}, 1)]
        tapes[dirty_tape].cells[1] = UNIT
        machine = Machine(program, tapes)
        try:
            machine.run(max_steps=1000)
        except Rejected:
            rejected.append("occupied_" + ("binary_workspace" if dirty_tape == 1 else "unary_workspace"))
        else:
            raise AssertionError("accepted occupied conversion workspace")
        require(tapes[dirty_tape].cells[1] == UNIT, "occupied current cell must not be overwritten")

    alias_controls = 0
    for roles in ((0, 0, 1), (0, 1, 0), (0, 1, 1)):
        try:
            emit_binary_to_unary(Assembler(3), *roles)
        except ValueError:
            alias_controls += 1
        else:
            raise AssertionError("accepted aliased conversion roles")

    return {
        "status": "PASS",
        "program_instructions": len(program.instructions),
        "fixed_tapes": program.tapes,
        "contiguous_extent_range": [1, 1024],
        "additional_extents": list(extra),
        "positive_cases": len(values),
        "exact_cost": "24*N - 7*popcount(N) + 15*bit_length(N) + 12, plus one halt",
        "total_transitions": total_steps,
        "largest_case_transitions": largest_steps,
        "rejected_inputs": rejected,
        "rejected_aliased_interfaces": alias_controls,
        "source_preserved_and_never_written": True,
        "binary_workspace_erased": True,
        "all_heads_returned_to_one": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
