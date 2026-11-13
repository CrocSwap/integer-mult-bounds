"""Stdlib literal width-wrapper verification; core files remain unchanged."""
from pathlib import Path
import argparse
import hashlib
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import endpoint as e
import verify as v


def need(ok, message):
    if not ok:
        raise ValueError(message)


def blank_tapes(capacity):
    tapes = [bytearray(capacity + 7) for _ in range(e.TAPES)]
    for tape in tapes:
        tape[0:2] = b'\x02\x03'
        tape[-2:] = b'\x01\x03'
    return tapes


def put(tapes, port, word):
    tapes[port][3:3 + len(word)] = bytes(v.SYMBOLS[x] for x in word)


def body(tape, symbols=(1, 2)):
    end = 3
    while tape[end] in symbols:
        end += 1
    return bytes(tape[3:end])


def run(code, tapes, *, commit=None, limit=200_000_000):
    instructions = v.numeric(code)
    heads, lows, highs = [3] * len(tapes), [3] * len(tapes), [3] * len(tapes)
    pc = steps = writes = early = 0
    rejected = False
    while True:
        op, tape, arg = instructions[pc]
        steps += 1
        if steps > limit:
            raise ValueError('finite wrapper verifier budget')
        if op == 0:
            pc = arg[tapes[tape][heads[tape]]]
            if pc < 0:
                rejected = True
                break
        elif op == 1:
            tapes[tape][heads[tape]] = arg
            if tape == e.DATA:
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
    return dict(steps=steps, rejected=rejected, writes=writes, early=early,
                heads=heads, lows=lows, highs=highs,
                history=sum(hi - lo + 1 for lo, hi in zip(lows, highs)))


def header_cases():
    code, _ = e.compile_header()
    total = 0
    fs = list(range(1, 33)) + [63, 64, 65, 127, 128, 255, 257, 511, 1023]
    for f in fs:
        w = 2 + (f % 17)
        shape = (f, 1 + f % 3, 1 + f % 5, 1 + f % 7, w, 1 << 257)
        k, wp = (f + 2) // 4, w + 2 * ((f + 2) // 4)
        expected = v.header(shape[:4] + (wp, shape[5]))
        original = v.header(shape) + '|001|'
        tapes = blank_tapes(4 * (f + wp + len(original) + 30))
        put(tapes, e.HEADER, original)
        before = [bytes(t) for t in tapes]
        result = run(code, tapes)
        need(not result['rejected'] and not result['writes'], 'header producer rejected')
        need(bytes(tapes[e.HEADER]) == before[e.HEADER], 'original header changed')
        wh_target = bytearray(before[e.WH])
        wh_target[2] = 3
        wh_target[3:3 + len(expected)] = bytes(v.SYMBOLS[x] for x in expected)
        need(tapes[e.WH] == wh_target, 'widened Gamma header/exterior')
        expected_guides = {e.F: f, e.R: shape[1], e.P: shape[2], e.S: shape[3],
                           e.WIDTH: w, e.K: k, e.WIDE: wp, e.BLEN: wp.bit_length()}
        for tape, count in expected_guides.items():
            target = bytearray(before[tape])
            target[2] = 3
            target[3:3 + count] = bytes([2]) * count
            need(tapes[tape] == target, 'header guide/exterior ' + str(tape))
        need(result['heads'] == [3] * e.TAPES, 'header unit heads not returned')
        for i, tape in enumerate(tapes):
            if i not in expected_guides and i not in (e.WH, e.HEADER):
                target = bytearray(before[i])
                if i in e.WRAPPER_PRIVATE:
                    target[2] = 3
                need(tape == target, 'unexpected live header helper ' + str(i))
        need(result['steps'] <= (1 << 20) * (f + wp + len(original) + 1), 'header linear bound')
        total += result['steps']
    return dict(cases=len(fs), transitions=total, max_f=max(fs), cutoff_bits=258)


