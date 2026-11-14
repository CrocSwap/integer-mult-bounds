"""Literal selected nine-coordinate linear maps on a packed Gaussian field.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. Split/merge, unary clocks and CNOT decomposition are credited
predecessor methods; this is their exact encoded all-column selected join.
"""
from pathlib import Path
import hashlib
import sys

HERE = Path(__file__).resolve().parent
MACHINE = HERE/'inputs/controller_reference.py'
EXPECTED_MACHINE = 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73'
if hashlib.sha256(MACHINE.read_bytes()).hexdigest() != EXPECTED_MACHINE:
    raise ValueError('frozen local machine source drift')
sys.path.insert(0, str(MACHINE.parent))
from controller_reference import Builder, Machine, Tape, BLANK, ONE, MARK

(HEADER, DATA, A, B, MODE, HTRACE, LENGTH, DOUBLE, F, R, P, S, WIDTH,
 VOLUME, AUX, PREFIX, MIDDLE, BLOCK, LEFT, RIGHT, LOUT, ROUT,
 Q0, Q1, Q2, Q3, DTRACE) = range(27)
PRIVATE = tuple(range(2, 27))
BITS = ('0', ONE)
CHUNKS = (Q0, Q1, Q2, Q3)
MATRICES = {
    'right': (239,129,130,132,136,16,160,192,256),
    'left': (3,5,9,17,32,65,129,1,256),
}
DIMENSION = 9


def cnot_word(rows):
    """Fixed-data Gaussian elimination; no input header is consulted."""
    if len(rows) != DIMENSION or any(type(x) is not int or not 0 <= x < 1 << DIMENSION for x in rows):
        raise ValueError('fixed nine-coordinate matrix')
    choices = []
    for order in (range(DIMENSION), range(DIMENSION-1, -1, -1)):
        a, eliminated, word = list(rows), set(), []
        def add(target, control):
            a[target] ^= a[control]
            word.append((target, control))
        for j in order:
            if not (a[j] >> j) & 1:
                candidates = [i for i in range(DIMENSION) if i not in eliminated and (a[i] >> j) & 1]
                if not candidates:
                    raise ValueError('singular fixed matrix')
                k = candidates[0]
                add(j, k); add(k, j); add(j, k)
            for i in range(DIMENSION):
                if i != j and (a[i] >> j) & 1:
                    add(i, j)
            eliminated.add(j)
        if a != [1 << i for i in range(DIMENSION)]:
            raise ValueError('fixed elimination invariant')
        choices.append(tuple(reversed(word)))
    return min(choices, key=lambda x: (len(x), x))


def fresh(a, stem):
    a.serial += 1
    return stem + str(a.serial) + '_'



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



def header_step(a):
    a.op('write', HTRACE, ONE)
    a.op('move', HTRACE, 1)
    a.op('move', HEADER, 1)



def gamma(a, target):
    """Actual positive Gamma code to unary, using only literal operations."""
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
    a.op('move', LENGTH, -1)
    a.mark(k+'tail')
    a.op('read', LENGTH, {ONE: k+'tailbit', MARK: k+'done'})
    a.mark(k+'tailbit')
    a.op('write', LENGTH, BLANK)
    a.op('read', HEADER, {str(b): k+'digit'+str(b) for b in (0, 1)})
    for b in (0, 1):
        a.mark(k+'digit'+str(b))
        unary_copy(a, target, DOUBLE, repeat=2, extra=b)
        clear(a, target)
        unary_copy(a, DOUBLE, target, erase=True)
        header_step(a)
        a.op('move', LENGTH, -1)
        a.op('goto', k+'tail')
    a.mark(k+'done')
    a.op('move', LENGTH, 1)



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



def multiply_guide(a, target, factor):
    product(a, target, factor, AUX)
    clear(a, target)
    unary_copy(a, AUX, target, erase=True)


