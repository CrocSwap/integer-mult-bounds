#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Hao Yan (@FanPUYen)
"""Packaging/admission and serialization controls for a strict T16 replay.

Authored with substantial OpenAI Codex assistance. This checks the new package
boundary, not the inherited mathematical controls. First rebind the unchanged
positive replay. Then mutate only temporary copies or the JSON reader's return
values; neither the repository nor the completed replay is modified.

The --replay directory must be a successful verify.py output. Supply the exact
--baseline799 and --ancestor741 used in that replay, including when they were
built under --replay/baseline799 by the default cold command. --out is a new JSON
file, outside the repository and all input directories.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'Cannot load '+str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_hashes(directory):
    return {path.relative_to(directory).as_posix(): sha(path)
            for path in directory.rglob('*') if path.is_file()}


def extra_controls(verifier, coverage, frozen_spec, plan_path, owners_path, ancestor, scratch):
    """Exercise generated-container portability and fixed ancestral coverage."""
    rejected, accepted = [], []

    def reject(name, action, expected, mutation):
        try:
            action()
        except (AssertionError, ValueError, RuntimeError) as error:
            reason = str(error)
            require(expected in reason, name+' rejected for an unrelated reason: '+reason)
            rejected.append(dict(name=name, mutation=mutation, rejection=reason))
        else:
            raise ValueError('Negative control unexpectedly accepted: '+name)

    source_plan = verifier.read(plan_path)
    source_owners = verifier.read(owners_path)
    semantic = verifier.semantic_identities(plan_path, owners_path)
    original_payload = gzip.decompress(owners_path.read_bytes())

    def fixture(name, level, timestamp, os_byte, owner_value=None, plan_edit=None):
        work = scratch/name
        for directory in ('owners', 'lift', 'runtime/data'):
            (work/directory).mkdir(parents=True)
        payload = original_payload if owner_value is None else json.dumps(
            owner_value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
        container = bytearray(gzip.compress(payload, compresslevel=level, mtime=timestamp))
        container[9] = os_byte
        owner_file = work/'owners/OWNERS.json.gz'
        owner_file.write_bytes(container)
        plan = copy.deepcopy(source_plan)
        plan['assignment_sha256'] = sha(owner_file)
        plan['replica_lift']['owners_file_sha256'] = sha(owner_file)
        plan['assignment_content_sha256'] = verifier.canonical_sha(
            source_owners if owner_value is None else owner_value)
        if plan_edit is not None:
            plan_edit(plan)
        (work/'lift/PLAN.json').write_bytes((json.dumps(plan, indent=1)+'\n').encode('utf-8'))
        return work

    # Both gzip level/headers and PLAN JSON formatting differ. Only complete
    # owner semantics and the two checked PLAN file references are normalized.
    for label, level, timestamp, os_byte in (('level1-unix', 1, 123456789, 3),
                                             ('level9-unknown', 9, 42, 255)):
        work = fixture(label, level, timestamp, os_byte)
        owner_file, plan_file = work/'owners/OWNERS.json.gz', work/'lift/PLAN.json'
        require(sha(owner_file) != sha(owners_path), 'Recompression positive did not change gzip bytes')
        value, identities = verifier.runtime_spec_value(frozen_spec, plan_file, owner_file)
        require(identities == semantic, 'Recompression changed proof identity')
        (work/'runtime/data/SPEC.json').write_bytes(json.dumps(value).encode('utf-8'))
        require(verifier.validate_runtime_spec(work, frozen_spec) == (value, identities),
                'Recompression runtime SPEC did not bind')
        accepted.append(dict(name=label, compresslevel=level, timestamp=timestamp,
                             os_byte=os_byte, owner_file_sha256=sha(owner_file),
                             plan_file_sha256=sha(plan_file), semantic_identities=identities))

    bad_owners = copy.deepcopy(source_owners)
    bad_owners[0]['offset'] += 1
    owner_case = fixture('changed-owner', 1, 1, 3, owner_value=bad_owners)
    reject('owner_content_changed',
           lambda: verifier.runtime_spec_value(frozen_spec, owner_case/'lift/PLAN.json', owner_case/'owners/OWNERS.json.gz'),
           'Generated owner semantic identity mismatch', 'Change one owner offset and update both literal file references')

    def move_window(plan):
        key = sorted(plan['windows'])[0]
        plan['windows'][key][1].append(999)

    window_case = fixture('changed-window', 1, 2, 3, plan_edit=move_window)
    reject('plan_window_changed',
           lambda: verifier.runtime_spec_value(frozen_spec, window_case/'lift/PLAN.json', window_case/'owners/OWNERS.json.gz'),
           'Generated PLAN semantic identity mismatch', 'Add an invalid invocation to a PLAN owner window')

    def change_dispatch(plan):
        plan['provider_calls'][0]['provider'] = 'changed-provider'

    dispatch_case = fixture('changed-dispatch', 9, 3, 255, plan_edit=change_dispatch)
    reject('plan_dispatch_changed',
           lambda: verifier.runtime_spec_value(frozen_spec, dispatch_case/'lift/PLAN.json', dispatch_case/'owners/OWNERS.json.gz'),
           'Generated PLAN semantic identity mismatch', 'Replace one PLAN provider dispatch identity')

    stale_case = fixture('stale-owner-reference', 1, 4, 3,
                         plan_edit=lambda plan: plan.update(assignment_sha256='0'*64))
    reject('stale_owner_container_reference',
           lambda: verifier.runtime_spec_value(frozen_spec, stale_case/'lift/PLAN.json', stale_case/'owners/OWNERS.json.gz'),
           'Stale generated owner container reference', 'Normalize attempt with one unverified literal owner-file reference')

    runtime_case = fixture('changed-runtime-spec', 9, 5, 255)
    value, identities = verifier.runtime_spec_value(frozen_spec, runtime_case/'lift/PLAN.json', runtime_case/'owners/OWNERS.json.gz')
    value['expected']['live'] += 1
    (runtime_case/'runtime/data/SPEC.json').write_bytes(json.dumps(value).encode('utf-8'))
    reject('runtime_spec_unapproved_field',
           lambda: verifier.validate_runtime_spec(runtime_case, frozen_spec),
           'Runtime SPEC contains unapproved changes', 'Change expected.live outside the three permitted runtime-reference fields')

    coverage_positive = coverage.check(ancestor)
    require(coverage_positive['ordered_stage_count'] == 22 and coverage_positive['mandatory_artifact_count'] == 44,
            'Ancestral positive coverage')
    receipt_path = (ancestor/'complex/RECEIPT.json').resolve()
    stages_path = (ancestor/'complex/STAGES.json').resolve()
    original_read = coverage.read

    def changed_coverage(receipt_edit=None, stages_edit=None):
        def read_changed(path):
            value = original_read(path)
            resolved = Path(path).resolve()
            if resolved == receipt_path and receipt_edit is not None:
                value = copy.deepcopy(value)
                receipt_edit(value)
            if resolved == stages_path and stages_edit is not None:
                value = copy.deepcopy(value)
                stages_edit(value)
            return value
        with patch.object(coverage, 'read', read_changed):
            return coverage.check(ancestor)

    def replace_stage(stages):
        stages[0]['name'] = 'unrecognized-replacement-stage'

    reject('ancestor_stage_replacement',
           lambda: changed_coverage(lambda receipt: replace_stage(receipt['stages']), replace_stage),
           'PR741 fixed ordered stage coverage', 'Replace one mandatory stage consistently in both stage inventories')
    reject('ancestor_artifact_omission',
           lambda: changed_coverage(lambda receipt: receipt['artifacts'].pop('local/CLIFFORD-REVIEW.json')),
           'PR741 fixed artifact coverage', 'Delete mandatory local phase artifact from the self-reported receipt')
    reject('ancestor_stages_disagreement',
           lambda: changed_coverage(stages_edit=lambda stages: stages[0].update(seconds=stages[0]['seconds']+1)),
           'PR741 STAGES receipt consistency', 'Change a STAGES field without matching receipt.stages')
    require(coverage.check(ancestor) == coverage_positive, 'Ancestral positive changed during controls')
    require(len(rejected) == 8 and len(accepted) == 2, 'Extra boundary-control inventory')
    return dict(controls_rejected=rejected, recompression_positive_controls=accepted,
                ancestral_coverage_positive=coverage_positive)


def main():
    require(not sys.flags.optimize, 'Package controls require enabled assertions')
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('replay', 'baseline799', 'ancestor741', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    replay, baseline, ancestor, out = [getattr(args, name).resolve()
                                      for name in ('replay', 'baseline799', 'ancestor741', 'out')]
    require(all(path.is_dir() for path in (replay, baseline, ancestor)), 'All input directories must exist')
    require(not out.exists(), 'Output file must be new')
    require(not any(out.is_relative_to(path) for path in (ROOT, replay, baseline, ancestor)),
            'Output must be outside repository and input directories')
    verifier = load_module('t16_package_verifier', HERE/'verify.py')
    adapter = load_module('t16_source_adapter', HERE/'source_adapters.py')
    coverage = load_module('t16_baseline_coverage', HERE/'baseline_coverage.py')
    pins = verifier.validate_pins()
    recorded = verifier.read(replay/'RESULT.json')
    require(recorded['status'] == 'PASS_STRICT_T16_PR799_OWNER_CONCENTRATION', 'Input is not a strict successful replay')
    require(recorded['baseline_mode'] in ('cold_rebuilt', 'explicitly_reused_and_rebound'), 'Unknown replay mode')
    reuse = recorded['baseline_mode'] == 'explicitly_reused_and_rebound'
    stages = verifier.read(replay/'STAGES.json')
    spec = HERE/'data/SPEC.json'

    def bind(selected_stages=None):
        return verifier.final_binding(replay, baseline, ancestor, spec, pins, reuse,
                                      stages if selected_stages is None else selected_stages)

    positive = bind()
    require(positive == recorded, 'Positive replay no longer binds to the recorded result')
    rejected = []

    def reject(name, action, expected, mutation):
        try:
            action()
        except (AssertionError, ValueError, RuntimeError) as error:
            reason = str(error)
            require(expected in reason, name+' rejected for an unrelated reason: '+reason)
            rejected.append(dict(name=name, mutation=mutation, rejection=reason))
        else:
            raise ValueError('Negative control unexpectedly accepted: '+name)

    def changed_receipt(relative, edit):
        target = (replay/relative).resolve()
        original_read = verifier.read

        def read_changed(path):
            value = original_read(path)
            if Path(path).resolve() == target:
                value = copy.deepcopy(value)
                edit(value)
            return value

        with patch.object(verifier, 'read', read_changed):
            return bind()

    # These controls exercise receipt binding, not alternate execution claims.
    reject('missing_mandatory_audit_stage',
           lambda: bind([stage for stage in stages if stage['name'] != 'audit']),
           'Complete ordered strict stage sequence', 'Remove audit from otherwise successful stage inventory')
    reject('stale_pr741_baseline',
           lambda: changed_receipt('BASELINE-BINDING.json', lambda value: value.update(kappa='0.001661202643272239')),
           'Accepted PR799 baseline binding', 'Substitute the older PR741 exponent in accepted-baseline receipt')
    reject('t8_complete_invocation_count',
           lambda: changed_receipt('INDEPENDENT-T16.json', lambda value: value.update(calls=72)),
           'Complete invocation inventory', 'Replace independently counted 144 complete invocations with 72')
    reject('t8_deficit',
           lambda: changed_receipt('INDEPENDENT-T16.json', lambda value: value.update(deficit=2560)),
           'Rank mass and deficit', 'Replace T16 deficit 5120 with the old T8 deficit 2560')

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='t16-package-controls-', dir=out.parent) as temporary:
        scratch = Path(temporary)
        # A deliberately wrong pin is tested at the source-adapter boundary,
        # independently of the stronger enclosing package manifest.
        pin_dir = scratch/'bad-pin'
        pin_dir.mkdir()
        source_pins = verifier.read(HERE/'SOURCE-PINS.json')
        source_pins['code/assemble.py'] = '0'*64
        (pin_dir/'SOURCE-PINS.json').write_bytes(json.dumps(source_pins).encode('utf-8'))

        def bad_pin():
            with patch.object(adapter, 'HERE', pin_dir):
                adapter.materialize(scratch/'bad-pin-runtime')

        reject('bad_source_pin', bad_pin, 'source pin', 'Change pinned PR799 assemble.py digest to 64 zeroes')
        require(not (scratch/'bad-pin-runtime').exists(), 'Source-pin failure must precede runtime creation')

        copy_dir = scratch/'package-copy'
        shutil.copytree(HERE, copy_dir, ignore=shutil.ignore_patterns('__pycache__'))
        with (copy_dir/'verify.py').open('ab') as stream:
            stream.write(b'\n# Deliberately changed package byte.\n')

        def bad_manifest():
            with patch.object(verifier, 'HERE', copy_dir):
                verifier.validate_pins()

        reject('changed_package_byte', bad_manifest, 'Package manifest mismatch',
               'Append one comment to a copied verifier while retaining the original manifest')

        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONOPTIMIZE', None)

        def rejected_cli(flags, work, expected):
            command = [sys.executable, *flags, '-B', str(HERE/'verify.py'), '--work', str(work)]
            process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                     text=True, timeout=30)
            output = process.stdout+process.stderr
            require(process.returncode != 0 and expected in output,
                    'CLI did not explicitly reject: '+output[-2000:])
            raise ValueError(expected)

        optimized = scratch/'optimized-work'
        reject('optimized_top_level',
               lambda: rejected_cli(['-O'], optimized, 'Assertions must remain enabled'),
               'Assertions must remain enabled', 'Run the real top-level CLI with Python -O')
        require(not optimized.exists(), '-O refusal must precede output creation')

        existing = scratch/'existing-work'
        existing.mkdir()
        (existing/'sentinel.txt').write_bytes(b'Existing work must remain byte-identical.\n')
        before = tree_hashes(existing)
        reject('existing_work_directory',
               lambda: rejected_cli([], existing, 'Output directory must be new'),
               'Output directory must be new', 'Run the real top-level CLI against a populated output directory')
        require(tree_hashes(existing) == before, 'Existing output was modified')

        extra = extra_controls(verifier, coverage, spec, replay/'lift/PLAN.json',
                               replay/'owners/OWNERS.json.gz', ancestor, scratch/'extra')
        rejected.extend(extra['controls_rejected'])

    require(len(rejected) == 16, 'Expected sixteen distinct package controls')
    require(verifier.validate_pins() == pins, 'Package inputs changed during controls')
    require(bind() == positive, 'Positive replay changed during controls')
    result = dict(status='PASS_T16_PACKAGE_BOUNDARY_NEGATIVE_CONTROLS',
                  controls_rejected=rejected, count=len(rejected),
                  recompression_positive_controls=extra['recompression_positive_controls'],
                  ancestral_coverage_positive=extra['ancestral_coverage_positive'],
                  positive_rebound=True, positive_kappa=positive['kappa'],
                  package_manifest_sha256=pins['package_manifest_sha256'],
                  replay_result_sha256=sha(replay/'RESULT.json'),
                  replay_stages_sha256=sha(replay/'STAGES.json'),
                  checker_sha256=sha(Path(__file__)),
                  scope='Sixteen package/admission controls plus two gzip recompression positives. Receipt controls inject isolated JSON values; byte controls use disposable copies. The original repository and successful replay are read-only. Mathematical and controller controls remain in the strict replay; fixed ancestral coverage does not authenticate historical process execution.')
    out.write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
    print(result['status'], result['count'])


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print('FAIL:', error, file=sys.stderr)
        raise SystemExit(1)
