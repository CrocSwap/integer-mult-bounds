#!/usr/bin/env python3
"""Place both irregular response-unit maps at the actual full boundary."""

from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CORE_PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'
WORDS_PIN = 'bd980a32b56768ee8e6454a789d4d53c805154a062e0d437373a0acc726dd801'
RAW_PIN = 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc'
SERIAL_PIN = '7399a1d153197faae5f44f04e0ae3675a6c961d343329419c0c71bdc263bb9d6'
WITNESS_PIN = '0a8d22fa0b523c261243e9b19cfd51926c9b515a9e6f9a962d1e3b5170105a8f'


def read_gzip(name, pin):
    raw = gzip.decompress((HERE / name).read_bytes())
    assert sha256(raw).hexdigest() == pin
    return json.loads(raw)


def module(name, filename, pin):
    path = HERE / filename
    assert sha256(path.read_bytes()).hexdigest() == pin
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def product(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in columns] for row in a]


def add(t, s, c):
    assert t != s and c
    return {'kind': 'add', 'target': t, 'source': s, 'coefficient': str(c), 'frame': 1}


def main():
    replay = module('irregular_unit_raw', 'emit_raw_selected.py', RAW_PIN)
    serial = module('irregular_unit_serial', 'emit_serial_balanced.py', SERIAL_PIN)
    core = read_gzip('CLEAN-J-PROGRAMS.json.gz', CORE_PIN)
    words = read_gzip('IRREGULAR-38-PROGRAMS.json.gz', WORDS_PIN)
    raw = (HERE.parent.parent / 'root/IRREGULAR-SPLIT-20261017.json').read_bytes()
    assert sha256(raw).hexdigest() == WITNESS_PIN
    witness = json.loads(raw)
    selected = set(words['selected_S'])
    r = [{int(p): Q(c) for p, c in row.items()} for row in core['R']]
    dense_r = [[row.get(p, Q(0)) for p in range(112)] for row in r]
    k = [[dense_r[j][p] / 4 for j in range(8)] for p in range(112)]
    signs = [-1 if p in selected else 1 for p in range(112)]
    ti = [[Q(c) for c in row] for row in witness['T_inverse']]
    wi = [[Q(c) for c in row] for row in witness['I_minus_D_inverse']]
    ktir, kwir = product(product(k, ti), dense_r), product(product(k, wi), dense_r)
    a = [[signs[p] * Q(p == q) + ktir[p][q] for q in range(112)] for p in range(112)]
    inv = [[signs[p] * Q(p == q) - signs[p] * kwir[p][q] * signs[q] for q in range(112)] for p in range(112)]
    programs, costs = {}, {}
    n = 632
    sign_word = [{'kind': 'scale', 'target': p, 'coefficient': '-1', 'frame': 1} for p in sorted(selected)]
    for inverse in (False, True):
        events = [{'kind': 'clear', 'target': n + i, 'frame': 1} for i in range(8)]
        for i, row in enumerate(r):
            events += [add(n + i, p, c) for p, c in sorted(row.items())]
        for t, s in ((0, 2), (0, 3), (1, 4), (1, 5)):
            events.append(add(n + t, n + s, Q(1, 2) if inverse else Q(-1, 4)))
        if inverse:
            events += [{'kind': 'scale', 'target': n + i,
                        'coefficient': str(Q(1, 4) if i < 2 else Q(1, 16)), 'frame': 1} for i in range(8)]
        for t, s in ((2, 0), (3, 0), (4, 1), (5, 1)):
            events.append(add(n + t, n + s, Q(1, 2) if inverse else Q(-1, 4)))
        if not inverse:
            events += [{'kind': 'scale', 'target': n + i, 'coefficient': '1/32', 'frame': 1} for i in range(8)]
        for i, row in enumerate(r):
            events += [add(p, n + i, (1 if inverse else -1) * signs[p] * c) for p, c in sorted(row.items())]
        events += [{'kind': 'clear', 'target': n + i, 'frame': 0} for i in range(8)]
        name = 'inverse_A' if inverse else 'A'
        programs[name] = sign_word + events if inverse else events + sign_word
        cost, scans = serial.price(programs[name])
        assert scans == 0
        costs[name] = cost
    assert costs == {'A': 7452, 'inverse_A': 7412}
    receipt = {'status': 'PASS_FULL_BOUNDARY_IRREGULAR_38_RESPONSE_UNIT',
               'scalar_real_primitives': costs, 'existing_owned_query_peak': 8,
               'new_private_fields': 0, 'new_native_children': 0, 'providers': {}}
    for provider, item in words['providers'].items():
        word = item['canonical']
        assert word['final'][:112] == [1] * 112 and len(word['final']) == n
        identity = {p: {(p, ()): Q(1)} for p in range(n + 8)}
        for name, matrix in (('A', a), ('inverse_A', inv)):
            frames = {p: f for p, f in enumerate(word['final'])}
            frames.update({n + i: 0 for i in range(8)})
            for e in programs[name]:
                t, f = e['target'], e['frame']
                if e['kind'] == 'clear':
                    assert n <= t < n + 8
                    frames[t] = f
                else:
                    assert frames[t] == f == 1
                    if e['kind'] == 'add':
                        assert frames[e['source']] == f and e['source'] != t
                        assert n <= t < n + 8 or n <= e['source'] < n + 8
                    else:
                        assert e['kind'] == 'scale' and (n <= t < n + 8 or t in selected)
            assert all(frames[n + i] == 0 for i in range(8))
            actual = replay.boundary(programs[name], identity, n)
            expected = deepcopy(identity)
            for p, row in enumerate(matrix):
                expected[p] = {(q, ()): c for q, c in enumerate(row) if c}
            for p in range(n, n + 8):
                expected[p] = {}
            assert actual == expected
        expected = deepcopy(identity)
        for p in range(n, n + 8):
            expected[p] = {}
        for first, second in (('A', 'inverse_A'), ('inverse_A', 'A')):
            assert replay.boundary(programs[first] + programs[second], identity, n) == expected
        receipt['providers'][provider] = {'all_input_columns': 640, 'both_literal_inverse_orders': True,
                                           'arbitrary_helpers_unchanged': 408, 'all_owned_queries_zero_at_I': 8}
    packet = {'schema': 'pr3133-irregular-38-full-response-unit-v1',
              'source_pins': {'core': CORE_PIN, 'native_words': WORDS_PIN, 'witness': WITNESS_PIN,
                              'raw_replay': RAW_PIN, 'serial_utility': SERIAL_PIN},
              'selected_S': sorted(selected), 'programs': programs, 'scalar_real_primitives': costs}
    raw = (json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (HERE / 'IRREGULAR-38-RESPONSE-UNIT.json').write_bytes(raw)
    receipt['payload_sha256'] = sha256(raw).hexdigest()
    receipt['source_pins'] = packet['source_pins']
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = 'Completed-FULL-X response unit. No partial-view decoder or complete supplier claim.'
    (HERE / 'IRREGULAR-38-UNIT-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], costs)


if __name__ == '__main__':
    main()
