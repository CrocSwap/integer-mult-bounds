"""One fixed literal graph for every row of one current CRT wire.

Four fixed control copies share the unchanged B5 twenty-owner point bank.
Constructors execute offline; runtime operations are only R/W/M/J/H.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
POINT_SHA = '3cf2c39145adb91bcb8d40f08ff4e6f9d7ec80008f78bb34092b56effa1e6010'
POINT_GRAPH = '2257055b689e0f88dca29532548639323dc3fa27a6e5150ea6652ed5636e07a2'
ROW, WIDTH, TAPES = 17, 19, 20


def point_source():
    path = HERE/'inputs/point/adapter.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != POINT_SHA:
        raise ValueError('exact B5 adapter source changed')
    module = types.ModuleType('_complete_row_point')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def zero_row(b):
    """Overwrite the complete inactive owned row body, preserving its frame."""
    b.expect(ROW, 'L')
    b.op('M', ROW, 1)
    loop, erase, done = (b.fresh(name) for name in ('zero_row', 'zero_digit', 'zero_end'))
    b.mark(loop)
    b.read(ROW, {'0': erase, '1': erase, 'R': done})
    b.mark(erase)
    b.op('W', ROW, '0')
    b.op('M', ROW, 1)
    b.jump(loop)
    b.mark(done)
    b.rewind(ROW)


def change_row(b, direction):
    """One literal carry/borrow, only after the complete row frame was checked."""
    if direction not in (-1, 1):
        raise ValueError('static counter direction')
    repeated, terminal = ('1', '0') if direction == 1 else ('0', '1')
    b.expect(ROW, 'L')
    b.op('M', ROW, 1)
    loop, carry, finish = (b.fresh(name) for name in ('carry', 'propagate', 'carry_end'))
    b.mark(loop)
    b.read(ROW, {repeated: carry, terminal: finish})
    b.mark(carry)
    b.op('W', ROW, terminal)
    b.op('M', ROW, 1)
    b.jump(loop)
    b.mark(finish)
    b.op('W', ROW, repeated)
    b.rewind(ROW)


def initial(b, inverse):
    name = 'INVERSE' if inverse else 'FORWARD'
    b.mark(name)
    zero_row(b)
    b.expect(WIDTH, 'L')
    b.op('M', WIDTH, 1)
    b.expect(WIDTH, '1')
    if inverse:
        b.op('M', WIDTH, 1)
        loop, step, end = (b.fresh(stem) for stem in ('height_loop', 'height_next', 'height_done'))
        b.mark(loop)
        b.read(WIDTH, {'1': step, 'R': end})
        b.mark(step)
        change_row(b, 1)
        change_row(b, 1)
        b.op('M', WIDTH, 1)
        b.jump(loop)
        b.mark(end)
        b.rewind(WIDTH)
        b.op('M', WIDTH, 1)
    b.jump(name+'_ASC_POINT_0')


def advance(b, name, direction):
    b.mark(name+'_ASC_AFTER')
    b.op('M', WIDTH, 1)
    b.read(WIDTH, {'1': name+'_ASC_UPDATE', 'R': name+'_TURN'})
    b.mark(name+'_TURN')
    b.op('M', WIDTH, -1)
    b.op('M', WIDTH, -1)
    b.read(WIDTH, {'1': name+'_DESC_UPDATE', 'L': 'FINISH'})
    b.mark(name+'_ASC_UPDATE')
    change_row(b, direction)
    b.jump(name+'_ASC_POINT_0')
    b.mark(name+'_DESC_UPDATE')
    change_row(b, direction)
    b.jump(name+'_DESC_POINT_0')
    b.mark(name+'_DESC_AFTER')
    b.op('M', WIDTH, -1)
    b.read(WIDTH, {'1': name+'_DESC_UPDATE', 'L': 'FINISH'})


def embed_point(b, code, mode):
    for pc, instruction in enumerate(code):
        b.mark(mode+'_POINT_'+str(pc))
        op, *args = instruction
        if op == 'R':
            b.read(args[0], {symbol: mode+'_POINT_'+str(target)
                             for symbol, target in args[1].items()})
        elif op == 'J':
            b.jump(mode+'_POINT_'+str(args[0]))
        elif op == 'H' and args[0] == 'DONE':
            b.jump(mode+'_AFTER')
        elif op in ('W', 'M', 'H'):
            b.op(op, *args)
        else:
            raise ValueError('unsupported literal point instruction')


def compile_controller():
    point = point_source()
    code, point_labels = point.compile_adapter()
    if len(code) != 2500 or point.digest(code) != POINT_GRAPH:
        raise ValueError('exact B5 point graph changed')
    b = point.Builder()
    initial(b, False)
    initial(b, True)
    advance(b, 'FORWARD', 1)
    advance(b, 'INVERSE', -1)
    b.mark('FINISH')
    zero_row(b)
    b.op('H', 'DONE')
    b.mark('ADAPTER_FAIL')
    b.op('H', 'MALFORMED')
    modes = ('FORWARD_ASC', 'FORWARD_DESC', 'INVERSE_ASC', 'INVERSE_DESC')
    for mode in modes:
        embed_point(b, code, mode)
    table, labels = b.finish()
    metadata = {'entries': {name: labels[name] for name in ('FORWARD', 'INVERSE')},
                'point_copies': {mode: {'start': labels[mode+'_POINT_0'], 'length': len(code),
                                       'after': labels[mode+'_AFTER']} for mode in modes},
                'point_labels': point_labels, 'tapes': TAPES}
    return table, labels, metadata


def digest(code):
    return sha256(json.dumps(code, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
