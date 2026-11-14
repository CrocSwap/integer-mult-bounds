"""Literal selected native quadratic phase, with complete owner commit.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. The multi-counter phase algorithm is credited to #5375. Header,
signed staging and return helpers are retained from the frozen C2 phase.
Only fixed-table read/write/unit-move/goto/halt instructions execute.
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

(HEADER, DATA, OUTPUT, HTRACE, LENGTH, DOUBLE, COLUMNS, COEFF, OUTER,
 SPECTATOR, WIDTH, REAL, IMAG, DTRACE) = range(14)
COUNTERS = tuple(range(14, 23))
PRIVATE = tuple(range(2, 23))
BITS = ('0', ONE)
SELECTED_LINEAR = (3, 3, 3, 3, 0, 3, 3, 2, 0)
SELECTED_ROWS = (111, 111, 111, 111, 0, 111, 111, 0, 0)
SELECTED_CONSTANT = 1


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


def load_component(a, target):
    k = fresh(a, 'load')
    a.mark(k)
    a.op('read', WIDTH, {ONE: k+'bit', BLANK: k+'done'})
    a.mark(k+'bit')
    a.op('read', DATA, {str(b): k+str(b) for b in (0, 1)})
    for b in (0, 1):
        a.mark(k+str(b))
        a.op('write', target, str(b))
        a.op('move', target, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('move', WIDTH, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(WIDTH, (ONE,))
    a.rewind(target, BITS)


def negate(a, tape):
    """Exact w-bit integer negation; reject the unrepresentable minimum."""
    k = fresh(a, 'neg')
    a.mark(k+'seek')
    a.op('read', tape, {'0': k+'step', ONE: k+'step', BLANK: k+'last'})
    a.mark(k+'step')
    a.op('move', tape, 1)
    a.op('goto', k+'seek')
    a.mark(k+'last')
    a.op('move', tape, -1)
    a.op('goto', k+'c1x0y0')
    for carry in (0, 1):
        for old_sign in (0, 1):
            for new_sign in (0, 1):
                name = k+f'c{carry}x{old_sign}y{new_sign}'
                a.mark(name)
                a.op('read', tape, {str(b): name+'b'+str(b) for b in (0, 1)} |
                     {MARK: 'reject' if old_sign and new_sign else k+'done'})
                for bit in (0, 1):
                    total = 1-bit+carry
                    digit, nxt = total % 2, total//2
                    a.mark(name+'b'+str(bit))
                    a.op('write', tape, str(digit))
                    a.op('move', tape, -1)
                    a.op('goto', k+f'c{nxt}x{bit}y{digit}')
    a.mark(k+'done')
    a.op('move', tape, 1)


def stage_component(a, tape):
    k = fresh(a, 'stage')
    a.mark(k)
    a.op('read', tape, {str(b): k+str(b) for b in (0, 1)} | {BLANK: k+'done'})
    for b in (0, 1):
        a.mark(k+str(b))
        a.op('write', OUTPUT, str(b))
        a.op('move', OUTPUT, 1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
        a.op('goto', k)
    a.mark(k+'done')
    a.rewind(tape, (BLANK,))


def initialize(a, counters, constant):
    """Generate f zero bits on each counter and retain constant*f mod 4."""
    a.op('goto', 'initialize0')
    for mode in range(4):
        name = 'initialize'+str(mode)
        a.mark(name)
        a.op('read', COLUMNS, {ONE: name+'bit', BLANK: name+'done'})
        a.mark(name+'bit')
        for tape in counters:
            a.op('write', tape, '0')
            a.op('move', tape, 1)
        a.op('move', COLUMNS, 1)
        a.op('goto', 'initialize'+str((mode+constant) % 4))
        a.mark(name+'done')
        a.rewind(COLUMNS, (ONE,))
        for tape in counters:
            a.rewind(tape, BITS)
        a.op('goto', 'record'+str(mode))


def advance(a, counters, linear, rows):
    """Fixed finite lowering of the credited synchronized counter updater."""
    m = len(counters)
    for i in range(m):
        neighbors = tuple(j for j in range(m) if j != i and
                          (rows[min(i, j)] >> max(i, j)) & 1)
        for mode in range(4):
            name = f'advance{i}q{mode}'
            a.mark(name)
            a.op('read', counters[i], {str(b): name+'b'+str(b) for b in (0, 1)} |
                 {BLANK: name+'overflow'})
            for bit in (0, 1):
                stem = name+'b'+str(bit)
                a.mark(stem)
                nxt = (mode+(1-2*bit)*linear[i]) % 4
                a.op('goto', stem+f'n0q{nxt}')
                for k, j in enumerate(neighbors):
                    for value in range(4):
                        label = stem+f'n{k}q{value}'
                        a.mark(label)
                        a.op('read', counters[j], {
                            str(b): stem+f'n{k+1}q{(value+2*b) % 4}'
                            for b in (0, 1)})
                for value in range(4):
                    a.mark(stem+f'n{len(neighbors)}q{value}')
                    a.op('write', counters[i], str(1-bit))
                    for tape in counters:
                        a.op('move', tape, 1)
                    a.op('goto', f'advance{i}q{value}' if bit else
                         'advanced'+str(value))
            a.mark(name+'overflow')
            for tape in counters:
                target = fresh(a, 'all_end')
                a.op('read', tape, {BLANK: target})
                a.mark(target)
            for tape in counters:
                a.rewind(tape, BITS)
            if i:
                a.op('goto', f'advance{i-1}q{mode}')
            else:
                a.op('move', OUTER, 1)
                a.op('read', OUTER, {ONE: 'record'+str(mode), BLANK: 'finish'})
    for mode in range(4):
        a.mark('advanced'+str(mode))
        for tape in counters:
            a.rewind(tape, BITS)
        a.op('goto', 'record'+str(mode))


def compile_phase(linear=SELECTED_LINEAR, rows=SELECTED_ROWS,
                  constant=SELECTED_CONSTANT):
    """Recipe is finite construction-time data; no runtime size is an argument."""
    m = len(linear)
    if not 1 <= m <= len(COUNTERS) or len(rows) != m:
        raise ValueError('fixed recipe dimension')
    if type(constant) is not int or not 0 <= constant < 4:
        raise ValueError('fixed constant phase')
    if any(type(x) is not int or not 0 <= x < 4 for x in linear):
        raise ValueError('fixed linear phase')
    if any(type(x) is not int or not 0 <= x < 1 << m for x in rows):
        raise ValueError('fixed quadratic rows')
    if any(((rows[i] >> j) ^ (rows[j] >> i)) & 1
           for i in range(m) for j in range(m)):
        raise ValueError('symmetric source quadratic matrix')
    if any((linear[i] ^ (rows[i] >> i)) & 1 for i in range(m)):
        raise ValueError('source diagonal parity')
    counters = COUNTERS[:m]
    a = Builder()
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    # Supplied local ABI: Gamma(f), Gamma(r), Gamma(P), Gamma(S), Gamma(w).
    for target in (COLUMNS, COEFF, OUTER, SPECTATOR, WIDTH):
        gamma(a, target)
    trace_return(a, HEADER, HTRACE)
    initialize(a, counters, constant)
    for mode in range(4):
        a.mark('record'+str(mode))
        a.op('read', SPECTATOR, {ONE: 'coefficient'+str(mode), BLANK: 'record_end'+str(mode)})
        a.mark('coefficient'+str(mode))
        a.op('read', COEFF, {ONE: 'payload'+str(mode), BLANK: 'coefficient_end'+str(mode)})
        a.mark('payload'+str(mode))
        load_component(a, REAL)
        load_component(a, IMAG)
        if mode in (2, 3):
            negate(a, REAL)
        if mode in (1, 2):
            negate(a, IMAG)
        order = (IMAG, REAL) if mode % 2 else (REAL, IMAG)
        for tape in order:
            stage_component(a, tape)
        a.op('move', COEFF, 1)
        a.op('goto', 'coefficient'+str(mode))
        a.mark('coefficient_end'+str(mode))
        a.rewind(COEFF, (ONE,))
        a.op('move', SPECTATOR, 1)
        a.op('goto', 'record'+str(mode))
        a.mark('record_end'+str(mode))
        a.rewind(SPECTATOR, (ONE,))
        a.op('goto', f'advance{m-1}q{mode}')
    advance(a, counters, linear, rows)
    a.mark('finish')
    a.op('read', DATA, {BLANK: 'verified', '0': 'reject', ONE: 'reject'})
    a.mark('verified')
    trace_return(a, DATA, DTRACE)
    a.rewind(OUTPUT, BITS)
    a.mark('commit')
    a.op('read', OUTPUT, {str(b): 'commit'+str(b) for b in (0, 1)} | {BLANK: 'committed'})
    for bit in ('0', ONE):
        a.mark('commit'+bit)
        a.op('write', DATA, bit)
        a.op('write', OUTPUT, BLANK)
        a.op('move', OUTPUT, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('goto', 'commit')
    a.mark('committed')
    trace_return(a, DATA, DTRACE)
    a.rewind(OUTPUT, (BLANK,))
    a.rewind(OUTER, (ONE,))
    for tape in (COLUMNS, OUTER, COEFF, SPECTATOR, WIDTH):
        clear(a, tape)
    for tape in counters:
        clear(a, tape, BITS)
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject')
    a.op('read', HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))
