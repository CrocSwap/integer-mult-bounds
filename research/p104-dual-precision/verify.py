#!/usr/bin/env python3
"""Exact local Hilbert-defect interface for PR2479's private-macro dual.

ywz65 with substantial OpenAI Codex assistance, Apache-2.0.
PR2096 supplies the all-cut Hilbert-defect method; no new method is claimed.
"""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'research/p104-native-channel/'
INPUTS = {BASE + p for p in ('NATIVE-RECIPES.json.gz', 'check_native.py',
          'inputs/LOWRANK-WITNESS.json', 'inputs/P104-FIXTURE.json', 'vendor/native_verify.py')}
RETAINED = {'source/pr2479/' + p for p in ('README.md', 'verify.py', 'SOURCES.json', 'WORD.json', 'RESULT.json')} | {'source/pr2096/README.md'}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def freeze(row):
    return {str(k): str(v) for k, v in sorted(row.items()) if v}


def source_word():
    live = [p for p in read(HERE / 'SOURCES.json')['files'] if p['usage'] == 'input']
    retained = read(HERE / 'PREDECESSORS.json')['files']
    require({p['path'] for p in live} == INPUTS, 'live source inventory')
    require({p['path'] for p in retained} == RETAINED, 'retained source inventory')
    for base, pins in ((ROOT, live), (HERE, retained)):
        for pin in pins:
            raw = (base / pin['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
            require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'], 'source Git blob: ' + pin['path'])
    spec = importlib.util.spec_from_file_location('credited_pr2479_dual', HERE / 'source/pr2479/verify.py')
    retained_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(retained_module)
    retained_module.ROOT = ROOT
    native, word = retained_module.compute()
    require(native == read(HERE / 'source/pr2479/RESULT.json'), 'retained native receipt')
    require(word == read(HERE / 'source/pr2479/WORD.json'), 'retained complete word')
    return word, native


def add(left, right, coefficient):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, F(0)) + coefficient * value
        if not out[key]:
            del out[key]
    return out


def scan(word):
    inputs = {name: {name: F(1)} for name in word['initial_frames']}
    errors = {name: {} for name in inputs}
    weights, kinds = {}, {}
    peaks = {key: {'value': F(1) if key == 'input' else F(0), 'cut': 0, 'register': 'X0', 'row': {'X0': F(1)} if key == 'input' else {}}
             for key in ('input', 'absolute', 'weighted', 'native')}
    discard_rows = []
    for cut, event in enumerate(word['program'], 1):
        op, target = event[:2]
        if op == 'erase':
            discard_rows.append({'cut': cut, 'input': freeze(inputs[target]), 'errors': freeze(errors[target])})
            del inputs[target], errors[target]
            continue
        if op == 'zero':
            inputs[target], errors[target] = {}, {}
        elif op == 'add':
            coefficient = F(event[3])
            inputs[target] = add(inputs[target], inputs[event[2]], coefficient)
            errors[target] = add(errors[target], errors[event[2]], coefficient)
            errors[target][cut] = F(1)
            weights[cut] = 1 + abs(coefficient)
            kinds[cut] = 'add'
        elif op == 'transport':
            errors[target][cut] = F(1)
            weights[cut] = F(1)
            kinds[cut] = 'transport'
        else:
            raise ValueError('unexpected event')
        candidates = {'input': inputs[target], 'absolute': errors[target],
                      'weighted': errors[target],
                      'native': {k: v for k, v in errors[target].items() if kinds[k] == 'transport'}}
        for kind, row in candidates.items():
            value = sum(abs(v) * (weights[k] if kind == 'weighted' else 1) for k, v in row.items())
            if value > peaks[kind]['value']:
                peaks[kind] = {'value': value, 'cut': cut, 'register': target, 'row': dict(row)}
    require(len(weights) == 4042 and len(discard_rows) == 8, 'defect/lifetime inventory')
    return peaks, inputs, errors, weights, kinds, discard_rows


def adjoint(word, cut, register):
    """Independent backward response; does not call the forward row updater."""
    current = {register: F(1)}
    defects = {}
    for index in range(cut - 1, -1, -1):
        event = word['program'][index]
        op, target = event[:2]
        if op == 'erase':
            require(target not in current, 'reverse lifetime collision')
        elif op == 'zero':
            current.pop(target, None)
        else:
            coefficient = current.get(target, F(0))
            if coefficient:
                defects[index + 1] = coefficient
                if op == 'add':
                    src = event[2]
                    updated = current.get(src, F(0)) + F(event[3]) * coefficient
                    if updated:
                        current[src] = updated
                    else:
                        current.pop(src, None)
    require(set(current) <= set(word['initial_frames']), 'reverse initial inventory')
    return current, defects


def execute_scalar(word, cut, initial, defects):
    """Actual rational execution on one collinear Hilbert direction."""
    values = {name: initial.get(name, F(0)) for name in word['initial_frames']}
    for index, event in enumerate(word['program'][:cut], 1):
        op, target = event[:2]
        if op == 'zero':
            values[target] = F(0)
        elif op == 'erase':
            del values[target]
        elif op == 'add':
            values[target] += F(event[3]) * values[event[2]] + defects.get(index, F(0))
        else:
            values[target] += defects.get(index, F(0))
    return values


def sign(value):
    return F(1 if value > 0 else -1)


def calculate():
    word, native = source_word()
    peaks, inputs, errors, weights, kinds, discarded = scan(word)
    expected = {'input': F(64), 'absolute': F(2393, 2), 'weighted': F(3025, 2), 'native': F(861, 2)}
    require({k: v['value'] for k, v in peaks.items()} == expected, 'all-cut constants')
    agreements = 0
    for name in inputs:
        initial, defects = adjoint(word, len(word['program']), name)
        require(initial == inputs[name] and defects == errors[name], 'independent full endpoint adjoint')
        agreements += len(initial) + len(defects)
    controls = []
    for kind, peak in peaks.items():
        initial, defects = adjoint(word, peak['cut'], peak['register'])
        expected_row = initial if kind == 'input' else defects
        if kind == 'native':
            expected_row = {k: v for k, v in defects.items() if kinds[k] == 'transport'}
        require(peak['row'] == expected_row, 'independent peak adjoint')
        initial_values = {k: sign(v) for k, v in peak['row'].items()} if kind == 'input' else {}
        injections = {} if kind == 'input' else {k: sign(v) * (weights[k] if kind == 'weighted' else 1) for k, v in peak['row'].items()}
        value = execute_scalar(word, peak['cut'], initial_values, injections)[peak['register']]
        require(value == peak['value'], 'sign-aligned attainment: ' + kind)
        controls.append('attained ' + kind + ' peak by literal scalar execution')
    require(peaks['absolute']['value'] > 450 and peaks['native']['value'] > 356, 'invalid forward-constant transfer not exposed')
    controls.append('attained dual errors exceed forward-only 450 and 356; no predecessor defect claimed')
    # Removing a private value cannot remove errors it has already exported.
    private_sites = []
    live_private = False
    for cut, event in enumerate(word['program'], 1):
        if event[0] == 'zero':
            live_private = True
        elif event[0] == 'erase':
            live_private = False
        elif live_private and event[1] == 'C':
            private_sites.append(cut)
    site, target, coefficient = next((site, name, row[site]) for name, row in errors.items() for site in private_sites if site in row)
    actual = execute_scalar(word, len(word['program']), {}, {site: F(1)})
    require(actual[target] == coefficient and coefficient != 0 and 'C' not in actual, 'private defect incorrectly cleared globally')
    private_witness = {'site': site, 'register': target, 'coefficient': str(coefficient)}
    controls.append('discarded private accumulator defect survives in public output')
    # Nonzero rational defects at every update, including all private lifetimes.
    dense = {site: F((-1 if site % 2 else 1) * (1 + site % 19), 13) for site in weights}
    initial_values = {name: F((i * 11) % 17 - 8, 7) for i, name in enumerate(inputs)}
    literal = execute_scalar(word, len(word['program']), initial_values, dense)
    for name in inputs:
        expected_value = sum(v * initial_values[k] for k, v in inputs[name].items()) + sum(v * dense[k] for k, v in errors[name].items())
        require(literal[name] == expected_value, 'dense defect response mismatch')
    controls.append('all 4042 dense rational defects agree with independent response maps')
    P, K = expected['input'], expected['weighted']
    guard_bits = next(g for g in range(1, 64) if 2**g >= K * (P + 1))
    require(guard_bits == 17 and K * (P + 1) == F(196625, 2), 'feedback sufficiency arithmetic')
    require(K / 2**17 < 1 and P*K / (2**17-K) <= 1, 'relative feedback guard')
    # Failure of this sufficient formula is not a lower bound on actual precision.
    require(P*K / (2**16-K) > 1, 'sixteen-bit formula control')
    controls.append('17-bit feedback formula succeeds; 16-bit sufficient-formula test fails')
    endpoint = {'inputs': {r: freeze(row) for r, row in sorted(inputs.items())},
                'errors': {r: freeze(row) for r, row in sorted(errors.items())}}
    return {'status': 'PASS_P104_DUAL_PRECISION', 'word_sha256': native['word_sha256'],
            'events': len(word['program']), 'independent_inputs': len(inputs), 'defect_sites': len(weights),
            'native_occurrences': native['operations']['transport'], 'native_rank_mass': native['rank_mass'],
            'peaks': {kind: {'value': str(p['value']), 'cut': p['cut'], 'register': p['register'], 'response': freeze(p['row'])} for kind, p in peaks.items()},
            'endpoint_input_max': str(max(sum(map(abs, row.values())) for row in inputs.values())),
            'endpoint_absolute_by_family': {p: str(max(sum(map(abs, row.values())) for name, row in errors.items() if name.startswith(p))) for p in ('X', 'Y', 'G', 'Q', 'D')},
            'independent_endpoint_coefficients': agreements,
            'endpoint_maps_sha256': hashlib.sha256(canonical(endpoint).encode()).hexdigest(),
            'private_discards': discarded, 'private_defect_witness': private_witness,
            'feedback': {'P': str(P), 'K': str(K), 'sufficient_guard_bits': guard_bits,
                         'threshold_K_times_P_plus_1': str(K * (P + 1))},
            'controls': controls,
            'limits': 'finite changed-word completed-instruction Hilbert defect contract; no rounded-child implementation, owner/storage admission, corrected supplier, precision-charge removal, all-size theorem or new kappa'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        with (HERE / 'RESULT.json').open('x', encoding='utf-8', newline='\n') as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write('\n')
    else:
        require(result == read(HERE / 'RESULT.json'), 'complete precision receipt mismatch')
    print('PASS_P104_DUAL_PRECISION input=64 absolute=2393/2 weighted=3025/2 native=861/2 guard=17 sites=4042 controls=8 no_new_kappa')


if __name__ == '__main__':
    main()
