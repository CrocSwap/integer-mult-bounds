"""Literal whole-layer normalization and toward-zero egress.

Apache-2.0. Prepared for CubeJerry with substantial OpenAI assistance.
All Python arithmetic here constructs a FIXED transition table.  The running
table uses only scanned symbols, fixed jumps, writes and unit moves.
"""
from pathlib import Path
import hashlib
import sys

HERE = Path(__file__).resolve().parent
REF = HERE / 'inputs' / 'controller_reference.py'
EXPECTED_MACHINE = 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73'
if hashlib.sha256(REF.read_bytes()).hexdigest() != EXPECTED_MACHINE:
    raise ValueError('frozen machine source drift')
sys.path.insert(0, str(REF.parent))
from controller_reference import Builder, Machine, Tape, BLANK, ONE, MARK

HEADER, DATA, OUTPUT, HTRACE, LENGTH, VALUE, DOUBLE, P, DU, D, W, H, SHIFT, X, Y, NUM, QBUF, DTRACE = range(18)
PRIVATE = tuple(range(2, 18))
BITS = ('0', '1')


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


def unary_copy(a, source, target, *, repeat=1, extra=0, erase=False, return_target=True):
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
    if return_target:
        a.rewind(target, (ONE,))


def header_step(a):
    a.op('write', HTRACE, ONE)
    a.op('move', HTRACE, 1)
    a.op('move', HEADER, 1)


def gamma(a, target=None):
    """Read one canonical positive Elias-gamma word, optionally to unary."""
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
    if target is not None:
        a.op('write', target, ONE)
    a.op('move', LENGTH, -1)
    a.mark(k+'tail')
    a.op('read', LENGTH, {ONE: k+'tailbit', MARK: k+'done'})
    a.mark(k+'tailbit')
    a.op('write', LENGTH, BLANK)
    a.op('read', HEADER, {str(b): k+'digit'+str(b) for b in (0, 1)})
    for b in (0, 1):
        a.mark(k+'digit'+str(b))
        if target is not None:
            unary_copy(a, target, DOUBLE, repeat=2, extra=b)
            clear(a, target)
            unary_copy(a, DOUBLE, target, erase=True)
        header_step(a)
        a.op('move', LENGTH, -1)
        a.op('goto', k+'tail')
    a.mark(k+'done')
    a.op('move', LENGTH, 1)


def trace_return(a, tape, trace):
    """Heads: tape at one-past its visited prefix; trace at unary end."""
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


