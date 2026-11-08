"""Literal finite child-shape grants for the PR6719 router.

Fixed template L>=2; physical binary inputs A_parent,H,R_parent. No runtime
host arithmetic computes either child grant. Arithmetic and quotient facts
are standard and retain predecessor credit; the new edge is this emitted
grant ABI and its direct instruction-level connection to the router.

thu-nmrc, substantial OpenAI Codex assistance; Apache-2.0.
David Arias's machine/counter and the PR6719 router are unchanged inputs.
"""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


m = load('machine', 'inputs/PR6719/machine.py')
c = load('counters', 'inputs/PR6719/counters.py')
r = load('router', 'inputs/PR6719/router.py')

A_INPUT, H_INPUT, R_INPUT = 0, 1, 2
A_CHILD, R_CHILD = 3, 4
A_UNARY, H_UNARY, R_UNARY, WORK = 5, 6, 7, 8


def increment(asm, tape, fail, prefix):
    """Unsigned canonical LSB-first counter; RIGHT alone is temporary zero.

    The head starts/returns at1. All data-dependent carries are emitted.
    Across k increments this costs at most18k microinstructions.
    """
    loop, zero, one, end, rewind = (asm.fresh(prefix+s) for s in
                                   ('_loop','_zero','_one','_end','_rewind'))
    asm.label(loop)
    asm.branch(tape, {m.ZERO: zero, m.ONE: one, m.RIGHT: end}, fail)
    asm.label(one)
    asm.write(tape, m.ZERO); asm.move(tape, 1); asm.goto(loop)
    asm.label(zero)
    asm.write(tape, m.ONE); asm.goto(rewind)
    asm.label(end)
    asm.write(tape, m.ONE); asm.move(tape, 1); asm.write(tape, m.RIGHT)
    asm.goto(rewind)
    asm.label(rewind)
    c.emit_rewind(asm, tape, prefix+'_return')


def marked_blank(asm, tape, fail, prefix, zero=False):
    empty = asm.fresh(prefix+'_empty')
    asm.branch(tape, {m.BLANK: empty}, fail); asm.label(empty)
    asm.write(tape, m.LEFT); asm.move(tape, 1)
    if zero:
        empty = asm.fresh(prefix+'_zero_empty')
        asm.branch(tape, {m.BLANK: empty}, fail); asm.label(empty)
        asm.write(tape, m.RIGHT)


def retire_unary_at_end(asm, tape, fail, prefix):
    """The head is at RIGHT; erase every visited guide cell and LEFT."""
    end, loop, more, done = (asm.fresh(prefix+s) for s in
                             ('_end','_loop','_more','_done'))
    asm.branch(tape, {m.RIGHT: end}, fail); asm.label(end)
    asm.write(tape, m.BLANK); asm.move(tape, -1)
    asm.label(loop)
    asm.branch(tape, {m.UNIT: more, m.LEFT: done}, fail)
    asm.label(more)
    asm.write(tape, m.BLANK); asm.move(tape, -1); asm.goto(loop)
    asm.label(done); asm.write(tape, m.BLANK)


