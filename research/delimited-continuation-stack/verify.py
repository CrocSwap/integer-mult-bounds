"""Check the sequential continuation and its retained source boundary.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
    if row['usage'] == 'input':
        if hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('source byte drift: ' + row['path'])
SOURCE = ROOT / 'research/complex-segment-boundary'
sys.path[:0] = [str(HERE), str(SOURCE / 'source')]
from stack import BASE, BLANK, END, LEFT, SEP, Counts, Stack, Tape, emit, need, rewind
from adapter import Arena
import streams
import compact
import monomial


def bits(n, salt=0):
    return tuple((i * 13 + (i // 3) + salt) % 2 for i in range(n))


def snapshot(tape):
    cells = list(tape.cells)
    while cells and cells[-1] == BLANK:
        cells.pop()
    return cells, tape.head


def load(tape, data, head=0):
    for bit in data:
        emit(tape, bit)
    rewind(tape, LEFT)
    for _ in range(head):
        tape.move(1)


def descriptor(tape, data):
    for bit in data:
        emit(tape, bit)
    rewind(tape, BASE)


def formulas():
    options = [(present, s, h) for s in range(4) for h in range(s + 1)
               for present in ((False, True) if s == 0 else (True,))]
    count = 0
    for roles in itertools.product(options, repeat=2):
        for dlen, qlen in itertools.product(range(4), range(3)):
            m = Counts()
            payload = [Tape(bits(17, i), counts=m) for i in range(2)]
            for t, (_, s, h) in zip(payload, roles):
                load(t, bits(s), h)
            c, d = Tape(bits(19), BASE, m), Tape((), BASE, m)
            descriptor(d, bits(dlen))
            before = [snapshot(t) for t in (*payload, c, d)]
            stack = Stack(payload, c, d)
            s = sum(x[1] for x in roles)
            h = sum(x[2] for x in roles)
            absent = sum(not x[0] for x in roles)
            start = m.total
            stack.push([x[0] for x in roles])
            need(m.total - start == 4*h + 2*s + 20 + 7*dlen + absent + 11, 'exact push invoice')
            # No Python object from push supplies the return frame.
            del stack
            descriptor(d, bits(qlen, 1))
            start = m.total
            state = Stack(payload, c, d).pop()
            need(m.total - start == 9*h + 2*s + 42 + 11*dlen + 5*qlen + absent + 28, 'exact pop invoice')
            need(state == list(roles), 'decoded metadata')
            need([snapshot(t) for t in (*payload, c, d)] == before, 'all tapes and heads restored')
            count += 1
    return count


def nested(depth, prefix):
    m = Counts()
    payload = [Tape(bits(prefix, i), counts=m) for i in range(16)]
    c, d = Tape(bits(prefix + 3), BASE, m), Tape((), BASE, m)
    expected = []
    for level in range(depth):
        roles = [(i % 3 != 0, (i + level) % 7 if i % 3 != 0 else 0) for i in range(16)]
        for i, (t, (present, size)) in enumerate(zip(payload, roles)):
            load(t, bits(size, level + i), size // 2)
        descriptor(d, bits(1 + 2*level, level))
        expected.append(([snapshot(t) for t in (*payload, c, d)], roles))
        Stack(payload, c, d).push([r[0] for r in roles])
    for old, roles in reversed(expected):
        state = Stack(payload, c, d).pop()
        need([snapshot(t) for t in (*payload, c, d)] == old, 'arbitrary-depth restoration')
        need(state == [(p, s, s//2) for p, s in roles], 'arbitrary-depth observer state')
        for t in payload:
            rewind(t, LEFT)
            while t.read() != BLANK:
                emit(t, BLANK)
            rewind(t, LEFT)
        # The next pop retires this current descriptor itself.
    return m.total


def direct(raw, layout, word):
    out = bytearray(len(raw))
    for i in range(layout.records):
        j = layout.encode(word.ideal(layout.decode(i), True))
        width = layout.record_bits
        out[j*width:(j+1)*width] = raw[i*width:(i+1)*width]
    return bytes(out)


def bind(arena):
    for module in (streams, compact, monomial):
        module.Tape = arena.tape


def source_case(prefix, late):
    a = Arena([bits(prefix, i) for i in range(16)], bits(prefix + 5))
    bind(a)
    fields = (('u', 1), ('t', 1)) + ((('y', 2), ('x', 2)) if late else (('x', 2), ('y', 2))) + (('b', 1),)
    layout, word = compact.Layout(fields, 8), compact.Compact(1, 1, 1, 0, 'x', 'y', late)
    raw = bytes(b for i in range(layout.records) for b in streams.bit_key(i, 8))
    current = a.tape(streams.Meter(), raw)
    current.read(7)
    other = [a.tape(streams.Meter(), bits(3 + i, i)) for i in range(15)]
    for i, role in enumerate(other):
        role.read(i % (len(role.data) + 1))
    outer = tuple(bit for byte in (SOURCE / 'BOUNDARY.json').read_bytes() for bit in streams.bit_key(byte, 8))
    a.set_descriptor(outer)
    before = [snapshot(t) for t in (*a.payloads, a.control, a.descriptor)]
    with a.child():
        try:
            current.rewind()
        except ValueError as error:
            need(str(error) == 'active role', 'suspended role rejection')
        else:
            raise ValueError('suspended role was accessible')
        child = a.tape(streams.Meter(), raw)
        child.read(11)
        a.set_descriptor(bits(43, 1))
        nested_before = [snapshot(t) for t in (*a.payloads, a.control, a.descriptor)]
        with a.child():
            data = a.tape(streams.Meter(), raw)
            out = compact.execute(data, layout, word)
            need(bytes(out.data) == direct(raw, layout, word), 'nested source endpoint')
            out.erase()
            a.set_descriptor(bits(17))
        need([snapshot(t) for t in (*a.payloads, a.control, a.descriptor)] == nested_before, 'nested source return')
        out = compact.execute(child, layout, word)
        need(bytes(out.data) == direct(raw, layout, word), 'source endpoint')
        out.erase()
    need([snapshot(t) for t in (*a.payloads, a.control, a.descriptor)] == before, 'sixteen source roles and control restored')
    need(bytes(current.data) == raw and current.head == 7, 'caller view restored')
    return {'prefix': prefix, 'late': late, 'steps': a.counts.total,
            'boundary_steps': a.boundary_steps, 'peak_roles': a.peak}


def phase_case():
    recipe = json.loads((SOURCE / 'RIGHT-RECIPE.json').read_text())
    a = Arena([bits(257, i) for i in range(16)])
    bind(a)
    class Fibre:
        records, record_bits = 1024, 8
        def decode(self, index):
            x, y = divmod(index, 2)
            return {'v' + str(i): ((x >> i) & 1) | (((y >> i) & 1) << 1) for i in range(9)}
    raw = bytes(b for i in range(1024) for b in streams.bit_key((37*i + 19) % 256, 8))
    a.set_descriptor(bits(43))
    with a.child():
        source = a.tape(streams.Meter(), raw)
        output = monomial.phase_pass(source, Fibre(), recipe, 2, 1, 0, 4)
        expected = bytearray()
        for index in range(1024):
            phase = 2 * recipe['phase']
            for value in divmod(index, 2):
                for i in range(9):
                    if value >> i & 1:
                        phase += recipe['linear_Z4'][i]
                        for j in range(i + 1, 9):
                            phase += 2*((recipe['quadratic_rows'][i] >> j) & 1)*((value >> j) & 1)
            real = sum(raw[index*8+i] << i for i in range(4))
            imag = sum(raw[index*8+4+i] << i for i in range(4))
            for _ in range(phase % 4):
                real, imag = -imag, real
            expected.extend(streams.bit_key(real % 16, 4))
            expected.extend(streams.bit_key(imag % 16, 4))
        need(bytes(output.data) == bytes(expected), 'actual recipe independent Gaussian oracle')
        restored = monomial.phase_pass(output, Fibre(), recipe, 2, 1, 0, 4, True)
        need(bytes(restored.data) == raw, 'source phase inverse')
        restored.erase()
    return {'records': 1024, 'steps': a.counts.total, 'boundary_sha256': hashlib.sha256((SOURCE/'BOUNDARY.json').read_bytes()).hexdigest()}


def controls():
    count = 0
    for fault in ('end', 'start', 'unary', 'head', 'child', 'presence'):
        p, c, d = Tape(bits(9)), Tape(bits(11), BASE), Tape((), BASE)
        load(p, (0, 1), 1)
        stack = Stack((p,), c, d)
        stack.push([True])
        start = c.floor + 1
        if fault == 'end': c.cells[c.head-1] = BLANK
        if fault == 'start': c.cells[start] = SEP
        if fault == 'unary': c.cells[start+3] = SEP
        if fault == 'head':
            c.cells[start+3:start+3] = [1, 1]
            c.head += 2
        if fault == 'child': p.write(1)
        if fault == 'presence': c.cells[start+1] = 0
        try:
            Stack((p,), c, d).pop()
        except ValueError:
            count += 1
        else:
            raise ValueError('accepted fault: ' + fault)
    return count


def allocation_cases():
    a = Arena([bits(7, i) for i in range(16)])
    for _ in range(32):
        parent = a.tape(streams.Meter())
        with a.child():
            child = a.tape(streams.Meter())
            with a.child():
                pass
            del child
            replacement = a.tape(streams.Meter())
            need(replacement.slot == 0, 'empty resumed role released')
            del replacement
        del parent
    return 32


def main():
    n = formulas()
    nesting = []
    for depth in (1, 2, 7, 31):
        costs = [nested(depth, prefix) for prefix in (0, 17, 4096)]
        need(len(set(costs)) == 1, 'nested cost independent of ancestors')
        nesting.append({'depth': depth, 'steps': costs[0]})
    source = [source_case(p, late) for late in (False, True) for p in (16, 257, 4096)]
    for offset in (0, 3):
        need(len({x['steps'] for x in source[offset:offset+3]}) == 1, 'source cost independent of ancestors')
        need(len({x['boundary_steps'] for x in source[offset:offset+3]}) == 1, 'boundary cost independent of ancestors')
    result = {'status': 'PASS_DELIMITED_CONTINUATION_STACK', 'exact_invoice_cases': n,
              'nested': nesting, 'source': source, 'phase': phase_case(), 'rejection_controls': controls(),
              'empty_role_lifetime_cases': allocation_cases(),
              'push_plus_pop': '13H+4S+31k+18d+5q+2A+39',
              'scope': 'Fixed alphabet control stack and scoped retained-source adapter; source lexical allocation and recursive output delivery remain separate.'}
    expected = HERE / 'RESULT.json'
    if expected.exists():
        need(json.loads(expected.read_text()) == result, 'committed receipt mismatch')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
