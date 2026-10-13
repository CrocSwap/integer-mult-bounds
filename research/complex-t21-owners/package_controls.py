# SPDX-License-Identifier: Apache-2.0
"""Package and final-binding mutations; successful replay inputs stay read-only."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from common import HERE, read, require, dump, sha, identity, write_gzip
import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, required=True)
    parser.add_argument('--baseline799', type=Path, required=True)
    parser.add_argument('--ancestor741', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    work, baseline, ancestor = (p.resolve() for p in (args.replay, args.baseline799, args.ancestor741))
    require(not args.out.exists(), 'Control output must be new')
    stages = read(work/'STAGES.json')
    prior = read(work/'RESULT.json')
    reuse = prior['baseline_mode'] == 'explicit_checked_reuse'
    pins = verify.validate_pins()
    honest = verify.final_binding(work, stages, pins, reuse, baseline, ancestor)
    rejected = []

    def expect(name, action):
        try:
            action()
        except (ValueError, AssertionError, KeyError) as error:
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError('Accepted package control: '+name)

    expect('missing_parent_stage', lambda: verify.final_binding(work, [s for s in stages if s['name'] != 'check-parent'], pins, reuse, baseline, ancestor))
    expect('duplicated_success_stage', lambda: verify.final_binding(work, stages+[stages[-1]], pins, reuse, baseline, ancestor))
    original_read = verify.read

    def injected(relative, mutate):
        path = work/relative
        def altered(p):
            value = original_read(p)
            if Path(p).resolve() == path:
                value = copy.deepcopy(value)
                mutate(value)
            return value
        verify.read = altered
        try:
            return verify.final_binding(work, stages, pins, reuse, baseline, ancestor)
        finally:
            verify.read = original_read

    cases = [
        ('owner_deficit', 'global/audit/OWNERS-AND-PROFILE.json', lambda x: x.__setitem__('deficit', 5120)),
        ('t16_invocation_count', 'INDEPENDENT-T21.json', lambda x: x.__setitem__('calls', 144)),
        ('missing_t5_control', 'INDEPENDENT-T5.json', lambda x: x['controls_rejected'].pop()),
        ('missing_partial_bank_control', 'PARENT-CHECK.json', lambda x: x['controls_rejected'].pop()),
        ('stale_partial_bank_parent', 'PARENT-CHECK.json', lambda x: x.__setitem__('parent_content_sha256', '0'*64)),
        ('missing_owner_edit_control', 'OWNER-CONTROLS.json', lambda x: x['omitted_edit_controls'].pop()),
        ('missing_delay_control', 'OWNER-CONTROLS.json', lambda x: x.__setitem__('omitted_delay_rejection', '')),
        ('missing_admission_control', 'ADMISSION-CONTROLS.json', lambda x: x['rejected_controls'].pop()),
        ('missing_bit_control', 'BIT-CONTROLS.json', lambda x: x['rejected_controls'].pop()),
        ('missing_native_phase_stage', 'native/STEPS.json', lambda x: x.pop()),
        ('changed_runtime_spec', 'runtime/data/SPEC.json', lambda x: x['expected'].__setitem__('live', 14336)),
        ('stale_ancestral_price', 'BASELINE-BINDING.json', lambda x: x.__setitem__('kappa', '1/1000')),
        ('omitted_ancestral_coverage', 'BASELINE741-COVERAGE.json', lambda x: x.__setitem__('ordered_stage_count', 1)),
    ]
    for name, relative, mutate in cases:
        expect(name, lambda relative=relative, mutate=mutate: injected(relative, mutate))
    positives = []
    with tempfile.TemporaryDirectory(prefix='t21-controls-') as directory:
        temp = Path(directory)
        # Recompression must preserve the full identity after both recorded
        # owner container references have first been checked and rebound.
        original_plan = read(work/'lift/PLAN.json')
        original_owners = read(work/'owners/OWNERS.json.gz')
        for level in (1, 9):
            owner_path, plan_path = temp/f'owners-{level}.json.gz', temp/f'plan-{level}.json'
            raw = json.dumps(original_owners, sort_keys=True, separators=(',', ':')).encode()
            owner_path.write_bytes(gzip.compress(raw, compresslevel=level, mtime=42))
            plan = copy.deepcopy(original_plan)
            plan['assignment_sha256'] = plan['replica_lift']['owners_file_sha256'] = sha(owner_path)
            dump(plan_path, plan)
            value, ids = verify.runtime_spec(plan_path, owner_path)
            require(ids == honest['semantic_identities'], 'Recompression identity')
            positives.append(dict(compresslevel=level, semantic_identities=ids))
        owner_path, plan_path = temp/'mutant-owner.json.gz', temp/'mutant-plan.json'
        bad = copy.deepcopy(original_owners)
        bad[0]['offset'] += 1
        write_gzip(owner_path, bad)
        plan = copy.deepcopy(original_plan)
        plan['assignment_sha256'] = plan['replica_lift']['owners_file_sha256'] = sha(owner_path)
        plan['assignment_content_sha256'] = identity(bad)
        dump(plan_path, plan)
        expect('consistent_changed_owner_semantics', lambda: verify.runtime_spec(plan_path, owner_path))
        plan = copy.deepcopy(original_plan)
        plan['windows'][next(iter(plan['windows']))][1].append(999)
        dump(plan_path, plan)
        expect('changed_window_semantics', lambda: verify.runtime_spec(plan_path, work/'owners/OWNERS.json.gz'))
        package = temp/'package'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        original_here = verify.HERE
        verify.HERE = package
        try:
            path = package/'build_owners.py'
            path.write_bytes(path.read_bytes()+b'\n# changed byte\n')
            expect('changed_package_byte', verify.validate_pins)
        finally:
            verify.HERE = original_here
        process = subprocess.run([sys.executable, '-O', str(HERE/'verify.py'), '--work', str(temp/'optimized')],
                                 text=True, capture_output=True)
        require(process.returncode != 0 and 'Assertions must remain enabled' in process.stderr, 'Top-level optimized rejection')
        rejected.append(dict(name='optimized_top_level', reason='Assertions must remain enabled'))
    result = dict(status='PASS_T21_PACKAGE_BOUNDARY_CONTROLS', count=len(rejected), controls_rejected=rejected,
                  recompression_positive_controls=positives, kappa=honest['kappa'],
                  replay_result_sha256=sha(work/'RESULT.json'), package_manifest_sha256=sha(HERE/'MANIFEST.json'),
                  scope='Exact package and final-binding mutation checks. Inputs are read-only. Receipt/log coverage does not authenticate execution history.')
    dump(args.out, result)
    print(result['status'], 'rejections='+str(len(rejected)), 'recompression_positives=2')


if __name__ == '__main__':
    main()
