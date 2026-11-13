"""Literal sharp-scale/width wrapper around the byte-frozen complete MOVE.

Apache-2.0. Gamma/unary helpers and floor-halving encoder follow the credited
retained literal modules. #7468 supplies the sharp integral scale. Only the
emitted fixed local-symbol table executes at runtime.
"""
from pathlib import Path
import hashlib
import sys

HERE = Path(__file__).resolve().parent
for path, expected in {
    'move.py': '42e4293ab59ffa1c99e0dbbd5fded0833a5d726e1e794f0f263ae9a4686587a5',
    'verify.py': '372eaf92353add7b7ce9a9513469408a341176aef749bcf3b0f60918c90630ca',
}.items():
    if hashlib.sha256((HERE / path).read_bytes()).hexdigest() != expected:
        raise ValueError('frozen core drift: ' + path)
sys.path.insert(0, str(HERE))
import move as core

Builder = core.Builder
BLANK, ONE, MARK = core.BLANK, core.ONE, core.MARK
BITS = ('0', ONE)
(HEADER, DATA, WH, WD, OUTPUT, HTRACE, TRACE, LENGTH, DOUBLE, F, R, P, S,
 WIDTH, K, WIDE, COUNT, AUX, TMP, HALF, DIGITS, BINARY, BLEN) = range(23)
WRAPPER_PRIVATE = tuple(range(2, 23))
CORE_PORTS = (WH, WD) + tuple(range(23, 52))
TAPES = 52


def fresh(a, stem):
    a.serial += 1
    return stem + str(a.serial) + '_'


def clear(a, tape):
    k = fresh(a, 'clear')
    a.mark(k)
    a.op('read', tape, {b: k + 'bit' for b in BITS} | {BLANK: k + 'done'})
    a.mark(k + 'bit')
    a.op('write', tape, BLANK)
    a.op('move', tape, 1)
    a.op('goto', k)
    a.mark(k + 'done')
    a.rewind(tape, (BLANK,))


def unary_copy(a, source, target, *, repeat=1, erase=False, return_target=True):
    k = fresh(a, 'copy')
    a.mark(k)
    a.op('read', source, {ONE: k + 'bit', BLANK: k + 'done'})
    a.mark(k + 'bit')
    for _ in range(repeat):
        a.op('write', target, ONE)
        a.op('move', target, 1)
    if erase:
        a.op('write', source, BLANK)
    a.op('move', source, 1)
    a.op('goto', k)
    a.mark(k + 'done')
    a.rewind(source, (BLANK,) if erase else (ONE,))
    if return_target:
        a.rewind(target, (ONE,))


def return_trace(a, source, trace):
    k = fresh(a, 'return')
    a.op('move', trace, -1)
    a.mark(k)
    a.op('read', trace, {ONE: k + 'bit', MARK: k + 'done'})
    a.mark(k + 'bit')
    a.op('write', trace, BLANK)
    a.op('move', trace, -1)
    a.op('move', source, -1)
    a.op('goto', k)
    a.mark(k + 'done')
    a.op('move', trace, 1)


def header_step(a, bit, copy):
    if copy:
        a.op('write', WH, bit)
        a.op('move', WH, 1)
    a.op('write', HTRACE, ONE)
    a.op('move', HTRACE, 1)
    a.op('move', HEADER, 1)


