#!/usr/bin/env python3
"""Check the complete coded exits on the frozen low-displacement paths."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
BASE = HERE.parent/'low-displacement-review-20261020'
SOURCE = LANES/'new-core-transfer-20261017/low-displacement-20261020'
OLD = HERE.parent/'matched-left-gauge-review-20261018'


def load(name, path, pin):
    if sha256(path.read_bytes()).hexdigest() != pin:
        raise ValueError('Independent interpreter pin: '+str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse(event):
    gate = event[1]
    return gate[0], gate[1], None if gate[0] == 'scale' else gate[2], F(*gate[-2:])


def phase_key(basis, circuit):
    return json.dumps([basis, circuit], sort_keys=True, separators=(',', ':'))


def accepted_exits(payload, need):
    records = {}
    for providers in payload['providers_by_output_code'].values():
        for directions in providers.values():
            for word in directions.values():
                for event in word['events']:
                    if event[0] == 'scalar':
                        continue
                    before, after = word['frames'][event[2]], word['frames'][event[3]]
                    if after['kind'] != 'literal':
                        continue
                    key = phase_key(before['basis'], after['circuit'])
                    record = word['native_recipes'][event[-1]]
                    need(key not in records or records[key] == record, 'Unambiguous accepted exit')
                    records[key] = record
    need(len(records) == 200, 'Complete earlier carry-W phase table')
    return records


def ledger(word, response, direction, review):
    current = list(word['start'])
    review.need(len(current) == len(word['final']) == 640, 'Exactly 640 live roles')
    rows = [{i: F(1)} for i in range(224)]
    maximum = F(1)
    converted = []
    for event in word['events']:
        if event[0] == 'scalar':
            op, target, origin, value = parse(event)
            frame = event[2]
            review.need(0 <= target < 224 and current[target] == frame, 'Actual scalar target frame')
            if op == 'add':
                review.need(0 <= origin < 224 and origin != target and current[origin] == frame,
                            'Actual equal scalar frames')
                review.add(rows[target], rows[origin], value)
            else:
                review.need(op == 'scale' and origin is None, 'Closed scalar grammar')
                rows[target] = {j: value*c for j, c in rows[target].items()}
            maximum = max(maximum, sum(abs(c) for c in rows[target].values()))
            converted.append(['scalar', [op, target, origin, str(value)], frame])
        else:
            review.need(event[0] in ('native', 'monomial'), 'Closed transformation grammar')
            target, before, after = event[1:4]
            review.need(0 <= target < 224 and current[target] == before, 'Actual transformation entry')
            rank = event[4] if event[0] == 'native' else 0
            record = word['native_recipes'][event[-1]]
            review.need(record['rank'] == rank and (rank > 0) == (event[0] == 'native'),
                        'Exact native or monomial rank')
            review.need(rank > 0 or record['right'] is None, 'One map for each zero-rank exit')
            current[target] = after
            converted.append(event)
    review.need(current == word['final'] and current[224:] == word['start'][224:],
                'All final frames and all 416 unchanged other roles')
    review.need(review.reverse(converted) == review.response_columns(response, direction),
                'Every input column of the complete coded word')
    profile = Counter(e[4] for e in word['events'] if e[0] == 'native')
    return {
        'all_input_columns': 640, 'untouched_arbitrary_roles': 416,
        'owned_fields': 0, 'private_fields': 0, 'native_profile': dict(sorted(profile.items())),
        'native_children': sum(profile.values()), 'native_mass': sum(r*n for r, n in profile.items()),
        'inline_monomials': sum(e[0] == 'monomial' for e in word['events']),
        'external_endpoint_maps': len(word['endpoint_adapters']),
        'native_side_map_bound': 2*sum(profile.values()),
        'real_scalar_primitives': review.scalar_price(converted),
        'maximum_child_rank': max(profile), 'top_level_array_norm_bound': str(maximum),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    review = load('accepted_low_native_review', BASE/'check_native.py',
                  'e397b24015a75b61b71562560d82db22dd02c754840a35d2b74fc668180a2a56')
    need = review.need
    review.frozen(BASE, 'NATIVE-REVIEW-FREEZE.json',
                  'cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976')
    review.frozen(BASE, 'EXTENSIONS-REVIEW-FREEZE.json',
                  'c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c')
    review.frozen(OLD, 'FREEZE.json',
                  'bc0352b29a7a7244ebea40e8b53e44fa5d16dbb645db87eecbe3e02cf3bbaf46')
    review.frozen(SOURCE, 'CODED-EXITS-FREEZE.json',
                  'f466ce7bc9d6f5459462acd1799f269a6c2685aea124a3d18f579d542f269936')
    payload = json.loads(review.read(SOURCE/'coded-normal/CODED-EXITS-PROGRAM.json.gz',
                                    '7f7efbd4a080f641b7ffcb774c677c66344de60d57c6ecc67cdfc0e6f2f6f73d', True))
    native = json.loads(review.read(SOURCE/'native-normal-v2/NATIVE-PROGRAM.json.gz',
                                   'e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558', True))
    odd = json.loads(review.read(SOURCE/'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
                                'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4', True))
    previous = json.loads(review.read(LANES/'oblique-native-20261017/matched-left-gauge/LEFT-GAUGE-PROGRAM.json.gz',
                                     '437f96b00ae04f410c55f3501ac28bc103e0b416005459c661ac02794c0f9891', True))
    known = accepted_exits(previous, need)
    cyclic = json.loads(review.read(LANES/'independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json',
                                   '3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585'))
    gauge = json.loads(review.read(LANES/'coherent-port/isotropic-pair-gauge-20261018/GAUGE-PROGRAMS.json',
                                  '20f14f021623761160b0ef461904b38f82efdc7dd0c4008271620415bf747701'))
    phase_path = HERE.parent/'isotropic-pair-review-20261018/check.py'
    phase_pin = 'e428f575ad93a8ade3a92b641a2b5eef111519f03ba5cceca4cd4957f008ba18'
    review.read(phase_path, phase_pin)
    phase = load('coded_full_spatial', phase_path, phase_pin)
    raw = {'rank30': native['providers'], 'rank16': odd['providers']}
    need(payload['responses'] == {'rank30': native['response'], 'rank16': odd['model']['response']},
         'Exact accepted response matrices')
    families = payload['providers_by_response_and_code']
    need(set(families) == {'rank30', 'rank16'}, 'Both response families')
    full = [['C', 1 << j, 1] for j in range(9)]
    w = gauge['W']['circuit']
    need(phase.compile_circuit(w) == phase.gauge(9, 45, 1), 'Exact W phase convention')
    large = {p for pair in cyclic['pair_codes'] for p in pair['ports']}
    need(len(large) == 48, 'Exact 48-port code support')
    q = cyclic['ports']
    cases, reports, controls = {}, {}, {}
    for name, codes in families.items():
        need(set(codes) == {'W48_I64', 'W112'}, 'Both output representations')
        reports[name] = {}
        response = [{int(k): F(v) for k, v in row.items()} for row in payload['responses'][name]]
        for code, providers in codes.items():
            selection = large if code == 'W48_I64' else set(range(112))
            need(set(providers) == {'base', 'extra'}, 'Both physical providers')
            reports[name][code] = {}
            for provider, directions in providers.items():
                need(set(directions) == {'forward', 'backward'}, 'Both directions')
                reports[name][code][provider] = {}
                for direction, word in directions.items():
                    old = raw[name][provider][direction]
                    need(word['start'] == old['start'] and word['source_pair_codes'] == cyclic['pair_codes'],
                         'Exact input frames and source pair-code metadata')
                    need(word['gauge_circuit'] == w and word['left_W_ports'] == sorted(selection)
                         and word['raw_output_ports'] == sorted(set(range(112))-selection),
                         'Exact output gauge and port partition')
                    need(word['frames'][:len(old['frames'])] ==
                         [{'kind': 'canonical', 'basis': basis} for basis in old['frames']],
                         'Exact original ordered frame bases')
                    need(len(word['frames']) == len(old['frames'])+1+len(selection),
                         'Only the required output frames are added')
                    adapters = [r for r in old['endpoint_adapters']
                                if r['role'] == 'source' or r['port'] not in selection]
                    need(word['endpoint_adapters'] == adapters, 'Only coded target adapters are removed')
                    need(len(word['events']) == len(old['events']), 'Same event positions')
                    changed_x, changed_y = [], []
                    for a, b in zip(old['events'], word['events']):
                        if a[0] == 'scalar':
                            op, target, origin, value = a[1]
                            need(b[0] == 'scalar' and parse(b) == (op, target, origin, F(value)),
                                 'Exact scalar schema conversion and unchanged content')
                            continue
                        _, target, before, after, rank, key = a
                        is_x = target in selection and after == 1
                        is_y = 112 <= target < 224 and target-112 in selection and after == old['final'][target]
                        if not (is_x or is_y):
                            need(b == a and word['native_recipes'][key] == old['native_recipes'][key],
                                 'Exact inherited native occurrence and recipe')
                            continue
                        need(b[1:3] == a[1:3], 'Changed exit has the exact old role and entry frame')
                        if is_x:
                            circuit = full+w
                            changed_x.append(target)
                        else:
                            circuit = [['C', q[target-112], -1]]+full+w
                            changed_y.append(target-112)
                        after_frame = word['frames'][b[3]]
                        need(after_frame['kind'] == 'literal' and after_frame['circuit'] == circuit,
                             'Exact ordered physical output circuit')
                        basis = old['frames'][before]
                        identity = phase_key(basis, circuit)
                        record = word['native_recipes'][b[-1]]
                        if identity in cases:
                            need(cases[identity]['record'] == record, 'Repeated physical exit is exact')
                        else:
                            cases[identity] = {'basis': basis, 'circuit': circuit, 'record': record, 'uses': 0}
                        cases[identity]['uses'] += 1
                        if is_y and len(controls) < 2:
                            expected = phase.compile_circuit(circuit)
                            adapter = next(r for r in old['endpoint_adapters']
                                           if r['role'] == 'target' and r['port'] == target-112)
                            wrong = {
                                'old_target_adapter_retained': expected+phase.inverse(phase.recipe(adapter)),
                                'W_on_wrong_side': phase.compile_circuit(w+full+[['C', q[target-112], -1]]),
                            }
                            for label, operation in wrong.items():
                                if label not in controls:
                                    column = next((x for x in range(512)
                                                   if phase.run(operation, x) != phase.run(expected, x)), None)
                                    if column is not None:
                                        controls[label] = {'spatial_column': column, 'port': target-112}
                    need(sorted(changed_x) == sorted(selection) and sorted(changed_y) == sorted(selection),
                         'Exactly one coded exit per selected bank role')
                    for p in range(112):
                        if p in selection:
                            need(word['frames'][word['final'][p]]['circuit'] == full+w
                                 and word['frames'][word['final'][112+p]]['circuit'] ==
                                 [['C', q[p], -1]]+full+w, 'Every coded final physical frame')
                        else:
                            need(word['final'][p] == old['final'][p]
                                 and word['final'][112+p] == old['final'][112+p], 'Every raw final frame')
                    report = ledger(word, response, direction, review)
                    profile = {
                        ('rank30', 'W48_I64'): {1: 988, 2: 48, 4: 55, 5: 55, 6: 9, 7: 9},
                        ('rank30', 'W112'): {1: 988, 2: 48, 5: 55, 6: 55, 7: 9, 8: 9},
                        ('rank16', 'W48_I64'): {1: 1472, 2: 112},
                        ('rank16', 'W112'): {1: 1408, 2: 112, 3: 64},
                    }[name, code]
                    need(report['native_profile'] == profile and report['native_mass'] ==
                         (1696 if code == 'W48_I64' else 1824), 'Complete changed native profile and mass')
                    need(report['real_scalar_primitives'] == (5288 if name == 'rank30' else 7384)
                         and report['inline_monomials'] == 48
                         and report['external_endpoint_maps'] == 224-len(selection), 'Complete local invoice')
                    bound = ('46' if direction == 'forward' else '30') if name == 'rank30' else '22'
                    need(report['top_level_array_norm_bound'] == bound, 'Unchanged complete prefix bound')
                    reports[name][code][provider][direction] = report
    need(len(cases) == 352, 'All distinct changed physical exits')
    inherited, fresh = [], []
    for identity, case in cases.items():
        record = case['record']
        if identity in known:
            need(record == known[identity], 'Exact accepted old exit recipe')
            inherited.append(identity)
            continue
        source = phase.canonical(case['basis'])
        target = phase.compile_circuit(case['circuit'])
        result = phase.compare(source+phase.recipe(record), target, 'Fresh coded exit')
        fresh.append({'ordered_frame_and_output': json.loads(identity), 'rank': record['rank'],
                      'occurrences': case['uses'], **result})
        if record['rank'] > 0 and 'rank_reduced_without_new_recipe' not in controls:
            bad_record = dict(record, rank=record['rank']-1)
            bad = source+phase.recipe(bad_record)
            column = next((x for x in range(512) if phase.run(bad, x) != phase.run(target, x)), None)
            need(column is not None, 'A claimed smaller child is rejected')
            controls['rank_reduced_without_new_recipe'] = {'spatial_column': column}
        if len(fresh) % 16 == 0:
            print('Independent fresh coded exits', len(fresh), '/ 304', flush=True)
    need(len(inherited) == 48 and len(fresh) == 304, 'Exact old and fresh coded phase split')
    need(len(controls) == 3, 'All physical negative controls')
    result = {
        'status': 'PASS_INDEPENDENT_LOW_DISPLACEMENT_CODED_EXITS',
        'literal_words': reports, 'distinct_changed_exits': 352,
        'accepted_previous_exits': [json.loads(key) for key in inherited],
        'fresh_exit_checks': fresh, 'changed_exit_occurrences': sum(c['uses'] for c in cases.values()),
        'negative_controls': controls, 'spatial_columns_per_fresh_exit': 512,
        'scope': 'Exact changed local output contracts and native profiles. No free code removal, stage transition, productive helper progress, recursive hosting, or complete supplier claim.',
    }
    for name, value in (('REVIEW.json', result), ('INPUTS.json', review.INPUTS)):
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
