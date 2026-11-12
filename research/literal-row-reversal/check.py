"""Bounded checks; numeric shapes and payload oracles belong only to tests.

The compiled machine receives thirteen tapes and a fixed instruction table.
It is never given the decoded shape, output mapping, or any Python callback.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import inspect
import itertools
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reverse as r

CODE, ALPHABET = r.compile_reverse()
SEED = 20261112


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest_table(code=CODE):
    raw = json.dumps([code, ALPHABET], sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())['files']
    for pin in pins:
        raw = (HERE / pin['local']).read_bytes()
        require(len(raw) == pin['bytes'], 'source byte length: '+pin['local'])
        require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 drift')
        obj = b'blob '+str(len(raw)).encode()+b'\0'+raw
        require(hashlib.sha1(obj).hexdigest() == pin['blob'], 'source Git blob drift')
    require(not inspect.signature(r.compile_reverse).parameters, 'runtime compiler parameter')
    for instruction in CODE:
        op, *args = instruction
        require(op in ('read', 'write', 'move', 'goto', 'halt'), 'unpriced opcode')
        if op in ('read', 'write', 'move'):
            require(type(args[0]) is int and 0 <= args[0] < 13, 'tape count')
        if op == 'read':
            require(set(args[1]) <= set(ALPHABET), 'foreign read symbol')
            require(all(type(pc) is int and 0 <= pc < len(CODE)
                        for pc in args[1].values()), 'read target')
        if op == 'write':
            require(args[1] in ALPHABET, 'foreign write symbol')
        if op == 'move':
            require(args[1] in (-1, 1), 'nonlocal head move')
        if op == 'goto':
            require(type(args[0]) is int and 0 <= args[0] < len(CODE), 'jump target')
    return len(pins)


def oracle(payload, p, rows, bits):
    # Direct address involution, independent of the program's two-stack method.
    return ''.join(payload[(i//(rows*bits)*rows + rows-1-(i//bits)%rows)*bits+i%bits]
                   for i in range(p*rows*bits))


def caps(p, rows, bits):
    v = p*rows*bits
    lengths = [x.bit_length() for x in (p, rows, bits)]
    return [*lengths, v, v, p, rows, bits, max(p, rows, bits),
            max(lengths), rows*bits, bits, v]


def cells(word, origin):
    return {origin+i: bit for i, bit in enumerate(word)}


def packet(p, rows, bits, payload, origins=None, roomy=None):
    origins = origins or tuple(7*i-31 for i in range(13))
    limits = roomy or caps(p, rows, bits)
    tapes = []
    for i, (origin, limit) in enumerate(zip(origins, limits)):
        # Opaque adjacent exteriors cannot be erased to repair a faulty scan.
        outside = {origin-3: '1', origin-2: '|', origin+limit+1: '0',
                   origin+limit+2: '|'}
        if i < 4:
            outside[origin-1] = '0'
        tapes.append(r.Tape(outside, origin))
    for i, value in enumerate((p, rows, bits)):
        tapes[i].cells.update(cells(bin(value)[2:], origins[i]))
    tapes[r.DATA].cells.update(cells(payload, origins[r.DATA]))
    return tapes, origins


class AuditMachine(r.Machine):
    """Observations never feed the finite controller."""
    def __init__(self, code, tapes):
        super().__init__(code, tapes)
        self.actions = Counter()
        self.writes = Counter()
        self.moves = Counter()
        self.local_low = [t.head for t in tapes]
        self.local_high = [t.head for t in tapes]

    def step(self):
        op, *args = self.code[self.pc]
        self.actions[op] += 1
        if op == 'write':
            self.writes[args[0]] += 1
        if op == 'move':
            self.moves[args[0]] += 1
        super().step()
        if op in ('read', 'write', 'move'):
            i = args[0]
            self.local_low[i] = min(self.local_low[i], self.tapes[i].head)
            self.local_high[i] = max(self.local_high[i], self.tapes[i].head)


def exact_time(p, rows, bits):
    e = sum(n.bit_length() for n in (p, rows, bits))
    s = sum(n.bit_count() for n in (p, rows, bits))
    return 53*p*rows*bits + 23*p*rows + 71*p + 54*rows + 54*bits + 28*e - 30*s - 8


def successful(p, rows, bits, payload, *, code=CODE, tapes=None, origins=None):
    if tapes is None:
        tapes, origins = packet(p, rows, bits, payload, origins)
    require(len(payload) == p*rows*bits, 'test fixture cardinality')
    before = [dict(t.cells) for t in tapes]
    k0 = sum(t.high-t.low+1 for t in tapes[4:])
    owners = tuple(map(id, tapes))
    cpu = AuditMachine(code, tapes).run(65536*(sum(x.bit_length() for x in (p, rows, bits))
                                              +len(payload)+1))
    expected = before[r.DATA] | cells(oracle(payload, p, rows, bits), origins[r.DATA])
    require(tapes[r.DATA].cells == expected, 'record reversal or DATA exterior failed')
    require(tuple(map(id, tapes)) == owners, 'owner identity changed')
    require(all(t.head == o for t, o in zip(tapes, origins)), 'head return failed')
    require(all(t.cells == before[i] for i, t in enumerate(tapes) if i != r.DATA),
            'descriptor/private/exterior restoration failed')
    require(cpu.writes[r.DATA] == len(payload), 'commit did not write every DATA cell once')
    require(not any(cpu.writes[i] for i in (r.PDESC, r.RDESC, r.BDESC)),
            'public descriptor was written')
    require(cpu.steps == exact_time(p, rows, bits), 'exact complete cost census failed')
    for i, (lo, hi, origin, limit) in enumerate(zip(cpu.local_low, cpu.local_high, origins,
                                                  caps(p, rows, bits))):
        require(lo >= origin-(i >= 4) and hi <= origin+limit, 'current-call frame escaped')
    extra = 8*len(payload)+sum(n.bit_length() for n in (p, rows, bits))+18
    require(sum(t.high-t.low+1 for t in tapes[4:]) <= k0+extra,
            'historical backing upper bound failed')
    return cpu


def rejected(p, rows, bits, payload, change, code=CODE):
    tapes, origins = packet(p, rows, bits, payload, roomy=[50]*13)
    change(tapes, origins)
    before = [dict(t.cells) for t in tapes]
    cpu = AuditMachine(code, tapes)
    try:
        cpu.run(1_000_000)
    except ValueError as exc:
        require(str(exc) == 'invalid scanned symbol', 'unexpected rejection cause')
    else:
        raise ValueError('invalid domain unexpectedly accepted')
    require(cpu.writes[r.DATA] == 0 and tapes[r.DATA].cells == before[r.DATA],
            'failed source validation modified DATA')
    require(all(tapes[i].cells == before[i] for i in range(3)),
            'failed source validation modified descriptors')
    return cpu.steps


def mutate(pattern, replacement, occurrence=0):
    matches = [i for i, op in enumerate(CODE) if op == pattern]
    require(len(matches) > occurrence, 'mutation site disappeared')
    code = list(CODE)
    code[matches[occurrence]] = replacement
    return tuple(code)


def mutation_control(code, shape=(2, 3, 3), word='001101010110000111'):
    try:
        successful(*shape, word, code=code)
    except ValueError:
        return True
    raise ValueError('semantic/cost mutant escaped detection')


def reuse():
    shapes = [(1, 1, 1), (3, 7, 9), (1, 2, 1), (2, 4, 3), (3, 7, 9), (1, 1, 1)]
    roomy = [max(caps(*s)[i] for s in shapes) for i in range(13)]
    first = shapes[0]
    tapes, origins = packet(*first, '1', roomy=roomy)
    owners = tuple(map(id, tapes))
    previous = [t.high-t.low+1 for t in tapes]
    history, total = [], 0
    rng = random.Random(SEED+1)
    for p, rows, bits in shapes:
        payload = ''.join(rng.choice('01') for _ in range(p*rows*bits))
        # Paid caller fixtures supply a new valid packet. Private banks, heads,
        # history observers and owners are never reinitialized or reset.
        for i, word in enumerate([*(bin(n)[2:] for n in (p, rows, bits)), payload]):
            origin = origins[i]
            for j in range(roomy[i]+1):
                tapes[i].cells.pop(origin+j, None)
            tapes[i].cells.update(cells(word, origin))
        cpu = successful(p, rows, bits, payload, tapes=tapes, origins=origins)
        require(tuple(map(id, tapes)) == owners, 'reuse replaced owner')
        now = [t.high-t.low+1 for t in tapes]
        require(all(a <= b for a, b in zip(previous, now)), 'history reset or shrink')
        previous = now
        history.append(sum(now[4:]))
        total += cpu.steps
    require(history[-1] == max(history), 'small call erased historical capacity')
    return {'calls': len(shapes), 'private_history': history, 'steps': total}


def translated_source_check():
    """Differential map check against exact pinned source-level flip_digit."""
    path = HERE / 'reference' / 'streams.py'
    spec = importlib.util.spec_from_file_location('pinned_streams', path)
    source = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = source
    spec.loader.exec_module(source)
    cases, steps = 0, 0
    rng = random.Random(SEED+2)
    for dimension in range(1, 7):
        for position in range(dimension):
            record_bits = 1+(dimension+position) % 5
            payload = bytes(rng.randrange(2) for _ in range((1 << dimension)*record_bits))
            old = source.flip_digit(source.Tape(source.Meter(), payload), dimension,
                                    position, record_bits)
            p = 1 << position
            bits = (1 << (dimension-position-1))*record_bits
            word = ''.join(map(str, payload))
            tapes, origins = packet(p, 2, bits, word)
            cpu = successful(p, 2, bits, word, tapes=tapes, origins=origins)
            actual = bytes(int(tapes[r.DATA].cells[origins[r.DATA]+i])
                           for i in range(len(word)))
            require(actual == bytes(old.data), 'pinned flip_digit map mismatch')
            cases += 1
            steps += cpu.steps
    return {'cases': cases, 'steps': steps,
            'scope': 'map equivalence only; the old Python caller is not lowered'}


def fixed_translation():
    """Fixed-size call compositions; descriptor supply is explicitly a fixture."""
    cases, calls, steps = 0, 0, 0
    rng = random.Random(SEED+3)
    for dimension, shift, record_bits in ((1, 1, 3), (3, 5, 2), (4, 15, 3),
                                           (6, 37, 2), (9, 341, 3)):
        v = (1 << dimension)*record_bits
        payload = ''.join(rng.choice('01') for _ in range(v))
        shapes = [(1 << (dimension-j-1), 2, (1 << j)*record_bits)
                  for j in range(dimension) if shift >> j & 1]
        roomy = [max(caps(*s)[i] for s in shapes) for i in range(13)]
        tapes, origins = packet(*shapes[0], payload, roomy=roomy)
        owners = tuple(map(id, tapes))
        word = payload
        for shape in shapes:
            for i, n in enumerate(shape):
                for j in range(roomy[i]+1):
                    tapes[i].cells.pop(origins[i]+j, None)
                tapes[i].cells.update(cells(bin(n)[2:], origins[i]))
            cpu = successful(*shape, word, tapes=tapes, origins=origins)
            word = ''.join(tapes[r.DATA].cells[origins[r.DATA]+i] for i in range(v))
            require(tuple(map(id, tapes)) == owners, 'fixed translation changed owners')
            calls += 1
            steps += cpu.steps
        expected = ''.join(payload[(address ^ shift)*record_bits+b]
                           for address in range(1 << dimension) for b in range(record_bits))
        require(word == expected, 'native fixed translation mismatch')
        cases += 1
    # Whole block reversal complements every bit, not merely stride-K positions.
    require((0 ^ 0b1010) != (15-0), 'strided-scope negative control vanished')
    return {'cases': cases, 'calls': calls, 'steps': steps,
            'scope_control': 'stride-2 selected-bit XOR differs from full 4-bit reversal'}


def main():
    source_count = authenticate()
    packets, bits_checked, steps, geometries = 0, 0, 0, 0
    for p in range(1, 9):
        for rows in range(1, 9):
            for bits in range(1, 9):
                v = p*rows*bits
                if v > 8:
                    continue
                geometries += 1
                for raw in itertools.product('01', repeat=v):
                    cpu = successful(p, rows, bits, ''.join(raw))
                    packets += 1
                    bits_checked += v
                    steps += cpu.steps
    rng = random.Random(SEED)
    for _ in range(64):
        p, rows, bits = (rng.randrange(1, 8) for _ in range(3))
        word = ''.join(rng.choice('01') for _ in range(p*rows*bits))
        cpu = successful(p, rows, bits, word)
        packets += 1
        bits_checked += len(word)
        steps += cpu.steps
    invalid = []
    for i in range(3):
        for symbol in ('0', r.BLANK, r.MARK):
            invalid.append(rejected(2, 3, 2, '000110110001',
                           lambda t, o, i=i, s=symbol: t[i].write(s)))
    invalid.append(rejected(2, 3, 2, '000110110001',
                   lambda t, o: t[r.DATA].cells.pop(o[r.DATA]+11)))
    invalid.append(rejected(2, 3, 2, '000110110001',
                   lambda t, o: t[r.DATA].cells.__setitem__(o[r.DATA]+12, '0')))
    invalid.append(rejected(2, 3, 2, '000110110001',
                   lambda t, o: t[r.RDESC].cells.__setitem__(o[r.RDESC]+1, r.MARK)))
    mutants = [
        mutate(('write', r.DATA, '0'), ('write', r.DATA, '1')),
        mutate(('write', r.OUTPUT, r.BLANK), ('write', r.OUTPUT, '1')),
        mutate(('move', r.GROUP, -1), ('move', r.GROUP, 1)),
        mutate(('move', r.RECORD, -1), ('move', r.RECORD, 1)),
        mutate(('move', r.DATA, -1), ('move', r.DATA, 1)),
        mutate(('write', r.BTR, '1'), ('write', r.BTR, '0')),
    ]
    for code in mutants:
        mutation_control(code)
    # Explicit alternative maps fail on a nonpalindromic multi-prefix witness.
    word, shape = '001101010110000111', (2, 3, 3)
    expected = oracle(word, *shape)
    wrong_bits = ''.join(word[i:i+9][::-1] for i in (0, 9))
    wrong_prefixes = ''.join(word[i:i+3] for i in range(15, -1, -3))
    require(expected != wrong_bits and expected != wrong_prefixes,
            'record-vs-bit / prefix-isolation control failed')
    reuse_result = reuse()
    source_result = translated_source_check()
    translation_result = fixed_translation()
    result = {'status': 'PASS', 'seed': SEED, 'instructions': len(CODE), 'tapes': 13,
              'alphabet': list(ALPHABET), 'table_sha256': digest_table(),
              'program_sha256': hashlib.sha256((HERE/'reverse.py').read_bytes()).hexdigest(),
              'authenticated_sources': source_count, 'exhaustive_domain': 'all P,R,B>=1 with PRB<=8; all payload bits',
              'exhaustive_geometries': geometries, 'extra_random_packets': 64,
              'success_packets': packets, 'payload_bits_checked': bits_checked,
              'success_transitions': steps, 'invalid_packets': len(invalid),
              'invalid_transitions': sum(invalid), 'graph_mutants_detected': len(mutants),
              'alternative_map_controls': 2, 'history_reuse': reuse_result,
              'pinned_source_map': source_result, 'fixed_translation': translation_result,
              'untouched': 'larger exhaustive domains; general affine/strided packing; literal caller composition; failure retirement'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