def gamma(a, target, copy):
    k = fresh(a, 'gamma')
    a.mark(k + 'prefix')
    a.op('read', HEADER, {'0': k + 'zero', ONE: k + 'one'})
    a.mark(k + 'zero')
    a.op('write', LENGTH, ONE)
    a.op('move', LENGTH, 1)
    header_step(a, '0', copy)
    a.op('goto', k + 'prefix')
    a.mark(k + 'one')
    header_step(a, ONE, copy)
    a.op('write', target, ONE)
    a.op('move', LENGTH, -1)
    a.mark(k + 'tail')
    a.op('read', LENGTH, {ONE: k + 'tailbit', MARK: k + 'done'})
    a.mark(k + 'tailbit')
    a.op('write', LENGTH, BLANK)
    a.op('read', HEADER, {str(b): k + 'digit' + str(b) for b in (0, 1)})
    for b in (0, 1):
        a.mark(k + 'digit' + str(b))
        unary_copy(a, target, DOUBLE, repeat=2)
        if b:
            # Append the known low digit before rewinding DOUBLE.
            seek = fresh(a, 'append')
            a.mark(seek)
            a.op('read', DOUBLE, {ONE: seek + 'step', BLANK: seek + 'end'})
            a.mark(seek + 'step')
            a.op('move', DOUBLE, 1)
            a.op('goto', seek)
            a.mark(seek + 'end')
            a.op('write', DOUBLE, ONE)
            a.op('move', DOUBLE, 1)
            a.rewind(DOUBLE, (ONE,))
        clear(a, target)
        unary_copy(a, DOUBLE, target, erase=True)
        header_step(a, str(b), copy)
        a.op('move', LENGTH, -1)
        a.op('goto', k + 'tail')
    a.mark(k + 'done')
    a.op('move', LENGTH, 1)


def scale_count(a):
    """Actual unary f loop; two initial remainder units implement (f+2)//4."""
    stem = fresh(a, 'scale')
    a.op('goto', stem + '2')
    for state in range(4):
        label = stem + str(state)
        a.mark(label)
        a.op('read', F, {ONE: label + 'bit', BLANK: stem + 'done'})
        a.mark(label + 'bit')
        if state == 3:
            a.op('write', K, ONE)
            a.op('move', K, 1)
        a.op('move', F, 1)
        a.op('goto', stem + str((state + 1) % 4))
    a.mark(stem + 'done')
    a.rewind(F, (ONE,))
    a.rewind(K, (ONE,))


def unary_binary(a):
    """Consume TMP by repeated floor-halving; no runtime integer service."""
    k = fresh(a, 'encode')
    a.op('goto', k + 'p0q0')
    for phase, (current, quotient) in enumerate(((TMP, HALF), (HALF, TMP))):
        for parity in (0, 1):
            name = k + f'p{phase}q{parity}'
            a.mark(name)
            a.op('read', current, {ONE: name + 'bit', BLANK: name + 'done'})
            a.mark(name + 'bit')
            a.op('write', current, BLANK)
            if parity:
                a.op('write', quotient, ONE)
                a.op('move', quotient, 1)
            a.op('move', current, 1)
            a.op('goto', k + f'p{phase}q{1-parity}')
            a.mark(name + 'done')
            a.rewind(current, (BLANK,))
            a.rewind(quotient, (ONE,))
            a.op('write', DIGITS, str(parity))
            a.op('move', DIGITS, 1)
            a.op('read', quotient, {ONE: k + f'p{1-phase}q0', BLANK: k + 'emit_start'})
    a.mark(k + 'emit_start')
    a.op('move', DIGITS, -1)
    a.mark(k + 'emit')
    a.op('read', DIGITS, {str(b): k + 'emit' + str(b) for b in (0, 1)} | {MARK: k + 'done'})
    for b in (0, 1):
        a.mark(k + 'emit' + str(b))
        a.op('write', BINARY, str(b))
        a.op('move', BINARY, 1)
        a.op('write', DIGITS, BLANK)
        a.op('move', DIGITS, -1)
        a.op('goto', k + 'emit')
    a.mark(k + 'done')
    a.op('move', DIGITS, 1)
    a.rewind(BINARY, BITS)


