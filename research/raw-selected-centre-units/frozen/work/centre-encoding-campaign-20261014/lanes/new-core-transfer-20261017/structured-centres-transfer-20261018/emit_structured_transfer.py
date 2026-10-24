#!/usr/bin/env python3
"""Bind the structured response to physical selected-port interfaces."""

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
SOURCE = LANE.parent / 'controller-followthrough-20261017' / 'structured-centres'
PINS = {
    'source_freeze': '5e762396d55ac47b34bbe60e30c62a429ddd6fc1f018cb4b4b94d3670d374a19',
    'source_payload': '2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1',
    'source_gauges': '27eb7e2d72fd5c06bb330f1ec6104cd85ae938a55d36aaf8e2e5e94e17c00930',
    'source_receipt': '7e3d19e85522d76c0e9d1375346474c8d5302382e111dbd53a2108ab01f0a0cc',
    'native_replay': 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc',
}
SCALED_GAUGE_FREEZE = 'deea4844f2327a73129c213df915819ec845fb9c97a30498d43f231a2267e733'
SCALED_GAUGE_PIN = '6b2e61547261ef28c8f08a29bc0cf5f681fe44ab6676e9530cc411c35d36a65c'


def need(condition, label):
    if not condition:
        raise ValueError(label)


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, 'Pinned input: ' + str(path))
    return json.loads(raw)


def scalar(kind, target, source=None, coefficient=None, frame=0):
    event = {'kind': kind, 'target': target, 'frame': frame}
    if source is not None:
        event['source'] = source
    if coefficient is not None:
        event['coefficient'] = str(coefficient)
    return event


def swap(left, right, frame):
    return [scalar('add', left, right, F(1), frame),
            scalar('add', right, left, F(-1), frame),
            scalar('add', left, right, F(1), frame),
            scalar('scale', right, coefficient=F(-1), frame=frame)]


def exchange(selected, frame):
    return [event for port in selected for event in swap(port, 112 + port, frame)]


def inverse_word(events):
    output = []
    for event in reversed(events):
        event = dict(event)
        coefficient = F(event['coefficient'])
        need(event['kind'] in ('add', 'scale'), 'Invertible scalar word')
        event['coefficient'] = str(-coefficient if event['kind'] == 'add' else 1 / coefficient)
        output.append(event)
    return output


def price(events):
    result = 0
    for event in events:
        if event['kind'] in ('copy', 'clear'):
            result += 2
            continue
        coefficient = F(event['coefficient'])
        numerator, denominator = abs(coefficient.numerator), coefficient.denominator
        need(numerator > 0 and denominator & (denominator - 1) == 0, 'Dyadic scalar')
        if event['kind'] == 'scale':
            need(numerator & (numerator - 1) == 0, 'Dyadic unit scale')
            result += 2 * (abs(numerator.bit_length() - denominator.bit_length()) + (coefficient < 0))
        else:
            need(event['kind'] == 'add', 'Known scalar price')
            result += 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1)
    return result


def product(left, right):
    output = []
    for row in left:
        result = {}
        for index, coefficient in row.items():
            replay.add(result, right[index], coefficient)
        output.append(result)
    return output


def signed_hadamard(ports, frame):
    output = []
    for (a, b), sign in zip(((0, 1), (2, 3), (0, 2), (1, 3)), (-1, 1, -1, 1)):
        left, right = ports[a], ports[b]
        output += [scalar('add', left, right, F(sign), frame),
                   scalar('scale', right, coefficient=F(2), frame=frame),
                   scalar('add', right, left, F(-sign), frame)]
    output += [scalar('scale', ports[i], coefficient=F(-1), frame=frame) for i in (1, 2)]
    need(price(output) == 76, 'Four-point Hadamard price')
    return output


