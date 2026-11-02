# SPDX-License-Identifier: Apache-2.0
"""Compile y -> y +/- (x+2) mod Q into fourteen local tapes.

David Arias / PR2776 supplies the assembler, counters and split/merge macros.
Charles Bethin / PR2829 supplies the fixed-carry interface and follow-up.
This compiler reuses the finished conversion workspace as a Q-position counter.
"""


def copy_q_counter(asm, b, m, fail):
    """Copy unary Q into the now-empty binary workspace; finish at both ends."""
    loop, unit, done = (asm.fresh("copy_q_" + s) for s in ("loop", "unit", "done"))
    asm.label(loop)
    asm.branch(b.LEFT_LENGTH, {m.UNIT: unit, m.RIGHT: done}, fail)
    asm.label(unit)
    asm.write(b.BINARY_WORK, m.UNIT)
    asm.move(b.LEFT_LENGTH, 1)
    asm.move(b.BINARY_WORK, 1)
    asm.goto(loop)
    asm.label(done)
    asm.write(b.BINARY_WORK, m.RIGHT)


def advance_split(asm, b, m, fail, prefix):
    """Advance R through 1,...,Q cyclically, keeping both heads at right ends."""
    positive, zero, transfer = (asm.fresh(prefix + s) for s in ("pos", "zero", "step"))
    asm.move(b.LEFT_LENGTH, -1)
    asm.branch(b.LEFT_LENGTH, {m.UNIT: positive, m.LEFT: zero}, fail)
    asm.label(positive)
    asm.move(b.LEFT_LENGTH, 1)
    asm.goto(transfer)
    asm.label(zero)
    asm.move(b.LEFT_LENGTH, 1)
    b._reset_lengths(asm, fail, prefix + "reset")
    asm.label(transfer)
    b._decrease_left_increase_right(asm, fail, prefix + "transfer")


def emit_phase(asm, modules, operations, fail, prefix):
    """Visit exactly Q fibres for each prefix, independently of split wrap."""
    b, m, c = modules
    names = ("p", "start_x", "x", "g", "body", "next_x", "next_p", "done")
    p_loop, start_x, x_loop, g_loop, body, next_x, next_p, done = (
        asm.fresh(prefix + name) for name in names
    )
    c.emit_rewind(asm, b.P_COUNT, prefix + "rewind_p")
    asm.label(p_loop)
    asm.branch(b.P_COUNT, {m.UNIT: start_x, m.RIGHT: done}, fail)
    asm.label(start_x)
    c.emit_rewind(asm, b.BINARY_WORK, prefix + "rewind_x")
    asm.label(x_loop)
    asm.branch(b.BINARY_WORK, {m.UNIT: g_loop, m.RIGHT: next_p}, fail)
    asm.label(g_loop)
    c.emit_rewind(asm, b.G_COUNT, prefix + "rewind_g")
    scan_g = asm.fresh(prefix + "scan_g")
    asm.label(scan_g)
    asm.branch(b.G_COUNT, {m.UNIT: body, m.RIGHT: next_x}, fail)
    asm.label(body)
    for index, (length, source, destination, consume) in enumerate(operations):
        b._segment(
            asm,
            length,
            source,
            destination,
            consume,
            fail,
            prefix + "segment" + str(index),
        )
    asm.move(b.G_COUNT, 1)
    asm.goto(scan_g)
    asm.label(next_x)
    advance_split(asm, b, m, fail, prefix + "advance")
    asm.move(b.BINARY_WORK, 1)
    asm.goto(x_loop)
    asm.label(next_p)
    asm.move(b.P_COUNT, 1)
    asm.goto(p_loop)
    asm.label(done)


def prepare(asm, modules, fail):
    """Convert descriptors, then reuse conversion storage and set carry two."""
    b, m, c = modules
    for tape in (b.OUTPUT,) + b.SCRATCH_TAPES:
        initialize = asm.fresh("initialize_" + b.TAPE_NAMES[tape])
        asm.branch(tape, {m.BLANK: initialize}, fail)
        asm.label(initialize)
        asm.write(tape, m.LEFT)
        asm.move(tape, 1)
    rows = (
        (b.P_INPUT, b.P_COUNT, "p"),
        (b.Q_INPUT, b.LEFT_LENGTH, "q"),
        (b.G_INPUT, b.G_COUNT, "g"),
        (b.S_INPUT, b.S_COUNT, "s"),
    )
    for source, unary, name in rows:
        c.emit_binary_to_unary(asm, source, b.BINARY_WORK, unary, "prepare_" + name)
    copy_q_counter(asm, b, m, fail)
    asm.write(b.RIGHT_LENGTH, m.RIGHT)
    advance_split(asm, b, m, fail, "initial_one")
    advance_split(asm, b, m, fail, "initial_two")


def finish(asm, modules, fail):
    """Finish the owned output and restore every source and scratch role."""
    b, m, c = modules
    for tape in (b.SPLIT_A, b.SPLIT_B):
        complete = asm.fresh("complete_split_" + str(tape))
        asm.branch(tape, {m.RIGHT: complete}, fail)
        asm.label(complete)
    asm.write(b.OUTPUT, m.RIGHT)
    c.emit_rewind(asm, b.SOURCE, "return_source")
    c.emit_rewind(asm, b.OUTPUT, "return_output")
    for tape in b.SCRATCH_TAPES:
        b._erase_back_to_origin(asm, tape, "clear_" + b.TAPE_NAMES[tape])
    asm.halt()
    asm.label(fail)
    asm.reject("carry-two shape, alphabet, or scratch invariant")


def build_program(modules, inverse=False):
    """Emit one fixed table; extents and payload are never compiler inputs."""
    if type(inverse) is not bool:
        raise ValueError("inverse must be a fixed Boolean program choice")
    b, m, c = modules
    asm = m.Assembler(b.TAPE_COUNT)
    fail = asm.fresh("invalid_carry_two_state")
    prepare(asm, modules, fail)
    gather = (
        (b.LEFT_LENGTH, b.SOURCE, b.SPLIT_A, False),
        (b.RIGHT_LENGTH, b.SOURCE, b.SPLIT_B, False),
    )
    emit = (
        (b.RIGHT_LENGTH, b.SPLIT_B, b.OUTPUT, True),
        (b.LEFT_LENGTH, b.SPLIT_A, b.OUTPUT, True),
    )
    if inverse:
        gather, emit = tuple(reversed(gather)), tuple(reversed(emit))
    emit_phase(asm, modules, gather, fail, "gather_")
    gathered = asm.fresh("gathered_exact_source")
    asm.branch(b.SOURCE, {m.RIGHT: gathered}, fail)
    asm.label(gathered)
    for tape in (b.SPLIT_A, b.SPLIT_B):
        asm.write(tape, m.RIGHT)
        c.emit_rewind(asm, tape, "split_start_" + str(tape))
    emit_phase(asm, modules, emit, fail, "emit_")
    finish(asm, modules, fail)
    return asm.finish()