def append_width_gamma(a):
    k = fresh(a, 'width_code')
    a.mark(k + 'length')
    a.op('read', BINARY, {b: k + 'count' for b in BITS} | {BLANK: k + 'counted'})
    a.mark(k + 'count')
    a.op('move', BINARY, 1)
    a.op('write', BLEN, ONE)
    a.op('move', BLEN, 1)
    a.op('goto', k + 'length')
    a.mark(k + 'counted')
    a.rewind(BINARY, BITS)
    a.rewind(BLEN, (ONE,))
    a.op('move', BLEN, 1)
    a.mark(k + 'zeroes')
    a.op('read', BLEN, {ONE: k + 'zero', BLANK: k + 'prefix_done'})
    a.mark(k + 'zero')
    a.op('write', WH, '0')
    a.op('move', WH, 1)
    a.op('move', BLEN, 1)
    a.op('goto', k + 'zeroes')
    a.mark(k + 'prefix_done')
    a.rewind(BLEN, (ONE,))
    a.mark(k + 'digits')
    a.op('read', BINARY, {b: k + 'digit' + b for b in BITS} | {BLANK: k + 'done'})
    for b in BITS:
        a.mark(k + 'digit' + b)
        a.op('write', WH, b)
        a.op('move', WH, 1)
        a.op('write', BINARY, BLANK)
        a.op('move', BINARY, 1)
        a.op('goto', k + 'digits')
    a.mark(k + 'done')
    a.rewind(BINARY, (BLANK,))


def cutoff_copy(a):
    """Copy exactly one Gamma word; never expand its represented value."""
    k = fresh(a, 'cutoff')
    a.mark(k + 'prefix')
    a.op('read', HEADER, {'0': k + 'zero', ONE: k + 'one'})
    a.mark(k + 'zero')
    a.op('write', LENGTH, ONE)
    a.op('move', LENGTH, 1)
    header_step(a, '0', True)
    a.op('goto', k + 'prefix')
    a.mark(k + 'one')
    header_step(a, ONE, True)
    a.op('move', LENGTH, -1)
    a.mark(k + 'tail')
    a.op('read', LENGTH, {ONE: k + 'tailbit', MARK: k + 'done'})
    a.mark(k + 'tailbit')
    a.op('write', LENGTH, BLANK)
    a.op('read', HEADER, {b: k + 'digit' + b for b in BITS})
    for b in BITS:
        a.mark(k + 'digit' + b)
        header_step(a, b, True)
        a.op('move', LENGTH, -1)
        a.op('goto', k + 'tail')
    a.mark(k + 'done')
    a.op('move', LENGTH, 1)


def prepare_header(a):
    for target in (F, R, P, S):
        gamma(a, target, True)
    gamma(a, WIDTH, False)
    for i in range(2):
        a.op('read', WIDTH, {ONE: 'width_ok' + str(i)})
        a.mark('width_ok' + str(i))
        a.op('move', WIDTH, 1)
    a.rewind(WIDTH, (ONE,))
    scale_count(a)
    unary_copy(a, WIDTH, WIDE, return_target=False)
    unary_copy(a, K, WIDE, repeat=2)
    unary_copy(a, WIDE, TMP)
    unary_binary(a)
    append_width_gamma(a)
    cutoff_copy(a)
    return_trace(a, HEADER, HTRACE)
    a.rewind(WH, BITS)


def double(a, target):
    unary_copy(a, target, DOUBLE, repeat=2)
    clear(a, target)
    unary_copy(a, DOUBLE, target, erase=True)


def multiply(a, factor):
    k = fresh(a, 'product')
    a.mark(k + 'outer')
    a.op('read', COUNT, {ONE: k + 'inner', BLANK: k + 'done'})
    a.mark(k + 'inner')
    a.op('read', factor, {ONE: k + 'bit', BLANK: k + 'row'})
    a.mark(k + 'bit')
    a.op('write', AUX, ONE)
    a.op('move', AUX, 1)
    a.op('move', factor, 1)
    a.op('goto', k + 'inner')
    a.mark(k + 'row')
    a.rewind(factor, (ONE,))
    a.op('move', COUNT, 1)
    a.op('goto', k + 'outer')
    a.mark(k + 'done')
    a.rewind(COUNT, (ONE,))
    a.rewind(AUX, (ONE,))
    clear(a, COUNT)
    unary_copy(a, AUX, COUNT, erase=True)


