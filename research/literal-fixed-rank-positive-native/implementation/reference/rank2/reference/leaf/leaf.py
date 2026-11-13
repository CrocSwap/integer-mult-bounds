"""Literal positive rank-one Gaussian C tensor leaf on a packed m=9 field.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. C arithmetic and tensor algebra are credited #3091 predecessors.
Only fixed local instructions execute; encoded inputs do not specialize code.
"""
from pathlib import Path
import hashlib
import sys

HERE = Path(__file__).resolve().parent
MACHINE = HERE / 'inputs' / 'controller_reference.py'
EXPECTED_MACHINE = 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73'
if hashlib.sha256(MACHINE.read_bytes()).hexdigest() != EXPECTED_MACHINE:
    raise ValueError('frozen literal machine source drift')
sys.path.insert(0, str(MACHINE.parent))
from controller_reference import Builder, Machine, Tape, BLANK, ONE, MARK

(HEADER, DATA, A, B, MODE, HTRACE, LENGTH, DOUBLE, F, R, P, S, WIDTH,
 FBIN, FLEN, TBIN, TLEN, PREFIX, SUFFIX, LEFT, RIGHT, LOUT, ROUT,
 AR, AI, BR, BI, NUM, DTRACE) = range(29)
PRIVATE = tuple(range(2, 29))
BITS = ('0', ONE)
INPUTS = (AR, AI, BR, BI)
ROWS = ((1, -1, 1, 1), (1, 1, -1, 1),
        (1, 1, 1, -1), (-1, 1, 1, 1))
NATIVE_DIMENSION = 9


def fresh(a, stem):
    a.serial += 1
    return stem + str(a.serial)


