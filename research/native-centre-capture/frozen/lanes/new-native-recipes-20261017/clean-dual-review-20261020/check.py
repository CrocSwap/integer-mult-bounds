#!/usr/bin/env python3
"""Check the physical inverse-adjoint and selected-field conjugate."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ACCEPTED = HERE.parent/'clean-centre-exchange-review-20261020'
HELPER = ACCEPTED/'check.py'
PIN = 'e6564514a878cfa2411a41990a3d9c012f97a464c1b8361fb358fa741968f35c'
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError('Independent helper pin')
spec = importlib.util.spec_from_file_location('independent_clean_review', HELPER)
clean = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean)
q = clean.q
q.read(HELPER, PIN)
need, P = q.need, q.P


def matrices(source):
    c, e = q.rows(source['code']), q.rows(source['response'])
    need(e == q.transpose(e, 112), 'Actual self-adjoint response')
    ci = q.unit(112)
    for p in P:
        need(c[p].get(p) == 1 and set(c[p]).intersection(P) == {p}, 'Normalized selected pivot')
        need(not set(e[p]).intersection(P), 'Actual E_PP is zero')
        for r in range(112):
            if r not in P:
                need(e[p].get(r, F(0)) == -c[p].get(r, F(0)), 'Actual E_PR equals negative B')
                q.add(ci[p], {r: c[p].get(r, F(0))}, F(-1))
    need(q.mul(c, ci) == q.unit(112) and q.mul(ci, c) == q.unit(112), 'Exact code inverse orders')
    for r in range(112):
        if r not in P:
            expected = {r: F(1)}
            for p in P:
                d = e[r].get(p, F(0))
                need(d == -c[p].get(r, F(0)), 'Actual D equals negative transpose of B')
                q.add(expected, c[p], d)
            need(e[r] == expected, 'Actual E_R equals [D,I+DB]')
    original = clean.endpoint(e, c)[:224]
    inverse = clean.inverse_endpoint(e, ci)
    need(q.mul(original, inverse) == q.unit(224) and q.mul(inverse, original) == q.unit(224),
         'Independent complete clean inverse orders')
    dual = q.transpose(inverse, 224)
    dual_inverse = q.transpose(original, 224)
    direct = q.unit(224)
    for p in range(112):
        if p in P:
            direct[p] = {112+p: F(-1)}
            direct[112+p] = {p: F(1)}
            for r, value in c[p].items():
                if r not in P:
                    q.add(direct[112+p], {112+r: value})
        else:
            q.add(direct[p], {112+p: F(-1)})
            for r in P:
                q.add(direct[p], {r: e[p].get(r, F(0))})
    need(dual == direct, 'Separate unpermuted block formula')
    return c, e, dual, dual_inverse


def conjugate(matrix, permutation):
    return [{permutation[j]: value for j, value in matrix[permutation[i]].items()}
            for i in range(len(matrix))]


def block_swap(c, e):
    matrix = q.unit(224)
    for p in range(112):
        if p in P:
            matrix[p] = {112+r: value for r, value in c[p].items()}
            matrix[112+p] = {p: F(-1)}
        else:
            q.add(matrix[p], {112+p: F(-1)})
            for r in P:
                q.add(matrix[p], {112+r: e[p].get(r, F(0))})
    return matrix


def check_word(word, source, permutation, expected):
    need(len(word['events']) == len(source['events']), 'No added boundary operations')
    need(word['stage_ranges'] == source['stage_ranges'], 'Exact stage chronology')
    need(word['wire_permutation'] ==
         {str(p): t for p, t in enumerate(permutation) if p != t}, 'Exact stored field permutation')
    need(all(permutation[permutation[p]] == p for p in range(640)), 'Involutive field permutation')
    for key in ('frames', 'native_recipes', 'start', 'final', 'output_views'):
        need(word[key] == source[key], 'Exact accepted physical record: '+key)
    need(all(source[key][p] == source[key][permutation[p]] for key in ('start', 'final')
             for p in range(640)), 'Selected endpoint frame invariance')
    input_source = {r['field']: r for r in source['input_views']}
    inputs = {r['field']: r for r in word['input_views']}
    need(len(inputs) == len(word['input_views']) == 128 and set(inputs) == set(input_source),
         'Every input adapter has one explicit physical field')
    physical_keys = ('port', 'frame', 'rank', 'left', 'right')
    for field, record in inputs.items():
        need(record['role'] == ('source' if field < 112 else 'selected_target'), 'Actual adapter role')
        need(all(record[k] == input_source[field][k] for k in physical_keys),
             'Same operator at each physical input')
        expected_record = deepcopy(input_source[permutation[field]])
        expected_record['field'], expected_record['role'] = field, record['role']
        need(record == expected_record, 'Exact adapter provenance and target rebind')
    for p in P:
        need(all(input_source[p][k] == input_source[112+p][k] for k in physical_keys),
             'Complete selected Q/Q input phase symmetry')
        need(source['final'][p] == source['final'][112+p] == 1, 'Complete FULL/FULL output symmetry')
    need(all(r['port'] not in P for r in word['output_views']), 'All ordinary output fields remain fixed')
    current = list(word['start'])
    count, used = Counter(), set()
    for event, old in zip(word['events'], source['events']):
        if old[0] == 'native':
            expected_event = deepcopy(old)
            expected_event[1] = permutation[old[1]]
            need(event == expected_event, 'Every unchanged unitary native occurrence is explicitly rebound')
            _, field, before, after, rank, key = event
            need(0 <= field < 224 and current[field] == before, 'Exact native input frame')
            need(word['native_recipes'][key]['rank'] == rank, 'Exact accepted child rank')
            current[field] = after
            count[rank] += 1
            used.add(key)
        else:
            need(old[0] == event[0] == 'scalar', 'Complete scalar grammar')
            op, target, origin, value = old[1]
            value = F(value)
            if op == 'add':
                expected_gate = ['add', permutation[origin], permutation[target], str(-value)]
            else:
                need(op == 'scale' and origin is None and value != 0, 'Invertible real scale')
                expected_gate = ['scale', permutation[target], None, str(1/value)]
            need(event == ['scalar', expected_gate, old[2]], 'Chronological inverse-adjoint scalar rule')
            op, target, origin, _ = event[1]
            need(0 <= target < 224 and current[target] == event[2], 'Actual scalar target frame')
            if op == 'add':
                need(0 <= origin < 224 and target != origin and current[origin] == event[2],
                     'Actual scalar source frame')
    need(current == word['final'] and used == set(word['native_recipes']), 'Complete final frame and recipe ledger')
    need(count == {1: 1392, 2: 64, 3: 48, 8: 16}, 'Complete native profile')
    scalars = [e[1] for e in word['events'] if e[0] == 'scalar']
    target = expected+q.unit(640)[224:]
    need(q.reverse(scalars, 640) == q.transpose(target, 640), 'All640 independent reverse columns')
    rows, growth = q.prefix(scalars, 640)
    need(rows == target and rows[224:] == q.unit(640)[224:], 'Separate forward rows and416 arbitrary roles')
    prices = {name: q.price([e[1] for e in word['events'][start:end] if e[0] == 'scalar'])
              for name, (start, end) in word['stage_ranges'].items()}
    need(prices == {'retained_core': 6456, 'selected_progress': 0,
                    'source_row_code': 1760, 'signed_selected_exchanges': 384}, 'Complete stage prices')
    need(q.price(scalars) == 8600, 'Exact full scalar price')
    need(growth == {'row_one_norm': '12', 'binary_height': 2}, 'Exact dual content prefix bound')
    need(q.reverse(list(reversed(scalars)), 640) != q.transpose(target, 640),
         'Wrong reversed scalar chronology control')
    return {
        'input_columns': 640, 'unchanged_arbitrary_roles': 416,
        'native_profile': dict(sorted(count.items())), 'native_children': sum(count.values()),
        'native_mass': sum(r*n for r, n in count.items()), 'real_scalar_primitives': 8600,
        'scalar_stage_prices': prices, 'input_views': 128, 'output_views': 96,
        'native_side_maps_upper_bound': 3040, 'runtime_boundary_swaps': 0,
        'new_fields': 0, 'private_fields': 0, 'odd_scans': 0, 'growth': growth,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source_dir = q.RAW/'clean-late-exchange-20261020'
    q.frozen(ACCEPTED, 'FREEZE.json', '6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d')
    q.frozen(source_dir, 'DUAL-FREEZE.json', 'fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43')
    source = json.loads(q.read(source_dir/'run-normal/CLEAN-LATE-EXCHANGE.json.gz',
                               'b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083', True))
    payload = json.loads(q.read(source_dir/'dual-normal/CLEAN-DUAL.json.gz',
                                '6c8869b1c1b45632635805e389899b83fa8348c9fe5b84e3c9c7821bcfd0568c', True))
    need(payload['selected_ports'] == source['selected_ports'] == P and
         payload['ports'] == source['ports'] and payload['code'] == source['code'] and
         payload['response'] == source['response'], 'Exact source matrix and port binding')
    c, e, dual, dual_inverse = matrices(source)
    identity = list(range(640))
    swap = [112+p if p in P else p-112 if p-112 in P else p for p in range(640)]
    maps = {'inverse_adjoint': dual, 'selected_swap_conjugate': conjugate(dual, swap[:224])}
    inverses = {'inverse_adjoint': dual_inverse,
                'selected_swap_conjugate': conjugate(dual_inverse, swap[:224])}
    need(maps['selected_swap_conjugate'] == block_swap(c, e), 'Separate selected-swap block formula')
    for name, matrix in maps.items():
        need(q.mul(matrix, inverses[name]) == q.unit(224) and
             q.mul(inverses[name], matrix) == q.unit(224), 'Both dual content inverse orders: '+name)
        need(q.rows(payload['content_maps'][name]) == matrix and
             q.rows(payload['inverse_content_maps'][name]) == inverses[name], 'Exact serialized matrix: '+name)
    need(set(payload['providers']) == {'base', 'extra'}, 'Both actual providers')
    reports = {}
    for provider, words in payload['providers'].items():
        need(set(words) == set(maps), 'Both complete dual variants')
        reports[provider] = {}
        for name, word in words.items():
            reports[provider][name] = check_word(
                word, source['providers'][provider]['Q'],
                identity if name == 'inverse_adjoint' else swap, maps[name])
    report = {
        'status': 'PASS_INDEPENDENT_CLEAN_DUAL_AND_SELECTED_CONJUGATE',
        'literal_words': reports, 'actual_D_equals_negative_B_transpose': True,
        'actual_E_PP_zero': True, 'actual_E_self_adjoint': True,
        'all_content_inverse_orders': True, 'new_phase_operators': 0,
        'phase_source_review': '6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d',
        'negative_control': 'Reversing scalar chronology changes the complete map.',
        'scope': 'Four complete local physical inverse-adjoint words, exact target-field phase symmetry, and unchanged local invoice. No routed two-call computation, helper host, or full supplier claim.',
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [('REVIEW.json', report), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
