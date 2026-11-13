"""Literal descriptor production and selected post-matrix X_1 translation.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. Gamma/unary patterns are credited to the retained native phase;
the complete-record permutation is the unchanged retained row-reversal graph.
All integer arithmetic below is fixed-table construction, never runtime work.
"""
from pathlib import Path
import hashlib
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    'reference/reverse.py': '4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245',
    'reference/inputs/controller_reference.py': 'e664a748e6b6797d4b60f60a7a7dd68b59a5608acf56b9c5d8b466f363755f73',
}
for path, expected in PINS.items():
    if hashlib.sha256((HERE / path).read_bytes()).hexdigest() != expected:
        raise ValueError('frozen source bytes: ' + path)
spec = importlib.util.spec_from_file_location('translation_retained_reverse', HERE / 'reference/reverse.py')
REV = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = REV
spec.loader.exec_module(REV)
Builder, BLANK, ONE, MARK = REV.Builder, REV.BLANK, REV.ONE, REV.MARK
clear, unary_copy, trace_return, fresh = REV.clear, REV.unary_copy, REV.trace_return, REV.fresh
BITS = ('0', ONE)

HEADER, DATA, PDESC, RDESC, BDESC = range(5)
# The retained reversal's nine private ports become 5,...,13.
HTRACE, LENGTH, DOUBLE, F, COEFF, OUTER, SPECTATOR, WIDTH, PRODUCT, HALF, DIGITS = range(14, 25)
PRODUCER_PRIVATE = (PDESC, RDESC, BDESC) + tuple(range(14, 25))
ALL_PRIVATE = tuple(range(2, 25))
REVERSE_PORTS = (PDESC, RDESC, BDESC, DATA) + tuple(range(5, 14))


def header_step(a):
    a.op('write', HTRACE, ONE)
    a.op('move', HTRACE, 1)
    a.op('move', HEADER, 1)


def gamma(a, target):
    """Retained five-Gamma decoding pattern on this fixed private inventory."""
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
    for bit in (0, 1):
        a.mark(k+'digit'+str(bit))
        unary_copy(a, target, DOUBLE, repeat=2, extra=bit)
        clear(a, target)
        unary_copy(a, DOUBLE, target, erase=True)
        header_step(a)
        a.op('move', LENGTH, -1)
        a.op('goto', k+'tail')
    a.mark(k+'done')
    a.op('move', LENGTH, 1)


