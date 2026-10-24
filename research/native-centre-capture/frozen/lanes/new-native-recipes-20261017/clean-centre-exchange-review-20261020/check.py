#!/usr/bin/env python3
"""Check a clean centre exchange on all arbitrary input fields."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ACCEPTED = HERE.parent/'row-capture-native-review-20261020'
HELPER = ACCEPTED/'check.py'
PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError('Independent helper pin')
spec = importlib.util.spec_from_file_location('independent_capture_review', HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, PIN)
need, P = q.need, q.P


def endpoint(response, code):
    result = q.unit(640)
    for p in range(112):
        if p in P:
            result[p] = {112+p: F(-1)}
            result[112+p] = dict(code[p])
        else:
            q.add(result[112+p], response[p])
    return result


def inverse_endpoint(response, code_inverse):
    z = [{112+p if p in P else p: F(1)} for p in range(112)]
    original_x = q.mul(code_inverse, z)
    result = original_x+[{} for _ in range(112)]
    for p in range(112):
        if p in P:
            result[112+p] = {p: F(-1)}
        else:
            result[112+p] = {112+p: F(1)}
            for j, value in response[p].items():
                q.add(result[112+p], original_x[j], -value)
    return result


def check_word(word, old, reference, code, response, c, entry):
    selected = {112+p for p in P}
    indices, removed = q.select_raw(old, selected)
    need(word['retained_original_event_indices'] == indices, 'Exact retained index ledger')
    kept = [old['events'][i] for i in indices]
    need(len(removed) == 250 and
         Counter(old['events'][i][4] for i in removed if old['events'][i][0] == 'native') == {1: 128},
         'Exact selected-path deletion')
    progress_name = 'selected_full_progress' if entry == 'I' else 'selected_line_progress'
    progress = reference['events'][slice(*reference['stage_ranges'][progress_name])]
    expected_rank = 9 if entry == 'I' else 8
    need(len(progress) == 16, 'Every selected progress child')
    for p, event in zip(P, progress):
        before = 0 if entry == 'I' else reference['start'][112+p]
        key = 'capture-full' if entry == 'I' else 'capture-line:'+str(p)
        need(event == ['native', 112+p, before, 1, expected_rank, key], 'Accepted progress binding')
    encode = [['scalar', list(gate), 1] for gate in code['scalar_word']]
    rotate = []
    for p in P:
        rotate += [
            ['scalar', ['add', 112+p, p, '1'], 1],
            ['scalar', ['add', p, 112+p, '-1'], 1],
            ['scalar', ['add', 112+p, p, '1'], 1],
        ]
    need(word['events'] == kept+progress+encode+rotate, 'Complete literal chronology')
    stages = [('retained_core', kept), ('selected_progress', progress),
              ('source_row_code', encode), ('signed_selected_exchanges', rotate)]
    ranges, cursor = {}, 0
    for name, events in stages:
        ranges[name] = [cursor, cursor+len(events)]
        cursor += len(events)
    need(word['stage_ranges'] == ranges, 'Exact stage cut ledger')
    for key in ('frames', 'start', 'final', 'input_views', 'output_views', 'native_recipes'):
        need(word[key] == reference[key], 'Accepted physical records: '+key)
    if entry == 'I':
        need(word['new_full_recipe_circuit'] == reference['new_full_recipe_circuit'],
             'Exact positive FULL circuit')
    current = list(word['start'])
    count, used = Counter(), set()
    for i, event in enumerate(word['events']):
        if i == ranges['source_row_code'][0]:
            need(all(current[p] == 1 for p in range(112)) and
                 all(current[p] == 1 for p in selected), 'Complete common-FULL exchange cut')
        if event[0] == 'native':
            _, field, before, after, rank, key = event
            need(0 <= field < 224 and current[field] == before, 'Actual native field and input frame')
            need(word['native_recipes'][key]['rank'] == rank, 'Actual native rank')
            if key == 'capture-full' or key.startswith('capture-line:'):
                need(event in progress, 'Exact accepted selected progress occurrence')
            else:
                need(key == str(before)+':'+str(after), 'Accepted ordered native pair')
            current[field] = after
            count[rank] += 1
            used.add(key)
        else:
            need(event[0] == 'scalar', 'Complete event grammar')
            _, gate, frame = event
            op, target, origin, _ = gate
            need(0 <= target < 224 and current[target] == frame, 'Scalar target frame')
            if op == 'add':
                need(0 <= origin < 224 and origin != target and current[origin] == frame,
                     'Scalar source frame')
            else:
                need(op == 'scale' and origin is None, 'Exact scalar scale grammar')
    need(current == word['final'] and used == set(word['native_recipes']), 'Final frame and recipe ledger')
    need(count == {1: 1392, 2: 64, 3: 48, expected_rank: 16}, 'Complete native profile')
    scalars = [e[1] for e in word['events'] if e[0] == 'scalar']
    expected = endpoint(response, c)
    need(q.reverse(scalars, 640) == q.transpose(expected, 640), 'All640 reverse input columns')
    rows, growth = q.prefix(scalars, 640)
    need(rows == expected and rows[224:] == q.unit(640)[224:], 'Separate forward rows and416 arbitrary roles')
    source_fields = [112+p if p in P else p for p in range(112)]
    other_fields = [p if p in P else 112+p for p in range(112)]
    need(sorted(source_fields+other_fields) == list(range(224)), 'Exact same-port bank partition')
    need([rows[field] for field in source_fields] == c, 'Clean encoded source on all112 ports')
    need(all(rows[112+p] == c[p] and rows[p] == {112+p: F(-1)} for p in P),
         'Every arbitrary baseline is retained with its sign')
    bills = {name: q.price([e[1] for e in events if e[0] == 'scalar']) for name, events in stages}
    need(bills == {'retained_core': 6456, 'selected_progress': 0,
                   'source_row_code': 1760, 'signed_selected_exchanges': 384}, 'Exact stage bills')
    need(q.price(scalars) == 8600, 'Complete scalar bill')
    need(growth == {'row_one_norm': '22', 'binary_height': 1}, 'Exact content prefix bound')
    for omitted in (encode, rotate):
        bad = kept+progress+(encode if omitted is rotate else [])+(rotate if omitted is encode else [])
        need(q.reverse([e[1] for e in bad if e[0] == 'scalar'], 640) != q.transpose(expected, 640),
             'Missing code or exchange control')
    wrong_rotation = [list(e[1]) for e in rotate]
    wrong_rotation[1][3] = '1'
    need(q.reverse([e[1] for e in kept+progress+encode if e[0] == 'scalar']+wrong_rotation, 640)
         != q.transpose(expected, 640), 'Wrong signed rotation control')
    return {
        'input_columns': 640, 'unchanged_arbitrary_roles': 416,
        'native_profile': dict(sorted(count.items())), 'native_children': sum(count.values()),
        'native_mass': sum(r*n for r, n in count.items()), 'real_scalar_primitives': 8600,
        'stage_prices': bills, 'input_views': 112 if entry == 'I' else 128, 'output_views': 96,
        'native_side_maps_upper_bound': 3008 if entry == 'I' else 3040,
        'new_fields': 0, 'private_fields': 0,
        'odd_scans': 0, 'growth': growth, 'source_fields': source_fields,
        'complementary_fields': other_fields,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = q.RAW/'clean-late-exchange-20261020'
    line_review = HERE.parent/'line-entry-reuse-review-20261020'
    q.frozen(ACCEPTED, 'FREEZE.json', '488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532')
    q.frozen(line_review, 'FREEZE.json', 'cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c')
    q.frozen(source, 'FREEZE.json', '96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc')
    q.frozen(q.ALG, 'FREEZE.json', '0810ec37cb70d819a1d40f817476a41dd1151535309972af1b5b1db2bcb42baf')
    raw = json.loads(q.read(q.RAW/'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
                            'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4', True))
    code = json.loads(q.read(q.ALG/'run-normal/ROW-CAPTURE.json',
                             '4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7'))
    refs = {
        'I': json.loads(q.read(q.NATIVE/'direct-normal/DIRECT-FULL-CAPTURE.json.gz',
                               'fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c', True)),
        'Q': json.loads(q.read(q.NATIVE/'reuse-normal/LINE-ENTRY-REUSE.json.gz',
                               'efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110', True)),
    }
    payload = json.loads(q.read(source/'run-normal/CLEAN-LATE-EXCHANGE.json.gz',
                                'b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083', True))
    response, c, _, algebra = q.algebra(raw, code)
    ci = q.rows(code['code_inverse'])
    expected, inverse = endpoint(response, c), inverse_endpoint(response, ci)
    need(q.mul(expected[:224], inverse) == q.unit(224) and
         q.mul(inverse, expected[:224]) == q.unit(224), 'Both complete content inverse orders')
    need(q.rows(payload['content_map']) == expected[:224] and
         q.rows(payload['inverse_content_map']) == inverse, 'Exact payload content maps')
    need(payload['selected_ports'] == P and payload['ports'] == raw['model']['ports'],
         'Exact ordered ports')
    need(q.rows(payload['code']) == c and q.rows(payload['response']) == response, 'Exact matrix source binding')
    need(set(payload['providers']) == {'base', 'extra'}, 'Both actual providers')
    reports = {}
    for provider, entries in payload['providers'].items():
        need(set(entries) == {'I', 'Q'}, 'Both entry contracts')
        reports[provider] = {}
        for entry, word in entries.items():
            reports[provider][entry] = check_word(
                word, raw['providers'][provider]['forward'],
                refs[entry]['providers'][provider], code, response, c, entry)
    report = {
        'status': 'PASS_INDEPENDENT_CLEAN_CENTRE_EXCHANGE',
        'algebra': algebra, 'content_inverse_both_orders': True, 'literal_words': reports,
        'new_phase_operators': 0,
        'phase_sources': {
            'I': '488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532',
            'Q': 'cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c',
        },
        'negative_controls': ['missing source code', 'missing signed exchanges', 'wrong rotation sign'],
        'scope': 'Four complete local clean-record words, exact physical contracts, arbitrary baseline preservation, and local invoice. The same-port role partition does not by itself admit or price a routed caller.',
    }
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [('REVIEW.json', report), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
