#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Finite binary-to-unary setup; source descriptors remain unchanged.

Input: canonical positive LSB-first source, and two distinct marked-empty
scratch tapes, all heads at1. Output: UNIT^N RIGHT on unary, empty scratch,
all three heads at1. Every data-dependent operation is emitted microcode.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
from machine import BLANK, LEFT, RIGHT, ZERO, ONE, UNIT


def emit_rewind(asm, tape, prefix="rewind"):
    loop, done = asm.fresh(prefix+"_loop"), asm.fresh(prefix+"_done")
    asm.move(tape, -1)
    asm.label(loop)
    asm.branch(tape, {LEFT: done}, loop+"_move")
    asm.label(loop+"_move")
    asm.move(tape, -1)
    asm.goto(loop)
    asm.label(done)
    asm.move(tape, 1)


def emit_binary_to_unary(asm, source, scratch, unary, prefix="binary_to_unary"):
    if len({source, scratch, unary}) != 3:
        raise ValueError("binary conversion requires three distinct tapes")
    tag = asm.fresh(prefix)
    def name(s):
        return tag+"_"+s
    fail = name("reject")
    # Copy while remembering the last bit in one finite control state.
    # At RIGHT, the only accepted last bit is ONE: canonical and positive.
    asm.goto(name("first"))
    asm.label(name("first"))
    asm.branch(source, {ZERO: name("copy_zero"), ONE: name("copy_one")}, fail)
    for bit, label in ((ZERO,"zero"),(ONE,"one")):
        asm.label(name("copy_"+label))
        asm.branch(scratch, {BLANK: name("write_"+label)}, fail)
        asm.label(name("write_"+label))
        asm.write(scratch, bit)
        asm.move(scratch, 1)
        asm.move(source, 1)
        asm.goto(name("after_"+label))
        asm.label(name("after_"+label))
        cases = {ZERO: name("copy_zero"), ONE: name("copy_one")}
        if bit == ONE:
            cases[RIGHT] = name("copied")
        asm.branch(source, cases, fail)
    asm.label(name("copied"))
    asm.branch(scratch, {BLANK: name("write_end")}, fail)
    asm.label(name("write_end"))
    asm.write(scratch, RIGHT)
    emit_rewind(asm, source, name("source"))
    emit_rewind(asm, scratch, name("scratch"))
    # One unary mark per positive countdown value. Ripple carries are paid
    # by actual moves; shrinking the top avoids scanning a padded word.
    asm.label(name("next_unit"))
    asm.branch(unary, {BLANK: name("append_unit")}, fail)
    asm.label(name("append_unit"))
    asm.write(unary, UNIT)
    asm.move(unary, 1)
    asm.label(name("ripple"))
    asm.branch(scratch, {ZERO: name("borrow"), ONE: name("found_one")}, fail)
    asm.label(name("borrow"))
    asm.write(scratch, ONE)
    asm.move(scratch, 1)
    asm.goto(name("ripple"))
    asm.label(name("found_one"))
    asm.write(scratch, ZERO)
    asm.move(scratch, 1)
    asm.branch(scratch, {RIGHT: name("shrink"), ZERO: name("rewind"), ONE: name("rewind")}, fail)
    asm.label(name("rewind"))
    emit_rewind(asm, scratch, name("countdown"))
    asm.goto(name("next_unit"))
    asm.label(name("shrink"))
    asm.write(scratch, BLANK)
    asm.move(scratch, -1)
    asm.write(scratch, RIGHT)
    asm.move(scratch, -1)
    asm.branch(scratch, {LEFT: name("zero"), ONE: name("top_one")}, fail)
    asm.label(name("top_one"))
    asm.move(scratch, 1)
    emit_rewind(asm, scratch, name("shrunken"))
    asm.goto(name("next_unit"))
    asm.label(name("zero"))
    asm.move(scratch, 1)
    asm.write(scratch, BLANK)
    asm.write(unary, RIGHT)
    emit_rewind(asm, unary, name("unary"))
    asm.goto(name("done"))
    asm.label(fail)
    asm.reject("positive canonical binary extent and empty conversion workspace")
    asm.label(name("done"))
