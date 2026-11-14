"""Stdlib local-CPU, integer rounding and direct source-kernel checks."""
from pathlib import Path
import argparse
import atexit
import hashlib
import itertools
import json
import random
import sys
import tempfile

HERE = Path(__file__).resolve().parent
_IMPORT_CACHE = tempfile.TemporaryDirectory(prefix='literal-rounded-check-')
atexit.register(_IMPORT_CACHE.cleanup)
_CACHE_PREFIX = Path(_IMPORT_CACHE.name) / 'required-absent'
if _CACHE_PREFIX.exists():
    raise ValueError('source import cache prefix must be absent')
sys.pycache_prefix = str(_CACHE_PREFIX)
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import rounded as m
import verify as v


def need(ok, label):
    if not ok:
        raise ValueError(label)


def packet(capacity, guards=False):
    tapes = [bytearray(capacity + 7) for _ in range(m.TAPES)]
    for tape in tapes:
        tape[0:2] = b'\x02\x03'
        tape[-2:] = b'\x01\x03'
    if guards:
        for t in m.PRIVATE:
            tapes[t][2] = 3
    return tapes


def put(tapes, port, text):
    tapes[port][3:3 + len(text)] = bytes(v.SYMBOLS[x] for x in text)


def guides(tapes, w, k, count):
    for port, n in ((m.WIDTH, w), (m.K, k), (m.MARGIN, k + 1),
                    (m.HIGH, w + k + 1), (m.COUNT, count)):
        put(tapes, port, '1' * n)


def run(program, tapes, *, commit=None, cumulative=None, limit=200_000_000):
    heads, lows, highs = [3] * len(tapes), [3] * len(tapes), [3] * len(tapes)
    pc = steps = writes = early = staged = 0
    rejected = False
    while True:
        op, tape, arg = program[pc]
        steps += 1
        if steps > limit:
            raise ValueError('finite literal budget')
        if op == 0:
            pc = arg[tapes[tape][heads[tape]]]
            if pc < 0:
                rejected = True
                break
        elif op == 1:
            tapes[tape][heads[tape]] = arg
            staged += tape == m.OUTPUT and heads[tape] >= 3 and (commit is None or pc < commit)
            if tape == m.DATA:
                writes += 1
                early += commit is None or pc < commit
            pc += 1
        elif op == 2:
            heads[tape] += arg
            if heads[tape] < lows[tape]:
                lows[tape] = heads[tape]
            if heads[tape] > highs[tape]:
                highs[tape] = heads[tape]
            need(0 <= heads[tape] < len(tapes[tape]), 'fixture window escaped')
            pc += 1
        elif op == 3:
            pc = tape
        else:
            break
    cumulative = list(zip(lows, highs)) if cumulative is None else [
        (min(lo, oldlo), max(hi, oldhi))
        for lo, hi, (oldlo, oldhi) in zip(lows, highs, cumulative)]
    return dict(steps=steps, rejected=rejected, writes=writes, early=early, staged=staged,
                heads=heads, lows=lows, highs=highs,
                history=sum(hi - lo + 1 for lo, hi in zip(lows, highs)),
                cumulative_history=sum(hi - lo + 1 for lo, hi in cumulative)), cumulative


