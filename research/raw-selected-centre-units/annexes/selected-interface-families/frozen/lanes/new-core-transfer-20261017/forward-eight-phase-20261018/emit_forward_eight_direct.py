#!/usr/bin/env python3
"""Emit the exact selected-X phase suffix on the signed eight-port core."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parent
LANES = LANE.parent
REDUCED = LANE / 'bipartite-eight-transfer-20261018'
SOURCE = LANES / 'controller-followthrough-20261017/bipartite-eight-20261018'
PINS = {
    'reduced_freeze': '84b1156a0c58ced62ee5834a92d02147346032f7a8beb181b3efe35a539d86f1',
    'reduced_payload': '740c10032c464723f4cdfecf054ef586832f9563055c62d48a78b6d9f055b62d',
    'source_freeze': 'c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1',
    'source_payload': '0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee',
    'native_replay': 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc',
    'scalar_tools': 'a174ac06bb5f0a2080698a2f7319c7d6ce15a2d04fbaa3ba34db9cf55f7f7ce2',
    'phase_interpreter': '087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b',
}


def need(condition, label):
    if not condition:
        raise ValueError(label)


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, 'Pinned input: ' + str(path))
    return json.loads(raw)


def module(name, path, pin):
    need(sha256(path.read_bytes()).hexdigest() == pin, 'Pinned tool: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def permutation(matrix):
    return {'matrix_rows': list(matrix), 'offset': 0, 'quadratic_rows': [0] * 9,
            'linear_Z4': [0] * 9, 'phase': 0}


def line_recipe(port, label):
    matrix = phase.transpose(phase.extend((label,), 9))
    inverse = phase.inverse(matrix)
    need(phase.mul(matrix, 1) == label, 'The first child axis is the actual port line')
    recipe = {'rank': 1, 'left': permutation(matrix), 'right': permutation(inverse)}
    actual = phase.recipe(recipe)
    target = (('C', label, 1),)
    phase.equal(actual, target, 'Direct live-field positive line')
    for source in range(512):
        expected = [(0, 0)] * 512
        expected[source], expected[source ^ label] = (1, 1), (1, -1)
        need(phase.state(actual, source) == (expected, 1), 'Every exact Gaussian spatial column')
    full = phase.fourier(9)
    phase.equal(full + actual, actual + full, 'Exact FULL commutation including phase')
    # A wrong inverse line has the same support, but fails its Gaussian phase.
    need(phase.state(actual) != phase.state((('C', label, -1),)), 'Line-sign negative control')
    return {'port': port, 'label': label, 'power': 1, 'recipe': recipe,
            'exact_circuit': [['C', label, 1]], 'spatial_columns': 512,
            'binding': 'Apply directly to current completed X at common FULL. No owned field is used.'}


def suffix_boundary(events, state, n, selected, recipes):
    state = deepcopy(state)
    scalar = []
    for event in events:
        if event['kind'] != 'data_line':
            scalar.append(event)
            continue
        need(not scalar, 'All direct children precede the scalar subtraction')
        port = event['port']
        need(port in selected and event['target'] == port and event['power'] == 1,
             'The direct child acts only on its current selected X field')
        need(event['frame'] == 1 and event['recipe'] == recipes[port]['recipe'], 'Exact FULL recipe binding')
        state[port] = replay.line(state[port], port, 1)
    return replay.boundary(scalar, state, n)


def expected_map(response, selected, identity, balanced):
    output = deepcopy(identity)
    for p in range(112):
        if p in selected:
            output[p] = replay.line(identity[p], p, 1)
            continue
        output[112 + p] = {} if balanced else dict(identity[112 + p])
        for q, value in response[p].items():
            if q in selected:
                replay.add(output[112 + p], replay.line(identity[112 + q], q, -1), value)
            else:
                replay.add(output[112 + p], identity[q], value)
                if balanced:
                    replay.add(output[112 + p], identity[112 + q], value)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out_dir.exists(), 'Use a new output directory')
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least 3 GiB of free space')
    for directory, key in ((REDUCED, 'reduced_freeze'), (SOURCE, 'source_freeze')):
        freeze = read(directory / 'FREEZE.json', PINS[key])
        for name, pin in freeze['artifacts'].items():
            need(sha256((directory / name).read_bytes()).hexdigest() == pin, 'Frozen source file: ' + name)
    source = read(SOURCE / 'BIPARTITE-EIGHT-PROGRAM.json.gz', PINS['source_payload'], True)
    reduced = read(REDUCED / 'run-normal/REDUCED-INTERFACES-PROGRAMS.json.gz', PINS['reduced_payload'], True)
    selected = source['selected_ports']
    need(selected == [0, 7, 15, 36, 42, 46, 79, 89], 'Current selected ports')
    response = [{int(q): F(value) for q, value in row.items()} for row in source['response']]
    ordinary = sorted(set(range(112)) - set(selected))
    labels = source['providers']['base']['canonical']['ports']
    recipes = {p: line_recipe(p, labels[p]) for p in selected}
    native = [{'kind': 'data_line', 'target': p, 'port': p, 'power': 1, 'frame': 1,
               'recipe': recipes[p]['recipe']} for p in selected]
    subtraction = [scalar.scalar('add', p, 112 + q if q in selected else q, -value, 1)
                   for p in selected for q, value in sorted(response[p].items())]
    need(len(subtraction) == 160 and scalar.price(subtraction) == 1600, 'Literal half-coefficient subtraction')
    need(Counter(F(e['coefficient']) for e in subtraction) == {F(-1, 2): 88, F(1, 2): 72}, 'Signed subtraction census')
    suffix = native + subtraction
    packet = {'schema': 'direct-selected-eight-phase-suffix-v1', 'source_pins': PINS,
              'selected_S': selected, 'ordinary_U': ordinary,
              'line_recipes': [recipes[p] for p in selected], 'suffix': suffix, 'providers': {}}
    receipt = {'status': 'PASS_DIRECT_SELECTED_EIGHT_PHASE_SUFFIX', 'source_pins': PINS,
               'exact_spatial_columns': 8 * 512, 'exact_FULL_commutations': 8,
               'line_sign_controls': 8, 'providers': {}}
    for provider, item in reduced['families']['eight']['providers'].items():
        word = item['canonical']
        n = len(word['start'])
        need(n == 632 and word == source['providers'][provider]['canonical'], 'Exact native geometry')
        need(word['ports'] == labels, 'Both provider intrinsic lines agree')
        identity = {p: {(p, ()): F(1)} for p in range(n + 8)}
        programs, reports = {}, {}
        for name in ('raw_forward', 'balanced_forward'):
            original = item['programs'][name]
            need(original['retained_core'] == source['providers'][provider]['programs']['forward'], 'Unchanged forward native core')
            prefix = original['prefix'] + original['input_exchange']
            scalar.check_frames(prefix, 0, n)
            scalar.check_frames(original['suffix'] + subtraction, 1, n)
            physical = deepcopy(identity)
            for p in range(112):
                physical[p] = replay.line(physical[p], p, 1)
            physical = replay.boundary(prefix, physical, n)
            logical = deepcopy(physical)
            for p in range(112):
                logical[p] = replay.line(logical[p], p, -1)
            logical, checks, warps = replay.core_replay(original['retained_core'], logical, word, False)
            physical = deepcopy(logical)
            for p in range(112):
                physical[112 + p] = replay.line(physical[112 + p], p, -1)
            physical = replay.boundary(original['suffix'], physical, n)
            before = deepcopy(physical)
            physical = suffix_boundary(suffix, physical, n, selected, recipes)
            actual = deepcopy(physical)
            for p in range(112):
                actual[112 + p] = replay.line(actual[112 + p], p, 1)
            expected = expected_map(response, selected, identity, name == 'balanced_forward')
            for p in range(n, n + 8):
                expected[p] = {}
            need(actual == expected, 'All640 ordered columns, arbitrary selected d: ' + provider + ' ' + name)
            need(all(physical[112 + p] == replay.line(identity[112 + p], p, -1) for p in selected), 'Physical selected Y remains q d')
            need(all(actual[p] == identity[p] for p in range(224, n)), 'Arbitrary helpers restored')
            need(all(not actual[p] for p in range(n, n + 8)), 'All owned fields zero')
            need(replay.boundary(subtraction, before, n) != physical, 'Omitted positive line rejects')
            wrong = deepcopy(before)
            for p in selected:
                wrong[p] = replay.line(wrong[p], p, -1)
            need(replay.boundary(subtraction, wrong, n) != physical, 'Inverse line rejects at the complete boundary')
            need(suffix_boundary(native, before, n, selected, recipes) != physical, 'Omitted row subtraction rejects')
            profile = Counter(e[5] for e in original['retained_core'] if e[0] == 'climb')
            profile[1] += len(native)
            need(dict(profile) == {1: 2441, 2: 724, 3: 228, 4: 102, 5: 20}, 'Full native profile')
            bill = replay.core_price(original['retained_core']) + scalar.price(prefix + original['suffix'] + subtraction)
            need(bill == (93072 if name == 'balanced_forward' else 89376), 'Complete scalar invoice')
            programs[name] = {'prefix': original['prefix'], 'input_exchange': original['input_exchange'],
                              'retained_core': original['retained_core'], 'output_exchange': original['suffix'],
                              'phase_suffix': suffix,
                              'events': prefix + original['retained_core'] + original['suffix'] + suffix}
            reports[name] = {'scalar_real_primitives': bill, 'native_rank_mass': 5081,
                             'native_children': 3515, 'new_rank_one_children': 8,
                             'new_pure_permutation_wrappers': 16, 'new_owned_fields': 0,
                             'new_private_fields': 0, 'new_scalar_primitives': 1600,
                             'native_profile': dict(sorted(profile.items())), 'all_input_columns': 640,
                             'arbitrary_helpers_restored': 408, 'private_zero_buffers_restored': 91,
                             'owned_final_zero': 8, 'core_scalar_frame_checks': checks,
                             'core_warp_events': warps, 'boundary_negative_controls': 3}
            print(provider, name, bill, 5081, flush=True)
        packet['providers'][provider] = {'canonical': word, 'programs': programs}
        receipt['providers'][provider] = reports
    raw = (json.dumps(packet, sort_keys=True, separators=(',', ':')) + '\n').encode()
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    receipt['scope'] = ('Exact local physical kernels and complete ordered forward maps. '
                        'Eight additional H1 calls and sixteen pure-permutation wrappers are retained. '
                        'Global child hosting, routed composition, exterior phase, precision and the supplier invoice remain open.')
    args.out_dir.mkdir(parents=True)
    (args.out_dir / 'FORWARD-EIGHT-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (args.out_dir / 'FORWARD-EIGHT-RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'], receipt['payload_decompressed_sha256'], flush=True)


if __name__ == '__main__':
    replay = module('f8_native_replay', LANE / 'emit_raw_selected.py', PINS['native_replay'])
    scalar = module('f8_scalar_tools', LANE / 'structured-centres-transfer-20261018/emit_structured_transfer.py', PINS['scalar_tools'])
    phase = module('f8_phase_interpreter', LANES / 'interface-proof/verify_native_lift.py', PINS['phase_interpreter'])
    main()
