#!/usr/bin/env python3
"""Review the irregular native words and their completed response unit."""
from copy import deepcopy
import argparse
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import time

HERE = Path(__file__).resolve().parent
LANES = HERE.parent
SOURCE = LANES / 'new-core-transfer-20261017'
SCRIPT_PIN = 'f8f833624f40c5a892383254ba274cf7fe32b4d93f68d3b6eb0549ecad0d5b6f'
path = HERE / 'check_serial_balanced.py'
if hashlib.sha256(path.read_bytes()).hexdigest() != SCRIPT_PIN:
    raise ValueError('Pinned independent scalar reviewer')
spec = importlib.util.spec_from_file_location('independent_balanced_review', path)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
review.read_bytes(path, SCRIPT_PIN)
need, read, read_bytes = review.need, review.read, review.read_bytes
atom, add, line = review.atom, review.add, review.line


def unit_frames(events, word, selected, n):
    frames = word['final'][:] + [0] * 8
    for event in events:
        kind, target, declared = event['kind'], event['target'], event['frame']
        need(0 <= target < 112 or n <= target < n + 8, 'Response unit touches X and owned queries')
        if kind == 'clear':
            need(n <= target < n + 8, 'Response unit clears only owned fields')
            frames[target] = declared
        else:
            need(frames[target] == declared == 1, 'Response unit target at FULL')
            if kind == 'add':
                source = event['source']
                need((0 <= source < 112 or n <= source < n + 8) and frames[source] == declared, 'Response unit source at FULL')
                need(source != target, 'Response unit ADD uses distinct fields')
            else:
                need(kind == 'scale' and (target >= n or target in selected and Q(event['coefficient']) == -1), 'Response unit dyadic query scale or selected sign')
    need(frames[:n] == word['final'] and frames[n:] == [0] * 8, 'Response unit exact frame restoration')


def query_order(events, n):
    data_write = False
    queries = set()
    for event in events:
        if event['kind'] != 'add':
            continue
        target, source = event['target'], event['source']
        if target >= n and source < n:
            need(not data_write, 'All current data queries precede every data scatter')
            queries.add(target)
        if target < n and source >= n:
            need(queries == set(range(n, n + 8)), 'All eight current queries exist before scatter')
            data_write = True
    need(data_write, 'The factor has a data scatter')


