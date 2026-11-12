"""Bounded exact source, descriptor, address, cleanup and cost verification."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('translation_subject', HERE / 'translate.py')
T = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = T
spec.loader.exec_module(T)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    bits = bin(n)[2:]
    return '0' * (len(bits) - 1) + bits


class Tape(T.REV.Tape):
    def __post_init__(self):
        super().__post_init__()
        self.reads = self.writes = self.moves = 0

    def read(self):
        self.reads += 1
        return super().read()

    def write(self, symbol):
        self.writes += 1
        return super().write(symbol)

    def move(self, direction):
        self.moves += 1
        super().move(direction)


def fresh_tapes():
    out = []
    for i in range(25):
        origin = i * 19 - 173
        t = Tape({origin - 2: '|', origin + 1000000000: '1'}, origin)
        t.low, t.high = origin - 1, origin + i % 7
        out.append(t)
    return out


def bits_at(tape, origin):
    out = []
    while tape.cells.get(origin, '_') != '_':
        out.append(tape.cells[origin])
        origin += 1
    return ''.join(out)


def payload(length, seed):
    state = seed
    out = []
    for _ in range(length):
        state ^= (state << 13) & 0xffffffff
        state ^= state >> 17
        state ^= (state << 5) & 0xffffffff
        state &= 0xffffffff
        out.append(str(state & 1))
    return ''.join(out)


def address_oracle(word, params):
    """Apply source xgate(1) to each of f columns, using coefficient addresses."""
    f, r, P, S, w = params
    Q = 1 << (9 * f)
    out = []
    for coefficient in range(P * Q * S * r):
        sr = coefficient % (S * r)
        address = coefficient // (S * r)
        prefix, q = divmod(address, Q)
        transformed = q ^ (((1 << f) - 1) << (8 * f))
        source = ((prefix * Q + transformed) * S * r + sr) * (2 * w)
        out.append(word[source:source + 2 * w])
    return ''.join(out)


def validate_graph(code):
    counts = Counter()
    for instruction in code:
        op, *args = instruction
        counts[op] += 1
        need(op in ('read', 'write', 'move', 'goto', 'halt'), 'only literal instructions')
        if op in ('read', 'write', 'move'):
            need(type(args[0]) is int and 0 <= args[0] < 25, 'fixed physical tape')
        if op == 'read':
            need(set(args[1]) <= {'_', '0', '1', '|'}, 'fixed read alphabet')
            need(all(type(v) is int and 0 <= v < len(code) for v in args[1].values()), 'fixed branches')
        if op == 'goto':
            need(type(args[0]) is int and 0 <= args[0] < len(code), 'fixed destination')
        if op == 'move':
            need(args[1] in (-1, 1), 'unit motion')
        if op == 'write':
            need(args[1] in ('_', '0', '1', '|'), 'fixed write alphabet')
    return dict(sorted(counts.items()))


def reversal_slice(code):
    start = next(i for i, row in enumerate(code) if row[0] in ('read', 'write', 'move') and row[1] == 5)
    old = T.REV.compile_reverse()[0]
    end = start + len(old)
    for pc, instruction in enumerate(old):
        op, *args = instruction
        if op == 'read':
            expected = (op, T.REVERSE_PORTS[args[0]], {s: start + v for s, v in args[1].items()})
        elif op in ('move', 'write'):
            expected = (op, T.REVERSE_PORTS[args[0]], args[1])
        elif op == 'goto':
            expected = (op, start + args[0])
        else:
            need(op == 'halt', 'retained grammar')
            expected = ('goto', end)
        need(tuple(code[start + pc]) == expected, 'exact retained graph embedding')
    return start, end


def run_case(code, params, seed=1, *, tapes=None, fault=None, check_descriptors=True):
    f, r, P, S, w = params
    R = 1 << f
    B = 2 * S * r * w * (1 << (8 * f))
    V = P * R * B
    header = ''.join(gamma(n) for n in params)
    source = payload(V, seed)
    expected = address_oracle(source, params)
    actual_input = source + ('0' if fault == 'extra' else '')
    if fault == 'missing':
        actual_input = actual_input[:-1]
    if fault == 'header':
        header = '|' + header[1:]
    tapes = fresh_tapes() if tapes is None else tapes
    origins = [t.head for t in tapes]
    private_before = [dict(t.cells) for t in tapes[2:]]
    history_before = sum(t.high - t.low + 1 for t in tapes[2:])
    metrics = [(t.reads, t.writes, t.moves) for t in tapes]
    for tape, word in zip(tapes[:2], (header, actual_input)):
        origin = tape.head
        tape.cells = {origin - 2: '|', origin + 1000000000: '1'}
        tape.cells.update({origin + i: bit for i, bit in enumerate(word)})
    tapes[0].cells[origins[0] + len(header)] = '|'
    public_before = [dict(t.cells) for t in tapes[:2]]
    machine = T.REV.Machine(code, tapes)
    start = next(i for i, row in enumerate(code) if row[0] in ('read', 'write', 'move') and row[1] == 5)
    rejection = None
    descriptors = None
    prefix_steps = None
    try:
        while machine.pc != start:
            need(machine.steps < 100000000, 'bounded producer verification')
            machine.step()
        descriptors = [bits_at(tapes[i], origins[i]) for i in (2, 3, 4)]
        if check_descriptors:
            need(descriptors == [bin(P)[2:], bin(R)[2:], bin(B)[2:]], 'exact produced binary descriptors')
        need(all(t.head == origin for t, origin in zip(tapes, origins)), 'all heads at descriptor join')
        need(tapes[1].writes == metrics[1][1], 'producer wrote DATA')
        prefix_steps = machine.steps
        machine.run(200000000)
    except ValueError as error:
        rejection = str(error)
    if fault:
        need(rejection == 'invalid scanned symbol', 'expected local rejection')
        need([dict(t.cells) for t in tapes[:2]] == public_before, 'failure changed public data')
        need(tapes[1].writes == metrics[1][1], 'failure wrote DATA')
        return {'parameters': params, 'fault': fault, 'steps': machine.steps, 'diagnostic': rejection}
    need(rejection is None, 'success expected: ' + str(rejection))
    need(machine.halted, 'complete program halt')
    result = ''.join(tapes[1].cells.get(origins[1] + i, '_') for i in range(V))
    need(result == expected, 'source coordinate translation')
    need(tapes[0].cells == public_before[0], 'header/exterior preservation')
    need(tapes[1].cells[origins[1] - 2] == '|' and tapes[1].cells[origins[1] + 1000000000] == '1',
         'DATA opaque exterior')
    need(tapes[1].cells.get(origins[1] + V, '_') == '_', 'same DATA frontier')
    need([dict(t.cells) for t in tapes[2:]] == private_before, 'all private bodies and guards retired')
    need(all(t.head == origin for t, origin in zip(tapes, origins)), 'all exact head returns')
    need(tapes[0].reads - metrics[0][0] == len(header), 'exact header reads')
    need(tapes[0].moves - metrics[0][2] == 2 * len(header), 'exact header return')
    need(tapes[1].reads - metrics[1][0] == V + 1 and tapes[1].writes - metrics[1][1] == V,
         'complete DATA census')
    need(tapes[1].moves - metrics[1][2] == 4 * V, 'complete DATA return bill')
    history_after = sum(t.high - t.low + 1 for t in tapes[2:])
    need(history_before <= history_after <= history_before + 32 * (V + len(header) + 1), 'history envelope')
    need(machine.steps <= 4096 * (V + len(header) + 1), 'complete time envelope')
    return {'parameters': params, 'bits': V, 'header_bits': len(header), 'descriptors': descriptors,
            'producer_steps': prefix_steps, 'steps': machine.steps,
            'history_before': history_before, 'history_after': history_after,
            'input_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'output_sha256': hashlib.sha256(result.encode()).hexdigest()}


def encoder_checks():
    a = T.Builder()
    roles = (T.BDESC, T.PRODUCT, T.HALF, T.DIGITS)
    for tape in roles:
        a.op('move', tape, -1); a.op('write', tape, '|'); a.op('move', tape, 1)
    T.unary_binary(a, T.PRODUCT, T.BDESC)
    for tape in roles:
        a.op('move', tape, -1); a.op('write', tape, '_'); a.op('move', tape, 1)
    a.op('halt')
    code = a.finish(('_', '0', '1', '|'))[0]
    rows = []
    for n in list(range(1, 97)) + [127, 128, 255, 256, 511, 512, 999, 1024]:
        tapes = fresh_tapes()
        origins = [t.head for t in tapes]
        for i in range(n):
            tapes[T.PRODUCT].cells[origins[T.PRODUCT] + i] = '1'
        machine = T.REV.Machine(code, tapes).run(100000)
        need(bits_at(tapes[T.BDESC], origins[T.BDESC]) == bin(n)[2:], 'standalone canonical encoder')
        need(machine.steps == 19 * n - 12 * n.bit_count() + 19 * n.bit_length() + 32,
             'exact linear encoder census')
        need(all(t.head == origin for t, origin in zip(tapes, origins)), 'encoder head restoration')
        for i in (T.PRODUCT, T.HALF, T.DIGITS):
            need(tapes[i].cells == {origins[i] - 2: '|', origins[i] + 1000000000: '1'}, 'encoder private retirement')
        rows.append((n, machine.steps))
    return {'cases': len(rows), 'maximum': rows[-1][0], 'sum_steps': sum(x[1] for x in rows),
            'census_sha256': hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()}


def mutant(label, replacements):
    text = (HERE / 'translate.py').read_text()
    for old, new in replacements:
        need(text.count(old) == 1, 'mutation anchor ' + label)
        text = text.replace(old, new)
    module = types.ModuleType('translation_mutant_' + label)
    module.__file__ = str(HERE / 'translate.py')
    sys.modules[module.__name__] = module
    exec(compile(text, module.__file__, 'exec'), module.__dict__)
    return module.compile_translation()[0]


def expect_failure(label, action, fragment):
    try:
        action()
    except ValueError as error:
        need(fragment in str(error), 'control diagnostic ' + label + ': ' + str(error))
        return {'mutation': label, 'diagnostic': str(error)}
    raise ValueError('mutation escaped: ' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='Development only: skip the complete f=2 fixture.')
    parser.add_argument('--write', action='store_true', help='Explicitly replace RESULT.json after complete verification.')
    args = parser.parse_args()
    code, alphabet = T.compile_translation()
    operations = validate_graph(code)
    start, end = reversal_slice(code)
    encoders = encoder_checks()
    parameters = [(1, 1, 1, 1, 1), (1, 2, 3, 2, 3), (1, 1, 6, 1, 2),
                  (1, 5, 1, 3, 1), (1, 1, 1, 1, 17)]
    if not args.quick:
        parameters.append((2, 1, 1, 1, 1))
    runs = [run_case(code, p, 17 + i) for i, p in enumerate(parameters)]
    tapes = fresh_tapes()
    identities = tuple(map(id, tapes))
    reuse = []
    for i, p in enumerate(((1, 2, 3, 2, 3), (1, 1, 1, 1, 1), (1, 1, 4, 2, 7))):
        reuse.append(run_case(code, p, 91 + i, tapes=tapes))
        need(tuple(map(id, tapes)) == identities, 'same physical objects')
    need(reuse[1]['steps'] == runs[0]['steps'], 'short reuse depends on old capacity')
    failures = [run_case(code, parameters[0], fault=fault) for fault in ('header', 'missing', 'extra')]
    controls = []
    bad = mutant('missing_complex_factor', [('for _ in range(2):', 'for _ in range(1):')])
    controls.append(expect_failure('missing real/imaginary factor', lambda: run_case(bad, parameters[0]),
                                   'exact produced binary descriptors'))
    wrong = mutant('wrong_axis', [
        ('unary_binary(a, OUTER, PDESC)', 'unary_binary(a, OUTER, BDESC)'),
        ('unary_binary(a, PRODUCT, BDESC)', 'unary_binary(a, PRODUCT, PDESC)')])
    controls.append(expect_failure('wrong prefix/suffix axis',
        lambda: run_case(wrong, (1, 1, 3, 1, 2), check_descriptors=False), 'source coordinate translation'))
    dirty = mutant('missing_descriptor_cleanup',
        [('for tape in PRODUCER_PRIVATE:\n        clear(a, tape, BITS)',
          'for tape in tuple(range(14, 25)):\n        clear(a, tape, BITS)')])
    controls.append(expect_failure('unretired generated descriptors', lambda: run_case(dirty, parameters[0]),
                                   'all private bodies and guards retired'))
    result = {
        'status': 'PASS_NATIVE_TRANSLATION_DESCRIPTOR' if not args.quick else 'DEVELOPMENT_QUICK_ONLY',
        'locations': len(code), 'tapes': 25, 'operations': operations,
        'table_sha256': hashlib.sha256(json.dumps(code, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'retained_reversal_interval': [start, end], 'encoder': encoders,
        'complete_runs': runs, 'same_owner_reuse': reuse, 'rejections': failures, 'negative_controls': controls,
        'completed_payload_bits': sum(row['bits'] for row in runs + reuse),
        'complete_success_steps': sum(row['steps'] for row in runs + reuse),
        'scope': 'One actual post-matrix translation on the supplied five-Gamma packed ABI; no full native body or new kappa.'
    }
    if args.write:
        need(not args.quick, 'never retain an incomplete fixture receipt')
        (HERE / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    elif not args.quick and (HERE / 'RESULT.json').exists():
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'frozen complete receipt')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
