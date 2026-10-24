#!/usr/bin/env python3
"""Replay Cao Yifan's PR4610 through Chris R/Clear1nsight's PR5241 audit.

Douglas Colkitt, with substantial OpenAI assistance. Apache-2.0.
Frozen predecessor selection is explicitly remapped into the closed export.
Git is used only to authenticate canonical source ancestry and stored input blobs.
This is conditional finite verification, not a proof of the inherited framework.
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
PACKAGE = 'research/final4610-independent-admission'
ARITHMETIC = 'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json'
REVIEW = 'docs/research/pr-intake-evidence/pr4610'
HEAD = '20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'


def read(root, name):
    return json.loads(explicit_file(root, name).read_bytes())


def claim_from_sources(arithmetic, previous):
    result = dict(previous)
    kappa = Q(arithmetic['kappa'])
    margins = {k: Q(v) for k, v in arithmetic['outer']['margins'].items()}
    result.update(kappa=str(kappa), source_result=ARITHMETIC,
                  uniform_templates=[
                      {'family': 'complex', 'rank_encoding': arithmetic['compiler']['N'],
                       'saving': arithmetic['compiler']['uniform_saving']},
                      previous['uniform_templates'][1]],
                  ordinary_BIT_saving=arithmetic['ordinary_BIT']['ordinary_saving'],
                  admitted_BIT_saving=arithmetic['ordinary_BIT']['admitted'],
                  nine_outer_savings={k: str(v) for k, v in margins.items()},
                  limiting_outer_saving=str(min(margins.values())),
                  strict_limiting_slack=str(min(margins.values()) - kappa),
                  scope='Maintainer-reviewed conditional PR4610 construction using the PR5241 independent audit. The five PR4470 framework assumptions are unchanged. Uniform words are not materialized.')
    return result


def authenticate(root=ROOT):
    record = read(root, 'certificates/selected-result.json')
    require(record['audited_source_head'] == HEAD, 'Use the current selected replay')
    check(record, root)
    require(Q(record['kappa']) == Q('0.0030217758'), 'Wrong PR4610 selection')
    require(record['assumptions'] == read(root, 'certificates/checkpoints/frontier4470.json')['assumptions'],
            'Inherited assumptions changed')
    require(read(root, record['certificate']) == claim_from_sources(
        read(root, ARITHMETIC), read(root, 'certificates/frontier4470/CLAIM.json')),
        'Selected adapter differs from reviewed source budgets')
    manifest = read(root, record['source_manifest'])
    reviewed = read(root, REVIEW + '/REVIEWED-SOURCES.json')['files']
    mapping = manifest['replay_inputs']
    require(set(mapping) == set(reviewed), 'Replay closure differs from review')
    for target, origin in mapping.items():
        # Validate the target spelling without requiring its historical contents
        # to equal the current selection at that path.
        explicit_file(root, target)
        require(origin in manifest['files'] and manifest['files'][origin] == reviewed[target],
                'Replay input differs from reviewed bytes: ' + target)
    require(mapping['certificates/selected-result.json'] == 'certificates/checkpoints/frontier4470.json',
            'Historical baseline must be explicitly remapped')
    require(REVIEW + '/run_bounded.py' in manifest['files'], 'Unbound resource guard')
    return record, manifest


def export(root, work, manifest):
    require(not work.exists(), 'Replay directory must be fresh')
    work.mkdir(parents=True)
    source = work / 'source'
    for target, origin in manifest['replay_inputs'].items():
        dest = source / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(explicit_file(root, origin), dest)
    shutil.copyfile(root / REVIEW / 'run_bounded.py', work / 'run_bounded.py')
    return source


def main():
    require(not sys.flags.optimize, 'Optimized execution is not supported')
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-only', action='store_true')
    modes.add_argument('--work', type=Path)
    parser.add_argument('--preflight-only', action='store_true',
                        help='Export and check source/claim bindings, without scientific replay')
    args = parser.parse_args()
    require(not (args.check_only and args.preflight_only), 'Preflight requires --work')
    record, manifest = authenticate()
    if args.check_only:
        print('PASS_FRONTIER4610_BINDINGS_ONLY (not an operator replay)')
        return
    work = args.work.resolve()
    source = export(ROOT, work, manifest)
    # Only the canonical object store/HEAD is external to the exported files.
    # No submitted executable source is read from Git during mathematical replay.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')
           and k not in ('PYTHONPATH', 'PYTHONOPTIMIZE', 'LEAN_AUDIT_BIN')}
    env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_GRAFT_FILE=os.devnull, GIT_NO_LAZY_FETCH='1')
    gitdir = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '--absolute-git-dir'],
                                    env=env, text=True).strip()
    env.update(GIT_DIR=gitdir, GIT_WORK_TREE=str(source))
    scratch = work / 'scratch'
    scratch.mkdir()
    env['TMPDIR'] = str(scratch)
    command = [sys.executable, '-B', str(work / 'run_bounded.py'), 'admission', '660',
               '-I', str(source / PACKAGE / 'verify.py'), '--repo', str(source),
               '--receipt', str(work / 'COLD-REPLAY.json')]
    if args.preflight_only:
        command.append('--preflight-only')
    process = subprocess.run(command, env=env, cwd=work)
    bounded = read(work, 'review-evidence/admission.json')
    require(process.returncode == 0 and bounded['exit'] == 0 and bounded['resource_stop'] is None,
            'Bounded admission replay failed')
    receipt = read(work, 'COLD-REPLAY.json')
    wanted = 'PASS_PREFLIGHT_ONLY' if args.preflight_only else 'PASS_INDEPENDENT_FINAL4610_CONDITIONAL_ADMISSION'
    require(receipt['status'] == wanted and receipt['complete'] is not args.preflight_only,
            'Partial check cannot certify complete admission')
    require(Q(receipt['claim']['kappa']) == Q(record['kappa']), 'Replay claim mismatch')
    for target, origin in manifest['replay_inputs'].items():
        require(sha256(explicit_file(source, target).read_bytes()).hexdigest() == manifest['files'][origin],
                'Export input changed during replay: ' + target)
    report = {'status': 'PASS_FRONTIER4610_PREFLIGHT_ONLY' if args.preflight_only else
              'PASS_FRONTIER4610_WITH_SOURCE_BOUND_FOUNDATION_REUSE',
              'kappa': record['kappa'], 'source_manifest_sha256': sha256(
                  (ROOT / record['source_manifest']).read_bytes()).hexdigest(),
              'selected_record_sha256': sha256((ROOT / 'certificates/selected-result.json').read_bytes()).hexdigest(),
              'bounded_run': bounded, 'reused_foundation': manifest['reused_foundation'],
              'scientific_receipt': 'COLD-REPLAY.json', 'uniform_word_materialized': False}
    (work / 'VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'])


if __name__ == '__main__':
    main()
