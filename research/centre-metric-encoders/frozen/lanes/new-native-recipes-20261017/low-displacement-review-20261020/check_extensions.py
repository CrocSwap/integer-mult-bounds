#!/usr/bin/env python3
"""Check exact path reuse and the fresh native edges in the frozen extensions."""
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as F
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
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
    review = load('rank30_native_review', HERE/'check_native.py',
                  'e397b24015a75b61b71562560d82db22dd02c754840a35d2b74fc668180a2a56')
    need = review.need
    review.read(HERE/'check_native.py',
                'e397b24015a75b61b71562560d82db22dd02c754840a35d2b74fc668180a2a56')
    review.frozen(HERE, 'NATIVE-REVIEW-FREEZE.json',
                  'cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976')
    review.frozen(LANES/'independent-review-20261017/response-extensions-review-20261020',
                  'FREEZE.json', '1c20e6736b1109ce10746472d3e00d464d5ea2629fe30c37a9d51bd5b74feedc')
    base_receipts = {
        'REVIEW.json': 'ea1674fbd0549cbf9161f1754a9dc0cb76d9c257ef295b391da9271df91a1aa6',
        'INPUTS.json': '8729c993a8eac3ed60b96c414160a4be8be33fb013905942ca9bdf61df728d90',
    }
    for name, digest in base_receipts.items():
        a = (HERE/'normal'/name).read_bytes()
        b = (HERE/'optimized'/name).read_bytes()
        need(a == b, 'Completed independent base runs agree')
        review.read(HERE/'normal'/name, digest)
        review.read(HERE/'optimized'/name, digest)
    checked = json.loads((HERE/'normal/REVIEW.json').read_text())
    need(checked['status'] == 'PASS_INDEPENDENT_FULL_NATIVE_RANK30'
         and len(checked['native_phase_checks']) == 1141
         and len(checked['endpoint_phase_checks']) == 224, 'Complete base phase dependency')
    review.frozen(SOURCE, 'EXTENSIONS-FREEZE.json',
                  'aec99dd0638e635619b14ffd056ab2581424d765d435462aed94b8c8f882a689')
    raw = json.loads(review.read(SOURCE/'native-normal-v2/NATIVE-PROGRAM.json.gz',
                                 'e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558', True))
    base = raw['providers']['base']['forward']
    known = {}
    for key, record in base['native_recipes'].items():
        before, after = map(int, key.split(':'))
        pair = tuple(base['frames'][before]), tuple(base['frames'][after])
        need(pair not in known or known[pair] == record, 'Unambiguous base physical edge')
        known[pair] = record
    phase_path = HERE.parent/'isotropic-pair-review-20261018/check.py'
    phase_pin = 'e428f575ad93a8ade3a92b641a2b5eef111519f03ba5cceca4cd4957f008ba18'
    review.read(phase_path, phase_pin)
    phase = load('full_spatial_extension_review', phase_path, phase_pin)
    pins = {
        'reciprocal-large': ('reciprocal-normal-v2', 'e4df61bf4e121364ba53538eb2ad612bd314807cfb2050050d4595efce9cf416'),
        'odd-grid-rank16': ('odd16-normal-v2', 'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4'),
    }
    reports = {}
    for kind, (directory, digest) in pins.items():
        data = json.loads(review.read(SOURCE/directory/'EXTENSION-PROGRAM.json.gz', digest, True))
        need(data['kind'] == kind and set(data['providers']) == {'base', 'extra'}, 'Exact extension family')
        need(data['providers']['base'] == data['providers']['extra'], 'Both provider words are byte-equal')
        words = data['providers']['base']
        need(set(words) == {'forward', 'backward'}, 'Both extension directions')
        word = words['forward']
        ports = data['model']['ports']
        frames = word['frames']
        response = [{int(k): F(v) for k, v in row.items()} for row in data['model']['response']]
        need(data['model']['selected_ports'] == raw['selected_ports'], 'Actual selected partition')
        per_word, used = {}, set()
        for direction, current in words.items():
            need(current['frames'] == frames and current['native_recipes'] == word['native_recipes'],
                 'Directions share exact native phase geometry')
            need(current['start'] == base['start'] and current['final'] == base['final']
                 and current['endpoint_adapters'] == base['endpoint_adapters'],
                 'Exact retained endpoint arrays and adapters')
            for index in set(current['start']+current['final']):
                need(frames[index] == base['frames'][index], 'Exact ordered endpoint frame basis')
            report, edges = review.ledger(current, ports, response, direction)
            want = ({1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9}
                    if kind == 'reciprocal-large' else {1: 1520, 2: 64, 3: 48})
            need(report['native_profile'] == want and report['native_mass'] == 1792,
                 'Complete extension native invoice')
            need(report['real_scalar_primitives'] == (5288 if kind == 'reciprocal-large' else 7384),
                 'Complete extension scalar invoice')
            wanted_bound = ('30' if direction == 'forward' else '46') if kind == 'reciprocal-large' else '22'
            need(report['top_level_array_norm_bound'] == wanted_bound, 'Complete extension prefix bound')
            if kind == 'reciprocal-large':
                old = raw['providers']['base'][direction]
                need(current['frames'] == old['frames']
                     and current['native_recipes'] == old['native_recipes'],
                     'Reciprocal geometry and recipes are byte-equal')
                need([e for e in current['events'] if e[0] == 'native'] ==
                     [e for e in old['events'] if e[0] == 'native'],
                     'Reciprocal native occurrence sequence is byte-equal')
            per_word[direction] = report
            used |= edges
        need(used == set(word['native_recipes']), 'All and only the emitted extension recipes are checked')
        inherited, fresh = [], []
        frame_cache = {}

        def frame(index):
            if index not in frame_cache:
                frame_cache[index] = phase.canonical(frames[index])
            return frame_cache[index]

        for key, record in word['native_recipes'].items():
            before, after = map(int, key.split(':'))
            pair = tuple(frames[before]), tuple(frames[after])
            if pair in known:
                need(record == known[pair], 'Exact inherited recipe at the same ordered frame pair')
                inherited.append(key)
                continue
            result = phase.compare(frame(before)+phase.recipe(record), frame(after),
                                   kind+' native '+key, 1 << len(frames[after]))
            fresh.append({'edge': key, 'rank': record['rank'], **result})
            if len(fresh) % 40 == 0:
                print('Independent fresh extension edges', kind, len(fresh), flush=True)
        need((len(inherited), len(fresh)) == ((1141, 0) if kind == 'reciprocal-large' else (685, 876)),
             'Exact inherited and fresh phase counts')
        for direction, current in words.items():
            missing = list(current['events'])
            del missing[current['transfer_records'][0]['event']]
            need(review.reverse(missing) != review.response_columns(response, direction),
                 'An omitted transfer changes the full extension response')
        reports[kind] = {
            'literal_words': per_word, 'both_providers': ['base', 'extra'],
            'exact_inherited_frame_pairs': inherited, 'fresh_native_phase_checks': fresh,
            'inherited_endpoints': 224, 'owned_fields': 0, 'private_fields': 0,
            'untouched_arbitrary_roles': 416,
            'inverse_grid_implementation': 'Not supplied or priced by this native review.',
        }
        print('Literal extension', kind, 'PASS', flush=True)
    output = {
        'status': 'PASS_INDEPENDENT_NATIVE_EXTENSIONS',
        'extensions': reports, 'spatial_columns_per_fresh_edge': 512,
        'scope': 'Complete local native data responses and physical phases. Matrix and inverse-code claims require their separate reviews. No odd-grid implementation, productive helper progress, recursive host, stage or terminal construction, or full supplier claim.',
    }
    for name, value in (('EXTENSIONS-REVIEW.json', output), ('EXTENSIONS-INPUTS.json', review.INPUTS)):
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(output['status'], flush=True)


if __name__ == '__main__':
    main()
