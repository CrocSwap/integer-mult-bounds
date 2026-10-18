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
import source_adapters


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
        ('t16_invocation_count', 'INDEPENDENT-T37.json', lambda x: x.__setitem__('calls', 144)),
        ('missing_t5_control', 'INDEPENDENT-T5.json', lambda x: x['controls_rejected'].pop()),
        ('missing_partial_bank_control', 'PARENT-CHECK.json', lambda x: x['controls_rejected'].pop()),
        ('stale_partial_bank_parent', 'PARENT-CHECK.json', lambda x: x.__setitem__('parent_content_sha256', '0'*64)),
        ('missing_owner_edit_control', 'OWNER-CONTROLS.json', lambda x: x['omitted_edit_controls'].pop()),
        ('missing_delay_control', 'OWNER-CONTROLS.json', lambda x: x.__setitem__('omitted_delay_rejection', '')),
        ('missing_t37_order_control', 'INDEPENDENT-T37.json', lambda x: x['order_controls_rejected'].pop()),
        ('undeclared_t37_order', 'INDEPENDENT-T37.json', lambda x: x.__setitem__('explicit_order_input', False)),
        ('nonboolean_order_binding', 'INDEPENDENT-T37.json', lambda x: x.__setitem__('declared_order_role_times_bound', 'true')),
        ('independent_payload512', 'INDEPENDENT-T37.json', lambda x: x.__setitem__('charged_prefix_bits', 512)),
        ('missing_inherited_t21_edit_control', 'OWNER-CONTROLS.json', lambda x: x['inherited_t21']['omitted_edit_controls'].pop()),
        ('missing_inherited_t16_edit_control', 'OWNER-CONTROLS.json', lambda x: x['inherited_t16']['omitted_edit_controls'].pop()),
        ('missing_inherited_t21_delay_control', 'OWNER-CONTROLS.json', lambda x: x['inherited_t21'].__setitem__('omitted_delay_rejection', '')),
        ('missing_underpaid_payload_control', 'OWNER-CONTROLS.json', lambda x: x.__setitem__('underpaid_payload_rejection', '')),
        ('unchecked_source_suborders', 'OWNER-CONTROLS.json', lambda x: x.__setitem__('source_suborders_checked_independently', False)),
        ('empty_owner_control_acceptance', 'OWNER-CONTROLS.json', lambda x: x.__setitem__('t37_independent_acceptance', {})),
        ('stale_owner_control_order', 'OWNER-CONTROLS.json', lambda x: x.__setitem__('order_sha256', '0'*64)),
        ('stale_inherited_t21_source', 'OWNER-CONTROLS.json', lambda x: x['inherited_t21'].__setitem__('owners_content_sha256', '0'*64)),
        ('missing_payload_control', 'PAYLOAD-CONTROLS.json', lambda x: x['rejected_controls'].pop()),
        ('duplicate_payload_control_name', 'PAYLOAD-CONTROLS.json', lambda x: x['rejected_controls'].__setitem__(1, x['rejected_controls'][0])),
        ('wrong_payload_failure_name', 'PAYLOAD-CONTROLS.json', lambda x: x['targeted_failures'][0].__setitem__('name', 'unrelated_guard')),
        ('untargeted_payload_failure', 'PAYLOAD-CONTROLS.json', lambda x: x['targeted_failures'][0].__setitem__('targeted_guard', False)),
        ('nonboolean_payload_guard', 'PAYLOAD-CONTROLS.json', lambda x: x['targeted_failures'][0].__setitem__('targeted_guard', 'true')),
        ('unrebound_payload_owner', 'PAYLOAD-CONTROLS.json', lambda x: x.__setitem__('owner_hash_rebound_for_each_mutation', False)),
        ('unchecked_payload_bit_pin', 'PAYLOAD-CONTROLS.json', lambda x: x.__setitem__('bit_injection_after_original_blob_pin', False)),
        ('stale_payload_owner_input', 'PAYLOAD-CONTROLS.json', lambda x: x['input_sha256'].__setitem__('owner', '0'*64)),
        ('stale_payload_bit_input', 'PAYLOAD-CONTROLS.json', lambda x: x['input_sha256'].__setitem__('bit_supplier', '0'*64)),
        ('stale_payload_kappa', 'PAYLOAD-CONTROLS.json', lambda x: x.__setitem__('valid_receipt_kappa', '1/1000')),
        ('complex_payload512', 'global/audit/PREFIX-AND-INVOICE.json', lambda x: x.__setitem__('charged_prefix_bits', 512)),
        ('stale_t21_row', 'global/audit/PREFIX-AND-INVOICE.json', lambda x: x['finite'].__setitem__('physical_row_coefficient', 16469)),
        ('stale_t21_prefix', 'global/audit/PREFIX-AND-INVOICE.json', lambda x: x.__setitem__('global_prefix_bits', 491)),
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
    with tempfile.TemporaryDirectory(prefix='t37-controls-') as directory:
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
        # A runtime mathematical guard must still match its literal source
        # adaptation even if the output-hash receipt is updated consistently.
        runtime = temp/'runtime'
        shutil.copytree(work/'runtime', runtime, ignore=shutil.ignore_patterns('__pycache__'))
        source_adapters.check_runtime(runtime)
        code_path = runtime/'code/assemble.py'
        code_bytes = code_path.read_bytes()
        before, after = b"invoice['charged_prefix_bits']==1024", b"invoice['charged_prefix_bits']==512"
        require(code_bytes.count(before) == 1, 'Unique complex runtime guard')
        code_path.write_bytes(code_bytes.replace(before, after))
        adapter_path = runtime/'ADAPTERS.json'
        original_adapters = read(adapter_path)
        changed_adapters = copy.deepcopy(original_adapters)
        changed_adapters['assemble.py']['output_sha256'] = sha(code_path)
        dump(adapter_path, changed_adapters)
        expect('changed_runtime_guard_rebound_receipt', lambda: source_adapters.check_runtime(runtime))
        code_path.write_bytes(code_bytes)
        dump(adapter_path, original_adapters)
        extra = runtime/'code/unregistered.py'
        extra.write_text('unregistered = True\n')
        expect('extra_runtime_code_file', lambda: source_adapters.check_runtime(runtime))
        extra.unlink()
        bit_path = runtime/'inputs/PR589-EXPECTED.json'
        bit_bytes = bit_path.read_bytes()
        bit_path.write_bytes(bit_bytes+b'\n')
        expect('changed_runtime_bit_input', lambda: source_adapters.check_runtime(runtime))
        bit_path.write_bytes(bit_bytes)
        source_adapters.check_runtime(runtime)
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
    result = dict(status='PASS_T37_PACKAGE_BOUNDARY_CONTROLS', count=len(rejected), controls_rejected=rejected,
                  recompression_positive_controls=positives, kappa=honest['kappa'],
                  replay_result_sha256=sha(work/'RESULT.json'), package_manifest_sha256=sha(HERE/'MANIFEST.json'),
                  scope='Exact package and final-binding mutation checks. Inputs are read-only. Receipt/log coverage does not authenticate execution history.')
    dump(args.out, result)
    print(result['status'], 'rejections='+str(len(rejected)), 'recompression_positives=2')


if __name__ == '__main__':
    main()