def component_count(a):
    unary_copy(a, P, COUNT)
    for factor in (S, R):
        multiply(a, factor)
    k = fresh(a, 'geometry')
    a.mark(k)
    a.op('read', F, {ONE: k + 'bit', BLANK: k + 'done'})
    a.mark(k + 'bit')
    for _ in range(9):
        double(a, COUNT)
    a.op('move', F, 1)
    a.op('goto', k)
    a.mark(k + 'done')
    a.rewind(F, (ONE,))
    double(a, COUNT)


def advance(a, source):
    a.op('move', source, 1)
    a.op('write', TRACE, ONE)
    a.op('move', TRACE, 1)


def ingress(a):
    k = fresh(a, 'ingress')
    a.mark(k)
    a.op('read', COUNT, {ONE: k + 'sign', BLANK: k + 'done'})
    a.mark(k + 'sign')
    a.op('read', DATA, {b: k + 'lead' + b for b in BITS})
    for sign in BITS:
        prefix = k + sign
        a.mark(k + 'lead' + sign)
        a.op('read', K, {ONE: prefix + 'extend', BLANK: prefix + 'extended'})
        a.mark(prefix + 'extend')
        a.op('write', WD, sign)
        a.op('move', WD, 1)
        a.op('move', K, 1)
        a.op('goto', k + 'lead' + sign)
        a.mark(prefix + 'extended')
        a.rewind(K, (ONE,))
        a.mark(prefix + 'copy')
        a.op('read', WIDTH, {ONE: prefix + 'read', BLANK: prefix + 'copied'})
        a.mark(prefix + 'read')
        a.op('read', DATA, {b: prefix + 'bit' + b for b in BITS})
        for b in BITS:
            a.mark(prefix + 'bit' + b)
            a.op('write', WD, b)
            a.op('move', WD, 1)
            advance(a, DATA)
            a.op('move', WIDTH, 1)
            a.op('goto', prefix + 'copy')
        a.mark(prefix + 'copied')
        a.rewind(WIDTH, (ONE,))
        a.mark(prefix + 'zeros')
        a.op('read', K, {ONE: prefix + 'zero', BLANK: prefix + 'zeroed'})
        a.mark(prefix + 'zero')
        a.op('write', WD, '0')
        a.op('move', WD, 1)
        a.op('move', K, 1)
        a.op('goto', prefix + 'zeros')
        a.mark(prefix + 'zeroed')
        a.rewind(K, (ONE,))
        a.op('move', COUNT, 1)
        a.op('goto', k)
    a.mark(k + 'done')
    a.op('read', DATA, {BLANK: k + 'valid'})
    a.mark(k + 'valid')
    return_trace(a, DATA, TRACE)
    a.rewind(WD, BITS)
    a.rewind(COUNT, (ONE,))