def matrix_result(matrix, n):
    result = [atom(i) for i in range(n + 8)]
    for p, row in enumerate(matrix):
        result[p] = {((), q): c for q, c in enumerate(row) if c}
    result[n:] = [{} for _ in range(8)]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New receipt path; existing files are not overwritten.")
    out = parser.parse_args().out.resolve()
    manifest = out.with_name(out.stem + "-INPUTS.json")
    need(out.parent.is_dir(), "Output directory exists")
    need(not out.exists() and not manifest.exists(), "Output files must be new")
    started = time.monotonic()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least 3 GiB free')
    freeze = read(SOURCE / 'FREEZE-IRREGULAR-38.json', '10214232ba25219d94821e5c9414b299166b15e471cd8bd9a3b343c61ef32f4f')
    for name, pin in freeze['files'].items():
        read_bytes(SOURCE / name, pin)
    packet = read(SOURCE / 'IRREGULAR-38-PROGRAMS.json.gz', 'bd980a32b56768ee8e6454a789d4d53c805154a062e0d437373a0acc726dd801', True)
    unit = read(SOURCE / 'IRREGULAR-38-RESPONSE-UNIT.json', 'c4fc86b3dd4aed536f1226a9339a80b0587a93da860601266d81771df3c96ac6')
    core = read(SOURCE / 'CLEAN-J-PROGRAMS.json.gz', 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa', True)
    witness = read(LANES.parent / 'root/IRREGULAR-SPLIT-20261017.json', '0a8d22fa0b523c261243e9b19cfd51926c9b515a9e6f9a962d1e3b5170105a8f')
    native = read(LANES / 'independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json', '924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d')
    prior = read(HERE / 'SERIAL-BALANCED-REVIEW.json', '1b77917f5e21e7383d0aa50dcf4a0eb4c3d0177dc2e280979fdf2740067bbfae')
    need(native['status'] == 'PASS_INDEPENDENT_NEW_CORE_NATIVE_RECIPES' and native['clean_payload_sha256'] == packet['source_pins']['core'], 'Inherited exact native phase binding')
    need(prior['status'] == 'PASS_INDEPENDENT_SERIAL_BALANCED_LOCAL_WORDS' and prior['exact_signed_endpoint_F_commutations'] == {'base': 224, 'extra': 224}, 'Exact all-port F commutations')
    need(packet['selected_S'] == unit['selected_S'] == witness['selected'] and len(packet['selected_S']) == 38, 'Exact irregular witness selection')
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in core['R']]
    need(all(sum(r[i][p] * r[j][p] for p in range(112)) == 56 * (i == j) for i in range(8) for j in range(8)), 'Full actual row Gram matrix')
    S, U, J, C, h, hi = review.geometry(r, packet['selected_S'])
    need(list(U) == packet['ordinary_U'] and len(U) == 74, 'Exact ordinary partition')
    selected_gram = [[sum(r[i][p] * r[j][p] for p in S) for j in range(8)] for i in range(8)]
    need(selected_gram == witness['gram'], 'Independent source Gram binding')
    W = [[Q(i == j) - selected_gram[i][j] / 4 for j in range(8)] for i in range(8)]
    wi = review.inverse(W)
    need(wi == [[Q(c) for c in row] for row in witness['I_minus_D_inverse']], 'Independent W inverse agrees')
    signs = [-1 if p in S else 1 for p in range(112)]
    wi_r = [[sum(wi[i][j] * r[j][q] for j in range(8)) for q in range(112)] for i in range(8)]
    A = [[signs[p] * Q(p == q) + C[p][q] for q in range(112)] for p in range(112)]
    AI = [[signs[p] * Q(p == q) - signs[p] * signs[q] * sum(r[i][p] * wi_r[i][q] for i in range(8)) / 4
           for q in range(112)] for p in range(112)]
    need(all(c.denominator & (c.denominator - 1) == 0 for row in A + AI for c in row), 'Both response matrices are dyadic')
    reports, core_checks = {}, {}
    costs = {'balanced_backward': 170446, 'diagonal_backward': 171662, 'balanced_forward': 171290}
    factor_costs = {'balanced_backward': 4944, 'diagonal_backward': 6160, 'balanced_forward': 4800}
    for provider, item in packet['providers'].items():
        word, n = item['canonical'], len(item['canonical']['start'])
        need(word == core['providers'][provider]['canonical'], 'Current canonical geometry')
        need(word['start'][112:224] == [0] * 112 and word['final'][:112] == [1] * 112, 'Common I and FULL boundary frames')
        cores = {}
        for direction in ('forward', 'backward'):
            cores[direction], core_checks[provider + '/' + direction] = review.core_operator(core['providers'][provider]['programs'][direction], word, J, direction)
        reports[provider] = {'native_words': {}, 'response_units': {}, 'composed_word': {}}
        for name, program in item['programs'].items():
            direction = program['orientation']
            events = program['retained_core']
            need(events == core['providers'][provider]['programs'][direction], 'Exact current native array')
            need(program['events'] == program['prefix'] + program['input_exchange'] + events + program['suffix'] + program['owned_cleanup'], 'Literal complete order')
            need(program['owned_cleanup'] == [], 'No uncounted owned cleanup')
            factor = program['prefix'] if direction == 'forward' else program['suffix']
            review.factor_frames(factor, 112 if direction == 'forward' else 0, 0 if direction == 'forward' else 1, n)
            query_order(factor, n)
            need(sum(e['kind'] == 'clear' for e in factor) == 16, 'Eight owned preparations and returns')
            need(review.invoice(factor) == (factor_costs[name], 0), 'Exact irregular factor invoice')
            actual, physical = review.execute(program, cores[direction], n)
            expected = review.expected_map(name, S, U, J, C, h, hi, n)
            need(actual == expected, 'All irregular ordered columns: ' + provider + '/' + name)
            need(actual[224:n] == [atom(p) for p in range(224, n)] and actual[n:] == [{}] * 8, 'All helper and owned outputs')
            if direction == 'backward':
                need(all(physical[112 + p] == atom(p) for p in S), 'Physical selected Y carries F times original X')
            review.check_inverse(name, actual, S, U, J, r, h, hi, n)
            scalar, scans = review.invoice(program['prefix'] + program['input_exchange'] + program['suffix'])
            need(scalar + 164514 == costs[name] and scans == 0, 'Complete irregular dyadic invoice')
            changed = deepcopy(program)
            changed['prefix' if direction == 'forward' else 'suffix'] = []
            need(review.execute(changed, cores[direction], n)[0] != expected, 'Omitted irregular factor rejects')
            changed = deepcopy(program)
            changed['input_exchange'] = []
            need(review.execute(changed, cores[direction], n)[0] != expected, 'Omitted physical exchange rejects')
            reports[provider]['native_words'][name] = {
                'scalar_real_primitives': costs[name], 'native_mass': 5073, 'native_children': 3507,
                'new_native_children': 0, 'new_private_fields': 0, 'owned_query_peak': 8,
                'arbitrary_columns': 640, 'logical_helpers_under_inherited_contract': 408,
                'private_zero_buffers': 91, 'owned_outputs_zero': 8, 'ordered_inverse_live_columns': 632,
            }
            print('PASS irregular native', provider, name, costs[name], flush=True)

        identity = [atom(i) for i in range(n + 8)]
        zero_owned_identity = deepcopy(identity)
        zero_owned_identity[n:] = [{}] * 8
        for name, matrix, scalar in (('A', A, 7452), ('inverse_A', AI, 7412)):
            events = unit['programs'][name]
            unit_frames(events, word, S, n)
            query_order(events, n)
            need(review.invoice(events) == (scalar, 0), 'Exact response-unit invoice')
            need(review.boundary(events, identity, n) == matrix_result(matrix, n), 'All exact response-unit columns')
            reports[provider]['response_units'][name] = {'scalar_real_primitives': scalar, 'all_input_columns': 640,
                'native_children': 0, 'owned_query_peak': 8, 'owned_outputs_zero_at_I': 8}
        for first, second in (('A', 'inverse_A'), ('inverse_A', 'A')):
            need(review.boundary(unit['programs'][first] + unit['programs'][second], identity, n) == zero_owned_identity, 'Both literal response-unit inverse orders')

        program = deepcopy(item['programs']['diagonal_backward'])
        program['suffix'] += unit['programs']['inverse_A']
        actual, physical = review.execute(program, cores['backward'], n)
        expected = deepcopy(identity)
        borrowed = {p: line(identity[112 + p], p, -1) if p in S else {((), 112 + p): Q(-1)} for p in range(112)}
        for p in range(112):
            expected[p] = line(identity[p], p, 1) if p in S else dict(identity[p])
            add(expected[p], review.combine({q: AI[p][q] for q in range(112) if AI[p][q]}, borrowed))
            if p in S:
                expected[112 + p] = line(identity[p], p, 1)
        expected[n:] = [{}] * 8
        need(actual == expected, 'Whole-core response-normalized backward map')
        scalar, scans = review.invoice(program['prefix'] + program['input_exchange'] + program['suffix'])
        need(scalar + 164514 == 179074 and scans == 0, 'Whole response-normalized word invoice')
        need(all(physical[112 + p] == atom(p) for p in S), 'Normalized word preserves selected physical carrier')
        reports[provider]['composed_word'] = {'scalar_real_primitives': 179074, 'native_mass': 5073, 'native_children': 3507,
            'arbitrary_columns': 640, 'original_X_response': 'diag(Q_S,I_U)', 'owned_outputs_zero': 8,
            'method': 'Literal complete core plus frozen inverse_A suffix, replayed in this review.'}
        print('PASS irregular units and whole normalized word', provider, flush=True)
    result = {'status': 'PASS_INDEPENDENT_IRREGULAR_38_NATIVE_AND_RESPONSE_UNIT', 'providers': reports,
              'core_checks': core_checks, 'source_payload_decompressed_sha256': 'bd980a32b56768ee8e6454a789d4d53c805154a062e0d437373a0acc726dd801',
              'response_unit_payload_sha256': 'c4fc86b3dd4aed536f1226a9339a80b0587a93da860601266d81771df3c96ac6',
              'not_claimed': ['Minimal selected size', 'Idle preparation', 'Complete inter-call decoder or controller', 'Owner histories', 'Recursive hosting, precision, complete supplier cost, or kappa'],
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'seconds': time.monotonic() - started}
    manifest.write_text(json.dumps(review.INPUTS, indent=2, sort_keys=True) + '\n')
    result['input_manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
