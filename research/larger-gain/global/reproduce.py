#!/usr/bin/env python3
"""Replay the frozen 63+9 width-seven physical and exact arithmetic witness.

Default: rebuild the pinned baseline and all six local providers, then replay
owners, invoice and both exact assemblies. Existing complete replays may be
reused only after their source, stages, logs and output bindings are checked.
The optimization software is not needed to reproduce the retained witness.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
CANDIDATE = HERE / 'width7'
PROVIDERS = RESEARCH / 'providers'
CANDIDATE_RESULT_SHA256 = 'c8af1a546efcf6389b6a1def24ac23b6ac32df1a4418375743f8e9b0bec5986b'
SOURCE_MANIFEST = 'dd602912d0e60c9bb2befba446629ae531ea42a9d4fecda922f98aac40762c41'
PROVIDER_STATUS = 'PASS_SIX_PROVIDERS_FULL_LOCAL_REPLAY'
STATUS = 'PASS_PORTABLE_WIDTH7_GLOBAL_REPLAY'
NAMES = ('zero', 'four', 'eight')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def safe_file(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root), 'Receipt path escapes its directory')
    return path


def provider_stages():
    names = []
    for name in NAMES:
        names += [name + '-construct-fourcold', name + '-independent-composition', name + '-construct-width7']
        for kind in ('fourcold', 'width7'):
            key = kind + '-' + name
            names += [key + '-' + pivot for pivot in ('extra-506', 'extra-518', 'extra-530', 'inherited-494')]
            names += [key + ('-static44' if kind == 'fourcold' else '-scalar-omission-transfer')]
            if kind == 'fourcold' and name != 'zero':
                names += [key + '-rank5-omissions']
            names += [key + '-' + action for action in ('native', 'ledgers', 'independent-replay', 'wrappers')]
    names += [kind + '-' + name + '-phases' for name in NAMES for kind in ('fourcold', 'width7')]
    return names


def verify_providers(work, baseline):
    receipt, result = read(work / 'RECEIPT.json'), read(work / 'RESULT.json')
    require(receipt['status'] == result['status'] == PROVIDER_STATUS, 'Incomplete provider replay')
    require(receipt['source_manifest_sha256'] == SOURCE_MANIFEST, 'Wrong provider source')
    require(receipt['baseline_receipt_sha256'] == sha(baseline / 'RECEIPT.json'), 'Wrong provider baseline binding')
    expected = provider_stages()
    actual = [step['name'] for step in receipt['steps']]
    require(actual in (expected, ['baseline564'] + expected), 'Missing, repeated or reordered provider stage')
    require(read(work / 'STAGES.json') == receipt['steps'], 'Provider stage receipt mismatch')
    for step in receipt['steps']:
        require(step['exit_code'] == 0, 'Failed provider stage')
        require(sha(work / 'logs' / (step['name'] + '.log')) == step['log_sha256'], 'Changed provider log')
    inventory = {p.relative_to(work).as_posix(): sha(p) for p in work.rglob('*')
                 if p.is_file() and p != work / 'RECEIPT.json' and not p.is_relative_to(work / 'baseline564')}
    require(receipt['artifacts'] == inventory, 'Incomplete or changed provider artifact inventory')
    required_inputs = {'reproduce.py', 'build_suffix_kernels.py', 'audit_suffix_composition.py', 'build_entrance_promotions.py', 'audit_frame_promotions.py'}
    require(required_inputs <= set(receipt['provider_inputs']), 'Missing provider source bindings')
    for name, expected_hash in receipt['provider_inputs'].items():
        require(sha(safe_file(PROVIDERS, name)) == expected_hash, 'Changed provider input: ' + name)
    keys = {kind + '-' + name for kind in ('fourcold', 'width7') for name in NAMES}
    require(set(result['providers']) == keys, 'Wrong provider set')
    for key, summary in result['providers'].items():
        kind, name = key.split('-')
        local = safe_file(work, summary['local'])
        expected_dir = PROVIDERS / ('fourcold-' + name) / 'local' if kind == 'fourcold' else PROVIDERS / 'width7' / name
        require(local == work / key / 'local', 'Wrong provider local path')
        for field, filename in [('canonical_word_sha256', 'CANONICAL-WORD.json.gz'), ('programs_sha256', 'LOCAL-PROGRAMS.json.gz')]:
            require(summary[field] == sha(local / filename) == sha(expected_dir / filename), 'Provider deterministic output differs')
        checks, phase = read(local / 'LOCAL-CHECKS.json'), read(local / 'CLIFFORD-REVIEW.json')
        require(summary['profile'] == checks['forward']['paid_profile'] == checks['backward']['paid_profile'], 'Wrong provider profile')
        expected_edges = 2929 if kind == 'fourcold' else 3005
        require(summary['directed_edges'] == phase['directed_edges'] == expected_edges and phase['endpoint_adapters'] == 224,
                'Wrong phase coverage')
        require(phase['all_child_equalities_include_global_phase'] is True, 'Failed exact phase equality')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Pinned PR564 complex-allcold source package')
    parser.add_argument('--work', type=Path, required=True, help='Fresh output directory')
    parser.add_argument('--baseline', type=Path, help='Reuse a complete pinned PR564 baseline replay')
    parser.add_argument('--provider-work', type=Path, help='Reuse a complete source-bound six-provider replay')
    args = parser.parse_args()
    require(__debug__, 'Run without -O; inherited verifiers require assertions')
    source, work = args.source.resolve(), args.work.resolve()
    require(not work.exists() and not work.is_relative_to(source) and not work.is_relative_to(RESEARCH),
            'Use a fresh work directory outside source/research packages')
    spec = importlib.util.spec_from_file_location('provider_reproduction', PROVIDERS / 'reproduce.py')
    provider_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(provider_module)
    provider_module.verify_source(source)
    require(sha(CANDIDATE / 'RESULT.json') == CANDIDATE_RESULT_SHA256, 'Changed frozen result inventory')
    adaptation, retained = read(CANDIDATE / 'ADAPTATION.json'), read(CANDIDATE / 'RESULT.json')
    require(adaptation['source_manifest_sha256'] == retained['source_manifest_sha256'] == SOURCE_MANIFEST, 'Wrong adapter source')
    require(retained['status'] == 'PASS_WIDTH7_NATIVE_PHYSICAL_AND_EXACT_ASSEMBLY', 'Wrong retained witness')
    require(set(row['name'] for row in adaptation['files']) == {
        'bind_providers_portable.py', 'emit_allcold.py', 'audit_allcold.py', 'invoice_allcold.py',
        'assemble.py', 'assembly_controls.py', 'phase_timing_controls.py'}, 'Incomplete adapter inventory')
    for row in adaptation['files']:
        require(sha(CANDIDATE / 'code' / row['name']) == row['adapted_sha256'], 'Changed frozen adapter')
        require(sha(source / 'code' / row['name']) == row['source_sha256'], 'Changed upstream adapter source')
    require(sha(CANDIDATE / 'ADAPTATION.patch') == adaptation['patch_sha256'], 'Changed adaptation patch')
    for name, expected in retained['artifact_sha256'].items():
        require(sha(safe_file(CANDIDATE, name)) == expected, 'Changed frozen witness artifact: ' + name)
    work.mkdir(parents=True)
    (work / 'logs').mkdir()
    steps = []
    start = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)

    def run(name, script, *arguments, portable=True):
        command = [sys.executable, '-B']
        if portable:
            command.append(str(source / 'code/run_portable.py'))
        command += [str(script)] + list(map(str, arguments))
        logfile = work / 'logs' / (name + '.log')
        t = time.monotonic()
        print('RUN', name, flush=True)
        with logfile.open('w') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, env=env)
        steps.append(dict(name=name, command=command, script_sha256=sha(script), exit_code=result.returncode,
                          seconds=time.monotonic()-t, log_sha256=sha(logfile)))
        dump(work / 'STAGES.json', steps)
        if result.returncode:
            raise RuntimeError(name + ' failed\n' + logfile.read_text()[-6000:])
        print('PASS', name, flush=True)

    baseline = args.baseline.resolve() if args.baseline else work / 'baseline564'
    if not args.baseline:
        run('baseline564', source / 'verify.py', '--work', baseline)
    provider_module.verify_baseline(source, baseline)
    providers = args.provider_work.resolve() if args.provider_work else work / 'providers'
    if not args.provider_work:
        run('six-provider-replay', PROVIDERS / 'reproduce.py', '--source', source, '--baseline', baseline,
            '--work', providers, portable=False)
    verify_providers(providers, baseline)
    global_root = work / 'global'
    code = CANDIDATE / 'code'
    run('bind-providers', code / 'bind_providers_portable.py', '--baseline', baseline / 'baseline558',
        '--plain', providers / 'fourcold-eight/local', '--width7', providers / 'width7-eight/local',
        '--plan', CANDIDATE / 'PLAN.json', '--out', global_root)
    run('emit-owners', code / 'emit_allcold.py', '--base', global_root / 'base',
        '--owners', CANDIDATE / 'OWNERS.json.gz', '--plan', global_root / 'PLAN.json', '--out', global_root / 'hosted')
    run('independent-owners', code / 'audit_allcold.py', global_root / 'base', global_root / 'hosted',
        global_root / 'audit/ASYNC-AUDIT.json', '--mutation-controls')
    run('fresh-invoice', code / 'invoice_allcold.py', '--base', global_root / 'base', '--hosted', global_root / 'hosted',
        '--audit', global_root / 'audit', '--out', global_root / 'audit', '--retained-invoice',
        source / 'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
    run('exact-assembly', code / 'assemble.py', source, global_root, global_root / 'ASSEMBLY.json')
    run('admission-controls', code / 'assembly_controls.py', '--source-package', source,
        '--owner', global_root / 'audit/OWNERS-AND-PROFILE.json', '--invoice', global_root / 'audit/PREFIX-AND-INVOICE.json',
        '--out', global_root / 'ASSEMBLY-CONTROLS.json')
    run('phase-timing-controls', code / 'phase_timing_controls.py', source, global_root / 'base',
        global_root / 'audit', global_root / 'PHASE-TIMING-CONTROLS.json')
    assembly = read(global_root / 'ASSEMBLY.json')
    require(Fraction(assembly['kappa']) == Fraction('0.001600067494703216'), 'Unexpected new bound')
    require(assembly['conservative_kappa_decimal'] == '0.001600067491919801', 'Unexpected conservative bound')
    require(assembly['complex_profile'] == retained['profile'] and assembly['provider_counts'] == retained['provider_counts'], 'Changed selected profile')
    require(len(read(global_root / 'audit/ASYNC-AUDIT.json')['mutations_rejected']) == 16, 'Missing owner controls')
    controls = read(global_root / 'ASSEMBLY-CONTROLS.json')
    require(len(controls['rejected_controls']) == 89, 'Missing admission controls')
    result = dict(status=STATUS, kappa=assembly['kappa'], kappa_decimal=assembly['kappa_decimal'],
                  conservative_kappa_decimal=assembly['conservative_kappa_decimal'], profile=assembly['complex_profile'],
                  provider_counts=assembly['provider_counts'], source_head=adaptation['source_head'],
                  source_manifest_sha256=SOURCE_MANIFEST, baseline_receipt_sha256=sha(baseline / 'RECEIPT.json'),
                  provider_receipt_sha256=sha(providers / 'RECEIPT.json'), seconds=time.monotonic()-start,
                  baseline_reused=bool(args.baseline), providers_reused=bool(args.provider_work), scope=assembly['scope'])
    dump(work / 'RESULT.json', result)
    artifacts = {p.relative_to(work).as_posix(): sha(p) for p in work.rglob('*')
                 if p.is_file() and not p.is_relative_to(baseline) and not p.is_relative_to(providers)}
    dump(work / 'RECEIPT.json', dict(status=STATUS, source_manifest_sha256=SOURCE_MANIFEST,
         driver_sha256=sha(Path(__file__)), candidate_result_sha256=sha(CANDIDATE / 'RESULT.json'),
         baseline_receipt_sha256=sha(baseline / 'RECEIPT.json'), provider_receipt_sha256=sha(providers / 'RECEIPT.json'),
         steps=steps, artifacts=artifacts))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
