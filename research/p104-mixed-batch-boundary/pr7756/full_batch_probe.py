"""Test every emitted caller event at two characters over a prime field. Apache-2.0."""
from fractions import Fraction
from functools import cache
from hashlib import sha256
import json

from mixed_caller import instructions, layout_bindings, need, place_roots, split_templates

CALLS = 1024
PRIME = 65537
I = 256
PHASE = (1, I, PRIME - 1, PRIME - I)
HALF = (PRIME + 1) // 2
CHARACTERS = (0x743dbf5d477085ce84729ffc83637aae4a,
              0x1349ac386527beccfa7b582cede689247d5)


@cache
def literal(real, imag):
    def residue(text):
        q = Fraction(text)
        return q.numerator * pow(q.denominator, -1, PRIME)
    return (residue(real) + I * residue(imag)) % PRIME


def port_views(character, layout, phase_bases):
    """Evaluate the change of central coordinates and both endpoint phases."""
    central = character & 511
    result = []
    for q in layout['ports']:
        frame = (q, *phase_bases['by_q'][str(q)])
        local = 0
        for j, axis in enumerate(frame):
            if central >> j & 1:
                local ^= axis
        restored = sum(((local & axis).bit_count() % 2) << j for j, axis in enumerate(frame))
        need(restored == central, 'central character round trip')
        head = (q & local).bit_count() % 2
        # On X the absolute exponent is the Hamming weight. On Y subtract the local head.
        forward = PHASE[(local.bit_count() - central.bit_count()) % 4]
        reverse = PHASE[(restored.bit_count() - local.bit_count()) % 4]
        need(head == (central & 1) and forward in (1, PRIME-1) and forward * reverse % PRIME == 1,
             'physical head and affine characters')
        result.append((forward, reverse, PHASE[head], PHASE[-head]))
    return result


def evaluate(character, layout, phase_bases, words, roots, bindings, offsets, initial):
    head = character & 1
    bodies = [((character >> (9 + 8*c)) & 255).bit_count() for c in range(16)]
    views = port_views(character, layout, phase_bases)
    hosted = set(layout['hosted']['Dports'])
    data = initial.copy()
    calls = caller_events = contacts = 0
    state = 'caller'
    # Q squared is a signed translation in the two terms of the local normalizer.
    normalizer = {s: ((1 + s*I) + (1 - s*I)*PHASE[2*head]) * HALF % PRIME for s in (-1, 1)}
    for row in instructions(words, roots, bindings, offsets):
        op = row[0]
        if op == 'PORT_VIEWS':
            _, side, t, ports = row
            entering = side == 'ENTER'
            need((entering and state == 'caller' and t == calls) or
                 (side == 'EXIT' and state == 'after native' and t == calls-1), 'paired view order')
            for regs, view in zip(ports, views, strict=True):
                sign = view[0 if entering else 1]
                for r in regs:
                    data[r] = data[r]*sign % PRIME
            state = 'before native' if entering else 'caller'
            continue
        if op == 'NATIVE':
            _, t, color, ports = row
            need(state == 'before native' and t == calls and color == t % 16 and len(ports) == 104,
                 'joint native occurrence')
            body = PHASE[bodies[color] % 4]
            for p, regs in enumerate(ports):
                q, adjoint = views[p][2:]
                x, y, *second = regs
                a, b = data[x], data[y]
                if p in hosted:
                    u, v = second
                    data[y] = (b + adjoint*a) % PRIME
                    data[u] = (data[u] - q*data[v]) % PRIME
                else:
                    need(not second, 'two-field native port')
                    data[x] = (a - q*b) % PRIME
                    data[y] = (b + adjoint*a)*HALF % PRIME
                for r in regs:
                    data[r] = data[r]*body % PRIME
            contacts += len(ports)
            calls += 1
            state = 'after native'
            continue
        need(state == 'caller', 'caller operation outside a native occurrence')
        caller_events += 1
        r = row[1]
        if op == 'ADD':
            data[r] = (data[r] + literal(*row[3])*data[row[2]]) % PRIME
        elif op == 'SCALE':
            data[r] = data[r]*literal(*row[2]) % PRIME
        elif op == 'SWAP':
            j = row[2]
            data[r], data[j] = data[j], data[r]
        elif op == 'QUERY':
            data[r] = (data[r] + PHASE[(row[3]*head) % 4]*data[row[2]]) % PRIME
        elif op == 'LAMBDA':
            data[r] = data[r]*normalizer[row[2]] % PRIME
        else:
            need(op in ('IDLE_ONE', 'IDLE_ODD'), 'known caller instruction')
            exponent = sum(bodies[j] for j in row[2]) + (row[3]*head if op == 'IDLE_ODD' else 0)
            data[r] = data[r]*PHASE[exponent % 4] % PRIME
    need(state == 'caller' and calls == CALLS and contacts == 104*CALLS, 'complete native batch')
    digest = sha256()
    for root, visits in roots.items():
        colors = [t % 16 for t, _ in visits]
        for i, (s, mask) in enumerate(words[root[0]][1]):
            r = offsets[root]+i
            exponent = s*head + sum(bodies[colors[j]] for j in mask)
            need(data[r] == initial[r]*PHASE[exponent % 4] % PRIME, 'full-batch signed diagonal output')
            digest.update(data[r].to_bytes(3, 'little'))
    return dict(character=hex(character), head_parity=head, native_calls=calls, native_contacts=contacts,
                caller_events=caller_events, checked_outputs=len(data), output_sha256=digest.hexdigest())


def verify(caller, layout, phase_bases):
    need(I*I % PRIME == PRIME-1, 'imaginary unit modulo the prime')
    words, roots = split_templates(caller), place_roots(caller, CALLS)
    bindings, offsets, receipt = layout_bindings(words, roots, layout, CALLS)
    initial = [1 + int.from_bytes(sha256(str(i).encode('ascii')).digest()[:8], 'little') % (PRIME-1)
               for i in range(receipt['root_owners'])]
    probes = [evaluate(k, layout, phase_bases, words, roots, bindings, offsets, initial) for k in CHARACTERS]
    return dict(modulus=PRIME, imaginary_unit=I, probes=probes)


if __name__ == '__main__':
    from time import monotonic
    from common import inputs, read
    start = monotonic()
    _, layout, *_ = inputs()
    print(json.dumps(verify(read('data/CALLER.json.gz'), layout, read('data/CALLER-PHASE-BASES.json')),
                     indent=2, sort_keys=True))
    print(f'PASS_FULL_BATCH_PROBE {monotonic()-start:.1f} seconds')
