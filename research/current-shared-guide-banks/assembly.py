"""Link one produced ruler to the fixed native reset schedule."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import program as guide
from machine import Assembler, need
from counters import emit_binary_to_unary, emit_rewind
import word


def source_schedule():
    _, native = word.words()
    sites = guide.banks.plan(native)
    need(len(sites) == 234, 'current native lifetime count')
    events = [(site[1], 234 + ordinal, 'INIT') for ordinal, site in enumerate(sites)]
    events += [(site[3], 234 + ordinal, 'CLEAR') for ordinal, site in enumerate(sites)]
    return sorted(events)


def link(asm, program, final=False):
    """Relocate fixed instructions and connect each halt to the next phase."""
    need(program.entry == 0 and program.tapes == 7, 'retained program boundary')
    prefix = asm.fresh('linked')
    label = lambda pc: prefix + '_' + str(pc)
    end = prefix + '_end'
    for pc, row in enumerate(program.instructions):
        asm.label(label(pc))
        op = row[0]
        if op == 'branch':
            asm.branch(row[1], {symbol: label(target) for symbol, target in row[2]}, label(row[3]))
        elif op == 'write':
            asm.write(row[1], row[2])
        elif op == 'move':
            asm.move(row[1], row[2])
        elif op == 'goto':
            asm.goto(label(row[1]))
        elif op == 'reject':
            asm.reject(row[1])
        elif final:
            asm.halt()
        else:
            asm.goto(end)
    asm.label(end)


def crosses(asm, direction):
    outer, ruler, step, turn, done = [asm.fresh('cross_' + name)
                                     for name in ('outer', 'ruler', 'step', 'turn', 'done')]
    asm.label(outer)
    asm.branch(guide.ROWS, {guide.UNIT: ruler, guide.RIGHT: done}, 'bad_control')
    asm.label(ruler)
    symbols = {symbol: step for symbol in guide.ENCODE.values() if symbol != guide.RIGHT}
    asm.branch(guide.GUIDE, {**symbols, guide.RIGHT: turn}, 'bad_control')
    asm.label(step)
    asm.move(guide.TARGET, direction)
    asm.move(guide.GUIDE, 1)
    asm.goto(ruler)
    asm.label(turn)
    asm.move(guide.TARGET, direction)
    emit_rewind(asm, guide.GUIDE)
    asm.move(guide.GUIDE, -1)
    asm.move(guide.ROWS, 1)
    asm.goto(outer)
    asm.label(done)
    emit_rewind(asm, guide.ROWS)


def reset(asm, slot, operation):
    need(slot > 0 and operation in ('INIT', 'CLEAR'), 'fixed positive bank request')
    # The bank number is fixed by the source program before N and W exist.
    asm.write(guide.WIDTH, guide.LEFT)
    asm.move(guide.WIDTH, 1)
    for bit in range(slot.bit_length()):
        asm.write(guide.WIDTH, guide.ONE if slot >> bit & 1 else guide.ZERO)
        asm.move(guide.WIDTH, 1)
    asm.write(guide.WIDTH, guide.RIGHT)
    emit_rewind(asm, guide.WIDTH)
    for tape in (guide.WORK, guide.ROWS):
        asm.write(tape, guide.LEFT)
        asm.move(tape, 1)
    emit_binary_to_unary(asm, guide.WIDTH, guide.WORK, guide.ROWS)
    crosses(asm, 1)
    link(asm, guide.consumer(operation))
    crosses(asm, -1)
    guide.erase(asm, guide.ROWS, (guide.UNIT,))
    guide.erase(asm, guide.WIDTH, (guide.ZERO, guide.ONE))
    asm.move(guide.WORK, -1)
    asm.write(guide.WORK, guide.BLANK)


def build(schedule):
    asm = Assembler(7)
    link(asm, guide.producer())
    blocks = []
    for clock, slot, operation in schedule:
        start = len(asm.instructions)
        reset(asm, slot, operation)
        blocks.append({'clock': clock, 'slot': slot, 'operation': operation,
                       'start': start, 'end': len(asm.instructions)})
    link(asm, guide.retire(), final=True)
    asm.label('bad_control')
    asm.reject('complete immutable ruler and unary bank counter')
    return asm.finish(), blocks