def hadamard64(response, ports, offset, frame):
    groups = {tuple(sorted(response[p])) for p in ports}
    need(len(groups) == 16 and all(len(group) == 4 for group in groups), 'Sixteen four-port groups')
    remaining, pairs, output = set(ports), [], []
    permutation = (0, 2, 1, 3)
    while remaining:
        first = min(remaining)
        right_set = set(response[first])
        left = sorted(response[min(right_set)])
        need(first in left and set(left).isdisjoint(right_set), 'Paired Hadamard groups')
        right = [None] * 4
        for index, p in enumerate(left):
            need(set(response[p]) == right_set, 'Common four-port support')
            negative = [q for q, value in response[p].items() if value == -1]
            need(len(negative) == 1 and all(abs(value) == 1 for value in response[p].values()), 'Signed Hadamard row')
            right[permutation[index]] = negative[0]
        need(set(right) == right_set, 'Physical partner ordering')
        pairs.append({'left': left, 'right': right})
        for group in (left, right):
            output += signed_hadamard([offset + p for p in group], frame)
        for a, b in zip(left, right):
            output += swap(offset + a, offset + b, frame)
        remaining -= set(left) | set(right)
    need(len(pairs) == 8 and price(output) == 2048, 'Full priced Hadamard factor')
    return output, pairs


def bind_gauge(source, offset, frame, n, extra_upper=None):
    output = [scalar('clear', n, frame=frame)]
    segments = []
    for event in source:
        need(event[0] == 'scalar' and event[2] == 0, 'Pinned common-frame gauge')
        gate = event[1]
        if gate[0] == 'copy':
            segments.append([])
        need(segments, 'Gauge starts with owned COPY')
        segments[-1].append(gate)
    if extra_upper is not None:
        need(len(segments) == 8, 'Eight serial query rows')
    for index, segment in enumerate(segments):
        last_scatter = max((position for position, gate in enumerate(segment)
                            if gate[0] == 'add' and gate[1][0] == 'L' and gate[2] == ['C', 0]), default=-1)
        for position, gate in enumerate(segment):
            def slot(token):
                need(token[0] == 'L' or token == ['C', 0], 'Gauge operand namespace')
                return offset + token[1] if token[0] == 'L' else n
            kind, target = gate[0], slot(gate[1])
            if kind == 'scale':
                output.append(scalar(kind, target, coefficient=F(*gate[2:4]), frame=frame))
            else:
                output.append(scalar(kind, target, slot(gate[2]), F(*gate[3:5]) if kind == 'add' else None, frame))
            if position == last_scatter and extra_upper is not None:
                scatter_scale = abs(F(*gate[3:5]))
                output += [scalar('add', offset + p, n, -value * scatter_scale, frame)
                           for p, value in sorted(extra_upper[index].items())]
    if frame:
        output.append(scalar('clear', n, frame=0))
    return output


def bind_data_gauge(source, frame, n):
    output = [scalar('clear', n, frame=frame)]
    for event in source:
        need(event[0] == 'scalar' and event[2] == 0, 'Pinned data gauge frame')
        gate = event[1]
        def slot(token):
            need(token[0] == 'L' or token == ['C', 0], 'Data gauge namespace')
            return token[1] if token[0] == 'L' else n
        if gate[0] == 'scale':
            output.append(scalar('scale', slot(gate[1]), coefficient=F(*gate[2:4]), frame=frame))
        else:
            output.append(scalar(gate[0], slot(gate[1]), slot(gate[2]),
                                 F(*gate[3:5]) if gate[0] == 'add' else None, frame))
    if frame:
        output.append(scalar('clear', n, frame=0))
    return output


def check_frames(events, frame, n):
    frames = {p: frame for p in range(224)} | {n + p: 0 for p in range(8)}
    for event in events:
        target, declared = event['target'], event['frame']
        if event['kind'] == 'clear':
            need(target == n, 'Only owned C0 admission or frame reset')
            frames[target] = declared
        else:
            need(frames[target] == declared == frame, 'Physical target frame')
            if 'source' in event:
                source = event['source']
                need(source != target and frames[source] == declared, 'Physical source frame')
    need(all(frames[n + p] == 0 for p in range(8)), 'Owned endpoint frames')


