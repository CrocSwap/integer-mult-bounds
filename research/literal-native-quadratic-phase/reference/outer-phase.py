"""Header-derived literal S_D phase sweep on implicit layer addresses.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. Gaussian phases and counter amortization are credited prior work;
see PROOF.md. Python constructs one fixed graph, never an input-sized graph.
Only scanned symbols, fixed jumps, one-cell writes and unit moves execute.
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

(HEADER, DATA, OUTPUT, HTRACE, LENGTH, DOUBLE, PREC, GLOBAL, COEFF, DIM,
 OUTER, SPECTATOR, BLOCK, SELECT, WIDTH, MASK, COUNT, REAL, IMAG, DTRACE) = range(20)
PRIVATE = tuple(range(2, 20))
BITS = ('0', ONE)


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


def make_geometry(a):
    """Generate D K-bit chunks with active position rho, all LSB first."""
    a.mark('build_chunk')
    a.op('read', DIM, {ONE: 'build_before', BLANK: 'geometry_done'})
    a.mark('build_before')
    a.op('read', BLOCK, {ONE: 'build_select', BLANK: 'reject'})
    a.mark('build_select')
    a.op('read', SELECT, {ONE: 'select_step'})
    a.mark('select_step')
    a.op('move', SELECT, 1)
    a.op('read', SELECT, {ONE: 'mask_before', BLANK: 'mask_active'})
    a.mark('build_after')
    a.op('read', BLOCK, {ONE: 'mask_after', BLANK: 'chunk_done'})
    for name, bit, nxt in (('mask_before', '0', 'build_before'),
                           ('mask_active', ONE, 'build_after'),
                           ('mask_after', '0', 'build_after')):
        a.mark(name)
        a.op('write', MASK, bit)
        a.op('move', MASK, 1)
        a.op('write', COUNT, '0')
        a.op('move', COUNT, 1)
        a.op('move', BLOCK, 1)
        a.op('goto', nxt)
    a.mark('chunk_done')
    a.rewind(BLOCK, (ONE,))
    a.rewind(SELECT, (ONE,))
    a.op('move', DIM, 1)
    a.op('goto', 'build_chunk')
    a.mark('geometry_done')
    a.rewind(DIM, (ONE,))
    a.rewind(MASK, BITS)
    a.rewind(COUNT, BITS)


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


def advance(a):
    """Full binary increment; phase is always fixed four-state control."""
    for mode in range(4):
        name = 'advance'+str(mode)
        a.mark(name)
        a.op('read', COUNT, {str(b): name+'b'+str(b) for b in (0, 1)} |
             {BLANK: 'overflow'+str(mode)})
        for bit in (0, 1):
            a.mark(name+'b'+str(bit))
            a.op('read', MASK, {str(active): name+f'b{bit}m{active}' for active in (0, 1)})
            for active in (0, 1):
                a.mark(name+f'b{bit}m{active}')
                nxt = (mode + (1-2*bit)*active) % 4
                a.op('write', COUNT, str(1-bit))
                a.op('move', COUNT, 1)
                a.op('move', MASK, 1)
                a.op('goto', 'advance'+str(nxt) if bit else 'advanced'+str(nxt))
    for mode in range(4):
        a.mark('advanced'+str(mode))
        a.rewind(COUNT, BITS)
        a.rewind(MASK, BITS)
        a.op('goto', 'record'+str(mode))
        a.mark('overflow'+str(mode))
        a.op('read', MASK, {BLANK: 'wrapped'+str(mode)})
        a.mark('wrapped'+str(mode))
        if mode:
            a.op('goto', 'reject')
        else:
            a.rewind(COUNT, BITS)
            a.rewind(MASK, BITS)
            a.op('move', OUTER, 1)
            a.op('read', OUTER, {ONE: 'record0', BLANK: 'finish'})


def compile_phase():
    a = Builder()
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    # Actual header: p,d,r,D,P,S,K,rho+1,w. Runtime values stay on tapes.
    for target in (PREC, GLOBAL, COEFF, DIM, OUTER, SPECTATOR, BLOCK, SELECT, WIDTH):
        gamma(a, target)
    trace_return(a, HEADER, HTRACE)
    a.mark('dimension_check')
    a.op('read', DIM, {ONE: 'dimension_global', BLANK: 'dimension_ok'})
    a.mark('dimension_global')
    a.op('read', GLOBAL, {ONE: 'dimension_step', BLANK: 'reject'})
    a.mark('dimension_step')
    a.op('move', DIM, 1)
    a.op('move', GLOBAL, 1)
    a.op('goto', 'dimension_check')
    a.mark('dimension_ok')
    a.rewind(DIM, (ONE,))
    a.rewind(GLOBAL, (ONE,))
    a.mark('width_check')
    a.op('read', PREC, {ONE: 'width_precision', BLANK: 'width_extra0'})
    a.mark('width_precision')
    a.op('read', WIDTH, {ONE: 'width_step', BLANK: 'reject'})
    a.mark('width_step')
    a.op('move', PREC, 1)
    a.op('move', WIDTH, 1)
    a.op('goto', 'width_check')
    for i in range(2):
        a.mark('width_extra'+str(i))
        a.op('read', WIDTH, {ONE: 'width_more'+str(i), BLANK: 'reject'})
        a.mark('width_more'+str(i))
        a.op('move', WIDTH, 1)
    a.rewind(PREC, (ONE,))
    a.rewind(WIDTH, (ONE,))
    make_geometry(a)
    for tape in (PREC, GLOBAL, DIM, BLOCK, SELECT):
        clear(a, tape)
    a.op('goto', 'record0')
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
        a.op('goto', 'advance'+str(mode))
    advance(a)
    a.mark('finish')
    # Header-derived geometry determines cardinality, not a host oracle.
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
    for tape in (OUTER, COEFF, SPECTATOR, WIDTH):
        clear(a, tape)
    for tape in (MASK, COUNT):
        clear(a, tape, BITS)
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject')
    a.op('read', HEADER, {})
    return a.finish((BLANK, '0', ONE, MARK))