def clear(a, tape, symbols=(ONE,)):
    k = fresh(a, 'clear')
    a.mark(k)
    a.op('read', tape, {s: k+'bit' for s in symbols} | {BLANK: k+'done'})
    a.mark(k+'bit')
    a.op('write', tape, BLANK)
    a.op('move', tape, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(tape, (BLANK,))


def unary_copy(a, source, target, *, repeat=1, extra=0, erase=False):
    k = fresh(a, 'copy')
    a.mark(k)
    a.op('read', source, {ONE: k+'bit', BLANK: k+'done'})
    a.mark(k+'bit')
    for _ in range(repeat):
        a.op('write', target, ONE)
        a.op('move', target, 1)
    if erase:
        a.op('write', source, BLANK)
    a.op('move', source, 1)
    a.op('goto', k)
    a.mark(k+'done')
    for _ in range(extra):
        a.op('write', target, ONE)
        a.op('move', target, 1)
    a.rewind(source, (BLANK,) if erase else (ONE,))
    a.rewind(target, (ONE,))


def trace_return(a, tape, trace):
    k = fresh(a, 'return')
    a.op('move', trace, -1)
    a.mark(k)
    a.op('read', trace, {ONE: k+'bit', MARK: k+'done'})
    a.mark(k+'bit')
    a.op('write', trace, BLANK)
    a.op('move', trace, -1)
    a.op('move', tape, -1)
    a.op('goto', k)
    a.mark(k+'done')
    a.op('move', trace, 1)


def header_step(a):
    a.op('write', HTRACE, ONE)
    a.op('move', HTRACE, 1)
    a.op('move', HEADER, 1)


def gamma(a, target, capture=None):
    """Unary decode for parameters bounded by the actual field volume."""
    k = fresh(a, 'gamma')
    a.mark(k+'prefix')
    a.op('read', HEADER, {'0': k+'zero', ONE: k+'one'})
    a.mark(k+'zero')
    a.op('write', LENGTH, ONE)
    a.op('move', LENGTH, 1)
    header_step(a)
    a.op('goto', k+'prefix')
    a.mark(k+'one')
    header_step(a)
    a.op('write', target, ONE)
    if capture:
        for tape, bit in ((capture[0], ONE), (capture[1], ONE)):
            a.op('write', tape, bit)
            a.op('move', tape, 1)
    a.op('move', LENGTH, -1)
    a.mark(k+'tail')
    a.op('read', LENGTH, {ONE: k+'tailbit', MARK: k+'done'})
    a.mark(k+'tailbit')
    a.op('write', LENGTH, BLANK)
    a.op('read', HEADER, {str(b): k+'digit'+str(b) for b in (0, 1)})
    for bit in (0, 1):
        a.mark(k+'digit'+str(bit))
        unary_copy(a, target, DOUBLE, repeat=2, extra=bit)
        clear(a, target)
        unary_copy(a, DOUBLE, target, erase=True)
        if capture:
            for tape, symbol in ((capture[0], str(bit)), (capture[1], ONE)):
                a.op('write', tape, symbol)
                a.op('move', tape, 1)
        header_step(a)
        a.op('move', LENGTH, -1)
        a.op('goto', k+'tail')
    a.mark(k+'done')
    a.op('move', LENGTH, 1)
    if capture:
        a.rewind(capture[0], BITS)
        a.rewind(capture[1], (ONE,))


def gamma_binary(a):
    """Keep cutoff in binary: its represented value can exceed V arbitrarily."""
    k = fresh(a, 'threshold')
    a.mark(k+'prefix')
    a.op('read', HEADER, {'0': k+'zero', ONE: k+'one'})
    a.mark(k+'zero')
    a.op('write', LENGTH, ONE)
    a.op('move', LENGTH, 1)
    header_step(a)
    a.op('goto', k+'prefix')
    a.mark(k+'one')
    a.op('write', TBIN, ONE)
    a.op('move', TBIN, 1)
    a.op('write', TLEN, ONE)
    a.op('move', TLEN, 1)
    header_step(a)
    a.op('move', LENGTH, -1)
    a.mark(k+'tail')
    a.op('read', LENGTH, {ONE: k+'read', MARK: k+'done'})
    a.mark(k+'read')
    a.op('write', LENGTH, BLANK)
    a.op('read', HEADER, {str(b): k+str(b) for b in (0, 1)})
    for bit in ('0', ONE):
        a.mark(k+bit)
        a.op('write', TBIN, bit)
        a.op('move', TBIN, 1)
        a.op('write', TLEN, ONE)
        a.op('move', TLEN, 1)
        header_step(a)
        a.op('move', LENGTH, -1)
        a.op('goto', k+'tail')
    a.mark(k+'done')
    a.op('move', LENGTH, 1)
    a.rewind(TBIN, BITS)
    a.rewind(TLEN, (ONE,))


def cutoff_guard(a):
    k = fresh(a, 'compare')
    a.mark(k+'length')
    a.op('read', FLEN, {ONE: k+'fmore', BLANK: k+'fend'})
    a.mark(k+'fmore')
    a.op('read', TLEN, {ONE: k+'step', BLANK: 'reject'})
    a.mark(k+'step')
    a.op('move', FLEN, 1)
    a.op('move', TLEN, 1)
    a.op('goto', k+'length')
    a.mark(k+'fend')
    a.op('read', TLEN, {ONE: k+'done', BLANK: k+'equal_length'})
    a.mark(k+'equal_length')
    a.rewind(FLEN, (ONE,))
    a.rewind(TLEN, (ONE,))
    a.mark(k+'lex')
    a.op('read', FBIN, {'0': k+'f0', ONE: k+'f1', BLANK: k+'equal'})
    a.mark(k+'f0')
    a.op('read', TBIN, {'0': k+'same', ONE: k+'done'})
    a.mark(k+'f1')
    a.op('read', TBIN, {'0': 'reject', ONE: k+'same'})
    a.mark(k+'same')
    a.op('move', FBIN, 1)
    a.op('move', TBIN, 1)
    a.op('goto', k+'lex')
    a.mark(k+'equal')
    a.op('read', TBIN, {BLANK: k+'done'})
    a.mark(k+'done')
    for tape, symbols in ((FLEN, (ONE,)), (TLEN, (ONE,)), (FBIN, BITS), (TBIN, BITS)):
        a.rewind(tape, symbols)
        clear(a, tape, symbols)


def double(a, tape):
    unary_copy(a, tape, DOUBLE, repeat=2)
    clear(a, tape)
    unary_copy(a, DOUBLE, tape, erase=True)


def halve(a, tape):
    k = fresh(a, 'halve')
    a.mark(k)
    a.op('read', tape, {ONE: k+'first', BLANK: k+'done'})
    a.mark(k+'first')
    a.op('write', tape, BLANK)
    a.op('move', tape, 1)
    a.op('read', tape, {ONE: k+'second', BLANK: 'reject'})
    a.mark(k+'second')
    a.op('write', tape, BLANK)
    a.op('move', tape, 1)
    a.op('write', DOUBLE, ONE)
    a.op('move', DOUBLE, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(tape, (BLANK,))
    a.rewind(DOUBLE, (ONE,))
    unary_copy(a, DOUBLE, tape, erase=True)


def product(a, left, right, target):
    k = fresh(a, 'product')
    a.mark(k+'outer')
    a.op('read', left, {ONE: k+'inner', BLANK: k+'done'})
    a.mark(k+'inner')
    a.op('read', right, {ONE: k+'bit', BLANK: k+'row'})
    a.mark(k+'bit')
    a.op('write', target, ONE)
    a.op('move', target, 1)
    a.op('move', right, 1)
    a.op('goto', k+'inner')
    a.mark(k+'row')
    a.rewind(right, (ONE,))
    a.op('move', left, 1)
    a.op('goto', k+'outer')
    a.mark(k+'done')
    a.rewind(left, (ONE,))
    a.rewind(target, (ONE,))


def geometry(a):
    product(a, S, R, SUFFIX)
    unary_copy(a, P, PREFIX)
    k = fresh(a, 'geometry')
    a.mark(k+'suffix')
    a.op('read', F, {ONE: k+'block', BLANK: k+'suffix_done'})
    a.mark(k+'block')
    for _ in range(NATIVE_DIMENSION-1):
        double(a, SUFFIX)
    a.op('move', F, 1)
    a.op('goto', k+'suffix')
    a.mark(k+'suffix_done')
    a.rewind(F, (ONE,))
    a.op('move', F, 1)
    a.mark(k+'prefix')
    a.op('read', F, {ONE: k+'more', BLANK: k+'done'})
    a.mark(k+'more')
    double(a, PREFIX)
    a.op('move', F, 1)
    a.op('goto', k+'prefix')
    a.mark(k+'done')
    a.rewind(F, (ONE,))
    for tape in (P, R, S):
        clear(a, tape)


def copy_width(a, source, target, *, rewind_target=False):
    k = fresh(a, 'widthcopy')
    a.mark(k)
    a.op('read', WIDTH, {ONE: k+'read', BLANK: k+'done'})
    a.mark(k+'read')
    a.op('read', source, {str(b): k+str(b) for b in (0, 1)})
    for bit in ('0', ONE):
        a.mark(k+bit)
        a.op('write', target, bit)
        a.op('move', target, 1)
        a.op('write', source, BLANK)
        a.op('move', source, 1)
        a.op('move', WIDTH, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(WIDTH, (ONE,))
    if rewind_target:
        a.rewind(target, BITS)


def load_suffix(a, source, target):
    k = fresh(a, 'suffix')
    a.mark(k)
    a.op('read', SUFFIX, {ONE: k+'pair', BLANK: k+'done'})
    a.mark(k+'pair')
    for _ in range(2):
        copy_width(a, source, target)
    a.op('move', SUFFIX, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(SUFFIX, (ONE,))
    a.rewind(target, BITS)


def emit_stream(a, source, target):
    k = fresh(a, 'stream')
    a.mark(k)
    a.op('read', source, {str(b): k+str(b) for b in (0, 1)} | {BLANK: k+'done'})
    for bit in ('0', ONE):
        a.mark(k+bit)
        a.op('write', target, bit)
        a.op('move', target, 1)
        a.op('write', source, BLANK)
        a.op('move', source, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(source, (BLANK,))


def tuple_branch(a, label, emit, prefix=()):
    """Compile the fixed sixteen branches of a four-symbol read."""
    name = label+''.join(map(str, prefix))
    a.mark(name)
    if len(prefix) == 4:
        emit(prefix)
    else:
        a.op('read', INPUTS[len(prefix)], {str(b): name+str(b) for b in (0, 1)})
        for bit in (0, 1):
            tuple_branch(a, label, emit, prefix+(bit,))


def c_component(a, signs, output):
    """Exact four-input numerator, two sign extensions, halving and fit."""
    k = fresh(a, 'C')
    a.mark(k+'seek')
    a.op('read', WIDTH, {ONE: k+'seekbit', BLANK: k+'seekend'})
    a.mark(k+'seekbit')
    for tape in INPUTS:
        a.op('move', tape, 1)
    a.op('move', WIDTH, 1)
    a.op('goto', k+'seek')
    a.mark(k+'seekend')
    a.rewind(WIDTH, (ONE,))
    for tape in INPUTS:
        a.op('move', tape, -1)
    a.op('goto', k+'digit0')
    for carry in (-1, 0, 1, 2):
        label = k+'digit'+str(carry)
        a.mark(label)
        a.op('read', WIDTH, {ONE: label+'read', BLANK: k+'extend'+str(carry)})
        def digit(bits, carry=carry):
            total = carry+sum(s*b for s, b in zip(signs, bits))
            a.op('write', NUM, str(total % 2))
            a.op('move', NUM, 1)
            for tape in INPUTS:
                a.op('move', tape, -1)
            a.op('move', WIDTH, 1)
            a.op('goto', k+'digit'+str(total//2))
        tuple_branch(a, label+'read', digit)
        a.mark(k+'extend'+str(carry))
        for tape in INPUTS:
            a.op('move', tape, 1)
        a.rewind(WIDTH, (ONE,))
        a.op('goto', k+'sign1c'+str(carry))
    for stage in (1, 2):
        for carry in (-1, 0, 1, 2):
            def extension(bits, carry=carry, stage=stage):
                total = carry+sum(s*b for s, b in zip(signs, bits))
                a.op('write', NUM, str(total % 2))
                a.op('move', NUM, 1)
                a.op('goto', k+'sign2c'+str(total//2) if stage == 1 else k+'check')
            tuple_branch(a, k+'sign'+str(stage)+'c'+str(carry), extension)
    a.mark(k+'check')
    a.rewind(NUM, BITS)
    a.op('read', NUM, {'0': k+'even', ONE: 'reject'})
    a.mark(k+'even')
    a.op('write', NUM, BLANK)
    a.op('move', NUM, 1)
    a.mark(k+'highseek')
    a.op('read', NUM, {'0': k+'highstep', ONE: k+'highstep', BLANK: k+'highend'})
    a.mark(k+'highstep')
    a.op('move', NUM, 1)
    a.op('goto', k+'highseek')
    a.mark(k+'highend')
    a.op('move', NUM, -1)
    a.op('read', NUM, {str(b): k+'top'+str(b) for b in (0, 1)})
    for bit in ('0', ONE):
        a.mark(k+'top'+bit)
        a.op('write', NUM, BLANK)
        a.op('move', NUM, -1)
        a.op('read', NUM, {bit: k+'emit'})
    a.mark(k+'emit')
    a.op('read', WIDTH, {ONE: k+'emitread', BLANK: k+'done'})
    a.mark(k+'emitread')
    a.op('read', NUM, {str(b): k+'emit'+str(b) for b in (0, 1)})
    for bit in ('0', ONE):
        a.mark(k+'emit'+bit)
        a.op('write', output, bit)
        a.op('move', output, 1)
        a.op('write', NUM, BLANK)
        a.op('move', NUM, -1)
        a.op('move', WIDTH, 1)
        a.op('goto', k+'emit')
    a.mark(k+'done')
    a.rewind(WIDTH, (ONE,))


def clone_source(a):
    """Clone exactly the generated volume; reject short/excess cardinality."""
    k = fresh(a, 'clone')
    a.mark(k+'prefix')
    a.op('read', PREFIX, {ONE: k+'blocks', BLANK: k+'done'})
    a.mark(k+'blocks')
    for side in range(2):
        name = k+'side'+str(side)
        a.mark(name)
        a.op('read', SUFFIX, {ONE: name+'coefficient', BLANK: name+'done'})
        a.mark(name+'coefficient')
        for component in range(2):
            field = name+'field'+str(component)
            a.mark(field)
            a.op('read', WIDTH, {ONE: field+'read', BLANK: field+'done'})
            a.mark(field+'read')
            a.op('read', DATA, {str(b): field+str(b) for b in (0, 1)})
            for bit in ('0', ONE):
                a.mark(field+bit)
                a.op('write', A, bit)
                a.op('move', A, 1)
                a.op('move', DATA, 1)
                a.op('write', DTRACE, ONE)
                a.op('move', DTRACE, 1)
                a.op('move', WIDTH, 1)
                a.op('goto', field)
            a.mark(field+'done')
            a.rewind(WIDTH, (ONE,))
        a.op('move', SUFFIX, 1)
        a.op('goto', name)
        a.mark(name+'done')
        a.rewind(SUFFIX, (ONE,))
    a.op('move', PREFIX, 1)
    a.op('goto', k+'prefix')
    a.mark(k+'done')
    a.rewind(PREFIX, (ONE,))
    a.op('read', DATA, {BLANK: k+'verified'})
    a.mark(k+'verified')
    trace_return(a, DATA, DTRACE)
    a.rewind(A, BITS)


def commit(a, source):
    k = fresh(a, 'commit')
    a.mark(k)
    a.op('read', source, {str(b): k+str(b) for b in (0, 1)} | {BLANK: k+'done'})
    for bit in ('0', ONE):
        a.mark(k+bit)
        a.op('write', DATA, bit)
        a.op('write', source, BLANK)
        a.op('move', source, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('goto', k)
    a.mark(k+'done')
    trace_return(a, DATA, DTRACE)
    a.rewind(source, (BLANK,))


def compile_leaf():
    a = Builder()
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    gamma(a, F, (FBIN, FLEN))
    for tape in (R, P, S, WIDTH):
        gamma(a, tape)
    gamma_binary(a)
    trace_return(a, HEADER, HTRACE)
    cutoff_guard(a)
    for i in range(2):
        a.op('read', WIDTH, {ONE: 'width'+str(i)})
        a.mark('width'+str(i))
        a.op('move', WIDTH, 1)
    a.rewind(WIDTH, (ONE,))
    geometry(a)
    clone_source(a)
    a.op('write', MODE, '0')
    a.mark('prefix')
    a.op('read', PREFIX, {ONE: 'load_select', BLANK: 'axis_end'})
    a.mark('load_select')
    a.op('read', MODE, {'0': 'loadA', ONE: 'loadB'})
    for mode, source in enumerate((A, B)):
        a.mark('load'+('A' if mode == 0 else 'B'))
        load_suffix(a, source, LEFT)
        load_suffix(a, source, RIGHT)
        a.op('goto', 'pairs')
    a.mark('pairs')
    a.op('read', SUFFIX, {ONE: 'pair', BLANK: 'pairs_done'})
    a.mark('pair')
    for source, target in ((LEFT, AR), (LEFT, AI), (RIGHT, BR), (RIGHT, BI)):
        copy_width(a, source, target, rewind_target=True)
    for signs, output in zip(ROWS, (LOUT, LOUT, ROUT, ROUT)):
        c_component(a, signs, output)
    for tape in INPUTS:
        clear(a, tape, BITS)
    a.op('move', SUFFIX, 1)
    a.op('goto', 'pairs')
    a.mark('pairs_done')
    a.rewind(SUFFIX, (ONE,))
    for tape in (LEFT, RIGHT):
        a.rewind(tape, (BLANK,))
    for tape in (LOUT, ROUT):
        a.rewind(tape, BITS)
    a.op('read', MODE, {'0': 'mergeB', ONE: 'mergeA'})
    for name, target in (('mergeB', B), ('mergeA', A)):
        a.mark(name)
        emit_stream(a, LOUT, target)
        emit_stream(a, ROUT, target)
        a.op('goto', 'prefix_done')
    a.mark('prefix_done')
    a.op('move', PREFIX, 1)
    a.op('goto', 'prefix')
    a.mark('axis_end')
    a.op('read', MODE, {'0': 'endA', ONE: 'endB'})
    for mode, source, target in ((0, A, B), (1, B, A)):
        name = 'end'+('A' if mode == 0 else 'B')
        a.mark(name)
        a.op('read', source, {BLANK: name+'valid'})
        a.mark(name+'valid')
        a.rewind(source, (BLANK,))
        a.rewind(target, BITS)
        a.op('write', MODE, str(1-mode))
        a.op('goto', 'axis_done')
    a.mark('axis_done')
    a.rewind(PREFIX, (ONE,))
    a.op('move', F, 1)
    a.op('read', F, {ONE: 'next_axis', BLANK: 'finish'})
    a.mark('next_axis')
    double(a, SUFFIX)
    halve(a, PREFIX)
    a.op('goto', 'prefix')
    a.mark('finish')
    a.op('read', MODE, {'0': 'commitA', ONE: 'commitB'})
    for name, source in (('commitA', A), ('commitB', B)):
        a.mark(name)
        commit(a, source)
        a.op('goto', 'retire')
    a.mark('retire')
    a.rewind(F, (ONE,))
    for tape in (F, WIDTH, PREFIX, SUFFIX):
        clear(a, tape)
    clear(a, MODE, BITS)
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject')
    a.op('read', HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))




