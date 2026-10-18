#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fourteen-tape unit-carry ordered shear: y -> y +/- (x+1) modulo Q.

Derived from David Arias's PR2776, retained byte-for-byte in predecessor/.
The split/merge method and all macros retain their original attribution.
The new phase starts at (Q-1,1), visits (Q-1,1),...,(0,Q), and restores
(Q-1,1) between prefixes. OpenAI Codex supplies substantial assistance.
"""


def build_program(modules, inverse=False):
    if type(inverse) is not bool:
        raise ValueError('inverse is a fixed Boolean program choice')
    b, m, c = modules['shear'], modules['machine'], modules['counters']
    asm = m.Assembler(b.TAPE_COUNT)
    fail = asm.fresh('invalid_unit_carry_state')

    def phase(operations, prefix):
        c.emit_rewind(asm, b.P_COUNT, prefix + '_rewind_P')
        p_loop, x_loop, g_loop, body, next_x, positive, zero, done = (
            asm.fresh(prefix + suffix) for suffix in
            ('_P', '_x', '_G', '_body', '_next_x', '_positive', '_zero', '_done'))
        asm.label(p_loop)
        asm.branch(b.P_COUNT, {m.UNIT: x_loop, m.RIGHT: done}, fail)
        asm.label(x_loop)
        c.emit_rewind(asm, b.G_COUNT, prefix + '_rewind_G')
        asm.label(g_loop)
        asm.branch(b.G_COUNT, {m.UNIT: body, m.RIGHT: next_x}, fail)
        asm.label(body)
        for index, (length, source, destination, consume) in enumerate(operations):
            b._segment(asm, length, source, destination, consume, fail,
                       prefix + '_segment_' + str(index))
        asm.move(b.G_COUNT, 1)
        asm.goto(g_loop)
        asm.label(next_x)
        # Inspect L before the transfer: L=0 is the final, identity fibre.
        asm.move(b.LEFT_LENGTH, -1)
        asm.branch(b.LEFT_LENGTH, {m.UNIT: positive, m.LEFT: zero}, fail)
        asm.label(positive)
        asm.move(b.LEFT_LENGTH, 1)
        b._decrease_left_increase_right(asm, fail, prefix + '_next_split')
        asm.goto(x_loop)
        asm.label(zero)
        asm.move(b.LEFT_LENGTH, 1)
        b._reset_lengths(asm, fail, prefix + '_restore_lengths')
        b._decrease_left_increase_right(asm, fail, prefix + '_restore_carry')
        asm.move(b.P_COUNT, 1)
        asm.goto(p_loop)
        asm.label(done)

    for tape in (b.OUTPUT,) + b.SCRATCH_TAPES:
        initialize = asm.fresh('initialize_' + b.TAPE_NAMES[tape])
        asm.branch(tape, {m.BLANK: initialize}, fail)
        asm.label(initialize)
        asm.write(tape, m.LEFT)
        asm.move(tape, 1)
    for source, unary, name in ((b.P_INPUT, b.P_COUNT, 'P'),
                                (b.Q_INPUT, b.LEFT_LENGTH, 'Q'),
                                (b.G_INPUT, b.G_COUNT, 'G'),
                                (b.S_INPUT, b.S_COUNT, 'S')):
        c.emit_binary_to_unary(asm, source, b.BINARY_WORK, unary, 'prepare_' + name)
    asm.write(b.RIGHT_LENGTH, m.RIGHT)
    b._seek_right(asm, b.LEFT_LENGTH, fail, 'initial_left_end')
    b._decrease_left_increase_right(asm, fail, 'initial_unit_carry')
    gather = ((b.LEFT_LENGTH, b.SOURCE, b.SPLIT_A, False),
              (b.RIGHT_LENGTH, b.SOURCE, b.SPLIT_B, False))
    emit = ((b.RIGHT_LENGTH, b.SPLIT_B, b.OUTPUT, True),
            (b.LEFT_LENGTH, b.SPLIT_A, b.OUTPUT, True))
    if inverse:
        gather, emit = tuple(reversed(gather)), tuple(reversed(emit))
    phase(gather, 'gather')
    gathered = asm.fresh('gathered_exact_source')
    asm.branch(b.SOURCE, {m.RIGHT: gathered}, fail)
    asm.label(gathered)
    for tape in (b.SPLIT_A, b.SPLIT_B):
        asm.write(tape, m.RIGHT)
        c.emit_rewind(asm, tape, 'split_start_' + str(tape))
    phase(emit, 'emit')
    for tape in (b.SPLIT_A, b.SPLIT_B):
        complete = asm.fresh('complete_split_' + str(tape))
        asm.branch(tape, {m.RIGHT: complete}, fail)
        asm.label(complete)
    asm.write(b.OUTPUT, m.RIGHT)
    c.emit_rewind(asm, b.SOURCE, 'return_source')
    c.emit_rewind(asm, b.OUTPUT, 'return_output')
    for tape in b.SCRATCH_TAPES:
        b._erase_back_to_origin(asm, tape, 'clear_' + b.TAPE_NAMES[tape])
    asm.halt()
    asm.label(fail)
    asm.reject('unit-carry shape, alphabet, or scratch invariant')
    return asm.finish()
