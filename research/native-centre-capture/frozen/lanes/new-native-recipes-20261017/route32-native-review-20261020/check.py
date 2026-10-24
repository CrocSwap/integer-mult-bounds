#!/usr/bin/env python3
"""Check the complete route32 native words and their fresh physical phases."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PREVIOUS = HERE.parent/'low-displacement-review-20261020'
SOURCE = LANES/'new-core-transfer-20261017/low-displacement-20261020'


def load(name, path, pin):
    if sha256(path.read_bytes()).hexdigest() != pin:
        raise ValueError('Independent interpreter pin: '+str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    review = load('accepted_native_review', PREVIOUS/'check_native.py',
                  'e397b24015a75b61b71562560d82db22dd02c754840a35d2b74fc668180a2a56')
    need = review.need
    review.frozen(PREVIOUS, 'NATIVE-REVIEW-FREEZE.json',
                  'cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976')
    review.frozen(PREVIOUS, 'EXTENSIONS-REVIEW-FREEZE.json',
                  'c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c')
    review.frozen(SOURCE/'route32', 'FREEZE.json',
                  '28354cf747adc5c2a10393f02035a936e0e0fa3f666717b419f4eaaeed1814af')
    payload = json.loads(review.read(SOURCE/'route32/native-normal/ROUTE32-NATIVE.json.gz',
                                    '2f037b4757c46efb849bcfd8ad6cc2919d8486c5a9001d6325152446caf0f3e5', True))
    model = json.loads(review.read(SOURCE/'route32/model-normal/ROUTE32-MODEL.json',
                                  '85d44223697700a916e4cffeb334c8f82179f6535f7b0db64a37eddf37bedf52'))
    need(payload['schema'] == 'route32-native-v1' and payload['model'] == model,
         'Exact frozen route32 model')
    sources = [
        ('rank30', 'native-normal-v2/NATIVE-PROGRAM.json.gz',
         'e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558'),
        ('rank16', 'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
         'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4'),
    ]
    accepted, known = {}, {}
    for name, relative, pin in sources:
        data = json.loads(review.read(SOURCE/relative, pin, True))
        old = data['providers']['base']['forward']
        accepted[name] = old
        for key, record in old['native_recipes'].items():
            before, after = map(int, key.split(':'))
            pair = tuple(old['frames'][before]), tuple(old['frames'][after])
            need(pair not in known or known[pair]['record'] == record,
                 'Accepted ordered phase pairs agree')
            known.setdefault(pair, {'record': record, 'sources': []})['sources'].append([name, key])
    cyclic = json.loads(review.read(LANES/'independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json',
                                   '3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585'))
    need(model['ports'] == cyclic['ports'], 'Actual supplier port directions')
    need(model['selected_ports'] == [] and model['ordinary_ports'] == list(range(112)),
         'Explicit empty selection and complete ordinary bank')
    phase_path = HERE.parent/'isotropic-pair-review-20261018/check.py'
    phase_pin = 'e428f575ad93a8ade3a92b641a2b5eef111519f03ba5cceca4cd4957f008ba18'
    review.read(phase_path, phase_pin)
    phase = load('route32_spatial_review', phase_path, phase_pin)
    need(set(payload['providers']) == {'base', 'extra'}, 'Both providers')
    need(payload['providers']['base'] == payload['providers']['extra'], 'Exact equal provider words')
    first = payload['providers']['base']['forward']
    frames = first['frames']
    base = accepted['rank16']
    response = [{int(k): F(v) for k, v in row.items()} for row in model['response']]
    need(len(response) == 112 and all(0 <= j < 112 for row in response for j in row),
         'Complete 112 by 112 response')
    reports, used, controls = {}, set(), {}
    for provider, words in payload['providers'].items():
        need(set(words) == {'forward', 'backward'}, 'Both native directions')
        reports[provider] = {}
        controls[provider] = {}
        for direction, word in words.items():
            need(word['frames'] == frames and word['native_recipes'] == first['native_recipes'],
                 'Exact common ordered phase geometry')
            need(word['start'] == base['start'] and word['final'] == base['final']
                 and word['endpoint_adapters'] == base['endpoint_adapters'],
                 'Exact accepted endpoint arrays and all 224 adapters')
            for index in set(word['start']+word['final']):
                need(frames[index] == base['frames'][index], 'Exact ordered endpoint frame')
            report, edges = review.ledger(word, model['ports'], response, direction)
            need(report['native_profile'] == {1: 944, 3: 48, 5: 64, 6: 64},
                 'Complete route32 native profile')
            need(report['native_children'] == 1120 and report['native_mass'] == 1792
                 and report['real_scalar_primitives'] == 4312,
                 'Complete route32 native and scalar invoice')
            need(report['top_level_array_norm_bound'] == '14', 'Complete route32 prefix bound')
            report['external_endpoint_maps'] = len(word['endpoint_adapters'])
            report['native_side_map_bound'] = 2*report['native_children']
            reports[provider][direction] = report
            used |= edges
            bad = list(word['events'])
            index = word['transfer_records'][0]['event']
            removed = bad.pop(index)
            need(review.reverse(bad) != review.response_columns(response, direction),
                 'Removal of a nonzero transfer changes the complete map')
            controls[provider][direction] = {'removed_event_index': index, 'removed_event': removed}
    need(used == set(first['native_recipes']) and len(used) == 1049,
         'All and only the complete native phase table is used')
    cache = {}

    def frame(index):
        if index not in cache:
            cache[index] = phase.canonical(frames[index])
        return cache[index]

    inherited, fresh = [], []
    for key, record in first['native_recipes'].items():
        before, after = map(int, key.split(':'))
        pair = tuple(frames[before]), tuple(frames[after])
        if pair in known:
            need(record == known[pair]['record'], 'Exact inherited ordered frame-pair recipe')
            inherited.append({'edge': key, 'accepted_sources': known[pair]['sources']})
            continue
        result = phase.compare(frame(before)+phase.recipe(record), frame(after),
                               'Route32 edge '+key, 1 << len(frames[after]))
        fresh.append({'edge': key, 'rank': record['rank'], **result})
        if len(fresh) % 24 == 0:
            print('Independent fresh route32 phases', len(fresh), '/ 297', flush=True)
    need(len(inherited) == 752 and len(fresh) == 297, 'Exact inherited and fresh phase counts')
    result = {
        'status': 'PASS_INDEPENDENT_ROUTE32_NATIVE',
        'literal_words': reports,
        'inherited_native_phases': inherited,
        'fresh_native_phases': fresh,
        'inherited_endpoint_phases': 224,
        'spatial_columns_per_fresh_edge': 512,
        'missing_transfer_controls': controls,
        'scope': 'Complete raw local native words for the pinned route32 response. Model, principal inverse and capture-code theorems require separate review. No root-gauge code, transition, odd-division implementation, productive helper progress, recursive hosting or complete supplier claim.',
    }
    for name, value in (('REVIEW.json', result), ('INPUTS.json', review.INPUTS)):
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
