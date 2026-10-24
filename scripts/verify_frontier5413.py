#!/usr/bin/env python3
"""Serial, closed-export replay of the selected conditional PR5413 construction.

Douglas Colkitt, with substantial OpenAI Codex assistance. Apache-2.0.
The three frozen packages authenticate their own source ancestry offline.
The previously reviewed PR4610 foundation is explicitly reused, not rerun.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
binding = runpy.run_path(str(ROOT / 'scripts/verify_selected_result.py'))
check, require, explicit_file = (binding[k] for k in ('check', 'require', 'explicit_file'))
REVIEW = 'docs/research/pr-intake-evidence/pr5413'
PRIMARY = 'research/coupled-helper-neutral-completion'
PROVIDER = 'research/coupled-provider-independent-audit'
COMPANION = 'research/neutral632-independent-verification'
PACKAGES = [PROVIDER, PRIMARY, COMPANION]
KAPPA = Q('0.003027288235')
PRIMARY_STAGES = ['source-loading', 'helper-aliases', 'local', 'global',
                  'caller-binding', 'invoice-funding', 'precision', 'conjunction']
PROVIDER_STAGES = ['algebra', 'same-chart-control', 'budget', 'local-envelope', 'clifford-proof']


def read(root, path):
    return json.loads(explicit_file(root, path).read_bytes())


def claim_from_sources(funding, previous):
    result = dict(previous)
    kappa = Q(funding['kappa'])
    margins = {k: Q(v) for k, v in funding['outer']['margins'].items()}
    result.update(kappa=str(kappa), source_result=PRIMARY + '/reports/expected/funding.json',
                  uniform_templates=[{'family': 'complex', 'rank_encoding': '2^' + str(funding['H']),
                                      'saving': funding['outer']['parameters']['complex_uniform_saving']},
                                     previous['uniform_templates'][1]],
                  ordinary_BIT_saving=funding['ordinary_BIT']['actual'],
                  admitted_BIT_saving=funding['ordinary_BIT']['admitted'],
                  nine_outer_savings={k: str(v) for k, v in margins.items()},
                  limiting_outer_saving=str(min(margins.values())),
                  strict_limiting_slack=str(min(margins.values()) - kappa),
                  scope='Maintainer-reviewed conditional PR5413 complete neutral caller, with PR5407 provider and PR5414 companion audits. The five selected framework assumptions are unchanged. Uniform words are not materialized.')
    return result


def authenticate(root=ROOT):
    record = read(root, 'certificates/selected-result.json')
    require(record['audited_source_head'] == '0c1fa2f47fb5ea17b93a4b67063d08e49cc38e51',
            'Use the current selected replay')
    check(record, root)
    require(Q(record['kappa']) == KAPPA, 'Wrong PR5413 selection')
    require(record['assumptions'] == read(root, 'certificates/checkpoints/frontier4610.json')['assumptions']
            == read(root, PRIMARY + '/CLAIMS.json')['assumptions'], 'Inherited assumptions changed')
    require(read(root, record['certificate']) == claim_from_sources(
        read(root, PRIMARY + '/reports/expected/funding.json'),
        read(root, 'certificates/frontier4610/CLAIM.json')), 'Selected adapter differs from source budgets')
    manifest = read(root, record['source_manifest'])
    require(manifest['package_roots'] == PACKAGES, 'Changed scientific replay package set')
    expected = {n for n in manifest['files'] if any(n.startswith(p + '/') for p in PACKAGES)}
    expected |= {REVIEW + '/' + n for n in ('run_bounded.py', 'macos_replay.py', 'macos_engine.py')}
    require(manifest['replay_inputs'] == {n: n for n in sorted(expected)}, 'Incomplete replay closure')
    for package in PACKAGES:
        actual = {p.relative_to(root).as_posix() for p in (root / package).rglob('*') if p.is_file()}
        require(actual == {n for n in expected if n.startswith(package + '/')}, 'Undeclared package file')
    return record, manifest


def validate_receipts(provider, primary, companion):
    for receipt, stages, status in (
        (provider, PROVIDER_STAGES, 'PASS_INDEPENDENT_PARTIAL_PROVIDER_AND_CONDITIONAL_BUDGET'),
        (primary, PRIMARY_STAGES, 'PASS_CONDITIONAL_COMPLETE_NEUTRAL_CALLER_AND_FUNDED_KAPPA')):
        require(receipt['status'] == status, 'Partial or failed scientific receipt')
        require([r['name'] for r in receipt['runs']] == stages
                and all(r['returncode'] == 0 for r in receipt['runs']), 'Incomplete stage schedule')
        require(set(receipt['fresh_scientific_summary']) == set(stages), 'Missing stable-output comparison')
    require(Q(primary['scope']['candidate_kappa']) == KAPPA, 'Replayed kappa differs')
    require(companion['status'] == 'PASS_INDEPENDENT_SCREEN_AND_RETAINED_APPLICABILITY_EVIDENCE'
            and companion['fresh_necessary_screen'] is True and companion['inputs_unchanged'] is True,
            'Companion integrity-only check is not a scientific replay')
    require(companion['primary_head'] == '0c1fa2f47fb5ea17b93a4b67063d08e49cc38e51',
            'Companion refers to another construction')


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-only', action='store_true')
    modes.add_argument('--work', type=Path)
    args = parser.parse_args()
    record, manifest = authenticate()
    if args.check_only:
        print('PASS_FRONTIER5413_BINDINGS_ONLY (not a scientific replay)')
        return
    work = args.work.resolve()
    require(not work.exists(), 'Replay directory must be fresh')
    work.mkdir(parents=True)
    source = work / 'source'
    for target, origin in manifest['replay_inputs'].items():
        dest = source / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(explicit_file(ROOT, origin), dest)
    shutil.copy2(source / REVIEW / 'run_bounded.py', work / 'run_bounded.py')
    scratch = work / 'scratch'
    scratch.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')
           and k not in ('PYTHONPATH', 'PYTHONOPTIMIZE', 'PYTHONHOME', 'LEAN_AUDIT_BIN')}
    env.update(TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE='1')
    guards = {}
    for name, package, timeout in [('provider', PROVIDER, 660), ('primary', PRIMARY, 660),
                                   ('companion', COMPANION, 120)]:
        engine = ['-I']
        if sys.platform == 'darwin':
            engine += [str(source / REVIEW / 'macos_replay.py')]
        engine += [str(source / package / 'verify.py')]
        if name != 'companion':
            engine += ['--output', str(work / (name.upper() + '-REPLAY.json'))]
        process = subprocess.run([sys.executable, '-I', '-B', str(work / 'run_bounded.py'),
                                  name, str(timeout), *engine], cwd=work, env=env)
        guard = read(work, 'review-evidence/' + name + '.json')
        require(process.returncode == 0 and guard['exit'] == 0 and guard['resource_stop'] is None,
                'Bounded ' + name + ' replay failed; inspect review-evidence logs')
        guards[name] = guard
    companion = json.loads((work / 'review-evidence/companion.log').read_text().splitlines()[-1])
    (work / 'COMPANION-REPLAY.json').write_text(json.dumps(companion, indent=2) + '\n')
    validate_receipts(read(work, 'PROVIDER-REPLAY.json'), read(work, 'PRIMARY-REPLAY.json'), companion)
    for target, origin in manifest['replay_inputs'].items():
        require(sha256(explicit_file(source, target).read_bytes()).hexdigest() == manifest['files'][origin],
                'Export input changed during replay: ' + target)
    authenticate()  # Catch any source/selection changes while engines ran.
    report = {'status': 'PASS_FRONTIER5413_WITH_SOURCE_BOUND_FOUNDATION_REUSE', 'complete': True,
              'kappa': record['kappa'], 'source_manifest_sha256': sha256(
                  (ROOT / record['source_manifest']).read_bytes()).hexdigest(),
              'selected_record_sha256': sha256((ROOT / 'certificates/selected-result.json').read_bytes()).hexdigest(),
              'bounded_runs': guards, 'reused_foundation': manifest['reused_foundation'],
              'scientific_receipts': ['PROVIDER-REPLAY.json', 'PRIMARY-REPLAY.json', 'COMPANION-REPLAY.json'],
              'platform': sys.platform, 'darwin_RLIMIT_AS_adapter': sys.platform == 'darwin',
              'uniform_word_materialized': False, 'unconditional_or_formal_theorem': False}
    (work / 'VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
