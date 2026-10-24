#!/usr/bin/env python3
"""Transfer the exact irregular split with eight current owned queries."""

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
RAW_PIN = 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc'
SERIAL_PIN = '7399a1d153197faae5f44f04e0ae3675a6c961d343329419c0c71bdc263bb9d6'
WITNESS_PIN = '0a8d22fa0b523c261243e9b19cfd51926c9b515a9e6f9a962d1e3b5170105a8f'


def need(test, label):
    if not test:
        raise ValueError(label)


def module(name, filename, pin):
    path = HERE / filename
    need(sha256(path.read_bytes()).hexdigest() == pin, 'Pinned replay: ' + filename)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def product(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in columns] for row in a]


def add_event(t, s, c, frame):
    need(t != s and c, 'Nonzero off-diagonal ADD')
    return {'kind': 'add', 'target': t, 'source': s, 'coefficient': str(c), 'frame': frame}


def factor(r, selected, inverse, upper, offset, frame, n):
    ordinary = set(range(112)) - set(selected)
    events = [{'kind': 'clear', 'target': n + i, 'frame': frame} for i in range(8)]
    for i, row in enumerate(r):
        events += [add_event(n + i, offset + p, c, frame) for p, c in sorted(row.items()) if p in ordinary]
    if inverse:
        for t, s in ((0, 2), (0, 3), (1, 4), (1, 5), (2, 0), (3, 0), (4, 1), (5, 1)):
            events.append(add_event(n + t, n + s, Q(-1, 4), frame))
    events += [{'kind': 'scale', 'target': n + i, 'coefficient': str(Q(1, 32) if inverse else Q(1, 4)),
                'frame': frame} for i in range(8)]
    for i, row in enumerate(r):
        events += [add_event(offset + p, n + i, -c, frame) for p, c in sorted(row.items()) if upper or p in ordinary]
    events += [{'kind': 'clear', 'target': n + i, 'frame': 0} for i in range(8)]
    return events


def check_frames(events, offset, frame, n):
    frames = {p: frame for p in range(offset, offset + 112)}
    frames.update({n + i: 0 for i in range(8)})
    for e in events:
        t, f = e['target'], e['frame']
        if e['kind'] == 'clear':
            need(n <= t < n + 8, 'Only owned queries are cleared')
            frames[t] = f
        else:
            need(frames[t] == f == frame, 'Factor target frame')
            if e['kind'] == 'add':
                s = e['source']
                need(s != t and frames[s] == f, 'Factor source frame')
                need(n <= s < n + 8 or n <= t < n + 8, 'Only data-query or query-query ADD')
            else:
                need(e['kind'] == 'scale' and n <= t < n + 8, 'Query SCALE')
    need(all(frames[n + i] == 0 for i in range(8)), 'All query fields return to I')


