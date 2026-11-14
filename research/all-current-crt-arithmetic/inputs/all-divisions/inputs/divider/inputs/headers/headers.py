"""Literal actual-source leaf headers and unchanged complete destination keys.

All constructors are offline. Runtime is the emitted finite graph only.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
Source record/header semantics are credited #7388, #7352 and predecessors.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
H, S, A, J, WIDTH = 14, 15, 16, 17, 19
SOURCE, AXIS, GUIDE, RESULT, SCRATCH = range(22, 27)
TAPES = 27
NUMERIC_SYMBOLS = ('0', '1', 'L', 'R', '_', 'WE', 'RE', 'ROOT',
                   'STEP', 'VALUE', 'CONSTANT', 'MULTIPLY', 'PAIR', 'RETURN')
ALPHABET = (*NUMERIC_SYMBOLS, '|')
KEY_SHA = '3df218d812d47c1e935715c87d716a7acf7a2bf2610c752ba409a9e29014d8f3'
KEY_GRAPH = '8f5ae62b89de8308eb021920185269d884f07f625a5b3ee10b39f27aee5a393b'


def key_source():
    path = HERE/'inputs/keypass/key_pass.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != KEY_SHA:
        raise ValueError('exact B7 key-pass source changed')
    module = types.ModuleType('_leaf_header_keypass')
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
            raise ValueError('duplicate label')
        self.labels[name] = len(self.code)

    def op(self, *instruction):
        self.code.append(instruction)

    def jump(self, target):
        self.op('J', target)

    def read(self, tape, branches):
        self.op('R', tape, {symbol: branches.get(symbol, 'FAIL') for symbol in ALPHABET})

    def expect(self, tape, symbol):
        after = self.fresh('expected')
        self.read(tape, {symbol: after})
        self.mark(after)

    def rewind(self, tape):
        loop, back, done = (self.fresh(s) for s in ('rewind', 'back', 'origin'))
        self.mark(loop)
        self.read(tape, {s: done if s == 'L' else back for s in ALPHABET})
        self.mark(back)
        self.op('M', tape, -1)
        self.jump(loop)
        self.mark(done)

    def native_rewind(self, tape):
        self.op('M', tape, -1)
        self.rewind(tape)
        self.op('M', tape, 1)

    def blank_emit(self, tape, symbol):
        self.expect(tape, '_')
        self.op('W', tape, symbol)
        self.op('M', tape, 1)

    def end_marker(self, tape):
        self.expect(tape, '_')
        self.op('W', tape, 'R')
        self.rewind(tape)

    def finish(self):
        table = []
        for op, *args in self.code:
            if op == 'R':
                table.append((op, args[0], {symbol: self.labels[target]
                                          for symbol, target in args[1].items()}))
            elif op == 'J':
                table.append((op, self.labels[args[0]]))
            else:
                table.append((op, *args))
        return tuple(table), dict(self.labels)


def zero_header(b, target):
    b.blank_emit(target, 'L')
    loop, digit, done = (b.fresh(s) for s in ('zero', 'zero_digit', 'zero_done'))
    b.mark(loop)
    b.read(GUIDE, {'1': digit, '_': done})
    b.mark(digit)
    b.blank_emit(target, '0')
    b.op('M', GUIDE, 1)
    b.jump(loop)
    b.mark(done)
    b.native_rewind(GUIDE)
    b.end_marker(target)


def skip_record(b, name, continuation):
    """Validate both padded fields using the actual blank width role."""
    b.mark(name)
    b.expect(SCRATCH, '_')
    b.expect(SOURCE, 'ROOT')
    b.op('M', SOURCE, 1)
    b.expect(SOURCE, '1')
    loop, mark, end = (b.fresh(s) for s in ('record_width', 'width_mark', 'width_end'))
    b.mark(loop)
    b.read(SOURCE, {'1': mark, 'WE': end})
    b.mark(mark)
    b.blank_emit(SCRATCH, '1')
    b.op('M', SOURCE, 1)
    b.jump(loop)
    b.mark(end)
    b.op('M', SOURCE, 1)
    b.blank_emit(SCRATCH, 'R')
    b.native_rewind(SCRATCH)
    for delimiter in ('WE', 'RE'):
        field, digit, read, done = (b.fresh(s) for s in ('field', 'field_digit', 'field_read', 'field_done'))
        b.mark(field)
        b.read(SCRATCH, {'1': digit, 'R': done})
        b.mark(digit)
        b.read(SOURCE, {'0': read, '1': read})
        b.mark(read)
        b.op('M', SOURCE, 1)
        b.op('M', SCRATCH, 1)
        b.jump(field)
        b.mark(done)
        b.expect(SOURCE, delimiter)
        b.op('M', SOURCE, 1)
        b.native_rewind(SCRATCH)
    loop, erase, empty = (b.fresh(s) for s in ('clear_width', 'erase_width', 'empty_width'))
    b.mark(loop)
    b.read(SCRATCH, {'1': erase, 'R': erase, '_': empty})
    b.mark(erase)
    b.op('W', SCRATCH, '_')
    b.op('M', SCRATCH, 1)
    b.jump(loop)
    b.mark(empty)
    b.native_rewind(SCRATCH)
    b.jump(continuation)


def increment_height(b):
    """Scan all p digits; carry is represented only by finite control."""
    b.expect(H, 'L')
    b.op('M', H, 1)
    carry, one, zero, scan, next_digit, done = (b.fresh(s) for s in
        ('height_carry', 'height1', 'height0', 'height_tail', 'height_next', 'height_done'))
    b.mark(carry)
    b.read(H, {'1': one, '0': zero})
    b.mark(one)
    b.op('W', H, '0')
    b.op('M', H, 1)
    b.jump(carry)
    b.mark(zero)
    b.op('W', H, '1')
    b.op('M', H, 1)
    b.jump(scan)
    b.mark(scan)
    b.read(H, {'0': next_digit, '1': next_digit, 'R': done})
    b.mark(next_digit)
    b.op('M', H, 1)
    b.jump(scan)
    b.mark(done)
    b.rewind(H)


def right_headers(b):
    b.mark('RIGHT_HEADERS')
    b.expect(SOURCE, 'ROOT')
    b.op('M', SOURCE, 1)
    b.blank_emit(WIDTH, 'L')
    b.expect(SOURCE, '1')
    loop, mark, end = (b.fresh(s) for s in ('right_width', 'right_mark', 'right_end'))
    b.mark(loop)
    b.read(SOURCE, {'1': mark, 'WE': end})
    b.mark(mark)
    b.blank_emit(WIDTH, '1')
    b.mark('HEIGHT_INCREMENT')
    increment_height(b)
    b.mark('HEIGHT_COUNTED')
    b.op('M', SOURCE, 1)
    b.jump(loop)
    b.mark(end)
    b.op('M', SOURCE, 1)
    b.end_marker(WIDTH)
    b.blank_emit(S, 'L')
    b.op('M', WIDTH, 1)
    loop, digit, zero, one, end = (b.fresh(s) for s in
        ('modulus', 'modulus_digit', 'modulus0', 'modulus1', 'modulus_end'))
    b.mark(loop)
    b.read(WIDTH, {'1': digit, 'R': end})
    b.mark(digit)
    b.read(SOURCE, {'0': zero, '1': one})
    for value, label in (('0', zero), ('1', one)):
        b.mark(label)
        b.expect(GUIDE, '1')
        b.blank_emit(S, value)
        for tape in (SOURCE, GUIDE, WIDTH):
            b.op('M', tape, 1)
        b.jump(loop)
    b.mark(end)
    b.expect(SOURCE, 'WE')
    b.op('M', SOURCE, 1)
    b.rewind(WIDTH)
    pad, digit, end = (b.fresh(s) for s in ('pad_modulus', 'pad0', 'padded'))
    b.mark(pad)
    b.read(GUIDE, {'1': digit, '_': end})
    b.mark(digit)
    b.blank_emit(S, '0')
    b.op('M', GUIDE, 1)
    b.jump(pad)
    b.mark(end)
    b.end_marker(S)
    b.native_rewind(GUIDE)
    b.op('M', WIDTH, 1)
    field, digit, bit, end = (b.fresh(s) for s in ('right_value', 'value_digit', 'value_bit', 'value_end'))
    b.mark(field)
    b.read(WIDTH, {'1': digit, 'R': end})
    b.mark(digit)
    b.read(SOURCE, {'0': bit, '1': bit})
    b.mark(bit)
    b.op('M', WIDTH, 1)
    b.op('M', SOURCE, 1)
    b.jump(field)
    b.mark(end)
    b.expect(SOURCE, 'RE')
    b.op('M', SOURCE, 1)
    b.expect(SOURCE, 'R')
    b.native_rewind(SOURCE)
    b.native_rewind(AXIS)
    b.rewind(WIDTH)


def offset_header(b):
    b.expect(RESULT, 'ROOT')
    b.op('M', RESULT, 1)
    b.blank_emit(A, 'L')
    loop, digit, zero, one, end = (b.fresh(s) for s in
        ('offset', 'offset_digit', 'offset0', 'offset1', 'offset_end'))
    b.mark(loop)
    b.read(GUIDE, {'1': digit, '_': end})
    b.mark(digit)
    b.read(RESULT, {'0': zero, '1': one})
    for value, label in (('0', zero), ('1', one)):
        b.mark(label)
        b.blank_emit(A, value)
        b.op('M', RESULT, 1)
        b.op('M', GUIDE, 1)
        b.jump(loop)
    b.mark(end)
    b.expect(RESULT, 'WE')
    b.op('M', RESULT, 1)
    b.native_rewind(GUIDE)
    b.blank_emit(A, '|')
    b.end_marker(A)
    b.native_rewind(RESULT)


def retire_outputs(b):
    b.mark('RETIRE')
    for tape in (H, S, A, J, WIDTH):
        b.expect(tape, 'L')
        b.op('M', tape, 1)
        loop, erase, end = (b.fresh(s) for s in ('retire', 'erase', 'retired'))
        b.mark(loop)
        b.read(tape, {'0': erase, '1': erase, 'R': end,
                      **({'|': erase} if tape == A else {})})
        b.mark(erase)
        b.op('W', tape, '_')
        b.op('M', tape, 1)
        b.jump(loop)
        b.mark(end)
        b.op('W', tape, '_')
        b.rewind(tape)
        b.op('W', tape, '_')
    b.op('H', 'RETIRED')


def compile_headers():
    predecessor = key_source()
    key_code, key_labels, key_metadata = predecessor.compile_pass()
    if len(key_code) != 21135 or predecessor.digest(key_code) != KEY_GRAPH:
        raise ValueError('exact complete key graph changed')
    b = Builder()
    for name, flag in (('BUILD', None), ('FORWARD', '0'), ('INVERSE', '1')):
        b.mark(name)
        b.expect(0, '_')
        if flag is not None:
            b.op('W', 0, flag)
        b.jump('CONSTRUCT')
    b.mark('CONSTRUCT')
    for tape in (H, S, A, J, WIDTH):
        b.expect(tape, '_')
    for tape in (SOURCE, AXIS, GUIDE, RESULT, SCRATCH):
        b.op('M', tape, -1)
        b.expect(tape, 'L')
        b.op('M', tape, 1)
    b.expect(AXIS, '1')
    b.expect(GUIDE, '1')
    b.expect(SCRATCH, '_')
    zero_header(b, H)
    zero_header(b, J)
    b.mark('PREFIX')
    b.read(AXIS, {'1': 'PREFIX_RECORD', 'STEP': 'LEFT_RECORD'})
    b.mark('PREFIX_ADVANCE')
    b.op('M', AXIS, 1)
    b.jump('PREFIX')
    skip_record(b, 'PREFIX_RECORD', 'PREFIX_ADVANCE')
    skip_record(b, 'LEFT_RECORD', 'RIGHT_HEADERS')
    right_headers(b)
    offset_header(b)
    b.mark('HEADERS_READY')
    b.read(0, {'_': 'HEADERS_RETURN', '0': 'KEY_FORWARD', '1': 'KEY_INVERSE'})
    b.mark('HEADERS_RETURN')
    b.op('H', 'HEADERS')
    for name in ('FORWARD', 'INVERSE'):
        b.mark('KEY_'+name)
        b.op('W', 0, '_')
        b.jump('KEY_'+str(key_metadata['entries'][name]))
    retire_outputs(b)
    b.mark('FAIL')
    b.op('H', 'MALFORMED')
    for pc, (op, *args) in enumerate(key_code):
        b.mark('KEY_'+str(pc))
        if op == 'R':
            b.op('R', args[0], {symbol: 'KEY_'+str(target) for symbol, target in args[1].items()})
        elif op == 'J':
            b.jump('KEY_'+str(args[0]))
        else:
            b.op(op, *args)
    code, labels = b.finish()
    metadata = {'entries': {name: labels[name] for name in ('BUILD', 'FORWARD', 'INVERSE', 'RETIRE')},
                'key_start': labels['KEY_0'], 'key_length': len(key_code),
                'key_labels': key_labels, 'key_metadata': key_metadata,
                'headers_ready': labels['HEADERS_READY'], 'tapes': TAPES,
                'numeric_ports': list(range(SOURCE, TAPES)), 'payload_port': 21}
    return code, labels, metadata


def digest(code):
    return sha256(json.dumps(code, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