def egress(a):
    k = fresh(a, 'egress')
    a.mark(k)
    a.op('read', COUNT, {ONE: k + 'sign', BLANK: k + 'done'})
    a.mark(k + 'sign')
    a.op('read', WD, {b: k + 'lead' + b for b in BITS})
    for sign in BITS:
        prefix = k + sign
        a.mark(k + 'lead' + sign)
        a.op('read', K, {ONE: prefix + 'check_lead', BLANK: prefix + 'led'})
        a.mark(prefix + 'check_lead')
        a.op('read', WD, {sign: prefix + 'valid_lead'})
        a.mark(prefix + 'valid_lead')
        advance(a, WD)
        a.op('move', K, 1)
        a.op('goto', k + 'lead' + sign)
        a.mark(prefix + 'led')
        a.rewind(K, (ONE,))
        a.op('read', WD, {sign: prefix + 'copy'})
        a.mark(prefix + 'copy')
        a.op('read', WIDTH, {ONE: prefix + 'read', BLANK: prefix + 'copied'})
        a.mark(prefix + 'read')
        a.op('read', WD, {b: prefix + 'bit' + b for b in BITS})
        for b in BITS:
            a.mark(prefix + 'bit' + b)
            a.op('write', OUTPUT, b)
            a.op('move', OUTPUT, 1)
            advance(a, WD)
            a.op('move', WIDTH, 1)
            a.op('goto', prefix + 'copy')
        a.mark(prefix + 'copied')
        a.rewind(WIDTH, (ONE,))
        a.mark(prefix + 'zeros')
        a.op('read', K, {ONE: prefix + 'check_zero', BLANK: prefix + 'zeroed'})
        a.mark(prefix + 'check_zero')
        a.op('read', WD, {'0': prefix + 'valid_zero'})
        a.mark(prefix + 'valid_zero')
        advance(a, WD)
        a.op('move', K, 1)
        a.op('goto', prefix + 'zeros')
        a.mark(prefix + 'zeroed')
        a.rewind(K, (ONE,))
        a.op('move', COUNT, 1)
        a.op('goto', k)
    a.mark(k + 'done')
    a.op('read', WD, {BLANK: k + 'valid'})
    a.mark(k + 'valid')
    return_trace(a, WD, TRACE)
    a.rewind(OUTPUT, BITS)
    a.rewind(COUNT, (ONE,))


def insert_core(a):
    code, alphabet = core.compile_move()
    if hashlib.sha256(repr(code).encode()).hexdigest() != '14f38b15157a9c9cd2828861f6904701a29b1e27507a7e43d60030e1ae4d9238':
        raise ValueError('frozen graph drift')
    for pc, (op, *args) in enumerate(code):
        a.mark('core_' + str(pc))
        if op == 'read':
            a.op(op, CORE_PORTS[args[0]], {s: 'core_' + str(dst) for s, dst in args[1].items()})
        elif op in ('write', 'move'):
            a.op(op, CORE_PORTS[args[0]], args[1])
        elif op == 'goto':
            a.op(op, 'core_' + str(args[0]))
        elif op == 'halt':
            a.op('goto', 'core_returned')
        else:
            raise ValueError('nonlocal core opcode')


def initialize(a):
    for tape in WRAPPER_PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)


def compile_header():
    """Unit boundary: initialized header/guides remain live, not retired."""
    a = Builder()
    initialize(a)
    prepare_header(a)
    a.op('halt')
    return a.finish((BLANK, '0', ONE, MARK))


def compile_converter(kind):
    """Unit boundary with supplied guarded WIDTH/K/COUNT, for small tests."""
    if kind not in ('ingress', 'egress'):
        raise ValueError('fixed converter kind')
    a = Builder()
    (ingress if kind == 'ingress' else egress)(a)
    a.op('halt')
    return a.finish((BLANK, '0', ONE, MARK))


def _compile_endpoint():
    a = Builder()
    initialize(a)
    prepare_header(a)
    component_count(a)
    ingress(a)
    entries = {'core': len(a.code)}
    insert_core(a)
    a.mark('core_returned')
    entries['egress'] = len(a.code)
    egress(a)
    entries['commit'] = len(a.code)
    a.mark('commit')
    a.op('read', OUTPUT, {b: 'commit' + b for b in BITS} | {BLANK: 'committed'})
    for b in BITS:
        a.mark('commit' + b)
        a.op('write', DATA, b)
        a.op('write', OUTPUT, BLANK)
        a.op('move', OUTPUT, 1)
        advance(a, DATA)
        a.op('goto', 'commit')
    a.mark('committed')
    return_trace(a, DATA, TRACE)
    a.rewind(OUTPUT, (BLANK,))
    for tape in WRAPPER_PRIVATE:
        clear(a, tape)
    for tape in WRAPPER_PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    code, alphabet = a.finish((BLANK, '0', ONE, MARK))
    return code, alphabet, entries


def compile_endpoint():
    """One fixed whole-call graph, without runtime recipe or size arguments."""
    code, alphabet, _ = _compile_endpoint()
    return code, alphabet
