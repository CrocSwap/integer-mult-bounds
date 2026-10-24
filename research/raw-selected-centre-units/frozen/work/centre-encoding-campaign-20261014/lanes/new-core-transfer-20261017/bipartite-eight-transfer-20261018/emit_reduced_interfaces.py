#!/usr/bin/env python3
"""Emit the eight-port interface and reduced exact backward normalizations."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANE = HERE.parent
LANES = LANE.parent
EIGHT = LANES / 'controller-followthrough-20261017/bipartite-eight-20261018'
STRUCTURED = LANES / 'controller-followthrough-20261017/structured-centres'
TRANSFER = LANE / 'structured-centres-transfer-20261018'
PINS = {
    'eight_freeze': 'c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1',
    'eight_payload': '0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee',
    'structured_payload': '2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1',
    'preceding_transfer_freeze': 'e0cd1e8a7c99e7aecf663e735e56a5b7e98b4bff4f696e6b0339463ccad4c280',
    'preceding_transfer_payload': 'ea140f936e4832d19db406bada5d4ab12ec6ea1dfc0d6e3e3a4c86991414ee2b',
    'scalar_tools': 'a174ac06bb5f0a2080698a2f7319c7d6ce15a2d04fbaa3ba34db9cf55f7f7ce2',
    'native_replay': 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, 'Input pin: ' + str(path))
    return json.loads(raw)


def module(name, path, pin):
    need(sha256(path.read_bytes()).hexdigest() == pin, 'Tool pin: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def decode(rows):
    return [{int(q): F(value) for q, value in row.items()} for row in rows]


def product(left, right):
    result = []
    for row in left:
        out = {}
        for q, value in row.items():
            r.add(out, right[q], value)
        result.append(out)
    return result


def inverse(matrix):
    size = len(matrix)
    rows = [[matrix[i].get(j, F(0)) for j in range(size)] + [F(i == j) for j in range(size)]
            for i in range(size)]
    for column in range(size):
        pivot = next(i for i in range(column, size) if rows[i][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        coefficient = rows[column][column]
        rows[column] = [value / coefficient for value in rows[column]]
        for i in range(size):
            if i != column and rows[i][column]:
                coefficient = rows[i][column]
                rows[i] = [a - coefficient * b for a, b in zip(rows[i], rows[column])]
    return [{j: value for j, value in enumerate(row[size:]) if value} for row in rows]


def identity_matrix():
    return [{p: F(1)} for p in range(112)]


def lift(matrix, ports):
    output = identity_matrix()
    for i, p in enumerate(ports):
        output[p] = {ports[j]: value for j, value in matrix[i].items()}
    return output


def bind(source, offset, frame):
    output = []
    for event in source:
        need(event[0] == 'scalar' and event[2] == 0, 'Scalar source frame')
        gate = event[1]
        need(gate[0] in ('add', 'scale'), 'No owned field or nonunit scalar operation')
        tokens = [token for token in gate[1:] if isinstance(token, list)]
        need(all(token[0] == 'L' and 0 <= token[1] < 112 for token in tokens), 'Data-only gauge')
        if gate[0] == 'add':
            output.append(u.scalar('add', offset + gate[1][1], offset + gate[2][1], F(*gate[3:5]), frame))
        else:
            output.append(u.scalar('scale', offset + gate[1][1], coefficient=F(*gate[2:4]), frame=frame))
    return output


def move(events, offset, frame):
    output = deepcopy(events)
    for event in output:
        event['frame'] = frame
        for key in ('target', 'source'):
            if key in event:
                need(0 <= event[key] < 112, 'Data-only Hadamard word')
                event[key] += offset
    return output


def boundary(events, state, n):
    start = 0
    for index, event in enumerate(events):
        if event['kind'] != 'clear':
            continue
        state = r.boundary(events[start:index], state, n)
        if index:
            need(not state[event['target']], 'Zero query before frame reset')
        state = r.boundary([event], state, n)
        start = index + 1
    return r.boundary(events[start:], state, n)


def apply_matrix(matrix, state, offset=0):
    output = deepcopy(state)
    for p, row in enumerate(matrix):
        output[offset + p] = {}
        for q, value in row.items():
            r.add(output[offset + p], state[offset + q], value)
    return output


def raw_expected(j, selected, identity, backward):
    output = deepcopy(identity)
    selected = set(selected)
    if backward:
        for p in range(112):
            if p in selected:
                output[p] = r.line(identity[112 + p], p, -1)
                output[112 + p] = r.line(identity[p], p, 1)
            for q, value in j[p].items():
                source = r.line(identity[q], q, 1) if q in selected else identity[112 + q]
                r.add(output[p], source, -value)
    else:
        for p in range(112):
            query = {}
            for q, value in j[p].items():
                source = r.line(identity[112 + q], q, -1) if q in selected else identity[q]
                r.add(query, source, value)
            if p in selected:
                r.add(output[p], r.line(query, p, -1))
            else:
                r.add(output[112 + p], query)
    return output


def selected_normalizer(j, selected):
    index = {p: i for i, p in enumerate(selected)}
    l = [{index[q]: value for q, value in j[p].items() if q in index} for p in selected]
    li = inverse(l)
    need(all(value.denominator & (value.denominator - 1) == 0 for row in li for value in row.values()), 'Dyadic selected inverse')
    need(product(l, li) == product(li, l) == [{i: F(1)} for i in range(len(selected))], 'Selected inverse orders')
    output = identity_matrix()
    for p in selected:
        output[p] = {selected[q]: -value for q, value in li[index[p]].items()}
    for p in range(112):
        if p in index:
            continue
        for q, value in j[p].items():
            if q in index:
                r.add(output[p], output[q], value)
    return output


def selected_query_normalizer(rows, selected, n):
    output = [u.scalar('clear', n, frame=1)]
    for row in rows:
        query = {p: value for p, value in row.items() if p in selected}
        ports = sorted(query)
        need(len(ports) == 6, 'Six selected query entries')
        output.append(u.scalar('copy', n, ports[0], frame=1))
        if query[ports[0]] == -1:
            output.append(u.scalar('scale', n, coefficient=F(-1), frame=1))
        output += [u.scalar('add', n, p, query[p], 1) for p in ports[1:]]
        output.append(u.scalar('scale', n, coefficient=F(1, 4), frame=1))
        output += [u.scalar('add', p, n, -value, 1) for p, value in sorted(row.items())]
        output.append(u.scalar('scale', n, coefficient=F(-2), frame=1))
        output += [u.scalar('add', n, p, -query[p], 1) for p in ports]
    output += [u.scalar('scale', p, coefficient=F(-1), frame=1) for p in sorted(selected)]
    output.append(u.scalar('clear', n, frame=0))
    need(u.price(output) == 1608, 'Selected-query normalized suffix price')
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out_dir.exists(), 'Use a new output directory')
    for directory, name, pin in ((EIGHT, 'FREEZE.json', PINS['eight_freeze']),
                                  (TRANSFER, 'FREEZE.json', PINS['preceding_transfer_freeze'])):
        freeze = read(directory / name, pin)
        for filename, value in freeze['artifacts'].items():
            need(sha256((directory / filename).read_bytes()).hexdigest() == value, 'Frozen dependency: ' + filename)
    eight = read(EIGHT / 'BIPARTITE-EIGHT-PROGRAM.json.gz', PINS['eight_payload'], True)
    structured = read(STRUCTURED / 'STRUCTURED-CENTRES-PROGRAM.json.gz', PINS['structured_payload'], True)
    preceding = read(TRANSFER / 'scaled-normal/STRUCTURED-TRANSFER-PROGRAMS.json.gz', PINS['preceding_transfer_payload'], True)
    packet = {'schema': 'reduced-native-selected-interfaces-v1', 'source_pins': PINS, 'families': {}}
    receipt = {'status': 'PASS_REDUCED_NATIVE_SELECTED_INTERFACES', 'source_pins': PINS, 'families': {}}
    for family_name in ('eight', 'twenty_four'):
        is_eight = family_name == 'eight'
        source = eight if is_eight else structured
        selected = source['selected_ports'] if is_eight else preceding['selected_S']
        ordinary = sorted(set(range(112)) - set(selected))
        j = decode(source['response'])
        if not is_eight:
            j = [{q: -value for q, value in row.items()} for row in j]
        normalizer = selected_normalizer(j, selected)
        family = {'selected_S': selected, 'ordinary_U': ordinary, 'providers': {}}
        reports = {}
        for provider, source_item in source['providers'].items():
            old = preceding['providers'][provider]
            word, n = source_item['canonical'], len(source_item['canonical']['start'])
            need(word == old['canonical'] and n == 632 and len(word['zero_buffers']) == 91, 'Exact retained geometry and resources')
            need(word['start'][112:224] == [0] * 112 and word['final'][:112] == [1] * 112, 'Boundary frames')
            native = source_item['programs'] if is_eight else {
                direction: old['programs']['raw_' + direction]['retained_core'] for direction in ('forward', 'backward')}
            for direction in native:
                records = lambda events: [event for event in events if event[0] in ('climb', 'warp', 'adapter', 'residual_adapter')]
                need(records(native[direction]) == records(old['programs']['raw_' + direction]['retained_core']), 'Identical native phase records')
                need(r.core_price(native[direction]) == 87360, 'Native scalar price')
            identity = {p: {(p, ()): F(1)} for p in range(n + 8)}
            raw_b = raw_expected(j, selected, identity, True)
            normalized = apply_matrix(normalizer, raw_b)
            if is_eight:
                centre_u, large, small = source['ordinary_centre_ports'], source['large_ports'], source['small_ports']
                gauges = source['gauge_programs']
                h64 = old['gauge_words']['hadamard_X']
                hi64 = old['gauge_words']['hadamard_inverse_X']
                h, hi = lift(decode(source['gauge_maps']['ordinary']), centre_u), lift(decode(source['gauge_maps']['ordinary_inverse']), centre_u)
                data, data_inverse = lift(decode(source['gauge_maps']['data']), large), lift(decode(source['gauge_maps']['data_inverse']), large)
                for p in small:
                    h[p] = dict(j[p])
                    hi[p] = {q: value / 4 for q, value in j[p].items()}
                    data[p], data_inverse[p] = dict(hi[p]), dict(h[p])
                need(product(h, hi) == product(hi, h) == identity_matrix(), 'Complete ordinary inverse orders')
                need(product(data, data_inverse) == product(data_inverse, data) == identity_matrix(), 'Complete data inverse orders')
                pre = bind(gauges['ordinary'], 112, 0) + move(h64, 112, 0)
                post_h = bind(gauges['ordinary_inverse'], 0, 1) + hi64
                upper = [u.scalar('add', p, q, -value, 1) for p in selected for q, value in sorted(j[p].items()) if q in ordinary]
                lower = [u.scalar('add', p, q, value, 1) for p in ordinary for q, value in sorted(j[p].items()) if q in selected]
                selected_source = [event for event in gauges['data']
                                   if all(token[1] in selected for token in event[1][1:] if isinstance(token, list))]
                selected_word = bind(selected_source, 0, 1)
                negative_lower = [dict(event, coefficient=str(-F(event['coefficient']))) for event in lower]
                need(bind(gauges['data'], 0, 1) == negative_lower + selected_word + bind(gauges['ordinary_inverse'], 0, 1) + upper,
                     'Literal source data factorization')
                selected_inverse = u.inverse_word(selected_word)
                short_post = selected_inverse + lower
                long_post = post_h + upper + bind(gauges['data_inverse'], 0, 1) + h64
                need(u.price(selected_inverse) == 192 and u.price(lower) == u.price(upper) == 1440, 'Selected and shear prices')
                balanced_b = apply_matrix(hi, raw_b)
                diagonal_b = deepcopy(identity)
                for p in range(112):
                    diagonal_b[p] = {}
                    for q, value in data[p].items():
                        src = r.line(identity[q], q, 1) if q in selected else identity[q]
                        r.add(diagonal_b[p], src, value)
                    if p in selected:
                        r.add(diagonal_b[p], r.line(identity[112 + p], p, -1))
                        diagonal_b[112 + p] = r.line(identity[p], p, 1)
                    else:
                        r.add(diagonal_b[p], identity[112 + p], -1)
                need(apply_matrix(data_inverse, diagonal_b) == normalized, 'Complete short and long map identity')
                raw_f = raw_expected(j, selected, identity, False)
                balanced_f = deepcopy(raw_f)
                for p in ordinary:
                    balanced_f[112 + p] = {}
                    for q, value in h[p].items():
                        r.add(balanced_f[112 + p], identity[q], value)
                        r.add(balanced_f[112 + p], identity[112 + q], value)
                    for q, value in j[p].items():
                        if q in selected:
                            r.add(balanced_f[112 + p], r.line(identity[112 + q], q, -1), value)
                for events, matrix, offset in ((pre, h, 112), (post_h, hi, 0)):
                    need(boundary(events, identity, n) == apply_matrix(matrix, identity, offset), 'Actual complete ordinary gauge')
                specs = {
                    'raw_backward': ('backward', [], [], raw_b, 87568),
                    'balanced_backward': ('backward', [], post_h, balanced_b, 91264),
                    'diagonal_backward': ('backward', [], post_h + upper, diagonal_b, 92704),
                    'long_normalized_backward': ('backward', [], long_post, normalized, 99472),
                    'short_normalized_backward': ('backward', [], short_post, normalized, 89200),
                    'raw_forward': ('forward', [], u.exchange(selected, 1), raw_f, 87776),
                    'balanced_forward': ('forward', pre, u.exchange(selected, 1), balanced_f, 91472),
                }
                local_words = {'ordinary_Y': pre, 'ordinary_inverse_X': post_h, 'selected_inverse_X': selected_inverse,
                               'upper_X': upper, 'lower_X': lower, 'short_normalizer_X': short_post,
                               'long_normalizer_X': long_post}
            else:
                rows = decode(source['centre_rows'])
                short_post = selected_query_normalizer(rows, selected, n)
                long_post = old['programs']['normalized_backward']['suffix']
                specs = {
                    'long_normalized_backward': ('backward', [], long_post, normalized, 96012),
                    'short_normalized_backward': ('backward', [], short_post, normalized, 89592),
                }
                local_words = {'short_normalizer_X': short_post, 'long_normalizer_X': long_post}
            for name, events in local_words.items():
                u.check_frames(events, 0 if name == 'ordinary_Y' else 1, n)
            expected_suffix = apply_matrix(normalizer, identity)
            if not is_eight:
                expected_suffix[n] = {}
            need(boundary(short_post, identity, n) == expected_suffix, 'Exact short scalar normalizer on all columns')
            need(boundary(short_post, identity, n) == boundary(long_post, identity, n), 'Literal short/long suffix equality')
            input_swap = u.exchange(selected, 0)
            actual_maps, programs, results = {}, {}, {}
            for name, (direction, pre, post, expected, total) in specs.items():
                expected = deepcopy(expected)
                for p in range(n, n + 8):
                    expected[p] = {}
                physical = deepcopy(identity)
                for p in range(112):
                    physical[p] = r.line(physical[p], p, 1)
                physical = boundary(pre + input_swap, physical, n)
                logical = deepcopy(physical)
                for p in range(112):
                    logical[p] = r.line(logical[p], p, -1)
                logical, checks, warps = r.core_replay(native[direction], logical, word, direction == 'backward')
                physical = deepcopy(logical)
                for p in range(112):
                    physical[112 + p] = r.line(physical[112 + p], p, -1)
                physical = boundary(post, physical, n)
                actual = deepcopy(physical)
                for p in range(112):
                    actual[112 + p] = r.line(actual[112 + p], p, 1)
                need(actual == expected, 'All640 ordered columns: ' + family_name + ' ' + provider + ' ' + name)
                need(all(actual[p] == identity[p] for p in range(224, n)), 'Arbitrary helpers restored')
                need(all(not actual[p] for p in range(n, n + 8)), 'All owned fields zero')
                if direction == 'backward':
                    need(all(physical[112 + p] == identity[p] for p in selected), 'Physical selected Y source')
                if 'normalized' in name:
                    for p in range(112):
                        part = {key: value for key, value in actual[p].items() if key[0] < 112}
                        need(part == (r.line(identity[p], p, 1) if p in selected else identity[p]), 'Normalized original-X response')
                bill = r.core_price(native[direction]) + u.price(pre + input_swap + post)
                need(bill == total, 'Complete scalar invoice')
                profile = Counter(event[5] for event in native[direction] if event[0] == 'climb')
                need(dict(profile) == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'Retained native profile')
                programs[name] = {'orientation': direction, 'prefix': pre, 'input_exchange': input_swap,
                                  'retained_core': native[direction], 'suffix': post,
                                  'events': pre + input_swap + native[direction] + post}
                results[name] = {'scalar_real_primitives': bill, 'native_rank_mass': 5073, 'native_children': 3507,
                                 'new_native_children': 0, 'new_private_fields': 0, 'native_profile': dict(sorted(profile.items())),
                                 'all_input_columns': 640, 'arbitrary_helpers_restored': 408,
                                 'private_zero_buffers_restored': 91, 'owned_final_zero': 8,
                                 'core_scalar_frame_checks': checks, 'core_warp_events': warps}
                actual_maps[name] = actual
                print(family_name, provider, name, bill, flush=True)
            need(actual_maps['short_normalized_backward'] == actual_maps['long_normalized_backward'], 'Complete native path equality')
            family['providers'][provider] = {'canonical': word, 'local_words': local_words, 'programs': programs}
            reports[provider] = {'programs': results, 'local_word_prices': {name: u.price(events) for name, events in local_words.items()},
                                 'complete_normalized_paths_equal': True, 'same_native_phase_records': True}
        packet['families'][family_name], receipt['families'][family_name] = family, reports
    raw = (json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n').encode()
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = ('Complete local physical interfaces and equal short/long normalization paths. '
                        'All Q operators remain ordered. Inter-call transport, exterior phase, hosting, '
                        'recursive precision and the complete supplier invoice remain separate.')
    args.out_dir.mkdir(parents=True)
    (args.out_dir / 'REDUCED-INTERFACES-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (args.out_dir / 'REDUCED-INTERFACES-RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], receipt['payload_decompressed_sha256'], flush=True)


if __name__ == '__main__':
    r = module('reduced_native_replay', LANE / 'emit_raw_selected.py', PINS['native_replay'])
    u = module('reduced_scalar_tools', TRANSFER / 'emit_structured_transfer.py', PINS['scalar_tools'])
    main()