def rounding_cases():
    code, _ = m.compile_converter('round')
    program = v.numeric(code)
    count = transitions = positive_ties = negative_ties = fits_count = 0
    witness = {}
    for w in range(2, 6):
        for k in range(1, 4):
            width = w + 2 * k + 1
            for z in range(-(1 << (width - 1)), 1 << (width - 1)):
                q = (z + (1 << (k - 1))) // (1 << k)
                fits = -(1 << (w - 1)) <= q < (1 << (w - 1))
                tapes = packet(4 * (width + 20), True)
                guides(tapes, w, k, 1)
                put(tapes, m.WD, v.signed(z, width))
                put(tapes, m.DATA, '101')
                put(tapes, m.HEADER, '1|01|')
                before = [bytes(t) for t in tapes]
                result, _ = run(program, tapes)
                need(result['rejected'] != fits and not result['writes'], 'round acceptance')
                need(tapes[m.DATA] == before[m.DATA] and tapes[m.HEADER] == before[m.HEADER],
                     'round public preservation')
                if fits:
                    expected = bytearray(before[m.OUTPUT])
                    word = v.signed(q, w)
                    expected[3:3 + w] = bytes(v.SYMBOLS[x] for x in word)
                    need(tapes[m.OUTPUT] == expected, 'nearest-UP integer result')
                    need(result['heads'] == [3] * m.TAPES, 'round unit return')
                    need(all(bytes(t) == before[i] for i, t in enumerate(tapes) if i != m.OUTPUT),
                         'round unit scratch/guide/exterior')
                    fits_count += 1
                else:
                    need(not result['staged'], 'overflow staged a bad component')
                if z % (1 << k) == 1 << (k - 1):
                    positive_ties += z >= 0
                    negative_ties += z < 0
                if w == 2 and k == 1 and z in (-5, -1, 1):
                    witness[str(z)] = dict(q=q, accepted=fits, literal_steps=result['steps'])
                transitions += result['steps']
                count += 1
    need(witness['-5']['q'] == -2 and witness['-5']['accepted'], 'post-round-fit control')
    need(witness['-1']['q'] == 0 and witness['1']['q'] == 1, 'signed half-tie controls')
    # These competing rules disagree with the actual local graph witnesses.
    need((-5 // 2) < -2, 'pre-round clipping mutant')
    need(round(0.5) != witness['1']['q'], 'ties-even mutant')
    need((-1 // 2) != witness['-1']['q'], 'floor-only mutant')
    return dict(cases=count, transitions=transitions, fitting_cases=fits_count,
                positive_half_ties=positive_ties, negative_half_ties=negative_ties,
                witnesses=witness, semantic_controls=['pre-round-fit', 'ties-even', 'floor-only'])


def header_and_lift_cases():
    header_code, _ = m.compile_header()
    header_program = v.numeric(header_code)
    lift_code, _ = m.compile_converter('ingress')
    lift_program = v.numeric(lift_code)
    total = cases = 0
    for f in list(range(1, 17)) + [31, 32, 33, 63, 64, 65, 129]:
        w, k = 2 + f % 13, (f + 1) // 2
        width = w + 2 * k + 1
        shape = (f, 2, 3, 5, w, 1 << 511)
        original = v.header(shape) + '|011|'
        expected = v.header(shape[:4] + (width, shape[5]))
        tapes = packet(4 * (f + width + len(original) + 20))
        put(tapes, m.HEADER, original)
        before = [bytes(t) for t in tapes]
        result, _ = run(header_program, tapes)
        need(not result['rejected'] and not result['writes'], 'header rejected')
        need(bytes(tapes[m.HEADER]) == before[m.HEADER], 'public header/opaque changed')
        live = {m.h.F: f, m.h.R: 2, m.h.P: 3, m.h.S: 5, m.WIDTH: w, m.K: k,
                m.WIDE: width, m.MARGIN: k + 1, m.HIGH: w + k + 1,
                m.h.BLEN: width.bit_length()}
        for port, n in live.items():
            target = bytearray(before[port])
            target[2] = 3
            target[3:3 + n] = bytes([2]) * n
            need(tapes[port] == target, 'header live guide ' + str(port))
        target = bytearray(before[m.WH])
        target[2] = 3
        target[3:3 + len(expected)] = bytes(v.SYMBOLS[x] for x in expected)
        need(tapes[m.WH] == target and result['heads'] == [3] * m.TAPES, 'private canonical header')
        total += result['steps']
        values = [-(1 << (w - 1)), -1, 0, 1, (1 << (w - 1)) - 1]
        word = ''.join(v.signed(x, w) for x in values)
        lifted = ''.join(v.signed(x << k, width) for x in values)
        tapes = packet(4 * (len(lifted) + 30), True)
        guides(tapes, w, k, len(values))
        put(tapes, m.DATA, word)
        before = [bytes(t) for t in tapes]
        result, _ = run(lift_program, tapes)
        target = bytearray(before[m.WD])
        target[3:3 + len(lifted)] = bytes(v.SYMBOLS[x] for x in lifted)
        need(not result['rejected'] and tapes[m.WD] == target, 'literal signed lift')
        need(all(bytes(t) == before[i] for i, t in enumerate(tapes) if i != m.WD),
             'lift public/metadata/exterior')
        need(result['heads'] == [3] * m.TAPES and not result['writes'], 'lift return')
        total += result['steps']
        cases += 1
    return dict(header_cases=cases, lift_cases=cases, transitions=total,
                max_f=129, max_k=65, cutoff_bits=512)


def source_column(address):
    x = v.unpack(address, 1)
    t = tuple(a ^ ((v.RIGHT['offset'] >> i) & 1)
              for i, a in enumerate(v.linear(v.RIGHT['matrix_rows'], x)))
    result = {}
    for b in (0, 1):
        z = (b,) + t[1:]
        output = v.pack(v.linear(v.LEFT['matrix_rows'], z), 1)
        coefficient = v.rotate((1, 1 if b == t[0] else -1),
                               v.phase(v.RIGHT, x, 1) + v.phase(v.LEFT, z, 1))
        result[output] = coefficient
    return result


def oracle(values):
    """Complete forward sparse Gaussian source kernel; denominator two."""
    totals = [(0, 0)] * 512
    for address, value in enumerate(values):
        for output, coefficient in source_column(address).items():
            term = v.mul(coefficient, value)
            prior = totals[output]
            totals[output] = prior[0] + term[0], prior[1] + term[1]
    return [((a + 1) // 2, (b + 1) // 2) for a, b in totals], totals


def full_packet(shape, values, tapes=None, cumulative=None):
    f, r, p, s, w, cutoff = shape
    need((f, r, p, s) == (1, 1, 1, 1), 'finite full-field corpus scope')
    word = v.encode(values, w)
    width = w + 3
    if tapes is None:
        tapes = packet(4 * (1024 * width + len(v.header(shape)) + 100))
    else:
        # Supplied next public packet replacement; old private/history are retained.
        for port in (m.HEADER, m.DATA):
            tapes[port][3:-2] = bytes(len(tapes[port]) - 5)
    put(tapes, m.HEADER, v.header(shape) + '|0101|')
    put(tapes, m.DATA, word)
    before = [bytes(t) for t in tapes]
    owners = tuple(map(id, tapes))
    expected, totals = oracle(values)
    fits = all(-(1 << (w - 1)) <= z < (1 << (w - 1)) for pair in expected for z in pair)
    code, _, entries = m._compile_rounded()
    result, cumulative = run(v.numeric(code), tapes, commit=entries['commit'], cumulative=cumulative)
    need(result['rejected'] != fits, 'full packet acceptance differs from true rounded fit')
    need(tuple(map(id, tapes)) == owners and bytes(tapes[m.HEADER]) == before[m.HEADER],
         'full owner/header preservation')
    need(not result['early'], 'early public DATA write')
    if fits:
        target = bytearray(before[m.DATA])
        target[3:3 + len(word)] = bytes(v.SYMBOLS[x] for x in v.encode(expected, w))
        need(tapes[m.DATA] == target, 'complete once-rounded source result')
        need(result['writes'] == len(word) and result['heads'] == [3] * m.TAPES, 'full commit/return')
        need(all(bytes(t) == before[i] for i, t in enumerate(tapes) if i != m.DATA),
             'full private/header/exterior restoration')
    else:
        need(bytes(tapes[m.DATA]) == before[m.DATA] and not result['writes'], 'overflow public mutation')
        need(result['staged'] > 0, 'overflow is not late after earlier staged outputs')
    need(result['steps'] <= (1 << 26) * (1024 * width + len(v.header(shape)) + 1), 'complete bill')
    result.update(shape=shape, payload_bits=len(word), wide_bits=1024 * width,
                  nonintegral_output_components=sum(z % 2 != 0 for pair in totals for z in pair))
    return result, tapes, cumulative


def full_cases():
    values = [(0, 0)] * 512
    values[0], values[1] = (1, 0), (0, -4)
    need(v.phase(v.RIGHT, v.unpack(1, 1), 1) == 1, 'most-negative input phase fixture')
    first, tapes, history = full_packet((1, 1, 1, 1, 3, 1), values)
    need(not first['rejected'] and first['nonintegral_output_components'] > 0, 'nonintegral full packet')
    values = [(0, 0)] * 512
    values[0] = (1, 0)
    second, _, history = full_packet((1, 1, 1, 1, 2, 1 << 257), values, tapes, history)
    need(not second['rejected'] and second['cumulative_history'] >= first['cumulative_history'],
         'successful smaller-call historical retention')
    a = 32
    support = set(source_column(a))
    b = next(i for i in range(512) if i != a and set(source_column(i)) == support)
    choices = list(itertools.product(range(-2, 2), repeat=2))
    for x, y in itertools.product(choices, repeat=2):
        bad = [(0, 0)] * 512
        bad[a], bad[b] = x, y
        rounded, _ = oracle(bad)
        if any(z < -2 or z > 1 for pair in rounded for z in pair):
            break
    else:
        raise ValueError('no late final-overflow fixture found')
    third, _, _ = full_packet((1, 1, 1, 1, 2, 1), bad)
    need(third['rejected'], 'true final overflow accepted')
    return dict(success=first, shorter_reuse=second, late_overflow=third,
                overflow_source_pair=[a, b], overflow_values=[x, y])


def verify(quick=False):
    need(sys.dont_write_bytecode and not Path(sys.pycache_prefix).exists(), 'source cache isolation')
    for pin in json.loads((HERE / 'ROUNDED-SOURCES.json').read_text())['files']:
        raw = (HERE / pin['local']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['blob'], 'immutable helper/source Git blob')
    code, alphabet, entries = m._compile_rounded()
    core, _ = m.h.core.compile_move()
    need(entries['round'] - entries['core'] == len(core), 'complete embedded core length')
    start, end = entries['core'], entries['round']
    for i, (op, *a) in enumerate(core):
        if op == 'read':
            expected = (op, m.CORE_PORTS[a[0]], {b: start + j for b, j in a[1].items()})
        elif op in ('write', 'move'):
            expected = (op, m.CORE_PORTS[a[0]], a[1])
        elif op == 'goto':
            expected = (op, start + a[0])
        else:
            need(op == 'halt', 'unknown core instruction')
            expected = ('goto', end)
        need(code[start + i] == expected, 'absolute-PC core relocation')
    need(not any(op == 'write' and a[0] in (m.HEADER, m.DATA)
                 for op, *a in code[:entries['commit']]), 'precommit public write')
    need(not any(op == 'write' and a[0] == m.HEADER for op, *a in code), 'public header write')
    result = dict(marker='PASS_LITERAL_ONCE_ROUNDED_SELECTED_MOVE', locations=len(code),
                  tapes=m.TAPES, alphabet=alphabet, entries=entries,
                  graph_sha256=hashlib.sha256(repr(code).encode()).hexdigest(),
                  source_cache_isolated=True,
                  relocated_core_instructions=len(core), header_lift=header_and_lift_cases(),
                  rounding=rounding_cases())
    if quick:
        result['marker'] += '_UNIT_ONLY'
    else:
        result['full_f1'] = full_cases()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    need(not (args.quick and args.write), 'unit-only mode cannot write accepted receipt')
    result = verify(args.quick)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'RESULT.json').write_text(text)
    print(text, end='')
