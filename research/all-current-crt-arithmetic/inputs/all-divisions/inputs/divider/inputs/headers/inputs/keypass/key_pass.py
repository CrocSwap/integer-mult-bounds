"""Literal destination-key pass over the actual fixed thirteen-bit payload ABI.

Constructors run offline. The same fixed graph handles every encoded h,p.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROUTE_SHA = 'efc3d8b0d089a56765f3eb6a2cc2a641a99f257a58f069a4d26fe5c912b1abd3'
ROUTE_GRAPH = 'f8f0bd615531c914efc110d8a9d5ce2fafa2b00c8a568bdbfb86bf24868a0ef7'
ADDRESS, WIDTH, INDEX, PAYLOAD, TAPES = 18, 19, 20, 21, 22
CODE_BITS = 13
CODES = {'<': 5, '>': 6, '0': 2, '1': 3}


def route_source():
    path = HERE/'inputs/route/controller.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != ROUTE_SHA:
        raise ValueError('exact whole-row source changed')
    module = types.ModuleType('_key_pass_whole_row')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def bits(symbol):
    return tuple(str((CODES[symbol] >> bit) & 1) for bit in range(CODE_BITS))


def consume_marker(b, symbol):
    for bit in bits(symbol):
        b.expect(PAYLOAD, bit)
        b.op('M', PAYLOAD, 1)


def clear_word(b, tape):
    b.expect(tape, 'L')
    b.op('M', tape, 1)
    loop, erase, end = (b.fresh(stem) for stem in ('clear', 'clear_bit', 'clear_end'))
    b.mark(loop)
    b.read(tape, {'0': erase, '1': erase, 'R': end})
    b.mark(erase)
    b.op('W', tape, '_')
    b.op('M', tape, 1)
    b.jump(loop)
    b.mark(end)
    b.op('W', tape, '_')
    b.rewind(tape)
    b.op('W', tape, '_')


def initialize_index(b):
    b.expect(INDEX, '_')
    b.expect(ADDRESS, '_')
    b.expect(WIDTH, 'L')
    b.op('W', INDEX, 'L')
    b.op('M', INDEX, 1)
    b.op('M', WIDTH, 1)
    b.expect(WIDTH, '1')
    loop, mark, end = (b.fresh(stem) for stem in ('width', 'index_digit', 'index_end'))
    b.mark(loop)
    b.read(WIDTH, {'1': mark, 'R': end})
    b.mark(mark)
    b.op('W', INDEX, '0')
    b.op('M', INDEX, 1)
    b.op('M', WIDTH, 1)
    b.jump(loop)
    b.mark(end)
    b.op('W', INDEX, 'R')
    b.rewind(INDEX)
    b.rewind(WIDTH)


def copy_index(b):
    b.expect(ADDRESS, '_')
    b.expect(INDEX, 'L')
    b.op('W', ADDRESS, 'L')
    b.op('M', ADDRESS, 1)
    b.op('M', INDEX, 1)
    loop, zero, one, end = (b.fresh(stem) for stem in ('copy', 'copy0', 'copy1', 'copied'))
    b.mark(loop)
    b.read(INDEX, {'0': zero, '1': one, 'R': end})
    for digit, label in (('0', zero), ('1', one)):
        b.mark(label)
        b.op('W', ADDRESS, digit)
        b.op('M', ADDRESS, 1)
        b.op('M', INDEX, 1)
        b.jump(loop)
    b.mark(end)
    b.op('W', ADDRESS, 'R')
    b.rewind(INDEX)
    b.rewind(ADDRESS)


def increment_index(b, more, complete):
    b.expect(INDEX, 'L')
    b.op('M', INDEX, 1)
    loop, carry, terminal, overflow = (b.fresh(stem) for stem in ('increment', 'carry', 'incremented', 'wrap'))
    b.mark(loop)
    b.read(INDEX, {'1': carry, '0': terminal, 'R': overflow})
    b.mark(carry)
    b.op('W', INDEX, '0')
    b.op('M', INDEX, 1)
    b.jump(loop)
    b.mark(terminal)
    b.op('W', INDEX, '1')
    b.rewind(INDEX)
    b.jump(more)
    b.mark(overflow)
    b.rewind(INDEX)
    b.jump(complete)


def write_key_code(b, digit):
    first = b.fresh('allocated_key_bit')
    b.read(PAYLOAD, {'0': first, '1': first})
    b.mark(first)
    b.op('M', PAYLOAD, 1)
    for value in ('1', *('0',)*11):
        b.expect(PAYLOAD, value)
        b.op('M', PAYLOAD, 1)
    for _ in range(CODE_BITS):
        b.op('M', PAYLOAD, -1)
    for value in bits(digit):
        b.op('W', PAYLOAD, value)
        b.op('M', PAYLOAD, 1)


def rekey(b):
    b.expect(ADDRESS, 'L')
    b.op('M', ADDRESS, 1)
    scan, next_bit, high = (b.fresh(stem) for stem in ('seek_high', 'seek_next', 'highest'))
    b.mark(scan)
    b.read(ADDRESS, {'0': next_bit, '1': next_bit, 'R': high})
    b.mark(next_bit)
    b.op('M', ADDRESS, 1)
    b.jump(scan)
    b.mark(high)
    b.op('M', ADDRESS, -1)
    loop, zero, one, written, end = (b.fresh(stem) for stem in ('rekey', 'key0', 'key1', 'key_written', 'keys_end'))
    b.mark(loop)
    b.read(ADDRESS, {'0': zero, '1': one, 'L': end})
    for digit, label in (('0', zero), ('1', one)):
        b.mark(label)
        write_key_code(b, digit)
        b.jump(written)
    b.mark(written)
    b.op('M', ADDRESS, -1)
    b.jump(loop)
    b.mark(end)


def rewind_payload(b):
    """Paid aligned thirteen-bit scan; Boolean matching is fixed control."""
    name, done = b.fresh('payload_home'), b.fresh('payload_returned')
    for bit, expected in enumerate(bits('<')):
        good, bad = name+'_good_'+str(bit), name+'_bad_'+str(bit)
        yes, no, ignore = (b.fresh(stem) for stem in ('matched', 'mismatched', 'already_false'))
        b.mark(good)
        b.read(PAYLOAD, {expected: yes, str(1-int(expected)): no})
        b.mark(yes)
        b.op('M', PAYLOAD, 1)
        b.jump(name+'_good_'+str(bit+1))
        b.mark(no)
        b.op('M', PAYLOAD, 1)
        b.jump(name+'_bad_'+str(bit+1))
        b.mark(bad)
        b.read(PAYLOAD, {'0': ignore, '1': ignore})
        b.mark(ignore)
        b.op('M', PAYLOAD, 1)
        b.jump(name+'_bad_'+str(bit+1))
    b.mark(name+'_good_'+str(CODE_BITS))
    for _ in range(CODE_BITS):
        b.op('M', PAYLOAD, -1)
    b.jump(done)
    b.mark(name+'_bad_'+str(CODE_BITS))
    for _ in range(2*CODE_BITS):
        b.op('M', PAYLOAD, -1)
    b.jump(name+'_good_0')
    b.mark(done)


def mode_pass(b, name, child_entry):
    b.mark(name)
    consume_marker(b, '<')
    initialize_index(b)
    b.mark(name+'_RECORD')
    for _ in range(12):
        b.op('M', PAYLOAD, 1)
    b.expect(PAYLOAD, '1')
    b.op('M', PAYLOAD, 1)
    b.mark(name+'_COPY_INDEX')
    copy_index(b)
    b.jump(name+'_ROUTE_'+str(child_entry))
    b.mark(name+'_ROUTE_RETURN')
    rekey(b)
    clear_word(b, ADDRESS)
    b.mark(name+'_INDEX_INCREMENT')
    increment_index(b, name+'_RECORD', name+'_FINISH')
    b.mark(name+'_FINISH')
    consume_marker(b, '>')
    for _ in range(CODE_BITS):
        b.op('M', PAYLOAD, -1)
    b.mark(name+'_PAYLOAD_REWIND')
    rewind_payload(b)
    b.mark(name+'_INDEX_RETIRE')
    clear_word(b, INDEX)
    b.op('H', 'DONE')


def embed_route(b, code, name):
    for pc, instruction in enumerate(code):
        b.mark(name+'_ROUTE_'+str(pc))
        op, *args = instruction
        if op == 'R':
            b.read(args[0], {symbol: name+'_ROUTE_'+str(target)
                             for symbol, target in args[1].items()})
        elif op == 'J':
            b.jump(name+'_ROUTE_'+str(args[0]))
        elif op == 'H' and args[0] == 'DONE':
            b.jump(name+'_ROUTE_RETURN')
        elif op in ('W', 'M', 'H'):
            b.op(op, *args)
        else:
            raise ValueError('unsupported whole-row instruction')


def compile_pass():
    route = route_source()
    code, route_labels, route_meta = route.compile_controller()
    if len(code) != 10123 or route.digest(code) != ROUTE_GRAPH:
        raise ValueError('exact whole-row graph changed')
    b = route.point_source().Builder()
    for name in ('FORWARD', 'INVERSE'):
        mode_pass(b, name, route_meta['entries'][name])
    b.mark('ADAPTER_FAIL')
    b.op('H', 'MALFORMED')
    for name in ('FORWARD', 'INVERSE'):
        embed_route(b, code, name)
    table, labels = b.finish()
    metadata = {'entries': {name: labels[name] for name in ('FORWARD', 'INVERSE')},
                'route_copies': {name: {'start': labels[name+'_ROUTE_0'], 'length': len(code),
                                       'return': labels[name+'_ROUTE_RETURN']}
                                 for name in ('FORWARD', 'INVERSE')},
                'route_metadata': route_meta, 'route_labels': route_labels,
                'tapes': TAPES, 'payload_port': PAYLOAD}
    return table, labels, metadata


def digest(code):
    return sha256(json.dumps(code, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