def copy_component(a, target):
    """Read H MSB source bits, leave target at its one-past end."""
    k = fresh(a, 'load')
    a.mark(k)
    a.op('read', H, {ONE: k+'bit', BLANK: k+'done'})
    a.mark(k+'bit')
    a.op('read', DATA, {str(b): k+str(b) for b in (0, 1)})
    for b in (0, 1):
        a.mark(k+str(b))
        a.op('write', target, str(b))
        a.op('move', target, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('move', H, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(H, (ONE,))
    a.rewind(target, BITS)


def seek_last(a, tape):
    k = fresh(a, 'last')
    a.mark(k)
    a.op('read', tape, {'0': k+'bit', ONE: k+'bit', BLANK: k+'done'})
    a.mark(k+'bit')
    a.op('move', tape, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.op('move', tape, -1)


def negate_magnitude(a):
    """In-place two's-complement negation of the signed LSB NUM buffer."""
    k = fresh(a, 'abs')
    a.op('goto', k+'1')
    for carry in (0, 1):
        a.mark(k+str(carry))
        a.op('read', NUM, {str(b): k+f'{carry}b{b}' for b in (0, 1)} | {BLANK: k+'done'})
        for b in (0, 1):
            t = 1-b+carry
            a.mark(k+f'{carry}b{b}')
            a.op('write', NUM, str(t % 2))
            a.op('move', NUM, 1)
            a.op('goto', k+str(t//2))
    a.mark(k+'done')
    a.rewind(NUM, BITS)


def quotient(a, negative, done):
    """Discard SHIFT absolute low bits; emit W signed bits with range guard."""
    k = fresh(a, 'quot')
    a.mark(k+'drop')
    a.op('read', SHIFT, {ONE: k+'skip', BLANK: k+'dropped'})
    a.mark(k+'skip')
    a.op('read', NUM, {'0': k+'advance', ONE: k+'advance'})
    a.mark(k+'advance')
    a.op('move', NUM, 1)
    a.op('move', SHIFT, 1)
    a.op('goto', k+'drop')
    a.mark(k+'dropped')
    a.rewind(SHIFT, (ONE,))
    a.op('goto', k+f'out{int(negative)}s0')
    for carry in (0, 1):
        for last in (0, 1):
            name = k+f'out{carry}s{last}'
            a.mark(name)
            a.op('read', W, {ONE: name+'read', BLANK: k+f'guard{carry}s{last}'})
            a.mark(name+'read')
            a.op('read', NUM, {s: name+'n'+s for s in ('0', ONE, BLANK)})
            for symbol in ('0', ONE, BLANK):
                b = int(symbol) if symbol != BLANK else 0
                t = 1-b+carry if negative else b
                digit, nxt = t % 2, t//2 if negative else 0
                a.mark(name+'n'+symbol)
                a.op('write', QBUF, str(digit))
                a.op('move', QBUF, 1)
                a.op('move', W, 1)
                if symbol != BLANK:
                    a.op('move', NUM, 1)
                a.op('goto', k+f'out{nxt}s{digit}')
            name = k+f'guard{carry}s{last}'
            a.mark(name)
            a.op('read', NUM, {s: name+'n'+s for s in ('0', ONE, BLANK)})
            for symbol in ('0', ONE, BLANK):
                b = int(symbol) if symbol != BLANK else 0
                t = 1-b+carry if negative else b
                digit, nxt = t % 2, t//2 if negative else 0
                a.mark(name+'n'+symbol)
                if digit != last:
                    a.op('goto', 'reject')
                elif symbol == BLANK:
                    a.op('goto', k+'accepted')
                else:
                    a.op('move', NUM, 1)
                    a.op('goto', k+f'guard{nxt}s{last}')
    a.mark(k+'accepted')
    a.rewind(W, (ONE,))
    a.op('move', QBUF, -1)
    a.mark(k+'store')
    a.op('read', QBUF, {str(b): k+'store'+str(b) for b in (0, 1)} | {MARK: k+'stored'})
    for b in (0, 1):
        a.mark(k+'store'+str(b))
        a.op('write', OUTPUT, str(b))
        a.op('move', OUTPUT, 1)
        a.op('write', QBUF, BLANK)
        a.op('move', QBUF, -1)
        a.op('goto', k+'store')
    a.mark(k+'stored')
    a.op('move', QBUF, 1)
    a.rewind(NUM, BITS)
    clear(a, NUM, BITS)
    a.op('goto', done)


def component(a, coefficients):
    """Evaluate one fixed signed row, then normalize/truncate it."""
    alpha, beta = coefficients
    k = fresh(a, 'row')
    seek_last(a, X)
    seek_last(a, Y)
    a.op('goto', k+'c0x0y0')
    for carry in (-2, -1, 0, 1):
        for sx in (0, 1):
            for sy in (0, 1):
                name = k+f'c{carry}x{sx}y{sy}'
                a.mark(name)
                a.op('read', H, {ONE: name+'readx', BLANK: name+'extend'})
                a.mark(name+'readx')
                a.op('read', X, {str(x): name+'x'+str(x) for x in (0, 1)})
                for x in (0, 1):
                    a.mark(name+'x'+str(x))
                    a.op('read', Y, {str(y): name+f'x{x}y{y}' for y in (0, 1)})
                    for y in (0, 1):
                        t = carry+alpha*x+beta*y
                        digit, nxt = t % 2, t//2
                        a.mark(name+f'x{x}y{y}')
                        a.op('write', NUM, str(digit))
                        a.op('move', NUM, 1)
                        a.op('move', X, -1)
                        a.op('move', Y, -1)
                        a.op('move', H, 1)
                        a.op('goto', k+f'c{nxt}x{x}y{y}')
                a.mark(name+'extend')
                c = carry
                for _ in range(2):
                    t = c+alpha*sx+beta*sy
                    digit, c = t % 2, t//2
                    a.op('write', NUM, str(digit))
                    a.op('move', NUM, 1)
                a.op('move', X, 1)
                a.op('move', Y, 1)
                a.rewind(H, (ONE,))
                a.rewind(NUM, BITS)
                a.op('goto', k+'negative' if digit else k+'positive')
    a.mark(k+'negative')
    negate_magnitude(a)
    quotient(a, True, k+'done')
    a.mark(k+'positive')
    quotient(a, False, k+'done')
    a.mark(k+'done')


def numerator_rows(mode):
    """Compile-time Gaussian rows for D mod 8 only."""
    even = ((1, 0), (0, 1))
    odd = ((1, 1), (-1, 1))
    rows = odd if mode % 2 else even
    for _ in range(mode//2):
        rows = (rows[1], tuple(-v for v in rows[0]))
    return rows


def compile_egress():
    a = Builder()
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    # The ACTUAL layer header, including the five skipped potentially huge fields.
    for target in (P, DU, None, D, None, None, None, None, W):
        gamma(a, target)
    trace_return(a, HEADER, HTRACE)
    # Check the two numerical domain predicates used by this implementation.
    a.mark('rank_le_d')
    a.op('read', D, {ONE: 'rank_d_check', BLANK: 'rank_ok'})
    a.mark('rank_d_check')
    a.op('read', DU, {ONE: 'rank_step', BLANK: 'reject'})
    a.mark('rank_step')
    a.op('move', D, 1)
    a.op('move', DU, 1)
    a.op('goto', 'rank_le_d')
    a.mark('rank_ok')
    a.rewind(D, (ONE,))
    a.rewind(DU, (ONE,))
    a.mark('width_ge_p')
    a.op('read', P, {ONE: 'width_check', BLANK: 'width_extra0'})
    a.mark('width_check')
    a.op('read', W, {ONE: 'width_step', BLANK: 'reject'})
    a.mark('width_step')
    a.op('move', P, 1)
    a.op('move', W, 1)
    a.op('goto', 'width_ge_p')
    for i in range(2):
        a.mark('width_extra'+str(i))
        a.op('read', W, {ONE: 'width_more'+str(i), BLANK: 'reject'})
        a.mark('width_more'+str(i))
        a.op('move', W, 1)
    a.rewind(P, (ONE,))
    a.rewind(W, (ONE,))
    unary_copy(a, P, H, return_target=False)
    unary_copy(a, DU, H, repeat=2, extra=4, return_target=False)
    a.rewind(H, (ONE,))
    unary_copy(a, DU, SHIFT, return_target=False)
    a.op('goto', 'phase0')
    for mode in range(8):
        a.mark('phase'+str(mode))
        a.op('read', D, {ONE: 'phasebit'+str(mode), BLANK: 'phaseend'+str(mode)})
        a.mark('phasebit'+str(mode))
        if mode % 2 == 0:
            a.op('write', SHIFT, ONE)
            a.op('move', SHIFT, 1)
        a.op('move', D, 1)
        a.op('goto', 'phase'+str((mode+1) % 8))
    for mode in range(8):
        a.mark('phaseend'+str(mode))
        a.rewind(D, (ONE,))
        a.rewind(SHIFT, (ONE,))
        for tape in (P, DU, D):
            clear(a, tape)
        # A successful packet is nonempty; all further ends occur between pairs.
        a.op('read', DATA, {'0': 'field'+str(mode), ONE: 'field'+str(mode)})
        a.mark('field'+str(mode))
        copy_component(a, X)
        copy_component(a, Y)
        for row in numerator_rows(mode):
            component(a, row)
        clear(a, X, BITS)
        clear(a, Y, BITS)
        a.op('read', DATA, {'0': 'field'+str(mode), ONE: 'field'+str(mode), BLANK: 'finish'})
    a.mark('finish')
    trace_return(a, DATA, DTRACE)
    a.rewind(OUTPUT, BITS)
    # Complete output is protected until this point; install it on the SAME owner.
    a.mark('commit')
    a.op('read', OUTPUT, {'0': 'commit0', ONE: 'commit1', BLANK: 'old_tail'})
    for bit in ('0', ONE):
        a.mark('commit'+bit)
        a.op('write', DATA, bit)
        a.op('write', OUTPUT, BLANK)
        a.op('move', OUTPUT, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('goto', 'commit')
    a.mark('old_tail')
    a.op('read', DATA, {'0': 'old_tail_bit', ONE: 'old_tail_bit', BLANK: 'committed'})
    a.mark('old_tail_bit')
    a.op('write', DATA, BLANK)
    a.op('move', DATA, 1)
    a.op('write', DTRACE, ONE)
    a.op('move', DTRACE, 1)
    a.op('goto', 'old_tail')
    a.mark('committed')
    trace_return(a, DATA, DTRACE)
    a.rewind(OUTPUT, (BLANK,))
    for tape in (W, H, SHIFT):
        clear(a, tape)
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject')
    a.op('read', HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))
