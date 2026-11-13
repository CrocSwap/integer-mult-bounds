"""One literal arbitrary-input, once-nearest-UP selected MOVE24472.

The immutable endpoint helper/core files are construction-time sources.
Only the emitted fixed four-symbol local instruction table runs. Apache-2.0.
"""
from pathlib import Path
import atexit
import hashlib
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_IMPORT_CACHE = tempfile.TemporaryDirectory(prefix='literal-rounded-source-')
atexit.register(_IMPORT_CACHE.cleanup)
_CACHE_PREFIX = Path(_IMPORT_CACHE.name) / 'required-absent'
if _CACHE_PREFIX.exists():
    raise ValueError('source import cache prefix must be absent')
sys.pycache_prefix = str(_CACHE_PREFIX)
sys.dont_write_bytecode = True
for pin in json.loads((HERE / 'ROUNDED-SOURCES.json').read_text())['files']:
    raw = (HERE / pin['local']).read_bytes()
    if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
        raise ValueError('rounded frozen source drift: ' + pin['local'])
sys.path.insert(0, str(HERE))
import endpoint as h

Builder, BLANK, ONE, MARK = h.Builder, h.BLANK, h.ONE, h.MARK
BITS = ('0', ONE)
HEADER, DATA, WH, WD, OUTPUT = h.HEADER, h.DATA, h.WH, h.WD, h.OUTPUT
WIDTH, K, WIDE, COUNT, TMP = h.WIDTH, h.K, h.WIDE, h.COUNT, h.TMP
MARGIN, HIGH = 23, 24
PRIVATE = tuple(range(2, 25))
CORE_PORTS = (WH, WD) + tuple(range(25, 54))
TAPES = 54


def initialize(a):
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)


def scale_count(a):
    stem = h.fresh(a, 'ceil_half')
    a.op('goto', stem + '1')
    for state in (0, 1):
        label = stem + str(state)
        a.mark(label)
        a.op('read', h.F, {ONE: label + 'bit', BLANK: stem + 'done'})
        a.mark(label + 'bit')
        if state:
            a.op('write', K, ONE)
            a.op('move', K, 1)
        a.op('move', h.F, 1)
        a.op('goto', stem + str(1 - state))
    a.mark(stem + 'done')
    a.rewind(h.F, (ONE,))
    a.rewind(K, (ONE,))


def append_one(a, tape):
    a.op('write', tape, ONE)
    a.op('move', tape, 1)
    a.rewind(tape, (ONE,))


def prepare_header(a):
    for tape in (h.F, h.R, h.P, h.S):
        h.gamma(a, tape, True)
    h.gamma(a, WIDTH, False)
    for i in range(2):
        a.op('read', WIDTH, {ONE: 'original_width_ok' + str(i)})
        a.mark('original_width_ok' + str(i))
        a.op('move', WIDTH, 1)
    a.rewind(WIDTH, (ONE,))
    scale_count(a)
    h.unary_copy(a, K, MARGIN, return_target=False)
    append_one(a, MARGIN)
    h.unary_copy(a, WIDTH, WIDE, return_target=False)
    h.unary_copy(a, K, WIDE, repeat=2, return_target=False)
    append_one(a, WIDE)
    h.unary_copy(a, WIDTH, HIGH, return_target=False)
    h.unary_copy(a, MARGIN, HIGH)
    h.unary_copy(a, WIDE, TMP)
    h.unary_binary(a)
    h.append_width_gamma(a)
    h.cutoff_copy(a)
    h.return_trace(a, HEADER, h.HTRACE)
    a.rewind(WH, BITS)


