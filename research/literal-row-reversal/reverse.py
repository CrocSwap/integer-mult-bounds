"""Literal complete-record reversal from three encoded binary descriptors.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
Apache-2.0. The two-stack algorithm is classical and already in 02-streams;
the unary/trace helper patterns come from the credited literal S_D package.
This zero-argument compiler emits one fixed local-symbol instruction graph.
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

(PDESC, RDESC, BDESC, DATA, OUTPUT, PTR, RTR, BTR, DOUBLE,
 HTRACE, GROUP, RECORD, DTRACE) = range(13)
PRIVATE = tuple(range(4, 13))
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


def descriptor_step(a, descriptor):
    a.op('write', HTRACE, ONE)
    a.op('move', HTRACE, 1)
    a.op('move', descriptor, 1)


def binary_descriptor(a, descriptor, target):
    """A positive canonical MSB-first binary word to a unary guide."""
    k = fresh(a, 'binary')
    a.op('read', descriptor, {ONE: k+'first'})
    a.mark(k+'first')
    a.op('write', target, ONE)
    descriptor_step(a, descriptor)
    a.mark(k+'digit')
    a.op('read', descriptor, {str(b): k+str(b) for b in (0, 1)} |
         {BLANK: k+'done'})
    for bit in (0, 1):
        a.mark(k+str(bit))
        unary_copy(a, target, DOUBLE, repeat=2, extra=bit)
        clear(a, target)
        unary_copy(a, DOUBLE, target, erase=True)
        descriptor_step(a, descriptor)
        a.op('goto', k+'digit')
    a.mark(k+'done')
    trace_return(a, descriptor, HTRACE)


def compile_reverse():
    """Compile once; no descriptor, shape, payload or origin argument."""
    a = Builder()
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, MARK)
        a.op('move', tape, 1)
    for descriptor, target in ((PDESC, PTR), (RDESC, RTR), (BDESC, BTR)):
        binary_descriptor(a, descriptor, target)
    a.mark('prefix')
    a.op('read', PTR, {ONE: 'load_record', BLANK: 'finish'})
    a.mark('load_record')
    a.op('read', RTR, {ONE: 'load_bit', BLANK: 'group_loaded'})
    a.mark('load_bit')
    a.op('read', BTR, {ONE: 'read_bit', BLANK: 'record_loaded'})
    a.mark('read_bit')
    a.op('read', DATA, {str(b): 'load'+str(b) for b in (0, 1)})
    for bit in ('0', ONE):
        a.mark('load'+bit)
        a.op('write', GROUP, bit)
        a.op('move', GROUP, 1)
        a.op('move', DATA, 1)
        a.op('write', DTRACE, ONE)
        a.op('move', DTRACE, 1)
        a.op('move', BTR, 1)
        a.op('goto', 'load_bit')
    a.mark('record_loaded')
    a.rewind(BTR, (ONE,))
    a.op('move', RTR, 1)
    a.op('goto', 'load_record')
    a.mark('group_loaded')
    a.rewind(RTR, (ONE,))
    a.op('move', GROUP, -1)
    a.mark('pop_record')
    a.op('read', RTR, {ONE: 'pop_bit', BLANK: 'group_popped'})
    a.mark('pop_bit')
    a.op('read', BTR, {ONE: 'pop_read', BLANK: 'record_popped'})
    a.mark('pop_read')
    a.op('read', GROUP, {str(b): 'pop'+str(b) for b in (0, 1)})
    for bit in ('0', ONE):
        a.mark('pop'+bit)
        a.op('write', RECORD, bit)
        a.op('move', RECORD, 1)
        a.op('write', GROUP, BLANK)
        a.op('move', GROUP, -1)
        a.op('move', BTR, 1)
        a.op('goto', 'pop_bit')
    a.mark('record_popped')
    a.rewind(BTR, (ONE,))
    a.op('move', RECORD, -1)
    a.mark('emit_record')
    a.op('read', RECORD, {str(b): 'emit'+str(b) for b in (0, 1)} |
         {MARK: 'record_emitted'})
    for bit in ('0', ONE):
        a.mark('emit'+bit)
        a.op('write', OUTPUT, bit)
        a.op('move', OUTPUT, 1)
        a.op('write', RECORD, BLANK)
        a.op('move', RECORD, -1)
        a.op('goto', 'emit_record')
    a.mark('record_emitted')
    a.op('move', RECORD, 1)
    a.op('move', RTR, 1)
    a.op('goto', 'pop_record')
    a.mark('group_popped')
    a.op('read', GROUP, {MARK: 'prefix_done'})
    a.mark('prefix_done')
    a.op('move', GROUP, 1)
    a.rewind(RTR, (ONE,))
    a.op('move', PTR, 1)
    a.op('goto', 'prefix')
    a.mark('finish')
    # Exact cardinality is derived from descriptor guides before DATA writes.
    a.op('read', DATA, {BLANK: 'verified', '0': 'reject', ONE: 'reject'})
    a.mark('verified')
    trace_return(a, DATA, DTRACE)
    a.rewind(OUTPUT, BITS)
    a.mark('commit')
    a.op('read', OUTPUT, {str(b): 'commit'+str(b) for b in (0, 1)} |
         {BLANK: 'committed'})
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
    a.rewind(PTR, (ONE,))
    for tape in (PTR, RTR, BTR):
        clear(a, tape)
    for tape in PRIVATE:
        a.op('move', tape, -1)
        a.op('write', tape, BLANK)
        a.op('move', tape, 1)
    a.op('halt')
    a.mark('reject')
    a.op('read', DATA, {})
    return a.finish((BLANK, '0', ONE, MARK))

