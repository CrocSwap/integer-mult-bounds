"""Emit a fixed whole-row graph with a literal address counter.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Jerry Chen supplied the builder. The point graph is retained without edits.
"""

from sources import load

point = load('retained_linear_point', 'retained/pr7735/program.py')
B, L, E = point.B, point.L, point.E
H, S, A, J, ADDRESS, BIT = range(6)
COUNT, ROW = 6, 14


def clear_body(b, tape):
    loop, erase, done = [b.fresh() for _ in range(3)]
    b.mark(loop); b.read(tape, {0: erase, 1: erase, E: erase, B: done})
    b.mark(erase); b.op('W', tape, B); b.op('M', tape, 1); b.jump(loop)
    b.mark(done); b.rewind(tape)
    b.op('M', tape, -1); b.op('W', tape, B); b.op('M', tape, 1)


def compile_row():
    b = point.Builder()
    for tape in (ADDRESS, BIT, COUNT):
        b.op('M', tape, -1); b.op('W', tape, L); b.op('M', tape, 1)
    last0, last1, put0, put1, copied = [b.fresh() for _ in range(5)]
    b.read(H, {0: put0, 1: put1})
    for bit, label, after in ((0, put0, last0), (1, put1, last1)):
        b.mark(label); b.op('W', COUNT, bit); b.op('M', COUNT, 1)
        b.op('M', H, 1); b.jump(after)
    b.mark(last0); b.read(H, {0: put0, 1: put1})
    b.mark(last1); b.read(H, {0: put0, 1: put1, B: copied})
    b.mark(copied); b.op('W', COUNT, E); b.rewind(COUNT); b.rewind(H)
    b.op('W', ADDRESS, 0); b.op('M', ADDRESS, 1)
    loop, append, ready = [b.fresh() for _ in range(3)]
    b.mark(loop); b.read(COUNT, {0: append, 1: append, E: ready})
    b.mark(append); b.op('W', ADDRESS, 0); b.op('M', ADDRESS, 1)
    b.compact_decrement(COUNT); b.jump(loop)
    b.mark(ready); b.rewind(ADDRESS)
    clear_body(b, COUNT)
    b.mark('row_query')
    code, _ = point.compile_query()
    for pc, ins in enumerate(code):
        b.mark('point_' + str(pc))
        if ins[0] == 'R':
            b.op('R', ins[1], {symbol: 'point_' + str(target) for symbol, target in ins[2].items()})
        elif ins[0] == 'J':
            b.jump('point_' + str(ins[1]))
        elif ins[0] == 'H':
            b.jump('row_return' if ins[1] == 'DONE' else 'row_reject')
        else:
            b.op(*ins)
    b.mark('row_return')
    zero, one = b.fresh(), b.fresh()
    b.read(BIT, {0: zero, 1: one})
    for bit, label in ((0, zero), (1, one)):
        b.mark(label); blank = b.fresh(); b.read(ROW, {B: blank}); b.mark(blank)
        b.op('W', ROW, bit); b.op('M', ROW, 1); b.op('W', BIT, B)
        b.jump('increment')
    b.mark('increment')
    carry, stop_carry, more = [b.fresh() for _ in range(3)]
    b.read(ADDRESS, {0: stop_carry, 1: carry})
    b.mark(carry); b.op('W', ADDRESS, 0); b.op('M', ADDRESS, 1); b.jump('increment')
    b.mark(stop_carry); b.op('W', ADDRESS, 1); b.op('M', ADDRESS, 1)
    b.read(ADDRESS, {0: more, 1: more, B: 'row_done'})
    b.mark(more); b.rewind(ADDRESS); b.jump('row_query')
    b.mark('row_done'); b.rewind(ADDRESS)
    clear_body(b, ADDRESS); clear_body(b, BIT); b.rewind(ROW); b.op('H', 'DONE')
    b.mark('row_reject')
    clear_body(b, ADDRESS); clear_body(b, BIT); b.op('H', 'REJECT')
    b.mark('reject'); b.op('H', 'REJECT')
    return b.finish(), dict(b.labels)
