#!/usr/bin/env python3
"""Offline integrity, literal-profile binding and exact arithmetic checks.

This does not rerun Lean, the finite words, CRT profiling, or source discovery.
Use verify_lean.py and the source-pinned package commands for those layers.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_moment as moment
import independent_assembly as assembly


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run with Python assertions enabled')
    manifest = read(HERE / 'publication-manifest.json')
    for name, expected in manifest['files'].items():
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe manifest path')
        path = HERE / relative
        require(path.is_file() and not path.is_symlink(), 'Missing regular artifact: ' + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Changed artifact: ' + name)
    print('PASS publication hashes:', len(manifest['files']), 'files', flush=True)
    results = {}
    candidates = [
        ('PR64', 'selected-certificate.json', 'next-proof/analytic'),
        ('PR68', 'transfer-proof/latest-analytic/pr68-candidate.json', 'transfer-proof/latest-analytic'),
        ('PR73', 'full-transfer/latest-analytic/pr73-candidate.json', 'full-transfer/latest-analytic'),
    ]
    for label, candidate, proof_dir in candidates:
        path = HERE / candidate
        data = read(path)
        exact = moment.run(path, search=False)
        public = data.get('assembly', data.get('preferred', {}).get('assembly'))
        checked = assembly.assemble(data, Q(data['bit_saving']), Q(data['kappa']), Q(public['parameters']['h']))
        for key in ('constraints', 'margins'):
            require(checked[key] == {k: Q(v) for k, v in public[key].items()}, label + ' assembly mismatch')
        checker = module('binding_' + label, HERE / proof_dir / 'check.py')
        binding = checker.check_binding(path) if label == 'PR64' else checker.check_binding(path, read(HERE / proof_dir / 'theorem-manifest.json'))
        results[label] = {'moment_gap': str(exact['certified_published_gap']), 'literal_binding': binding,
                          'inequalities': len(checked['constraints']), 'margins': len(checked['margins'])}
        print('PASS', label, 'literal Lean profile, exact characteristic and 47 inequalities / 7 margins', flush=True)
    # PR76 is an independently recorded finite-audit view, NOT a Lean profile.
    data = read(HERE / 'stream-transfer/audit/pr76-independent-receipt.json')
    candidate_path = HERE / 'stream-transfer/audit/pr76-arithmetic.json'
    public = read(candidate_path)
    source = read(HERE / 'stream-transfer/audit/pr76-SOURCE.json')
    require(hashlib.sha256(candidate_path.read_bytes()).hexdigest() == source['candidate_sha256'] == data['candidate_sha256'], 'PR76 immutable candidate hash')
    require(source['pin'] == data['pin'], 'PR76 source pin')
    for key in ('m', 'W', 'deficit', 'child_multiplicities'):
        require(public['profile'][key] == data[key], 'PR76 public profile differs: ' + key)
    require(public['profile']['total_rank'] == data['rank_mass'], 'PR76 public rank')
    require(all(public[k] == data[k] for k in ('bit_saving', 'kappa')), 'PR76 public parameters')
    rows = {int(t): n for t, n in data['child_multiplicities'].items()}
    require(sum(t*n for t, n in rows.items()) == data['rank_mass'], 'PR76 rank mass')
    require(data['m']*data['W']-data['rank_mass'] == data['deficit'], 'PR76 deficit')
    lo, hi = moment.moment(data['m'], data['W'], rows, Q(data['bit_saving']))
    next_lo, next_hi = moment.moment(data['m'], data['W'], rows, Q(data['bit_saving']) + Q(1, 10**18))
    require(hi < 1 < next_lo, 'PR76 accepted/adjacent characteristic')
    require([str(lo), str(hi)] == data['characteristic'], 'PR76 enclosure receipt')
    view = {'bit': {'m': data['m'], 'W': data['W'], 'maxchild': max(rows)}, 'finite_bridge': data['finite_bridge']}
    checked = assembly.assemble(view, Q(data['bit_saving']), Q(data['kappa']), Q(data['assembly']['h']))
    for key in ('constraints', 'margins'):
        require(checked[key] == {k: Q(v) for k, v in data['assembly'][key].items()}, 'PR76 assembly mismatch')
        require(checked[key] == {k: Q(v) for k, v in public['assembly']['assembly'][key].items()}, 'PR76 public assembly mismatch')
    results['PR76'] = {'moment_gap': str(1-hi), 'inequalities': 47, 'margins': 7,
                       'scope': 'Recomputed receipt arithmetic; full finite replay is a separate command; no literal Lean instantiation.'}
    print('PASS PR76 receipt arithmetic and updated finite bridge; no Lean claim', flush=True)
    combo = read(HERE / 'stream-transfer/experiments/combined-comparison.json')
    profile = combo['profile']
    rows = {int(t): n for t, n in profile['child_multiplicities'].items()}
    require(sum(t*n for t, n in rows.items()) == profile['total_rank'], 'Combined rank mass')
    require(profile['m']*profile['W']-profile['total_rank'] == profile['deficit'], 'Combined deficit')
    for h in (23, 25):
        base = HERE / 'stream-transfer/experiments/verification'
        for key, name in (('comparison_sha256', f'comparison-{h}.json'),
                          ('profile_sha256', f'balanced-split-{h}.bin.profiles.json')):
            require(hashlib.sha256((base/name).read_bytes()).hexdigest() == combo['inputs'][str(h)][key], 'Combined input hash')
    lo, hi = moment.moment(profile['m'], profile['W'], rows, Q(combo['bit_saving']))
    next_lo, next_hi = moment.moment(profile['m'], profile['W'], rows, Q(combo['excluded_next_bit_saving']))
    require(Q(combo['excluded_next_bit_saving']) == Q(combo['bit_saving']) + Q(1, 10**18), 'Combined adjacent grid')
    require(hi < 1 < next_lo, 'Combined characteristic and adjacent-grid rejection')
    view = {'bit': {**profile, 'maxchild': max(rows)}, 'finite_bridge': combo['finite_bridge']}
    checked = assembly.assemble(view, Q(combo['bit_saving']), Q(combo['kappa']), Q(combo['backoff']))
    for key in ('constraints', 'margins'):
        require(checked[key] == {k: Q(v) for k, v in combo['preferred']['assembly'][key].items()}, 'Combined assembly mismatch')
    prior = read(HERE / 'full-transfer/latest-analytic/pr73-candidate.json')
    require(Q(prior['kappa']) < Q(combo['kappa']) < Q(data['kappa']), 'Combined comparison against PR73 and PR76')
    results['balanced_split'] = {'moment_gap': str(1-hi), 'kappa': combo['kappa'],
                                 'inequalities': 47, 'margins': 7, 'scope': 'Finite conditional witness; no literal Lean instantiation.'}
    print('PASS balanced/split exact characteristic, assembly and comparison; below PR76', flush=True)
    with tempfile.TemporaryDirectory(prefix='transfer-negative-') as directory:
        output = Path(directory) / 'dominance.json'
        subprocess.run([sys.executable, '-B', str(HERE / 'full-transfer/audit/check_normalized_dominance.py'), '--output', str(output)], check=True)
        require(read(output) == read(HERE / 'full-transfer/audit/normalized-dominance-control.json'), 'Dominance receipt changed')
    result = {'status': 'PASS', 'hashed_files': len(manifest['files']), 'profiles': results,
              'scope': 'Offline integrity, exact arithmetic and literal data binding only; no new kernel, finite replay or CRT run.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS machine-transfer offline checkpoint')


if __name__ == '__main__':
    main()