def boundary(events, state, n):
    start = 0
    for index, event in enumerate(events):
        if event['kind'] != 'clear':
            continue
        state = replay.boundary(events[start:index], state, n)
        if index:
            need(not state[event['target']], 'The query is zero before each later frame reset')
        state = replay.boundary([event], state, n)
        start = index + 1
    return replay.boundary(events[start:], state, n)


def negate_core(item):
    original = item['programs']
    output = deepcopy(original)
    need(len(original['forward']) == len(original['backward']), 'Paired native event indexing')
    sites = []
    for index, event in enumerate(original['forward']):
        if event[0] != 'scalar' or event[1][0] != 'add':
            continue
        target, source = event[1][1:3]
        is_y = lambda token: token[0] == 'L' and 112 <= token[1] < 224
        if is_y(target) and not is_y(source):
            need(original['backward'][index][1][1:3] == [source, target], 'Literal transposed transfer site')
            sites.append(index)
            for direction in ('forward', 'backward'):
                output[direction][index][1][3] *= -1
    need(len(sites) == 184, 'All structured scalar transfer sites')
    for direction in output:
        need([event for event in output[direction] if event[0] != 'scalar'] ==
             [event for event in original[direction] if event[0] != 'scalar'], 'Unchanged native records')
        need(replay.core_price(output[direction]) == 87360, 'Unchanged core scalar bill')
    return output, sites