def main():
    replay = module('irregular_raw', 'emit_raw_selected.py', RAW_PIN)
    serial = module('irregular_serial', 'emit_serial_balanced.py', SERIAL_PIN)
    raw = gzip.decompress((HERE / 'CLEAN-J-PROGRAMS.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == CORE_PIN, 'Core payload pin')
    core = json.loads(raw)
    path = HERE.parent.parent / 'root/IRREGULAR-SPLIT-20261017.json'
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == WITNESS_PIN, 'Independent witness pin')
    witness = json.loads(raw)
    selected = witness['selected']
    ordinary = [p for p in range(112) if p not in selected]
    need(len(selected) == 38 and len(ordinary) == 74, 'Irregular split sizes')
    r = [{int(p): Q(c) for p, c in row.items()} for row in core['R']]
    dense_r = [[row.get(p, Q(0)) for p in range(112)] for row in r]
    k = [[dense_r[i][p] / 4 for i in range(8)] for p in range(112)]
    gram = product(k, dense_r)
    selected_gram = [[sum(row.get(p, 0) * col.get(p, 0) for p in selected) for col in r] for row in r]
    need(selected_gram == witness['gram'], 'Actual selected Gram matrix')
    t = [[selected_gram[i][j] / 4 - 13 * (i == j) for j in range(8)] for i in range(8)]
    ti = [[Q(c) for c in row] for row in witness['T_inverse']]
    eye8 = [[Q(i == j) for j in range(8)] for i in range(8)]
    need(product(t, ti) == product(ti, t) == eye8, 'Actual centre inverse both orders')
    l_inverse = deepcopy(eye8)
    for i, j in ((0, 2), (0, 3), (1, 4), (1, 5)):
        l_inverse[i][j] -= Q(1, 4)
    derived = product(list(map(list, zip(*l_inverse))), l_inverse)
    need([[-c / 8 for c in row] for row in derived] == ti, 'Explicit inverse shear factor')
    pmat = product(product(k, ti), dense_r)
    jmat = [[Q(p == q) - gram[p][q] for q in range(112)] for p in range(112)]
    packet = {'schema': 'pr3133-irregular-38-native-words-v1',
              'source_pins': {'core': CORE_PIN, 'raw_replay': RAW_PIN, 'serial_utility': SERIAL_PIN, 'witness': WITNESS_PIN},
              'selected_S': selected, 'ordinary_U': ordinary, 'T_inverse': witness['T_inverse'], 'providers': {}}
    receipt = {'status': 'PASS_PR3133_IRREGULAR_38_NATIVE_WORDS', 'selected_ports': 38,
               'ordinary_ports': 74, 'existing_owned_query_peak': 8, 'new_private_fields': 0,
               'new_native_children': 0, 'factor_scalar_costs': {}, 'providers': {}}
    for provider, item in core['providers'].items():
        word, n = item['canonical'], len(item['canonical']['start'])
        need(n == 632 and len(word['zero_buffers']) == 91, 'Exact provider')
        need(word['start'][112:224] == [0] * 112 and word['final'][:112] == [1] * 112, 'Actual common endpoint frames')
        identity = {p: {(p, ()): Q(1)} for p in range(n + 8)}
        fs = factor(r, selected, False, False, 112, 0, n)
        bs = factor(r, selected, True, False, 0, 1, n)
        ds = factor(r, selected, True, True, 0, 1, n)
        for events, offset, frame, factor_name in ((fs, 112, 0, 'H'), (bs, 0, 1, 'H_inverse'), (ds, 0, 1, 'fused_inverse')):
            check_frames(events, offset, frame, n)
            actual = replay.boundary(events, identity, n)
            expected = deepcopy(identity)
            for p in ordinary:
                matrix = jmat if factor_name == 'H' else pmat
                expected[offset + p] = {(offset + q, ()): matrix[p][q] + (Q(p == q) if factor_name != 'H' else 0)
                                        for q in ordinary if matrix[p][q] + (Q(p == q) if factor_name != 'H' else 0)}
            if factor_name == 'fused_inverse':
                for p in selected:
                    for q in ordinary:
                        replay.add(expected[p], identity[q], pmat[p][q])
            for i in range(8):
                expected[n + i] = {}
            need(actual == expected, 'Exact finite-query factor: ' + factor_name)
            price, scans = serial.price(events)
            need(not scans, 'All new factors are dyadic')
            receipt['factor_scalar_costs'][factor_name] = price
        need(receipt['factor_scalar_costs'] == {'H': 4800, 'H_inverse': 4944, 'fused_inverse': 6160}, 'Factor scalar invoices')
        swaps = serial.exchange(selected)
        def evaluate(direction, pre, post):
            physical = deepcopy(identity)
            for p in range(112):
                physical[p] = replay.line(physical[p], p, 1)
            physical = replay.boundary(pre + swaps, physical, n)
            logical = deepcopy(physical)
            for p in range(112):
                logical[p] = replay.line(logical[p], p, -1)
            logical, checks, warps = replay.core_replay(item['programs'][direction], logical, word, direction == 'backward')
            physical = deepcopy(logical)
            for p in range(112):
                physical[112 + p] = replay.line(physical[112 + p], p, -1)
            physical = replay.boundary(post, physical, n)
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
                replay.add(eb[p], replay.line(identity[q], q, 1), -jmat[p][q])
                replay.add(query, replay.line(identity[112 + q], q, -1), jmat[p][q])
            for q in ordinary:
                replay.add(eb[p], identity[112 + q], -jmat[p][q])
                replay.add(query, identity[q], jmat[p][q])
            replay.add(ef[p], replay.line(query, p, -1))
        for p in ordinary:
            eb[p] = {key: -c for key, c in identity[112 + p].items()}
            replay.add(ed[p], identity[112 + p], -1)
            ef[112 + p] = {}
            for q in ordinary:
                replay.add(eb[p], identity[q], Q(p == q) + pmat[p][q])
                replay.add(ef[112 + p], identity[q], jmat[p][q])
                replay.add(ef[112 + p], identity[112 + q], jmat[p][q])
            for q in selected:
                replay.add(eb[p], replay.line(identity[q], q, 1), pmat[p][q])
                replay.add(ef[112 + p], replay.line(identity[112 + q], q, -1), jmat[p][q])
        for p in range(112):
            for q in range(112):
                src = replay.line(identity[q], q, 1) if q in selected else identity[q]
                replay.add(ed[p], src, pmat[p][q])
        for expected in (eb, ed, ef):
            for p in range(n, n + 8):
                expected[p] = {}
        specs = {'balanced_backward': ('backward', [], bs, eb, 170446),
                 'diagonal_backward': ('backward', [], ds, ed, 171662),
                 'balanced_forward': ('forward', fs, swaps, ef, 171290)}
        programs, results = {}, {}
        for name, (direction, pre, post, expected, total) in specs.items():
            actual, physical, checks, warps = evaluate(direction, pre, post)
            need(actual == expected, 'All 640 ordered columns: ' + name)
            need(all(actual[p] == identity[p] for p in range(224, n)), 'All arbitrary helpers restored')
            need(all(not actual[p] for p in range(n, n + 8)), 'All owned outputs zero without extra cleanup')
            if direction == 'backward':
                need(all(physical[112 + p] == identity[p] for p in selected), 'Selected productive Y retains original X')
            native = item['programs'][direction]
            scalar, scans = serial.price(pre + swaps + post)
            scalar += replay.core_price(native)
            need(scalar == total and not scans, 'Complete scalar bill')
            profile = Counter(e[5] for e in native if e[0] == 'climb')
            need(dict(profile) == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'No extra native child')
            programs[name] = {'orientation': direction, 'prefix': pre, 'input_exchange': swaps,
                              'retained_core': native, 'suffix': post, 'owned_cleanup': [],
                              'events': pre + swaps + native + post}
            results[name] = {'scalar_real_primitives': scalar, 'native_rank_mass': 5073, 'native_children': 3507,
                             'native_profile': dict(sorted(profile.items())), 'all_input_columns': 640,
                             'arbitrary_helpers_restored': 408, 'private_zero_buffers_restored': 91,
                             'owned_private_final_zero': 8, 'owned_query_peak': 8,
                             'new_native_children': 0, 'new_private_fields': 0,
                             'core_scalar_frame_checks': checks, 'core_warp_events': warps}
            print(provider, name, scalar, 5073, flush=True)
        packet['providers'][provider] = {'canonical': word, 'programs': programs}
        receipt['providers'][provider] = results
    raw = (json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'IRREGULAR-38-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['source_pins'] = packet['source_pins']
    receipt['scope'] = 'Six complete local dyadic words. Eight existing owned queries. No global decoder, owner, precision, or supplier claim.'
    (HERE / 'IRREGULAR-38-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['payload_sha256'])


if __name__ == '__main__':
    main()