def ingress(a):
    stem = h.fresh(a, 'lift')
    a.mark(stem)
    a.op('read', COUNT, {ONE: stem + 'sign', BLANK: stem + 'done'})
    a.mark(stem + 'sign')
    a.op('read', DATA, {b: stem + 'lead' + b for b in BITS})
    for sign in BITS:
        s = stem + sign
        a.mark(stem + 'lead' + sign)
        a.op('read', MARGIN, {ONE: s + 'extend', BLANK: s + 'extended'})
        a.mark(s + 'extend')
        a.op('write', WD, sign)
        a.op('move', WD, 1)
        a.op('move', MARGIN, 1)
        a.op('goto', stem + 'lead' + sign)
        a.mark(s + 'extended')
        a.rewind(MARGIN, (ONE,))
        a.mark(s + 'copy')
        a.op('read', WIDTH, {ONE: s + 'read', BLANK: s + 'copied'})
        a.mark(s + 'read')
        a.op('read', DATA, {b: s + 'bit' + b for b in BITS})
        for b in BITS:
            a.mark(s + 'bit' + b)
            a.op('write', WD, b)
            a.op('move', WD, 1)
            h.advance(a, DATA)
            a.op('move', WIDTH, 1)
            a.op('goto', s + 'copy')
        a.mark(s + 'copied')
        a.rewind(WIDTH, (ONE,))
        a.mark(s + 'zeros')
        a.op('read', K, {ONE: s + 'zero', BLANK: s + 'zeroed'})
        a.mark(s + 'zero')
        a.op('write', WD, '0')
        a.op('move', WD, 1)
        a.op('move', K, 1)
        a.op('goto', s + 'zeros')
        a.mark(s + 'zeroed')
        a.rewind(K, (ONE,))
        a.op('move', COUNT, 1)
        a.op('goto', stem)
    a.mark(stem + 'done')
    a.op('read', DATA, {BLANK: stem + 'valid'})
    a.mark(stem + 'valid')
    h.return_trace(a, DATA, h.TRACE)
    a.rewind(WD, BITS)
    a.rewind(COUNT, (ONE,))


def increment(a):
    """Signed prefix increment modulo its complete width; -1->0 is valid."""
    s = h.fresh(a, 'increment')
    a.mark(s + 'seek')
    a.op('read', TMP, {b: s + 'step' for b in BITS} | {BLANK: s + 'end'})
    a.mark(s + 'step')
    a.op('move', TMP, 1)
    a.op('goto', s + 'seek')
    a.mark(s + 'end')
    a.op('move', TMP, -1)
    a.mark(s + 'carry')
    a.op('read', TMP, {'0': s + 'zero', ONE: s + 'one', MARK: s + 'wrap'})
    a.mark(s + 'one')
    a.op('write', TMP, '0')
    a.op('move', TMP, -1)
    a.op('goto', s + 'carry')
    a.mark(s + 'zero')
    a.op('write', TMP, ONE)
    a.op('move', TMP, 1)
    a.rewind(TMP, BITS)
    a.op('goto', s + 'done')
    a.mark(s + 'wrap')
    a.op('move', TMP, 1)
    a.mark(s + 'done')