def build(low_types):
    """Nine fixed tapes; A divisible by L*H; outputs A/(L*H),H*R.

    Inputs use the unchanged PR2776 positive canonical binary ABI, heads1.
    Outputs/scratch begin blank at local origin0. The table receives only L.
    """
    m.need(type(low_types) is int and low_types >= 2, 'fixed integer L>=2')
    a = m.Assembler(9)
    fail = a.fresh('invalid_descriptor_or_work')
    for tape in (A_CHILD, R_CHILD):
        marked_blank(a, tape, fail, 'output', zero=True)
    for tape in (A_UNARY, H_UNARY, R_UNARY, WORK):
        marked_blank(a, tape, fail, 'workspace')
    for source, unary in ((A_INPUT,A_UNARY),(H_INPUT,H_UNARY),(R_INPUT,R_UNARY)):
        c.emit_binary_to_unary(a, source, WORK, unary, 'shape')

    # Consume exactly L complete H-guides before each quotient increment.
    group, nonempty, quotient_done = (a.fresh(s) for s in
                                     ('group','group_nonempty','quotient_done'))
    a.label(group)
    a.branch(A_UNARY, {m.UNIT: nonempty, m.RIGHT: quotient_done}, fail)
    a.label(nonempty)
    for low in range(low_types):
        c.emit_rewind(a, H_UNARY, 'H_for_fixed_low_'+str(low))
        loop, take, advance, done = (a.fresh(s) for s in
                                    ('H_loop','take_A','advance_A_H','H_done'))
        a.label(loop)
        a.branch(H_UNARY, {m.UNIT: take, m.RIGHT: done}, fail)
        a.label(take); a.branch(A_UNARY, {m.UNIT: advance}, fail)
        a.label(advance)
        a.move(A_UNARY, 1); a.move(H_UNARY, 1); a.goto(loop)
        a.label(done)
    increment(a, A_CHILD, fail, 'quotient_increment')
    a.goto(group)
    a.label(quotient_done)

    # H complete R-guides, with one binary increment per actual pair.
    c.emit_rewind(a, H_UNARY, 'product_H')
    outer, begin, inner, take, advance, next_H, done = (a.fresh(s) for s in
        ('product','product_R_begin','product_R','product_take',
         'product_advance','product_next_H','product_done'))
    a.label(outer)
    a.branch(H_UNARY, {m.UNIT: begin, m.RIGHT: done}, fail)
    a.label(begin); c.emit_rewind(a, R_UNARY, 'product_R_return')
    a.label(inner)
    a.branch(R_UNARY, {m.UNIT: take, m.RIGHT: next_H}, fail)
    a.label(take); increment(a, R_CHILD, fail, 'product_increment')
    a.label(advance); a.move(R_UNARY, 1); a.goto(inner)
    a.label(next_H); a.move(H_UNARY, 1); a.goto(outer)
    a.label(done)
    for tape in (A_UNARY, H_UNARY, R_UNARY):
        retire_unary_at_end(a, tape, fail, 'erase_guide')
    # Counter source restoration leaves WORK empty at1, retaining only LEFT0.
    a.move(WORK, -1)
    left = a.fresh('work_left')
    a.branch(WORK, {m.LEFT: left}, fail); a.label(left)
    a.write(WORK, m.BLANK)
    a.halt()
    a.label(fail); a.reject('positive canonical inputs, exact L*H divisor, blank owned work')
    return a.finish()


def linked_split(low_types):
    """One literal program: produce both grants, then the actual child split.

    The source child packet is already present at fixed role L+9. Appending
    finite tables here is compile-time only, with no runtime interpreter call.
    """
    shape, split = build(low_types), r.build(low_types)
    offset = len(shape.instructions)
    p = r.ports(low_types)
    mapping = {bank: 9+bank for bank in p['banks']}
    mapping.update({p['source']:low_types+9, p['output']:low_types+10,
                    p['repeats_input']:A_CHILD, p['block_input']:R_CHILD,
                    p['repeats']:A_UNARY, p['block']:H_UNARY,
                    p['binary_work']:WORK})
    rows = [('goto',offset+split.entry) if row[0]=='halt' else row
            for row in shape.instructions]
    for row in split.instructions:
        op = row[0]
        if op == 'branch':
            rows.append((op,mapping[row[1]],tuple((v,k+offset)for v,k in row[2]),row[3]+offset))
        elif op in ('write','move'):
            rows.append((op,mapping[row[1]],row[2]))
        elif op == 'goto':
            rows.append((op,row[1]+offset))
        else:
            rows.append(row)
    return m.Program(tuple(rows), low_types+11, shape.entry)


def retire_delivered(low_types, linked=False):
    """Explicit fixture consumer: retire delivered grants and owned copies.

    A production consumer may keep the grants for the matching merge. This
    separate finite table records their actual eventual erasure cost instead
    of granting an uncharged reset to the producer.
    """
    m.need(type(low_types) is int and low_types>=2 and type(linked) is bool,
           'fixed consumer template')
    a=m.Assembler(low_types+11 if linked else 9)
    fail=a.fresh('consumer_invalid_packet')
    roles=(A_CHILD,R_CHILD)+(tuple(range(9,9+low_types)) if linked else ())
    for tape in roles:
        loop,more,end=(a.fresh(s)for s in ('consume','consume_bit','consume_end'))
        a.label(loop);a.branch(tape,{m.ZERO:more,m.ONE:more,m.RIGHT:end},fail)
        a.label(more);a.write(tape,m.BLANK);a.move(tape,1);a.goto(loop)
        a.label(end);a.write(tape,m.BLANK)
        c.emit_rewind(a,tape,'consumer_rewind')
        a.move(tape,-1);a.write(tape,m.BLANK)
    a.halt();a.label(fail);a.reject('delivered canonical binary packets')
    return a.finish()
