#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""A literal fourteen-tape controller for an ordered cyclic shear.

For positive binary extents P,Q,G,S, move opaque bits on
    [P] x [Q] x [G] x [Q] x [S]
by (p,x,g,y,s) -> (p,x,g,y+x mod Q,s), or its inverse.

The assembler below only builds a finite instruction table.  It receives no
runtime extents or payload, and emits no callbacks, computed addressing,
integer arithmetic, or data-dependent Python loops.  Numerical setup and all
loops run on the same physical tapes as the payload.  Inputs are preserved;
the owned output is marked and rewound; every scratch cell, including its
temporary origin marker, is erased and its head returned to its origin.

Prepared for David Arias with substantial OpenAI Codex assistance.  The
two-piece stream permutation is inherited from the retained ordered-affine
lemma; this file supplies its finite-control, fully charged realization.

Instruction ledger for this exact table (either direction), with
V=P*Q*Q*G*S and c(N)=24N-7*popcount(N)+15*bit_length(N)+12:

  T = sum(c(N) for N in (P,Q,G,S)) + 36V + 20P Q^2 G
      + 28P QG + 50P Q + 19P + 7Q + G + S + 104 <= 442V.

This is a proof annotation, never evaluated by the controller.  Each rewind
from relative head h costs exactly 3h transitions.  One record costs
(11+consume)S+4, except the first record saves 3S.  Summing the two phases
gives 23V+20P Q^2 G+28P QG+50PQ+15P-3G-3S+8; the remaining operations
besides conversion cost 13V+4(P+G+S)+7Q+96.  Since bit_length(N)<=N and
popcount(N)>=1, c(N)<=44N.  Every positive factor above is at most V.

The total visited-cell span, including preserved inputs, output, erased
bucket regions and all markers, is
  3V+P+G+S+2Q+max(bit_length(N))+sum(bit_length(N))+28 <= 41V.
