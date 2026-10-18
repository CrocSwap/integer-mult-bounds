#!/usr/bin/env python3
"""Replay T37 with complete baseline coverage and recomputed final bindings.

PR942: Jonathan Capalbo; predecessor construction and verification credits are
retained in research/complex-t37-owners/NOTICE.md. Maintainer adapter by Douglas
Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_replay_coverage import check_selected, require


def check(work, baseline):
    require(not sys.flags.optimize, 'Supplier workers require assertions')
    parent = check_selected(baseline, baseline / 'ancestor')
    package = ROOT / 'research/complex-t37-owners'
    sys.path.insert(0, str(package))
    spec = importlib.util.spec_from_file_location('frontier942_binding', package / 'final_binding.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    binding = module.check(work, baseline)
    require(binding == module.read(work / 'FINAL-BINDING.json'),
            'Stored T37 final binding differs from the checked artifacts')
    recorded = module.read(work / 'RESULT.json')
    claim = module.read(package / 'CLAIM.json')
    require(recorded['status'] == 'PASS_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY', 'T37 status')
    require(recorded['kappa'] == binding['kappa'] and
            recorded['kappa_decimal'] == claim['kappa_decimal'], 'T37 result kappa')
    require(recorded['pins'] == binding['pins'] and
            recorded['final_binding_sha256'] == module.sha(work / 'FINAL-BINDING.json'),
            'T37 result source/binding pins')
    require(recorded['stages'] == module.read(work / 'STAGES.json') and
            recorded['stages'][-1]['name'] == 'final-binding', 'T37 complete final stage')
    required_sources = {'research/complex-t37-owners/' + name for name in
                        ('OWNERS.json.gz', 'ORDER.json', 'EDITS.json', 'prepare.py',
                         'replay.py', 'verify.py', 'final_binding.py')}
    require(set(recorded['source_sha256']) == required_sources, 'T37 source inventory')
    for name, digest in recorded['source_sha256'].items():
        require(module.sha(ROOT / name) == digest, 'T37 recorded source changed: ' + name)
    for key in ('roles', 'calls', 'prefix_bits', 'charged_prefix_bits'):
        require(recorded[key] == claim[key], 'T37 count mismatch: ' + key)
    require(recorded['row_coefficient'] == claim['physical_row_coefficient'], 'T37 row coefficient')
    require(Path(recorded['cold_baseline']).resolve() == baseline.resolve() and
            type(recorded['reused_completed_baseline']) is bool, 'T37 baseline provenance')
    require(recorded['reused_completed_baseline'] is
            (recorded['stages'][0]['name'] != 'baseline799-cold'), 'T37 reuse flag differs from stages')
    return dict(status='PASS_COMPLETE_PR942_COMPOSITION', kappa=binding['kappa'],
                decimal=recorded['kappa_decimal'], selected_binding=binding,
                ancestor_coverage=parent,
                reused_completed_baseline=recorded['reused_completed_baseline'],
                scope='Finite construction and complete evidence admission; inherited all-size/compiler, '
                      'realization, hosting, precision/tape, analytic and bit H1-H5 assumptions remain.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--baseline799', type=Path)
    p.add_argument('--check-only', action='store_true')
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    require(not sys.flags.optimize, 'Supplier workers require assertions')
    work = a.work.resolve()
    raw = work if a.check_only else work / 'replay'
    baseline = a.baseline799.resolve() if a.baseline799 else raw / 'baseline799'
    if not a.check_only:
        require(not work.exists() and not work.is_relative_to(ROOT), 'Use fresh external output')
        if a.baseline799:
            check_selected(baseline, baseline / 'ancestor')
        work.mkdir(parents=True)
        command = [sys.executable, '-B', str(ROOT / 'research/complex-t37-owners/verify.py'),
                   '--work', str(raw)]
        if a.baseline799:
            command += ['--baseline799', str(baseline)]
        subprocess.run(command, check=True, cwd=ROOT)
    result = check(raw, baseline)
    output = a.out if a.check_only else work / 'RESULT.json'
    if output:
        with output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['decimal'])


if __name__ == '__main__':
    main()