def conversion_cases():
    ingress, _ = e.compile_converter('ingress')
    egress, _ = e.compile_converter('egress')
    rng = random.Random(746824472)
    total = cases = rejected = 0
    widths = (2, 3, 4, 7, 17)
    for f in (1, 2, 3, 5, 6, 9, 10, 17, 31, 65):
        k = (f + 2) // 4
        for w in widths:
            values = [-(1 << (w - 1)), (1 << (w - 1)) - 1, -1, 0, 1,
                      rng.randrange(-(1 << (w - 1)), 1 << (w - 1))]
            word = ''.join(v.signed(x, w) for x in values)
            wide = ''.join(v.signed(x << k, w + 2 * k) for x in values)
            tapes = blank_tapes(4 * (len(wide) + 50))
            for tape in e.WRAPPER_PRIVATE:
                tapes[tape][2] = 3
            for tape, count in ((e.WIDTH, w), (e.K, k), (e.COUNT, len(values))):
                put(tapes, tape, '1' * count)
            put(tapes, e.DATA, word)
            before = [bytes(t) for t in tapes]
            result = run(ingress, tapes)
            need(not result['rejected'] and not result['writes'], 'ingress rejection')
            expected = bytearray(before[e.WD])
            expected[3:3 + len(wide)] = bytes(v.SYMBOLS[x] for x in wide)
            need(tapes[e.WD] == expected, 'ingress signed scale/width')
            need(all(bytes(t) == before[i] for i, t in enumerate(tapes) if i != e.WD),
                 'ingress public/guides/trace/exterior')
            need(result['heads'] == [3] * e.TAPES, 'ingress helper return')
            need(result['steps'] <= (1 << 12) * (len(wide) + 1), 'ingress complete bound')
            total += result['steps']
            before = [bytes(t) for t in tapes]
            result = run(egress, tapes)
            target = bytearray(before[e.OUTPUT])
            target[3:3 + len(word)] = bytes(v.SYMBOLS[x] for x in word)
            need(not result['rejected'] and tapes[e.OUTPUT] == target, 'egress exact drop')
            need(all(bytes(t) == before[i] for i, t in enumerate(tapes) if i != e.OUTPUT),
                 'egress public/guides/source/trace/exterior')
            need(result['heads'] == [3] * e.TAPES and not result['writes'], 'egress helper return')
            total += result['steps']
            cases += 2
            if k:
                for label, index in (('low_nonzero', w + 2 * k - 1), ('leading_mismatch', k)):
                    bad = [bytearray(t) for t in tapes]
                    # Retire prior unit output only; the tested source and guides remain live.
                    bad[e.OUTPUT][3:3 + len(word)] = bytes(len(word))
                    bad[e.WD][3 + index] = 1 if bad[e.WD][3 + index] == 2 else 2
                    before_bad = [bytes(t) for t in bad]
                    result = run(egress, bad)
                    need(result['rejected'] and not result['writes'], label + ' not rejected')
                    need(bytes(bad[e.DATA]) == before_bad[e.DATA], label + ' public changed')
                    rejected += 1
    return dict(cases=cases, transitions=total, arithmetic_rejections=rejected,
                max_k=(65 + 2) // 4, component_widths=widths)


def encoder_cases():
    a = e.Builder()
    e.unary_binary(a)
    a.op('halt')
    code, _ = a.finish((e.BLANK, '0', e.ONE, e.MARK))
    total = 0
    values = list(range(1, 129)) + [255, 256, 257, 511, 512, 1023, 1024]
    for n in values:
        tapes = blank_tapes(4 * n + 100)
        for tape in e.WRAPPER_PRIVATE:
            tapes[tape][2] = 3
        put(tapes, e.TMP, '1' * n)
        result = run(code, tapes)
        need(not result['rejected'], 'literal floor-halving rejected')
        need(body(tapes[e.BINARY]) == bytes(v.SYMBOLS[x] for x in bin(n)[2:]), 'literal binary width')
        need(body(tapes[e.TMP]) == body(tapes[e.HALF]) == body(tapes[e.DIGITS]) == b'',
             'encoder scratch not retired')
        need(result['steps'] == 19 * n - 12 * n.bit_count() + 19 * n.bit_length() + 8,
             'exact encoder instruction census')
        total += result['steps']
    return dict(cases=len(values), transitions=total, max_unary=max(values))


def full_case():
    shape = (1, 1, 1, 1, 4, 1)
    rng = random.Random(748024472)
    values = [(2 * rng.randrange(-1, 2), 2 * rng.randrange(-1, 2)) for _ in range(512)]
    word, expected = v.encode(values, shape[4]), v.oracle(values, shape)
    tapes = blank_tapes(4 * (len(word) + len(v.header(shape)) + 30))
    put(tapes, e.HEADER, v.header(shape) + '|010|')
    put(tapes, e.DATA, word)
    before = [bytes(t) for t in tapes]
    owners = tuple(map(id, tapes))
    code, alphabet, entries = e._compile_endpoint()
    result = run(code, tapes, commit=entries['commit'])
    need(not result['rejected'], 'full endpoint wrapper rejected')
    target = bytearray(before[e.DATA])
    target[3:3 + len(expected)] = bytes(v.SYMBOLS[x] for x in expected)
    need(tapes[e.DATA] == target, 'full endpoint kernel')
    need(all(bytes(t) == before[i] for i, t in enumerate(tapes) if i != e.DATA),
         'full endpoint private/header/exterior retirement')
    need(result['heads'] == [3] * e.TAPES and result['writes'] == len(word) and not result['early'],
         'full endpoint original-owner transaction')
    need(tuple(map(id, tapes)) == owners, 'full endpoint replaced owner')
    need(result['steps'] <= (1 << 26) * (len(word) + len(v.header(shape)) + 1), 'full complete time')
    need(result['history'] <= e.TAPES + 4096 * (len(word) + len(v.header(shape)) + 1),
         'full retained history')
    return dict(shape=shape, bits=len(word), **result)


def verify(quick=False):
    for pin in json.loads((HERE / 'ENDPOINT-SOURCES.json').read_text())['files']:
        raw = (HERE / pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'],
             'endpoint source hash')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['blob'], 'endpoint source Git blob')
    code, alphabet, entries = e._compile_endpoint()
    v.numeric(code)
    need(alphabet == ('_', '0', '1', '|'), 'four-symbol wrapper')
    need(max(args[0] for op, *args in code if op in ('read', 'write', 'move')) == e.TAPES - 1,
         'fixed wrapper owner inventory')
    result = dict(marker='PASS_LITERAL_ENDPOINT_WIDTH_WRAPPER', locations=len(code), tapes=e.TAPES,
                  graph_sha256=hashlib.sha256(repr(code).encode()).hexdigest(), entries=entries,
                  header=header_cases(), encoder=encoder_cases(), converters=conversion_cases())
    if quick:
        result['marker'] += '_UNIT_ONLY'
    else:
        result['full_f1'] = full_case()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    need(not (args.quick and args.write), 'unit-only checks cannot write accepted full receipt')
    result = verify(args.quick)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'ENDPOINT-RESULT.json').write_text(text)
    print(text, end='')