def rounded_egress(a):
    s = h.fresh(a, 'round')
    a.mark(s)
    a.op('read', COUNT, {ONE: s + 'load', BLANK: s + 'done'})
    a.mark(s + 'load')
    a.op('read', HIGH, {ONE: s + 'read', BLANK: s + 'loaded'})
    a.mark(s + 'read')
    a.op('read', WD, {b: s + 'load' + b for b in BITS})
    for b in BITS:
        a.mark(s + 'load' + b)
        a.op('write', TMP, b)
        a.op('move', TMP, 1)
        h.advance(a, WD)
        a.op('move', HIGH, 1)
        a.op('goto', s + 'load')
    a.mark(s + 'loaded')
    a.rewind(HIGH, (ONE,))
    a.rewind(TMP, BITS)
    a.op('read', WD, {b: s + 'discard' + b for b in BITS})
    for up in BITS:
        q = s + up
        a.mark(s + 'discard' + up)
        a.op('read', K, {ONE: q + 'bit', BLANK: q + 'discarded'})
        a.mark(q + 'bit')
        a.op('read', WD, {b: q + 'advance' for b in BITS})
        a.mark(q + 'advance')
        h.advance(a, WD)
        a.op('move', K, 1)
        a.op('goto', s + 'discard' + up)
        a.mark(q + 'discarded')
        a.rewind(K, (ONE,))
        if up == ONE:
            increment(a)
        a.op('goto', s + 'fit')
    a.mark(s + 'fit')
    a.op('read', TMP, {b: s + 'sign' + b for b in BITS})
    for sign in BITS:
        q = s + 'fit' + sign
        a.mark(s + 'sign' + sign)
        a.op('read', MARGIN, {ONE: q + 'check', BLANK: q + 'checked'})
        a.mark(q + 'check')
        a.op('read', TMP, {sign: q + 'same'})
        a.mark(q + 'same')
        a.op('move', TMP, 1)
        a.op('move', MARGIN, 1)
        a.op('goto', s + 'sign' + sign)
        a.mark(q + 'checked')
        a.rewind(MARGIN, (ONE,))
        a.op('read', TMP, {sign: q + 'copy'})
        a.mark(q + 'copy')
        a.op('read', WIDTH, {ONE: q + 'read', BLANK: q + 'copied'})
        a.mark(q + 'read')
        a.op('read', TMP, {b: q + 'out' + b for b in BITS})
        for b in BITS:
            a.mark(q + 'out' + b)
            a.op('write', OUTPUT, b)
            a.op('move', OUTPUT, 1)
            a.op('move', TMP, 1)
            a.op('move', WIDTH, 1)
            a.op('goto', q + 'copy')
        a.mark(q + 'copied')
        a.op('read', TMP, {BLANK: q + 'valid'})
        a.mark(q + 'valid')
        a.rewind(WIDTH, (ONE,))
        a.rewind(TMP, BITS)
        h.clear(a, TMP)
        a.op('move', COUNT, 1)
        a.op('goto', s)
    a.mark(s + 'done')
    a.op('read', WD, {BLANK: s + 'valid'})
    a.mark(s + 'valid')
    h.return_trace(a, WD, h.TRACE)
    a.rewind(OUTPUT, BITS)
    a.rewind(COUNT, (ONE,))


def insert_core(a):
    code, alphabet = h.core.compile_move()
    if hashlib.sha256(repr(code).encode()).hexdigest() != '14f38b15157a9c9cd2828861f6904701a29b1e27507a7e43d60030e1ae4d9238':
        raise ValueError('core graph changed')
    for pc, (op, *args) in enumerate(code):
        a.mark('core_' + str(pc))
        if op == 'read':
            a.op(op, CORE_PORTS[args[0]], {b: 'core_' + str(j) for b, j in args[1].items()})
        elif op in ('write', 'move'):
            a.op(op, CORE_PORTS[args[0]], args[1])
        elif op == 'goto':
            a.op(op, 'core_' + str(args[0]))
        elif op == 'halt':
            a.op('goto', 'core_returned')
        else:
            raise ValueError('nonlocal core instruction')


def compile_header():
    a = Builder()
    initialize(a)
    prepare_header(a)
    a.op('halt')
    return a.finish((BLANK, '0', ONE, MARK))


def compile_converter(kind):
    if kind not in ('ingress', 'round'):
        raise ValueError('fixed converter')
    a = Builder()
    (ingress if kind == 'ingress' else rounded_egress)(a)
    a.op('halt')
    return a.finish((BLANK, '0', ONE, MARK))


def _compile_rounded():
    a = Builder()
    initialize(a)
    prepare_header(a)
    h.component_count(a)
    ingress(a)
    entries = {'core': len(a.code)}
    insert_core(a)
    a.mark('core_returned')
    entries['round'] = len(a.code)
    rounded_egress(a)
    entries['commit'] = len(a.code)
    a.mark('commit')
    a.op('read', OUTPUT, {b: 'commit' + b for b in BITS} | {BLANK: 'committed'})
    for b in BITS:
        a.mark('commit' + b)
        a.op('write', DATA, b)
        a.op('write', OUTPUT, BLANK)
        a.op('move', OUTPUT, 1)
        h.advance(a, DATA)
        a.op('goto', 'commit')
    a.mark('committed')
    h.return_trace(a, DATA, h.TRACE)
    a.rewind(OUTPUT, (BLANK,))
    for tape in PRIVATE:
        h.clear(a, tape)
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    code, alphabet = a.finish((BLANK, '0', ONE, MARK))
    return code, alphabet, entries


def compile_rounded():
    code, alphabet, _ = _compile_rounded()
    return code, alphabet
