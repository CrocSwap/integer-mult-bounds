#!/usr/bin/env python3
"""Replay PR4470 serially, reusing explicitly bound prior foundation reviews.

Douglas Colkitt, with substantial OpenAI assistance. Apache-2.0.
The source export is closed: unlisted checkout files cannot enter the replay.
This is finite conditional evidence, not a proof of the inherited theorem.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import os
import shutil
import subprocess
import sys
from verify_selected_result import check, explicit_file, require

ROOT = Path(__file__).resolve().parents[1]
HEAD = 'b9a13c1673e0e9697de410de16e8bbf3207a7363'
SOURCE = 'research/joint-helper-lattice/RESULT.json'
QUERY = 'research/query-thinned-controllers/RESULT.json'
REVIEW = 'docs/research/pr-intake-evidence/pr4470'
JOBS = [
    ('dependencies', 300, 'research/joint-helper-lattice/verify.py', '--part', 'dependencies'),
    ('native', 600, 'research/joint-helper-lattice/verify.py', '--part', 'native'),
    ('arithmetic', 300, 'research/joint-helper-lattice/verify.py', '--part', 'arithmetic'),
    ('all-final-transports', 300, 'review-evidence/all_final_transports.py'),
    ('independent-frame', 120, 'research/pr4470-frame-audit/verify.py'),
    ('independent-arithmetic', 300, 'research/pr4470-arithmetic-check/verify.py'),
    ('stage-zero', 120, 'research/stage-zero-commutation-audit/verify.py'),
    ('forced-translation', 120, 'research/stage-zero-forced-translation/verify.py'),
]


def read(root, name):
    return json.loads((root / name).read_text())


def claim_from_sources(result, query):
    """Schema adapter for orientation; every budget remains at its actual stage."""
    margins = {k: Q(v) for k, v in result['outer']['margins'].items()}
    kappa = Q(result['kappa'])
    return {
        'schema': 'proposed-conditional-integer-multiplication-claim/1',
        'kappa': str(kappa),
        'source_result': SOURCE,
        'uniform_templates': [
            {'family': 'complex', 'rank_encoding': result['compiler']['N'],
             'saving': result['compiler']['uniform_saving']},
            {'family': 'BIT before cover', 'rank_encoding': query['bit_strictification']['uniform_N'],
             'saving': query['ordinary_BIT']['before_cover']},
        ],
        'ordinary_BIT_saving': query['ordinary_BIT']['ordinary_saving'],
        'admitted_BIT_saving': query['ordinary_BIT']['admitted'],
        'nine_outer_savings': {k: str(v) for k, v in margins.items()},
        'limiting_outer_saving': str(min(margins.values())),
        'strict_limiting_slack': str(min(margins.values()) - kappa),
        'scope': 'Maintainer-reviewed conditional PR4470 construction. Inherited native/all-column, owned-erasure, whole-job, compiler, precision/tape, analytic, prime and recovery hypotheses remain. Uniform words are not materialized.',
    }


def authenticate(root=ROOT):
    record = read(root, 'certificates/selected-result.json')
    require(record['audited_source_head'] == HEAD, 'Use the current selected reproduction command')
    check(record, root)
    require(Q(record['kappa']) == Q('0.00302015'), 'Wrong PR4470 selection')
    require(read(root, record['certificate']) == claim_from_sources(read(root, SOURCE), read(root, QUERY)),
            'Selected adapter differs from reviewed source budgets')
    manifest = read(root, record['source_manifest'])
    reviewed = read(root, REVIEW + '/REVIEWED-SOURCES.json')['files']
    mapping = manifest['replay_inputs']
    require(set(mapping) == set(reviewed), 'Replay closure differs from reviewed input inventory')
    for target, source in mapping.items():
        # Check target spelling separately; historical provenance is deliberately
        # remapped from frozen files, never from the new selected record.
        explicit_file(root, target)  # target also exists in the checkout
        require(source in manifest['files'], 'Unbound replay source')
        require(manifest['files'][source] == reviewed[target], 'Replay source differs from review')
    return record, manifest


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check-only', action='store_true')
    modes.add_argument('--work', type=Path)
    args = parser.parse_args()
    record, manifest = authenticate()
    if args.check_only:
        print('PASS_FRONTIER4470_BINDINGS_AND_REPLAY_PLAN (not an operator replay)')
        return
    work = args.work.resolve()
    require(not work.exists(), 'Replay directory must be fresh')
    work.mkdir(parents=True)
    source = work / 'source'
    source.mkdir()
    for target, origin in manifest['replay_inputs'].items():
        dest = source / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / origin, dest)
    for origin, target in [(REVIEW + '/run_bounded.py', 'run_bounded.py'),
                           (REVIEW + '/all_final_transports.py', 'review-evidence/all_final_transports.py')]:
        require(origin in manifest['files'], 'Unbound replay harness')
        dest = source / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / origin, dest)
    scratch = work / 'scratch'
    scratch.mkdir()
    env = dict(os.environ, TMPDIR=str(scratch))
    report = {'status': 'RUNNING', 'kappa': record['kappa'],
              'selected_record_sha256': sha256((ROOT / 'certificates/selected-result.json').read_bytes()).hexdigest(),
              'source_manifest_sha256': sha256((ROOT / record['source_manifest']).read_bytes()).hexdigest(),
              'reused_foundation': manifest['reused_foundation'],
              'serial': True, 'sampled_memory_limit_kib': 1048576, 'runs': []}
    receipt = work / 'VALIDATION.json'
    def save():
        receipt.write_text(json.dumps(report, indent=2) + '\n')
    save()
    for name, limit, *command in JOBS:
        process = subprocess.run([sys.executable, '-B', str(source / 'run_bounded.py'),
                                  name, str(limit), *command], cwd=source, env=env)
        result = source / 'review-evidence' / (name + '.json')
        row = json.loads(result.read_text()) if result.exists() else {'exit': process.returncode}
        report['runs'].append({'name': name, **row})
        report['status'] = 'RUNNING' if process.returncode == 0 else 'FAIL'
        save()
        require(process.returncode == 0 and row['exit'] == 0 and row['resource_stop'] is None,
                'Bounded selected replay failed: ' + name)
    for target, origin in manifest['replay_inputs'].items():
        require(sha256((source / target).read_bytes()).hexdigest() == manifest['files'][origin],
                'Replay mutated a frozen input: ' + target)
    report['status'] = 'PASS_FRONTIER4470_WITH_SOURCE_BOUND_FOUNDATION_REUSE'
    save()
    print(report['status'], 'kappa=' + record['kappa'])


if __name__ == '__main__':
    main()