In particular, clearing consumed cells does not remove them from the space
bill.  Both bounds are attained when P=Q=G=S=1.
"""
from machine import Assembler, BLANK, LEFT, RIGHT, ZERO, ONE, UNIT
from counters import emit_binary_to_unary, emit_rewind


SOURCE, OUTPUT, SPLIT_A, SPLIT_B = 0, 1, 2, 3
P_INPUT, Q_INPUT, G_INPUT, S_INPUT = 4, 5, 6, 7
P_COUNT, G_COUNT, S_COUNT = 8, 9, 10
LEFT_LENGTH, RIGHT_LENGTH, BINARY_WORK = 11, 12, 13
TAPE_COUNT = 14
INPUT_TAPES = (SOURCE, P_INPUT, Q_INPUT, G_INPUT, S_INPUT)
SCRATCH_TAPES = (SPLIT_A, SPLIT_B, P_COUNT, G_COUNT, S_COUNT,
                 LEFT_LENGTH, RIGHT_LENGTH, BINARY_WORK)
TAPE_NAMES = ("source", "output", "split_a", "split_b", "P_input",
              "Q_input", "G_input", "S_input", "P_count", "G_count",
              "S_count", "Q_minus_x", "x", "binary_work")


def _seek_right(asm, tape, fail, prefix):
    """Start at the first unary symbol; finish on its RIGHT marker."""
    loop, advance, done = (asm.fresh(prefix + suffix)
                           for suffix in ("_loop", "_advance", "_done"))
    asm.label(loop)
    asm.branch(tape, {UNIT: advance, RIGHT: done}, fail)
    asm.label(advance)
    asm.move(tape, 1)
    asm.goto(loop)
    asm.label(done)


def _copy_record(asm, source, destination, consume, fail, prefix):
    """Copy one S-bit record; S_COUNT starts/ends at a fixed local marker.

    Both payload heads advance.  The source is erased exactly when consume
    is true.  There is one finite branch on each opaque source bit.
    """
    emit_rewind(asm, S_COUNT, prefix + "_rewind_S")
    loop, read, advance, done = (asm.fresh(prefix + suffix)
                                for suffix in ("_loop", "_read", "_advance", "_done"))
    zero, one = asm.fresh(prefix + "_zero"), asm.fresh(prefix + "_one")
    asm.label(loop)
    asm.branch(S_COUNT, {UNIT: read, RIGHT: done}, fail)
    asm.label(read)
    asm.branch(source, {ZERO: zero, ONE: one}, fail)
    for label, symbol in ((zero, ZERO), (one, ONE)):
        asm.label(label)
        asm.write(destination, symbol)
        if consume:
            asm.write(source, BLANK)
        asm.goto(advance)
    asm.label(advance)
    asm.move(source, 1)
    asm.move(destination, 1)
    asm.move(S_COUNT, 1)
    asm.goto(loop)
    asm.label(done)


def _segment(asm, length, source, destination, consume, fail, prefix):
    """Copy length*S cells; the unary length may be zero."""
    emit_rewind(asm, length, prefix + "_rewind_length")
    loop, record, done = (asm.fresh(prefix + suffix)
                         for suffix in ("_loop", "_record", "_done"))
    asm.label(loop)
    asm.branch(length, {UNIT: record, RIGHT: done}, fail)
    asm.label(record)
    _copy_record(asm, source, destination, consume, fail, prefix + "_record")
    asm.move(length, 1)
    asm.goto(loop)
    asm.label(done)


def _decrease_left_increase_right(asm, fail, prefix):
    """At right markers, change (L,R) to (L-1,R+1), for L>=1."""
    unit = asm.fresh(prefix + "_unit")
    asm.write(LEFT_LENGTH, BLANK)
    asm.move(LEFT_LENGTH, -1)
    asm.branch(LEFT_LENGTH, {UNIT: unit}, fail)
    asm.label(unit)
    asm.write(LEFT_LENGTH, RIGHT)
    asm.write(RIGHT_LENGTH, UNIT)
    asm.move(RIGHT_LENGTH, 1)
    asm.write(RIGHT_LENGTH, RIGHT)


def _reset_lengths(asm, fail, prefix):
    """Restore (L,R)=(Q,0) from (0,Q), both heads at right markers.

    Transfer one unary mark at a time.  Every overwritten old right marker
    is erased, so no former tail survives beyond either returned head.
    """
    loop, unit, zero, done = (asm.fresh(prefix + suffix)
                             for suffix in ("_loop", "_unit", "_zero", "_done"))
    asm.label(loop)
    asm.move(RIGHT_LENGTH, -1)
    asm.branch(RIGHT_LENGTH, {UNIT: unit, LEFT: zero}, fail)
    asm.label(unit)
    asm.move(RIGHT_LENGTH, 1)
    asm.write(RIGHT_LENGTH, BLANK)
    asm.move(RIGHT_LENGTH, -1)
    asm.write(RIGHT_LENGTH, RIGHT)
    asm.write(LEFT_LENGTH, UNIT)
    asm.move(LEFT_LENGTH, 1)
    asm.write(LEFT_LENGTH, RIGHT)
    asm.goto(loop)
    asm.label(zero)
    asm.move(RIGHT_LENGTH, 1)
    asm.goto(done)
    asm.label(done)


def _phase(asm, operations, fail, prefix):
    """One complete P,x,G traversal; operations are two compile-time segments.

    At each x, LEFT_LENGTH=Q-x and RIGHT_LENGTH=x.  Their endpoints encode
    x: no separate x value, host counter, comparison, or multiplication is
    used.  Each phase returns (Q,0), ready for the next complete phase.
    """
    emit_rewind(asm, P_COUNT, prefix + "_rewind_P")
    p_loop, x_loop, g_loop, body, next_x, positive, zero, done = (
        asm.fresh(prefix + suffix) for suffix in
        ("_P", "_x", "_G", "_body", "_next_x", "_positive", "_zero", "_done"))
    asm.label(p_loop)
    asm.branch(P_COUNT, {UNIT: x_loop, RIGHT: done}, fail)
    asm.label(x_loop)
    emit_rewind(asm, G_COUNT, prefix + "_rewind_G")
    asm.label(g_loop)
    asm.branch(G_COUNT, {UNIT: body, RIGHT: next_x}, fail)
    asm.label(body)
    for index, (length, source, destination, consume) in enumerate(operations):
        _segment(asm, length, source, destination, consume, fail,
                 prefix + "_segment_" + str(index))
    asm.move(G_COUNT, 1)
    asm.goto(g_loop)
    asm.label(next_x)
    _decrease_left_increase_right(asm, fail, prefix + "_increment_x")
    asm.move(LEFT_LENGTH, -1)
    asm.branch(LEFT_LENGTH, {UNIT: positive, LEFT: zero}, fail)
    asm.label(positive)
    asm.move(LEFT_LENGTH, 1)
    asm.goto(x_loop)
    asm.label(zero)
    asm.move(LEFT_LENGTH, 1)
    _reset_lengths(asm, fail, prefix + "_restore_lengths")
    asm.move(P_COUNT, 1)
    asm.goto(p_loop)
    asm.label(done)


def _erase_back_to_origin(asm, tape, prefix):
    """Clear all cells through the temporary LEFT marker, finishing on it.

    Caller invariant: every nonblank cell is at or left of the current head.
    This holds even for the already consumed split streams and the shrunken
    unary lengths; all old tail cells have already been erased.
    """
    loop, erase, origin = (asm.fresh(prefix + suffix)
                          for suffix in ("_loop", "_erase", "_origin"))
    asm.label(loop)
    asm.branch(tape, {LEFT: origin}, erase)
    asm.label(erase)
    asm.write(tape, BLANK)
    asm.move(tape, -1)
    asm.goto(loop)
    asm.label(origin)
    asm.write(tape, BLANK)


def build_program(inverse=False):
    """Return one finite controller, independent of all runtime extents.

    inverse is a compile-time choice between two fixed tables.  It is not
    an encoded coefficient or a runtime callback.  The program accepts
    arbitrary positive canonical binary P,Q,G,S, including Q=1.
    """
    if type(inverse) is not bool:
        raise ValueError("inverse is one fixed Boolean program choice")
    asm = Assembler(TAPE_COUNT)
    fail = asm.fresh("invalid_kernel_state")
    for tape in (OUTPUT,) + SCRATCH_TAPES:
        initialize = asm.fresh("initialize_" + TAPE_NAMES[tape])
        asm.branch(tape, {BLANK: initialize}, fail)
        asm.label(initialize)
        asm.write(tape, LEFT)
        asm.move(tape, 1)
    for source, unary, name in ((P_INPUT, P_COUNT, "P"),
                                (Q_INPUT, LEFT_LENGTH, "Q"),
                                (G_INPUT, G_COUNT, "G"),
                                (S_INPUT, S_COUNT, "S")):
        emit_binary_to_unary(asm, source, BINARY_WORK, unary, "prepare_" + name)
    asm.write(RIGHT_LENGTH, RIGHT)
    _seek_right(asm, LEFT_LENGTH, fail, "initial_left_end")
    gather = ((LEFT_LENGTH, SOURCE, SPLIT_A, False),
              (RIGHT_LENGTH, SOURCE, SPLIT_B, False))
    emit = ((RIGHT_LENGTH, SPLIT_B, OUTPUT, True),
            (LEFT_LENGTH, SPLIT_A, OUTPUT, True))
    if inverse:
        gather, emit = tuple(reversed(gather)), tuple(reversed(emit))
    _phase(asm, gather, fail, "gather")
    gathered = asm.fresh("gathered_exact_source")
    asm.branch(SOURCE, {RIGHT: gathered}, fail)
    asm.label(gathered)
    for tape in (SPLIT_A, SPLIT_B):
        asm.write(tape, RIGHT)
        emit_rewind(asm, tape, "split_start_" + str(tape))
    _phase(asm, emit, fail, "emit")
    for tape in (SPLIT_A, SPLIT_B):
        complete = asm.fresh("complete_split_" + str(tape))
        asm.branch(tape, {RIGHT: complete}, fail)
        asm.label(complete)
    asm.write(OUTPUT, RIGHT)
    emit_rewind(asm, SOURCE, "return_source")
    emit_rewind(asm, OUTPUT, "return_output")
    for tape in SCRATCH_TAPES:
        _erase_back_to_origin(asm, tape, "clear_" + TAPE_NAMES[tape])
    asm.halt()
    asm.label(fail)
    asm.reject("ordered shear shape, bit alphabet, or scratch invariant")
    return asm.finish()