def power_descriptor(a):
    """Write the canonical descriptor 1 followed by f zeroes, not unary 2^f."""
    a.op('write', RDESC, ONE)
    a.op('move', RDESC, 1)
    k = fresh(a, 'power')
    a.mark(k)
    a.op('read', F, {ONE: k+'bit', BLANK: k+'done'})
    a.mark(k+'bit')
    a.op('write', RDESC, '0')
    a.op('move', RDESC, 1)
    a.op('move', F, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(F, (ONE,))
    a.rewind(RDESC, BITS)


def product_guide(a):
    """Generate exactly 2*S*r*w unary marks by actual nested local scans."""
    k = fresh(a, 'product')
    a.mark(k+'s')
    a.op('read', SPECTATOR, {ONE: k+'r', BLANK: k+'done'})
    a.mark(k+'r')
    a.op('read', COEFF, {ONE: k+'w', BLANK: k+'r_done'})
    a.mark(k+'w')
    a.op('read', WIDTH, {ONE: k+'bit', BLANK: k+'w_done'})
    a.mark(k+'bit')
    for _ in range(2):
        a.op('write', PRODUCT, ONE)
        a.op('move', PRODUCT, 1)
    a.op('move', WIDTH, 1)
    a.op('goto', k+'w')
    a.mark(k+'w_done')
    a.rewind(WIDTH, (ONE,))
    a.op('move', COEFF, 1)
    a.op('goto', k+'r')
    a.mark(k+'r_done')
    a.rewind(COEFF, (ONE,))
    a.op('move', SPECTATOR, 1)
    a.op('goto', k+'s')
    a.mark(k+'done')
    a.rewind(SPECTATOR, (ONE,))
    a.rewind(PRODUCT, (ONE,))


def suffix_power(a):
    """Multiply the PRODUCT guide by 2^(8f), in eight fixed doublings per mark."""
    k = fresh(a, 'suffix')
    a.mark(k)
    a.op('read', F, {ONE: k+'bit', BLANK: k+'done'})
    a.mark(k+'bit')
    for _ in range(8):
        unary_copy(a, PRODUCT, DOUBLE, repeat=2)
        clear(a, PRODUCT)
        unary_copy(a, DOUBLE, PRODUCT, erase=True)
    a.op('move', F, 1)
    a.op('goto', k)
    a.mark(k+'done')
    a.rewind(F, (ONE,))


def unary_binary(a, source, destination):
    """Consume positive unary n; emit canonical MSB-first binary n in O(n).

    source, HALF, DIGITS and destination are distinct guarded physical roles.
    Every parity, quotient and termination choice is a local scanned branch.
    """
    k = fresh(a, 'encode')
    a.op('goto', k+'p0q0')
    for phase, (current, quotient) in enumerate(((source, HALF), (HALF, source))):
        for parity in (0, 1):
            name = k+f'p{phase}q{parity}'
            a.mark(name)
            a.op('read', current, {ONE: name+'bit', BLANK: name+'done'})
            a.mark(name+'bit')
            a.op('write', current, BLANK)
            if parity:
                a.op('write', quotient, ONE)
                a.op('move', quotient, 1)
            a.op('move', current, 1)
            a.op('goto', k+f'p{phase}q{1-parity}')
            a.mark(name+'done')
            a.rewind(current, (BLANK,))
            a.rewind(quotient, (ONE,))
            a.op('write', DIGITS, str(parity))
            a.op('move', DIGITS, 1)
            a.op('read', quotient, {ONE: k+f'p{1-phase}q0', BLANK: k+'emit_start'})
    a.mark(k+'emit_start')
    a.op('move', DIGITS, -1)
    a.mark(k+'emit')
    a.op('read', DIGITS, {str(b): k+'emit'+str(b) for b in (0, 1)} | {MARK: k+'done'})
    for bit in (0, 1):
        a.mark(k+'emit'+str(bit))
        a.op('write', destination, str(bit))
        a.op('move', destination, 1)
        a.op('write', DIGITS, BLANK)
        a.op('move', DIGITS, -1)
        a.op('goto', k+'emit')
    a.mark(k+'done')
    a.op('move', DIGITS, 1)
    a.rewind(destination, BITS)


def retained_reversal(a, after):
    """Construction-only relabeling; every retained runtime instruction remains local."""
    code, alphabet = REV.compile_reverse()
    if alphabet != (BLANK, '0', ONE, MARK):
        raise ValueError('retained alphabet')
    for pc, instruction in enumerate(code):
        a.mark('reverse_'+str(pc))
        op, *args = instruction
        if op == 'read':
            a.op(op, REVERSE_PORTS[args[0]], {s: 'reverse_'+str(dst) for s, dst in args[1].items()})
        elif op in ('write', 'move'):
            a.op(op, REVERSE_PORTS[args[0]], args[1])
        elif op == 'goto':
            a.op(op, 'reverse_'+str(args[0]))
        elif op == 'halt':
            a.op('goto', after)
        else:
            raise ValueError('nonlocal retained opcode')


def compile_translation():
    """One fixed 25-tape program; no runtime integer or recipe argument."""
    a = Builder()
    for tape in PRODUCER_PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    for target in (F, COEFF, OUTER, SPECTATOR, WIDTH):
        gamma(a, target)
    trace_return(a, HEADER, HTRACE)
    power_descriptor(a)
    product_guide(a)
    suffix_power(a)
    unary_binary(a, OUTER, PDESC)
    unary_binary(a, PRODUCT, BDESC)
    retained_reversal(a, 'retire_descriptors')
    a.mark('retire_descriptors')
    for tape in PRODUCER_PRIVATE:
        clear(a, tape, BITS)
    for tape in PRODUCER_PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    return a.finish((BLANK, '0', ONE, MARK))
