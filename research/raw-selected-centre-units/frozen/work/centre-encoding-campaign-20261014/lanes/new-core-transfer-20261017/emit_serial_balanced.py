#!/usr/bin/env python3
"""Transfer scalar row factors onto both complete native providers."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CORE_PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'
REPLAY_PIN = 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc'
FIVE_PIN = 'a16521b290c39468fa491e1da10e5d5ffe6869226563a02ac8146a4feaca0afe'


def need(test, label):
    if not test:
        raise ValueError(label)


def load(name, pin):
    raw = gzip.decompress((HERE / name).read_bytes())
    need(sha256(raw).hexdigest() == pin, 'Source pin: ' + name)
    return json.loads(raw)


def factor(r, selected, inverse, upper, offset, frame, n):
    ordinary = set(range(112)) - set(selected)
    binary, odd = ((16, 3) if len(selected) == 8 else (32, 1)) if inverse else (4, 1)
    events = [{'kind': 'clear', 'target': n, 'frame': frame}]
    for i, row in enumerate(r):
        events += [{'kind': 'add', 'target': n, 'source': offset + p,
                    'coefficient': str(c), 'frame': frame}
                   for p, c in sorted(row.items()) if p in ordinary]
        events.append({'kind': 'scale', 'target': n, 'coefficient': str(Q(1, binary)), 'frame': frame})
        if odd > 1:
            events.append({'kind': 'divide_odd', 'target': n, 'divisor': odd, 'frame': frame})
        events += [{'kind': 'add', 'target': offset + p, 'source': n,
                    'coefficient': str(-c), 'frame': frame}
                   for p, c in sorted(row.items()) if upper or p in ordinary]
        events.append({'kind': 'clear', 'target': n, 'frame': 0 if i == 7 else frame})
    return events


def exchange(selected):
    result = []
    for p in selected:
        for t, s, c in ((p, 112 + p, 1), (112 + p, p, -1), (p, 112 + p, 1)):
            result.append({'kind': 'add', 'target': t, 'source': s, 'coefficient': str(c)})
        result.append({'kind': 'scale', 'target': 112 + p, 'coefficient': '-1'})
    return result


def price(events):
    scalar, scans = 0, 0
    for e in events:
        if e['kind'] == 'divide_odd':
            need(e['divisor'] == 3, 'Specified odd scan')
            scans += 2
        elif e['kind'] == 'clear':
            scalar += 2
        else:
            c = Q(e['coefficient'])
            a, b = abs(c.numerator), c.denominator
            need(a and b & (b - 1) == 0, 'Nonzero dyadic scalar')
            if e['kind'] == 'scale':
                need(a & (a - 1) == 0, 'Dyadic unit SCALE')
                scalar += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
            else:
                need(e['kind'] == 'add', 'Known boundary scalar')
                scalar += 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)
    return scalar, scans


def boundary(replay, events, state, n):
    exact = []
    for event in events:
        e = dict(event)
        if e['kind'] == 'divide_odd':
            need(e['target'] == n and e['divisor'] == 3, 'Owned odd division')
            e = {'kind': 'scale', 'target': n, 'coefficient': '1/3'}
        exact.append(e)
    return replay.boundary(exact, state, n)


def check_factor_frames(events, offset, frame, n):
    frames = {p: frame for p in range(offset, offset + 112)}
    frames[n] = 0
    for e in events:
        t, f = e['target'], e['frame']
        if e['kind'] == 'clear':
            need(t == n, 'Only owned C0 is cleared')
            frames[t] = f
        else:
            need(frames[t] == f == frame, 'Factor target frame')
            if e['kind'] == 'add':
                s = e['source']
                need(s != t and frames[s] == f, 'Factor source frame')
                need(n in (s, t), 'Serial C0 factor ADD')
            else:
                need(t == n, 'Only the private query is scaled')
    need(frames[n] == 0 and sum(e['kind'] == 'clear' for e in events) == 9, 'Nine owned clears, final I')


def main():
    replay_path = HERE / 'emit_raw_selected.py'
    need(sha256(replay_path.read_bytes()).hexdigest() == REPLAY_PIN, 'Frozen native replay')
    spec = importlib.util.spec_from_file_location('serial_native_replay', replay_path)
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    core, five = load('CLEAN-J-PROGRAMS.json.gz', CORE_PIN), load('BALANCED-FIVE-MINOR-PROGRAMS.json.gz', FIVE_PIN)
    r = [{int(p): Q(c) for p, c in row.items()} for row in core['R']]
    gram = {p: {q: sum(row.get(p, 0) * row.get(q, 0) for row in r) / 4 for q in range(112)} for p in range(112)}
    j = {p: {q: Q(p == q) - gram[p][q] for q in range(112)} for p in range(112)}
    packet = {'schema': 'pr3133-serial-balanced-native-words-v1',
              'source_pins': {'core': CORE_PIN, 'native_replay': REPLAY_PIN, 'five_minor_words': FIVE_PIN},
              'families': {}}
    receipt = {'status': 'PASS_PR3133_SERIAL_BALANCED_WORDS', 'families': {}}
    for name, selected in (('one_minor', five['selected_minors'][0]), ('five_minors', five['selected_S'])):
        selected = sorted(selected)
        ordinary = [p for p in range(112) if p not in selected]
        lam = 14 - len(selected) // 8
        need(all(sum(row.get(p, 0) * col.get(p, 0) for p in ordinary) == (4 * lam if i == k else 0)
                 for i, row in enumerate(r) for k, col in enumerate(r)), 'Actual ordinary row Gram matrix')
        h = {p: {q: j[p][q] for q in ordinary} for p in ordinary}
        hi = {p: {q: Q(p == q) - gram[p][q] / (lam - 1) for q in ordinary} for p in ordinary}
        family, reports = {'selected_S': selected, 'ordinary_U': ordinary, 'lambda': lam, 'providers': {}}, {}
        for provider, item in core['providers'].items():
            word, n = item['canonical'], len(item['canonical']['start'])
            need(n == 632 and len(word['zero_buffers']) == 91, 'Exact provider')
            need(word['start'][112:224] == [0] * 112 and word['final'][:112] == [1] * 112, 'Actual factor endpoints')
            identity = {p: {(p, ()): Q(1)} for p in range(n + 8)}
            fs = factor(r, selected, False, False, 112, 0, n)
            bs = factor(r, selected, True, False, 0, 1, n)
            ds = factor(r, selected, True, True, 0, 1, n)
            for events, offset, frame in ((fs, 112, 0), (bs, 0, 1), (ds, 0, 1)):
                check_factor_frames(events, offset, frame, n)
            for events, matrix, offset in ((fs, h, 112), (bs, hi, 0)):
                actual = boundary(replay, events, identity, n)
                expected = deepcopy(identity)
                for p in ordinary:
                    expected[offset + p] = {(offset + q, ()): c for q, c in matrix[p].items() if c}
                expected[n] = {}
                need(actual == expected, 'Exact serial ordinary factor')
            swaps = exchange(selected)
            cleanup = [{'kind': 'clear', 'target': n + p} for p in range(1, 8)]
            def evaluate(direction, pre, post):
                physical = deepcopy(identity)
                for p in range(112):
                    physical[p] = replay.line(physical[p], p, 1)
                physical = boundary(replay, pre + swaps, physical, n)
                logical = deepcopy(physical)
                for p in range(112):
                    logical[p] = replay.line(logical[p], p, -1)
                logical, checks, warps = replay.core_replay(item['programs'][direction], logical, word, direction == 'backward')
                physical = deepcopy(logical)
                for p in range(112):
                    physical[112 + p] = replay.line(physical[112 + p], p, -1)
                physical = boundary(replay, post + cleanup, physical, n)
                logical = deepcopy(physical)
                for p in range(112):
                    logical[112 + p] = replay.line(logical[112 + p], p, 1)
                return logical, physical, checks, warps
            eb, ed, ef = deepcopy(identity), deepcopy(identity), deepcopy(identity)
            for p in selected:
                eb[p] = replay.line(identity[112 + p], p, -1)
                ed[p] = replay.line(identity[112 + p], p, -1)
                replay.add(ed[p], replay.line(identity[p], p, 1), -1)
                eb[112 + p] = ed[112 + p] = replay.line(identity[p], p, 1)
                query = {}
                for q in selected:
                    replay.add(eb[p], replay.line(identity[q], q, 1), -j[p][q])
                    replay.add(query, replay.line(identity[112 + q], q, -1), j[p][q])
                for q in ordinary:
                    replay.add(eb[p], identity[112 + q], -j[p][q])
                    replay.add(query, identity[q], j[p][q])
                replay.add(ef[p], replay.line(query, p, -1))
            for p in ordinary:
                eb[p] = {key: -c for key, c in identity[112 + p].items()}
                replay.add(ed[p], identity[112 + p], -1)
                ef[112 + p] = {}
                for q in ordinary:
                    replay.add(eb[p], identity[q], hi[p][q])
                    replay.add(ef[112 + p], identity[q], h[p][q])
                    replay.add(ef[112 + p], identity[112 + q], h[p][q])
                for q in selected:
                    replay.add(eb[p], replay.line(identity[q], q, 1), -gram[p][q] / (lam - 1))
                    replay.add(ef[112 + p], replay.line(identity[112 + q], q, -1), j[p][q])
            for p in range(112):
                for q in range(112):
                    src = replay.line(identity[q], q, 1) if q in selected else identity[q]
                    replay.add(ed[p], src, -gram[p][q] / (lam - 1))
            for expected in (eb, ed, ef):
                for p in range(n, n + 8):
                    expected[p] = {}
            specs = {'balanced_backward': ('backward', [], bs, eb),
                     'diagonal_backward': ('backward', [], ds, ed),
                     'balanced_forward': ('forward', fs, swaps, ef)}
            programs, result = {}, {}
            for variant, (direction, pre, post, expected) in specs.items():
                actual, physical, checks, warps = evaluate(direction, pre, post)
                need(actual == expected, 'All 640 ordered columns: ' + name + ' ' + variant)
                need(all(actual[p] == identity[p] for p in range(224, n)), 'All arbitrary helpers restored')
                need(all(not actual[p] for p in range(n, n + 8)), 'Owned outputs zero')
                if direction == 'backward':
                    need(all(physical[112 + p] == identity[p] for p in selected), 'Selected productive Y keeps original X')
                native = item['programs'][direction]
                old, scans = price(pre + swaps + post + cleanup)
                old += replay.core_price(native)
                profile = Counter(e[5] for e in native if e[0] == 'climb')
                need(dict(profile) == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'No new native child')
                programs[variant] = {'orientation': direction, 'prefix': pre, 'input_exchange': swaps,
                                     'retained_core': native, 'suffix': post, 'owned_cleanup': cleanup,
                                     'events': pre + swaps + native + post + cleanup}
                result[variant] = {'scalar_real_primitives': old, 'additional_real_divide_by_3_scans': scans,
                                   'native_profile': dict(sorted(profile.items())), 'native_rank_mass': 5073,
                                   'native_children': 3507, 'new_native_children': 0, 'new_private_fields': 0,
                                   'all_input_columns': 640, 'arbitrary_helpers_restored': 408,
                                   'private_zero_buffers_restored': 91, 'owned_private_final_zero': 8,
                                   'core_scalar_frame_checks': checks, 'core_warp_events': warps}
                print(name, provider, variant, old, scans, flush=True)
            family['providers'][provider] = {'canonical': word, 'programs': programs}
            reports[provider] = result
        packet['families'][name], receipt['families'][name] = family, reports
    raw = (json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'SERIAL-BALANCED-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['source_pins'] = packet['source_pins']
    receipt['scope'] = ('Twelve complete native words. Odd division is recorded separately, with no invented old-primitive cost. '
                        'The exact odd-grid implementation, global controller, precision, hosting and supplier bill remain separate.')
    (HERE / 'SERIAL-BALANCED-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['payload_sha256'])


if __name__ == '__main__':
    main()
