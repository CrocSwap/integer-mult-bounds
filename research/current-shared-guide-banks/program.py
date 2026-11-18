"""Emit one fixed guide producer, two source consumers and a retire program."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parents[1] / 'research/delayed-cover-physical-batch-routing/core'
sys.path.insert(0, str(RUNTIME))
from machine import Assembler, BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK
from counters import emit_binary_to_unary, emit_rewind
sys.path.insert(0, str(HERE / 'source'))
import banks

N, W, WORK, ROWS, WIDTH, GUIDE, TARGET = range(7)
ENCODE = {('left', None): LEFT, ('right', None): RIGHT,
          ('cell', '0'): ZERO, ('cell', ':'): UNIT,
          ('cell', '|'): MARK, ('cell', '_'): BLANK}
PAYLOAD = {'0': ZERO, ':': UNIT, '|': MARK, '_': BLANK}


def erase(asm, tape, symbols):
    """Erase a marked body and both markers; return to its blank origin."""
    loop, cell, end, fail = [asm.fresh('erase_' + name) for name in ('loop', 'cell', 'end', 'fail')]
    asm.label(loop)
    asm.branch(tape, {**{s: cell for s in symbols}, RIGHT: end}, fail)
    asm.label(cell)
    asm.write(tape, BLANK)
    asm.move(tape, 1)
    asm.goto(loop)
    asm.label(end)
    asm.write(tape, BLANK)
    emit_rewind(asm, tape)
    asm.move(tape, -1)
    asm.write(tape, BLANK)
    done = asm.fresh('erase_done')
    asm.goto(done)
    asm.label(fail)
    asm.reject('complete marked body')
    asm.label(done)


def producer():
    asm = Assembler(7)
    for tape in (WORK, ROWS, WIDTH):
        asm.write(tape, LEFT)
        asm.move(tape, 1)
    emit_binary_to_unary(asm, N, WORK, ROWS, 'rows')
    emit_binary_to_unary(asm, W, WORK, WIDTH, 'width')
    asm.write(GUIDE, LEFT)
    asm.move(GUIDE, 1)
    asm.label('next_record')
    asm.branch(ROWS, {UNIT: 'record', RIGHT: 'finished'}, 'bad_rows')
    asm.label('record')
    for component in ('real', 'imaginary'):
        loop, cell, done = [asm.fresh(component + '_' + name) for name in ('loop', 'cell', 'done')]
        asm.label(loop)
        asm.branch(WIDTH, {UNIT: cell, RIGHT: done}, 'bad_width')
        asm.label(cell)
        asm.write(GUIDE, ZERO)
        asm.move(GUIDE, 1)
        asm.move(WIDTH, 1)
        asm.goto(loop)
        asm.label(done)
        emit_rewind(asm, WIDTH)
        asm.write(GUIDE, UNIT if component == 'real' else MARK)
        asm.move(GUIDE, 1)
    asm.write(GUIDE, BLANK)
    asm.move(GUIDE, 1)
    asm.move(ROWS, 1)
    asm.goto('next_record')
    asm.label('finished')
    asm.write(GUIDE, RIGHT)
    emit_rewind(asm, GUIDE)
    asm.move(GUIDE, -1)
    emit_rewind(asm, ROWS)
    erase(asm, ROWS, (UNIT,))
    erase(asm, WIDTH, (UNIT,))
    asm.move(WORK, -1)
    asm.write(WORK, BLANK)
    asm.halt()
    asm.label('bad_rows')
    asm.reject('positive unary record count')
    asm.label('bad_width')
    asm.reject('positive unary component width')
    return asm.finish()


def retire():
    asm = Assembler(7)
    asm.move(GUIDE, 1)
    erase(asm, GUIDE, (ZERO, UNIT, MARK, BLANK))
    asm.halt()
    return asm.finish()


def consumer(operation):
    source = banks.graph(operation)
    asm = Assembler(7)
    for state in ('start', 'out', 'back'):
        cases = {token: source[state, *token] for token in sorted(ENCODE, key=ENCODE.get)
                 if (state, *token) in source}
        labels = {token: asm.fresh(state + '_action') for token in cases}
        asm.label(state)
        asm.branch(GUIDE, {ENCODE[t]: labels[t] for t in cases}, 'bad_guide')
        for token, (next_state, write, move) in cases.items():
            asm.label(labels[token])
            if write is not None:
                asm.write(TARGET, PAYLOAD[write])
            if move:
                asm.move(GUIDE, move)
                asm.move(TARGET, move)
            asm.goto(next_state)
    asm.label('done')
    asm.halt()
    asm.label('bad_guide')
    asm.reject('current flat zero guide')
    return asm.finish('start')


def build():
    return {'produce': producer(), 'INIT': consumer('INIT'),
            'CLEAR': consumer('CLEAR'), 'retire': retire()}
