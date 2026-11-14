"""Literal current-header/current-wire query and physical Boolean consumption.

Fixed graph constructors run offline. Apache-2.0; substantial OpenAI assistance.
The arithmetic predicate is the exact credited B4 graph, itself based on #7504.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ALPHABET = ('_', 'L', 'R', '|', '0', '1')
H, S, A, J, X, OUT = range(6)
INPUTS = tuple(range(6))
PRIVATE = tuple(range(6, 14))
SOURCE_H, SOURCE_S, SOURCE_A, SOURCE_J, SOURCE_X, WIDTH = range(14, 20)
TAPES = 20
SWITCH_SHA = '89fe721a2920943dbc58eefe7f855ac1573e653e8af3b029c9c2ef838fdeac40'


def source():
    path = HERE/'inputs/switch/switch.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != SWITCH_SHA:
        raise ValueError('frozen direct-switch source drift')
    module = types.ModuleType('_current_crt_switch_core')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


class Builder:
    def __init__(self):
        self.code, self.labels, self.serial = [], {}, 0

    def fresh(self, stem='q'):
        self.serial += 1
        return stem+'_'+str(self.serial)

    def mark(self, name):
        if name in self.labels:
            raise ValueError('duplicate graph label')
        self.labels[name] = len(self.code)

    def op(self, *args):
        self.code.append(args)

    def jump(self, target):
        self.op('J', target)

    def read(self, tape, branches):
        self.op('R', tape, {symbol: branches.get(symbol, 'ADAPTER_FAIL')
                           for symbol in ALPHABET})

    def expect(self, tape, symbol):
        after = self.fresh('expected')
        self.read(tape, {symbol: after})
        self.mark(after)

    def rewind(self, tape):
        loop, back, done = (self.fresh(stem) for stem in ('rewind', 'left', 'origin'))
        self.mark(loop)
        self.read(tape, {s: done if s == 'L' else back for s in ALPHABET})
        self.mark(back)
        self.op('M', tape, -1)
        self.jump(loop)
        self.mark(done)

    def body(self, tape):
        self.rewind(tape)
        self.op('M', tape, 1)

    def copy_height(self):
        self.op('M', SOURCE_H, 1)
        loop, done = self.fresh('height'), self.fresh('height_copied')
        zero, one = self.fresh('height0'), self.fresh('height1')
        self.mark(loop)
        self.read(SOURCE_H, {'0': zero, '1': one, 'R': done})
        for bit, label in (('0', zero), ('1', one)):
            self.mark(label)
            self.op('W', H, bit)
            self.op('M', H, 1)
            self.op('M', SOURCE_H, 1)
            self.jump(loop)
        self.mark(done)
        self.rewind(SOURCE_H)
        self.op('M', H, -1)
        trim, erase, trimmed = (self.fresh(stem) for stem in ('trim', 'trim0', 'canonical'))
        self.mark(trim)
        self.read(H, {'0': erase, '1': trimmed})
        self.mark(erase)
        self.op('W', H, '_')
        self.op('M', H, -1)
        self.jump(trim)
        self.mark(trimmed)
        self.body(H)

    def copy_field(self, source_tape, target, *, offset=False, address=False):
        """WIDTH has h marks, exactly one temporarily '|'; copy h+1 bits."""
        self.op('M', source_tape, 1)
        self.op('M', WIDTH, 1)
        loop, digit, suffix = (self.fresh(stem) for stem in ('field', 'digit', 'suffix'))
        zero, one = self.fresh('copy0'), self.fresh('copy1')
        self.mark(loop)
        self.read(WIDTH, {'1': digit, '|': digit, 'R': suffix})
        self.mark(digit)
        self.read(source_tape, {'0': zero, '1': one})
        for bit, label in (('0', zero), ('1', one)):
            self.mark(label)
            self.op('W', target, bit)
            for t in (target, source_tape, WIDTH):
                self.op('M', t, 1)
            self.jump(loop)
        self.mark(suffix)
        if address:
            self.expect(source_tape, 'R')
            self.op('W', target, '0')
            self.op('M', target, 1)
        else:
            extra0, extra1, copied = (self.fresh(stem) for stem in ('extra0', 'extra1', 'extra_done'))
            self.read(source_tape, {'0': extra0, '1': extra1})
            for bit, label in (('0', extra0), ('1', extra1)):
                self.mark(label)
                self.op('W', target, bit)
                self.op('M', target, 1)
                self.op('M', source_tape, 1)
                self.jump(copied)
            self.mark(copied)
            tail, advance, done = (self.fresh(stem) for stem in ('high_zero', 'high_next', 'field_end'))
            self.mark(tail)
            self.read(source_tape, {'0': advance, '|': done} if offset else {'0': advance, 'R': done})
            self.mark(advance)
            self.op('M', source_tape, 1)
            self.jump(tail)
            self.mark(done)
            if offset:
                self.op('M', source_tape, 1)
                self.expect(source_tape, 'R')
        self.rewind(source_tape)
        self.body(target)
        self.rewind(WIDTH)

    def consume(self, switch_bit, after):
        self.op('M', WIDTH, 1)
        self.op('M', SOURCE_X, 1)
        loop, advance, target = (self.fresh(stem) for stem in ('seek_target', 'next_target', 'target'))
        self.mark(loop)
        self.read(WIDTH, {'1': advance, '|': target})
        self.mark(advance)
        self.op('M', WIDTH, 1)
        self.op('M', SOURCE_X, 1)
        self.jump(loop)
        self.mark(target)
        zero, one, done = (self.fresh(stem) for stem in ('target0', 'target1', 'toggled'))
        self.read(SOURCE_X, {'0': zero, '1': one})
        for bit, label in ((0, zero), (1, one)):
            self.mark(label)
            self.op('W', SOURCE_X, str(bit ^ switch_bit))
            self.jump(done)
        self.mark(done)
        self.op('W', WIDTH, '1')
        self.rewind(SOURCE_X)
        self.jump(after)

    def restore_target(self):
        self.op('M', WIDTH, 1)
        loop, advance, done = (self.fresh(stem) for stem in ('restore_target', 'restore_next', 'restored_target'))
        self.mark(loop)
        self.read(WIDTH, {'1': advance, '|': done})
        self.mark(advance)
        self.op('M', WIDTH, 1)
        self.jump(loop)
        self.mark(done)
        self.op('W', WIDTH, '1')

    def cleanup(self, result):
        for tape in INPUTS:
            self.body(tape)
            loop, erase, done = (self.fresh(stem) for stem in ('clear_input', 'erase_input', 'input_empty'))
            self.mark(loop)
            self.read(tape, {'0': erase, '1': erase, '_': done})
            self.mark(erase)
            self.op('W', tape, '_')
            self.op('M', tape, 1)
            self.jump(loop)
            self.mark(done)
            self.rewind(tape)
            self.op('W', tape, '_')
        for tape in PRIVATE:
            self.op('M', tape, -1)
        self.op('H', result)

    def finish(self):
        table = []
        for instruction in self.code:
            op, *args = instruction
            if op == 'R':
                table.append((op, args[0], {key: self.labels[value] for key, value in args[1].items()}))
            elif op == 'J':
                table.append((op, self.labels[args[0]]))
            else:
                table.append(instruction)
        return tuple(table), dict(self.labels)


def compile_adapter():
    b = Builder()
    for tape in range(14):
        b.expect(tape, '_')
    for tape in (SOURCE_H, SOURCE_S, SOURCE_A, SOURCE_J, SOURCE_X):
        b.expect(tape, 'L')
    b.expect(WIDTH, '1')
    b.op('W', WIDTH, '|')
    b.rewind(WIDTH)
    for tape in INPUTS:
        b.op('W', tape, 'L')
        b.op('M', tape, 1)
    b.copy_height()
    for src, dst in ((SOURCE_S, S), (SOURCE_A, A), (SOURCE_J, J)):
        b.copy_field(src, dst, offset=src == SOURCE_A)
    b.mark('COPY_X_START')
    b.copy_field(SOURCE_X, X, address=True)
    b.mark('COPY_X_END')
    for tape in PRIVATE:
        b.op('M', tape, 1)
    b.mark('CORE_ENTRY')
    code, labels = source().compile_query()
    symbol = {0: '0', 1: '1', 2: '_', 3: 'L', 4: '|'}
    for pc, instruction in enumerate(code):
        b.mark('core_'+str(pc))
        op, *args = instruction
        if op == 'R':
            targets = {symbol[value]: 'core_'+str(target) for value, target in args[1].items()}
            targets['R'] = 'core_'+str(labels['reject'])
            b.read(args[0], targets)
        elif op == 'W':
            b.op('W', args[0], symbol[args[1]])
        elif op == 'M':
            b.op('M', *args)
        elif op == 'J':
            b.jump('core_'+str(args[0]))
        elif op == 'H':
            b.jump('CORE_DONE' if args[0] == 'DONE' else 'CORE_REJECT')
        else:
            raise ValueError('nonliteral predecessor instruction')
    b.mark('CORE_DONE')
    b.read(OUT, {'0': 'CONSUME0', '1': 'CONSUME1'})
    b.mark('CONSUME0')
    b.consume(0, 'CLEAN_DONE')
    b.mark('CONSUME1')
    b.consume(1, 'CLEAN_DONE')
    b.mark('CORE_REJECT')
    b.restore_target()
    b.cleanup('REJECT')
    b.mark('CLEAN_DONE')
    b.cleanup('DONE')
    b.mark('ADAPTER_FAIL')
    b.op('H', 'MALFORMED')
    return b.finish()


def digest(code):
    return sha256(json.dumps(code, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