def column_doublings(a, target, times):
    """times is fixed construction data; the actual F loop survives."""
    k = fresh(a, 'column_double')
    a.mark(k)
    a.op('read', F, {ONE: k+'more', BLANK: k+'done'})
    a.mark(k+'more')
    for _ in range(times):
        double(a, target)
    a.op('move', F, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(F, (ONE,))


def volume(a):
    unary_copy(a, P, VOLUME)
    for factor in (R, S, WIDTH):
        multiply_guide(a, VOLUME, factor)
    column_doublings(a, VOLUME, DIMENSION)
    double(a, VOLUME)


def geometry(a, high, low):
    # At j=0: A=P*2^((high+1)f-1), M=2^((low-high)f-1),
    # B=2wrS*2^((8-low)f). Temporary doubles are also paid.
    unary_copy(a, P, PREFIX)
    column_doublings(a, PREFIX, high+1)
    halve(a, PREFIX)
    a.op('write', MIDDLE, ONE)
    column_doublings(a, MIDDLE, low-high)
    halve(a, MIDDLE)
    product(a, R, S, BLOCK)
    multiply_guide(a, BLOCK, WIDTH)
    double(a, BLOCK)
    column_doublings(a, BLOCK, DIMENSION-1-low)


def clone(a):
    k = fresh(a, 'clone')
    a.mark(k)
    a.op('read', VOLUME, {ONE: k+'read', BLANK: k+'done'})
    a.mark(k+'read')
    a.op('read', DATA, {str(b): k+str(b) for b in (0, 1)})
    for bit in BITS:
        a.mark(k+bit)
        a.op('write', A, bit)
        a.op('move', A, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('move', VOLUME, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(VOLUME, (ONE,))
    a.op('read', DATA, {BLANK: k+'valid'})
    a.mark(k+'valid')
    trace_return(a, DATA, DTRACE)
    a.rewind(A, BITS)


def copy_block(a, source, target, *, return_target=False):
    k = fresh(a, 'block_copy')
    a.mark(k)
    a.op('read', BLOCK, {ONE: k+'read', BLANK: k+'done'})
    a.mark(k+'read')
    a.op('read', source, {str(b): k+str(b) for b in (0, 1)})
    for bit in BITS:
        a.mark(k+bit)
        a.op('write', target, bit)
        a.op('move', target, 1)
        a.op('write', source, BLANK)
        a.op('move', source, 1)
        a.op('move', BLOCK, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(BLOCK, (ONE,))
    if return_target:
        a.rewind(target, BITS)


def load_half(a, source, target):
    k = fresh(a, 'half')
    a.mark(k)
    a.op('read', MIDDLE, {ONE: k+'two', BLANK: k+'done'})
    a.mark(k+'two')
    for _ in range(2):
        copy_block(a, source, target)
    a.op('move', MIDDLE, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(MIDDLE, (ONE,))
    a.rewind(target, BITS)


def cnot_columns(a, target, control):
    """All encoded F columns of one fixed CNOT, both physical directions."""
    high, low = min(target, control), max(target, control)
    permutation = (0, 1, 3, 2) if control == high else (0, 3, 2, 1)
    geometry(a, high, low)
    k = fresh(a, 'cnot')
    a.mark(k+'prefix')
    a.op('read', PREFIX, {ONE: k+'load_select', BLANK: k+'end'})
    a.mark(k+'load_select')
    a.op('read', MODE, {'0': k+'loadA', ONE: k+'loadB'})
    for source, label in ((A, 'A'), (B, 'B')):
        a.mark(k+'load'+label)
        load_half(a, source, LEFT)
        load_half(a, source, RIGHT)
        a.op('goto', k+'middle')
    a.mark(k+'middle')
    a.op('read', MIDDLE, {ONE: k+'chunks', BLANK: k+'middle_done'})
    a.mark(k+'chunks')
    for source, chunk in ((LEFT, Q0), (LEFT, Q1), (RIGHT, Q2), (RIGHT, Q3)):
        copy_block(a, source, chunk, return_target=True)
    for i, index in enumerate(permutation):
        emit_stream(a, CHUNKS[index], LOUT if i < 2 else ROUT)
    a.op('move', MIDDLE, 1)
    a.op('goto', k+'middle')
    a.mark(k+'middle_done')
    a.rewind(MIDDLE, (ONE,))
    for tape in (LEFT, RIGHT):
        a.rewind(tape, (BLANK,))
    for tape in (LOUT, ROUT):
        a.rewind(tape, BITS)
    a.op('read', MODE, {'0': k+'mergeB', ONE: k+'mergeA'})
    for label, destination in (('mergeB', B), ('mergeA', A)):
        a.mark(k+label)
        emit_stream(a, LOUT, destination)
        emit_stream(a, ROUT, destination)
        a.op('goto', k+'prefix_done')
    a.mark(k+'prefix_done')
    a.op('move', PREFIX, 1)
    a.op('goto', k+'prefix')
    a.mark(k+'end')
    a.op('read', MODE, {'0': k+'endA', ONE: k+'endB'})
    for mode, source, destination in ((0, A, B), (1, B, A)):
        label = k+'end'+('A' if mode == 0 else 'B')
        a.mark(label)
        a.op('read', source, {BLANK: label+'valid'})
        a.mark(label+'valid')
        a.rewind(source, (BLANK,))
        a.rewind(destination, BITS)
        a.op('write', MODE, str(1-mode))
        a.op('goto', k+'column_done')
    a.mark(k+'column_done')
    a.rewind(PREFIX, (ONE,))
    a.op('move', F, 1)
    a.op('read', F, {ONE: k+'next_column', BLANK: k+'finished'})
    a.mark(k+'next_column')
    double(a, BLOCK)
    halve(a, PREFIX)
    a.op('goto', k+'prefix')
    a.mark(k+'finished')
    a.rewind(F, (ONE,))
    for tape in (PREFIX, MIDDLE, BLOCK):
        clear(a, tape)


def compile_linear(side):
    """side is fixed construction data: exactly 'left' or 'right'."""
    if side not in MATRICES:
        raise ValueError('one of the two selected fixed linear maps is required')
    word = cnot_word(MATRICES[side])
    a = Builder()
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    for target in (F, R, P, S, WIDTH):
        gamma(a, target)
    trace_return(a, HEADER, HTRACE)
    volume(a)
    clone(a)
    a.op('write', MODE, '0')
    for target, control in word:
        cnot_columns(a, target, control)
    a.op('read', MODE, {'0': 'commitA', ONE: 'commitB'})
    for label, source in (('commitA', A), ('commitB', B)):
        a.mark(label)
        commit(a, source)
        a.op('goto', 'retire')
    a.mark('retire')
    for tape in (F, R, P, S, WIDTH, VOLUME):
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