def apply_matrix(matrix, state, offset=0):
    output = deepcopy(state)
    for p, row in enumerate(matrix):
        output[offset + p] = {}
        for q, coefficient in row.items():
            replay.add(output[offset + p], state[offset + q], coefficient)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--gauges', choices=('original', 'scaled'), default='original')
    options = parser.parse_args()
    need(not options.out_dir.exists(), 'Use a new output directory')
    freeze = read(SOURCE / 'FREEZE.json', PINS['source_freeze'])
    for name, pin in freeze['artifacts'].items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, 'Frozen source artifact: ' + name)
    core = read(SOURCE / 'STRUCTURED-CENTRES-PROGRAM.json.gz', PINS['source_payload'], True)
    gauge_source = read(SOURCE / 'RANK8-GAUGES.json', PINS['source_gauges'])
    source_receipt = read(SOURCE / 'STRUCTURED-CENTRES.json', PINS['source_receipt'])
    pins = dict(PINS)
    if options.gauges == 'scaled':
        gauge_freeze = read(SOURCE / 'GAUGES-V2-FREEZE.json', SCALED_GAUGE_FREEZE)
        for name, pin in gauge_freeze['artifacts'].items():
            need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, 'Frozen scaled gauge: ' + name)
        gauge_source = read(SOURCE / 'RANK8-GAUGES-V2.json', SCALED_GAUGE_PIN)
        pins['preceding_gauges'] = pins['source_gauges']
        pins['source_gauges'] = SCALED_GAUGE_PIN
        pins['scaled_gauge_freeze'] = SCALED_GAUGE_FREEZE
    response = [{int(q): F(value) for q, value in row.items()} for row in core['response']]
    rows = [{int(q): F(value) for q, value in row.items()} for row in core['centre_rows']]
    selected = sorted(source_receipt['gauge_identities']['3']['selected_ports'])
    centre_ports = sorted(source_receipt['centre_support_ports'])
    centre_ordinary = sorted(set(centre_ports) - set(selected))
    hadamard_ports = sorted(set(range(112)) - set(centre_ports))
    ordinary = sorted(set(range(112)) - set(selected))
    need(len(selected) == 24 and len(ordinary) == 88 and len(hadamard_ports) == 64, 'Actual physical split')
    need(selected == sorted(p for minor in source_receipt['orthogonal_minor_ports'][:3] for p in minor), 'First three complete minors')
    identity_matrix = [{p: F(1)} for p in range(112)]
    j = [{q: -value for q, value in row.items()} for row in response]
    outer = [{} for _ in range(112)]
    for row in rows:
        for p, value in row.items():
            replay.add(outer[p], row, value)
    h, hi, data, data_inverse = [deepcopy(identity_matrix) for _ in range(4)]
    for p in ordinary:
        h[p] = {q: value for q, value in j[p].items() if q in ordinary}
    for p in centre_ordinary:
        replay.add(hi[p], {q: value for q, value in outer[p].items() if q in centre_ordinary}, F(-1, 4))
    for p in hadamard_ports:
        hi[p] = {q: -value / 4 for q, value in response[p].items()}
        data[p], data_inverse[p] = dict(hi[p]), dict(j[p])
    signs = {p: F(-1) if p in selected else F(1) for p in range(112)}
    for p in centre_ports:
        data[p] = {p: signs[p]}
        replay.add(data[p], outer[p], F(-1, 4))
        data_inverse[p] = {p: signs[p]}
        replay.add(data_inverse[p], {q: value * signs[q] for q, value in outer[p].items()}, signs[p] / 4)
    need(product(h, hi) == product(hi, h) == identity_matrix, 'Both complete ordinary inverse orders')
    need(product(data, data_inverse) == product(data_inverse, data) == identity_matrix, 'Both complete data inverse orders')

    packet = {'schema': 'structured-centres-physical-transfer-v1', 'source_pins': pins,
              'selected_S': selected, 'ordinary_U': ordinary, 'centre_ordinary': centre_ordinary,
              'hadamard_ports': hadamard_ports, 'providers': {}}
    receipt = {'status': 'PASS_STRUCTURED_CENTRES_PHYSICAL_TRANSFER', 'source_pins': pins,
               'selected_ports': 24, 'ordinary_ports': 88, 'providers': {}}
    for provider, item in core['providers'].items():
        word, n = item['canonical'], len(item['canonical']['start'])
        need(n == 632 and len(word['zero_buffers']) == 91, 'Actual provider resources')
        need(word['start'][112:224] == [0] * 112 and word['final'][:112] == [1] * 112, 'Physical gauge endpoints')
        native, sites = negate_core(item)
        identity = {p: {(p, ()): F(1)} for p in range(n + 8)}
        h64_x, pairs = hadamard64(response, hadamard_ports, 0, 1)
        hi64_x = inverse_word(h64_x)
        h64_y, other_pairs = hadamard64(response, hadamard_ports, 112, 0)
        need(pairs == other_pairs and price(hi64_x) == 2048, 'Same Hadamard pairs and inverse bill')
        prefix = bind_gauge(gauge_source['programs']['ordinary'], 112, 0, n) + h64_y
        backward = bind_gauge(gauge_source['programs']['ordinary_inverse'], 0, 1, n) + hi64_x
        selected_rows = [{p: value for p, value in row.items() if p in selected} for row in rows]
        diagonal = bind_gauge(gauge_source['programs']['ordinary_inverse'], 0, 1, n, selected_rows) + hi64_x
        full_data = bind_data_gauge(gauge_source['programs']['data'], 1, n) + hi64_x
        full_inverse = bind_data_gauge(gauge_source['programs']['data_inverse'], 1, n) + h64_x
        gauge_words = {'ordinary_Y': prefix, 'ordinary_inverse_X': backward,
                       'fused_inverse_X': diagonal, 'data_X': full_data, 'data_inverse_X': full_inverse,
                       'hadamard_X': h64_x, 'hadamard_inverse_X': hi64_x}
        for name, events in gauge_words.items():
            check_frames(events, 0 if name == 'ordinary_Y' else 1, n)
        for events, matrix, offset in ((prefix, h, 112), (backward, hi, 0),
                                       (full_data, data, 0), (full_inverse, data_inverse, 0)):
            actual = boundary(events, identity, n)
            expected = apply_matrix(matrix, identity, offset)
            expected[n] = {}
            need(actual == expected, 'All scalar gauge columns')
        for first, second in ((h64_x, hi64_x), (hi64_x, h64_x)):
            need(boundary(first + second, identity, n) == identity, 'Both literal Hadamard inverse orders')
        zero_c0 = deepcopy(identity)
        zero_c0[n] = {}
        for first, second in ((full_data, full_inverse), (full_inverse, full_data)):
            need(boundary(first + second, identity, n) == zero_c0, 'Both literal full-data inverse orders')
        input_swap, output_swap = exchange(selected, 0), exchange(selected, 1)
        need(price(input_swap) == price(output_swap) == 624, 'All selected exchanges priced')
        check_frames(input_swap, 0, n)
        check_frames(output_swap, 1, n)

        def evaluate(direction, pre, post):
            physical = deepcopy(identity)
            for p in range(112):
                physical[p] = replay.line(physical[p], p, 1)
            physical = boundary(pre + input_swap, physical, n)
            logical = deepcopy(physical)
            for p in range(112):
                logical[p] = replay.line(logical[p], p, -1)
            logical, checks, warps = replay.core_replay(native[direction], logical, word, direction == 'backward')
            physical = deepcopy(logical)
            for p in range(112):
                physical[112 + p] = replay.line(physical[112 + p], p, -1)
            physical = boundary(post, physical, n)
            logical = deepcopy(physical)
            for p in range(112):
                logical[112 + p] = replay.line(logical[112 + p], p, 1)
            return logical, physical, checks, warps

        raw_b, raw_f, balanced_b, balanced_f = [deepcopy(identity) for _ in range(4)]
        for p in selected:
            raw_b[p] = replay.line(identity[112 + p], p, -1)
            raw_b[112 + p] = replay.line(identity[p], p, 1)
            balanced_b[p], balanced_b[112 + p] = deepcopy(raw_b[p]), deepcopy(raw_b[112 + p])
            query = {}
            for q, coefficient in j[p].items():
                source = replay.line(identity[q], q, 1) if q in selected else identity[112 + q]
                replay.add(raw_b[p], source, -coefficient)
                replay.add(balanced_b[p], source, -coefficient)
                source = replay.line(identity[112 + q], q, -1) if q in selected else identity[q]
                replay.add(query, source, coefficient)
            replay.add(raw_f[p], replay.line(query, p, -1))
            replay.add(balanced_f[p], replay.line(query, p, -1))
        for p in ordinary:
            for q, coefficient in j[p].items():
                source = replay.line(identity[q], q, 1) if q in selected else identity[112 + q]
                replay.add(raw_b[p], source, -coefficient)
                source = replay.line(identity[112 + q], q, -1) if q in selected else identity[q]
                replay.add(raw_f[112 + p], source, coefficient)
            balanced_b[p] = {key: -value for key, value in identity[112 + p].items()}
            balanced_f[112 + p] = {}
            for q, coefficient in hi[p].items():
                replay.add(balanced_b[p], identity[q], coefficient)
                for a, value in j[q].items():
                    if a in selected:
                        replay.add(balanced_b[p], replay.line(identity[a], a, 1), -coefficient * value)
            for q, coefficient in h[p].items():
                replay.add(balanced_f[112 + p], identity[q], coefficient)
                replay.add(balanced_f[112 + p], identity[112 + q], coefficient)
            for q, coefficient in j[p].items():
                if q in selected:
                    replay.add(balanced_f[112 + p], replay.line(identity[112 + q], q, -1), coefficient)
        diagonal_b = deepcopy(identity)
        for p in range(112):
            diagonal_b[p] = {}
            for q, coefficient in data[p].items():
                source = replay.line(identity[q], q, 1) if q in selected else identity[q]
                replay.add(diagonal_b[p], source, coefficient)
            if p in selected:
                replay.add(diagonal_b[p], replay.line(identity[112 + p], p, -1))
                diagonal_b[112 + p] = replay.line(identity[p], p, 1)
            else:
                replay.add(diagonal_b[p], identity[112 + p], -1)
        normalized_b = apply_matrix(data_inverse, diagonal_b)
        for expected in (raw_b, raw_f, balanced_b, balanced_f, diagonal_b, normalized_b):
            for p in range(n, n + 8):
                expected[p] = {}
        totals = (91368, 91944, 96684, 91894) if options.gauges == 'original' else (91208, 91592, 96012, 91830)
        specs = {
            'raw_backward': ('backward', [], [], raw_b, 87984),
            'balanced_backward': ('backward', [], backward, balanced_b, totals[0]),
            'diagonal_backward': ('backward', [], diagonal, diagonal_b, totals[1]),
            'normalized_backward': ('backward', [], diagonal + full_inverse, normalized_b, totals[2]),
            'raw_forward': ('forward', [], output_swap, raw_f, 88608),
            'balanced_forward': ('forward', prefix, output_swap, balanced_f, totals[3]),
        }
        programs, reports = {}, {}
        for name, (direction, pre, post, expected, total) in specs.items():
            actual, physical, checks, warps = evaluate(direction, pre, post)
            need(actual == expected, 'All 640 ordered columns: ' + provider + ' ' + name)
            need(all(actual[p] == identity[p] for p in range(224, n)), 'All arbitrary helpers restored')
            need(all(not actual[p] for p in range(n, n + 8)), 'All owned fields zero')
            if direction == 'backward':
                need(all(physical[112 + p] == identity[p] for p in selected), 'Selected productive Y contains original X')
            if name == 'normalized_backward':
                for p in range(112):
                    original_x = {key: value for key, value in actual[p].items() if key[0] < 112}
                    expected_x = replay.line(identity[p], p, 1) if p in selected else identity[p]
                    need(original_x == expected_x, 'Normalized original-X response')
            profile = Counter(event[5] for event in native[direction] if event[0] == 'climb')
            need(dict(profile) == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'Native child profile')
            bill = replay.core_price(native[direction]) + price(pre + input_swap + post)
            need(bill == total, 'Complete scalar bill: ' + name)
            programs[name] = {'orientation': direction, 'prefix': pre, 'input_exchange': input_swap,
                              'retained_core': native[direction], 'suffix': post,
                              'events': pre + input_swap + native[direction] + post}
            reports[name] = {'scalar_real_primitives': bill, 'native_rank_mass': 5073, 'native_children': 3507,
                             'native_profile': dict(sorted(profile.items())), 'new_native_children': 0,
                             'new_private_fields': 0, 'all_input_columns': 640, 'arbitrary_helpers_restored': 408,
                             'private_zero_buffers_restored': 91, 'owned_final_zero': 8,
                             'core_scalar_frame_checks': checks, 'core_warp_events': warps}
            print(provider, name, bill, flush=True)
        packet['providers'][provider] = {'canonical': word, 'negative_transfer_sites': sites,
                                         'gauge_words': gauge_words, 'hadamard_pairs': pairs, 'programs': programs}
        receipt['providers'][provider] = {'programs': reports,
                                          'gauge_costs': {name: price(events) for name, events in gauge_words.items()},
                                          'hadamard_physical_exchanges': 32, 'selected_physical_exchanges_per_pass': 24,
                                          'native_scalar_transfer_sign_changes': len(sites)}
    raw = (json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n').encode()
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = ('Twelve complete local native words and full common-frame scalar gauges. '
                        'All Q operators retain their order. Native phase uses the unchanged pinned provider recipes. '
                        'Inter-call code transport, caller exterior phase, storage hosting, recursive precision, '
                        'and the complete supplier invoice remain open.')
    options.out_dir.mkdir(parents=True)
    (options.out_dir / 'STRUCTURED-TRANSFER-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (options.out_dir / 'STRUCTURED-TRANSFER-RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], receipt['payload_decompressed_sha256'], flush=True)


if __name__ == '__main__':
    replay_path = LANE / 'emit_raw_selected.py'
    need(sha256(replay_path.read_bytes()).hexdigest() == PINS['native_replay'], 'Pinned native replay utility')
    spec = importlib.util.spec_from_file_location('structured_native_replay', replay_path)
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    main()
