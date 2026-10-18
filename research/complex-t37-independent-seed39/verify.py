# SPDX-License-Identifier: Apache-2.0
"""Cold U8/T37/PR589 replay, with explicit hash-checked ancestry reuse.

Default rebuilds PR799, PR741 and PR589 before rebuilding the U8 local word.
The only reuse option accepts a complete PR799 replay and its complete ancestry;
the unchanged upstream binding checker and fixed stage-coverage check rerun.
No discovery mode or optimizer is exposed. Outputs must be outside this checkout.
"""
import argparse
import copy
from fractions import Fraction
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from common import HERE, ROOT, read, require, sha, identity, dump, load

SOURCE = ROOT/'research/complex-k492-owner-repair/vendor/multicold'


def validate_pins():
    path = HERE/'MANIFEST.json'
    manifest = read(path)
    actual = {p.relative_to(HERE).as_posix(): sha(p) for p in HERE.rglob('*')
              if p.is_file() and p != path and '__pycache__' not in p.parts}
    require(actual == manifest, 'Package manifest mismatch')
    for relative, expected in read(HERE/'DEPENDENCY-PINS.json').items():
        p = (ROOT/relative).resolve()
        require(not Path(relative).is_absolute() and p.is_relative_to(ROOT), 'Dependency path')
        require(sha(p) == expected, 'Repository dependency changed: '+relative)
    for label, record in read(HERE/'VENDOR-PINS.json').items():
        for relative, expected in record['files'].items():
            require(sha(HERE/'vendor'/label/relative) == expected, 'Vendored source changed: '+relative)
    return dict(manifest_sha256=sha(path), dependencies_sha256=sha(HERE/'DEPENDENCY-PINS.json'))


def semantic_identities(plan_path, owner_path):
    plan, roles = read(plan_path), read(owner_path)
    require(plan['assignment_sha256'] == plan['replica_lift']['owners_file_sha256'] == sha(owner_path),
            'Stale owner container reference')
    content = identity(roles)
    require(plan['assignment_content_sha256'] == content, 'Stale owner content reference')
    value = copy.deepcopy(plan)
    value['assignment_sha256'] = value['replica_lift']['owners_file_sha256'] = content
    return dict(owners_content_sha256=content, plan_semantic_sha256=identity(value))


def runtime_spec(plan_path, owner_path):
    frozen = read(HERE/'data/SPEC.json')
    ids = semantic_identities(plan_path, owner_path)
    require(all(frozen['data'][key] == value for key, value in ids.items()), 'Frozen owner/plan semantic identity')
    value = copy.deepcopy(frozen)
    value['data']['owners_sha256'], value['data']['plan_sha256'] = sha(owner_path), sha(plan_path)
    pivot = (HERE/frozen['pivot_swap']['recipe']).resolve()
    require(pivot.is_relative_to(HERE) and sha(pivot) == frozen['pivot_swap']['sha256'], 'Immutable pivot recipe')
    value['pivot_swap']['recipe'] = str(pivot)
    return value, ids


def final_binding(work, stages, pins, reuse, baseline, ancestor):
    claim = read(HERE/'data/CLAIM.json')
    assembly = read(work/'ASSEMBLY.json')
    independent = read(work/'INDEPENDENT-T37.json')
    g = work/'global'
    owners = read(g/'audit/OWNERS-AND-PROFILE.json')
    controller = read(g/'audit/ASYNC-AUDIT.json')
    invoice = read(g/'audit/PREFIX-AND-INVOICE.json')
    price = read(work/'INDEPENDENT-PRICE.json')
    spec, identities = runtime_spec(work/'lift/PLAN.json', work/'owners/OWNERS.json.gz')
    require(spec == read(work/'runtime/data/SPEC.json'), 'Only authorized runtime SPEC fields may change')
    adapters = load(HERE/'source_adapters.py', 'exact_t37_runtime_adapters')
    require(adapters.check_runtime(work/'runtime') == read(work/'runtime/ADAPTERS.json'),
            'Exact materialized runtime source and input binding')
    require(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY', 'Assembly status')
    require(assembly['kappa'] == str(Fraction(claim['kappa'])) == price['prices']['native']['outer']['kappa'], 'Two exact prices agree')
    require(Fraction(assembly['complex_lower']) == Fraction(claim['complex_lower']) and
            Fraction(assembly['bit_lower']) == Fraction(claim['bit_lower']), 'Both certified endpoints')
    require(Fraction(assembly['kappa']) > Fraction(claim['baseline890_kappa']), 'Strict gain over PR890')
    require(assembly['complex_profile'] == independent['profile'] == owners['paid_profile'] ==
            controller['complex_profile'] == read(work/'lift/PLAN.json')['profile'] == spec['expected']['global_profile'],
            'All independent profile recounts agree')
    for key in ('roles', 'calls', 'live', 'physical', 'rank_mass', 'deficit', 'prefix_bits'):
        require(independent[key] == claim[key], 'Independent T37 '+key)
    for key in ('live', 'physical', 'rank_mass', 'deficit'):
        require(owners[key] == independent[key], 'Owner/independent '+key)
    require(independent['roles'] == owners['hosted_residuals'] == controller['complex_hosted_residuals'] == 167832, 'Whole-helper inventory')
    require(independent['calls'] == controller['complete_invocations'] == invoice['complete_invocation_sweeps'] == 333, 'Complete invocation inventory')
    require(independent['physical_row_coefficient'] == invoice['finite']['physical_row_coefficient'] == claim['row_coefficient'] < 20161, 'Physical row reserve')
    require(independent['prefix_bits'] == invoice['global_prefix_bits'] == 779 < invoice['charged_prefix_bits'] == 1024, 'Prefix reserve')
    require(independent['actual_73_axis_charts'] == owners['actual_73column_sigmas'] == controller['actual_orthogonal_73column_maps'], 'Independent chart recount')
    require(independent['idle'] == claim['idle'] and len(independent['controls_rejected']) == 6 and len(independent['order_controls_rejected']) == 3, 'T37 independent controls')
    require(all(independent[key] is True for key in
                ('explicit_order_input', 'declared_order_bijection',
                 'declared_order_role_times_bound', 'per_replica_stage_order')),
            'Explicit T37 order and role-time admission')
    require(independent['charged_prefix_bits'] == claim['charged_complex_payload'] ==
            invoice['charged_prefix_bits'] == 1024, 'One charged complex payload')
    five = read(work/'INDEPENDENT-T5.json')
    require(len(five['controls_rejected']) == 6 and five['roles'] == 22680 and five['calls'] == 45 and
            five['idle'] == {'48': 1498, '6': 1}, 'T5 independent witness and controls')
    pc = read(work/'PARENT-CHECK.json')
    require(pc['status'] == 'PASS_INDEPENDENT_T37_PARTIAL_BANK_ENVELOPE' and len(pc['controls_rejected']) == 8, 'Partial-bank audit and controls')
    require(pc['parent_content_sha256'] == identity(read(work/'lift/GLOBAL-TEMPLATE.json.gz')) ==
            invoice['parent_template_sha256'], 'Exact checked partial-bank parent identity')
    require(pc['source_content_sha256'] == identity(read(baseline/'global/global/base/split-centres/GLOBAL-TEMPLATE.json.gz')), 'Exact original parent identity')
    oc = read(work/'OWNER-CONTROLS.json')
    require(len(oc['omitted_edit_controls']) == 10 and oc['omitted_delay_rejection'], 'Ten edits and interleave control')
    construction = read(work/'owners/OWNER-CONSTRUCTION.json')
    require(construction['changed_roles'] == 10 and construction['relocated_roles'] == 6 and construction['both_source_suborders_preserved'], 'Owner construction coverage')
    require(construction['owners_sha256'] == sha(work/'owners/OWNERS.json.gz') and
            construction['owners_content_sha256'] == identities['owners_content_sha256'], 'Constructed owner binding')
    require(oc['status'] == 'PASS_T37_T21_T16_OMITTED_EDITS_AND_DELAYS' and
            oc['owners_sha256'] == construction['owners_sha256'] and
            oc['owners_content_sha256'] == construction['owners_content_sha256'] and
            oc['order_sha256'] == sha(work/'owners/ORDER.json') and
            oc['order_content_sha256'] == construction['order_content_sha256'] == identity(read(work/'owners/ORDER.json')),
            'Owner control inputs and constructed source order')
    require(oc['source_suborders_preserved'] is True and oc['source_suborders_checked_independently'] is True and
            oc['underpaid_payload_rejection'] == 'prefix reserve' and
            oc['t37_independent_acceptance'] == {k: v for k, v in independent.items()
                if k not in ('controls_rejected', 'order_controls_rejected', 'input_sha256')},
            'Independent control acceptance and underpaid-prefix rejection')
    for label in ('t21', 't16'):
        source = oc['inherited_'+label]
        require(source['owners_content_sha256'] == construction[label+'_content_sha256'] and
                source['order_content_sha256'] == construction[label+'_order_content_sha256'] and
                source['independent_acceptance']['local_profile'] == claim['local_profile'],
                'Inherited owner source and fresh U8 interface: '+label)
    require(len(oc['inherited_t21']['omitted_edit_controls']) == 9 and oc['inherited_t21']['omitted_delay_rejection'] and
            len(oc['inherited_t16']['omitted_edit_controls']) == 11, 'Inherited T21 and T16 edit controls')
    payload = read(work/'PAYLOAD-CONTROLS.json')
    expected_payload_controls = ['old_complex_payload512', 'stale_row_prefix_extra1024',
                                 'stale_row16469', 'old_global_prefix491', 'bit_allowance1024']
    require(payload['status'] == 'PASS_T37_PAYLOAD_TARGETED_NEGATIVE_CONTROLS' and
            payload['rejected_controls'] == expected_payload_controls and
            [check['name'] for check in payload['targeted_failures']] == expected_payload_controls and
            all(check['targeted_guard'] is True for check in payload['targeted_failures']) and
            all(payload[key] is True for key in ('honest_assembly_passed', 'bit_loader_restored',
                'owner_hash_rebound_for_each_mutation', 'bit_injection_after_original_blob_pin')) and
            payload['valid_receipt_kappa'] == assembly['kappa'] and
            payload['input_sha256']['owner'] == sha(g/'audit/OWNERS-AND-PROFILE.json') and
            payload['input_sha256']['invoice'] == sha(g/'audit/PREFIX-AND-INVOICE.json') and
            payload['input_sha256']['runtime_spec'] == sha(work/'runtime/data/SPEC.json') and
            payload['input_sha256']['bit_supplier'] == sha(work/'runtime/inputs/PR589-EXPECTED.json') ==
                assembly['input_sha256']['package:inputs/PR589-EXPECTED.json'] and
            payload['assembler_sha256'] == sha(work/'runtime/code/assemble.py'), 'Targeted payload controls')
    ac, bc = read(work/'ADMISSION-CONTROLS.json'), read(work/'BIT-CONTROLS.json')
    require(len(ac['rejected_controls']) == 69 and not ac['discovery_accepted_controls'], 'Strict admission controls')
    require(len(bc['rejected_controls']) == 12 and bc['derived_deficit'] == 10272, 'PR589 controls')
    require(controller['mutation_controls_run'] and len(controller['mutations_rejected']) == 15, 'Controller mutation controls')
    require(invoice['strict_checks'] and all(invoice['strict_checks'].values()), 'Complete finite invoice')
    require(len(assembly['outer']) == 47 and all(Fraction(v) > 0 for v in assembly['outer'].values()), 'All 47 strict outer inequalities')
    require(assembly['template_sha256'] == owners['template_sha256'] == invoice['template_sha256'] == controller['complex_template_sha256'], 'One emitted controller identity')
    require(invoice['owner_audit_sha256'] == sha(g/'audit/OWNERS-AND-PROFILE.json') and invoice['controller_audit_sha256'] == sha(g/'audit/ASYNC-AUDIT.json'), 'Invoice receipt binding')
    native_steps = read(work/'native/STEPS.json')
    require([s['step'] for s in native_steps] == ['barch', 'barch-controls', 'layer-end-controls', 'native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and
            all(s['exit_code'] == 0 for s in native_steps), 'Complete fresh U8 local stages')
    require(len(read(work/'native/barch-controls/controls.json')) == 38, 'U8 construction control inventory')
    require(len(read(work/'native/controls/COLD-END-CONTROLS.json')['rejected']) == 95, 'Inherited end-control inventory')
    native = work/'native/local'
    for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
                 'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json'):
        require(read(g/'base/providers/gauge44'/name) == read(native/name), 'Fresh local-provider binding: '+name)
    names = ['baseline741-coverage', 'baseline799-binding', 'native-u8', 'independent-local', 'build-owners',
             'build-parent', 'check-parent', 'independent-t5', 'independent-t37', 'owner-controls', 'source-adapters',
             'bind', 'emit', 'audit', 'invoice', 'assembly', 'admission-controls', 'bit-controls', 'payload-controls', 'independent-price']
    require([s['name'] for s in stages] == ([] if reuse else ['baseline799-cold'])+names and
            all(s['exit_code'] == 0 for s in stages), 'Fixed complete stage sequence')
    for stage in stages:
        require(sha(work/stage['log']) == stage['log_sha256'], 'Stage log binding')
    coverage = load(HERE/'vendor/pr858/baseline_coverage.py', 'fixed_ancestral_coverage')
    require(read(work/'BASELINE741-COVERAGE.json') == coverage.check(ancestor), 'Complete fixed ancestral coverage binding')
    sys.path.insert(0, str(ROOT/'scripts'))
    try:
        binding = load(ROOT/'scripts/verify_frontier799_bindings.py', 'unchanged_frontier799_binding')
        expected = binding.check(ancestor, baseline/'native', baseline/'global',
                                 baseline/'INDEPENDENT-LOCAL.json', baseline/'INDEPENDENT-PRICE.json')
    finally:
        sys.path.pop(0)
    require(read(work/'BASELINE-BINDING.json') == expected, 'Complete fresh ancestral binding')
    require(expected['kappa'] == str(Fraction('0.001661634653669567')), 'PR799 ancestor exponent')
    artifacts = ['ASSEMBLY.json', 'INDEPENDENT-T5.json', 'INDEPENDENT-T37.json', 'INDEPENDENT-PRICE.json',
                 'INDEPENDENT-LOCAL.json', 'PARENT-CHECK.json', 'OWNER-CONTROLS.json', 'ADMISSION-CONTROLS.json',
                 'BIT-CONTROLS.json', 'PAYLOAD-CONTROLS.json', 'BASELINE-BINDING.json', 'BASELINE741-COVERAGE.json', 'RUNTIME-BINDING.json',
                 'owners/OWNER-CONSTRUCTION.json', 'owners/OWNERS.json.gz', 'owners/ORDER.json',
                 'lift/PLAN.json', 'lift/GLOBAL-TEMPLATE.json.gz', 'lift/PARENT-LIFT.json', 'runtime/ADAPTERS.json',
                 'runtime/data/SPEC.json', 'global/PLAN.json', 'global/BINDING.json', 'global/hosted/GLOBAL-TEMPLATE.json.gz',
                 'global/audit/ASYNC-AUDIT.json', 'global/audit/OWNERS-AND-PROFILE.json', 'global/audit/PREFIX-AND-INVOICE.json',
                 'native/STEPS.json', 'native/barch-controls/controls.json', 'native/controls/COLD-END-CONTROLS.json']
    return dict(status='PASS_STRICT_U8_T37_PR589_COMPOSITION', kappa=assembly['kappa'], kappa_decimal=assembly['kappa_decimal'],
                delta_over_pr890=str(Fraction(assembly['kappa'])-Fraction(claim['baseline890_kappa'])),
                complex_lower=assembly['complex_lower'], bit_lower=assembly['bit_lower'],
                profile=assembly['complex_profile'], roles=167832, calls=333, prefix_bits=779, row_coefficient=17495,
                baseline_mode='explicit_checked_reuse' if reuse else 'cold_rebuilt', package_pins=pins,
                semantic_identities=identities, stages=len(stages), artifact_sha256={p: sha(work/p) for p in artifacts}, scope=claim['scope'])


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline799', type=Path)
    parser.add_argument('--ancestor741', type=Path)
    args = parser.parse_args()
    require((args.baseline799 is None) == (args.ancestor741 is None), 'Reuse requires both complete ancestry directories')
    work = args.work.resolve()
    require(not work.exists() and not work.is_relative_to(ROOT), 'New output directory outside the checkout required')
    pins = validate_pins()
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               PYTHON=sys.executable, SW4_FRAME8_PYTHON=sys.executable, MULTICOLD_SOURCE=str(SOURCE), GAIN_PR564_SOURCE=str(SOURCE))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []

    def run(name, script, *arguments):
        log = work/(name+'.log')
        start = time.monotonic()
        with log.open('w', encoding='utf-8', newline='\n') as stream:
            process = subprocess.run([sys.executable, '-B', str(SOURCE/'code/run_portable.py'), str(script), *map(str, arguments)],
                                     cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=process.returncode, seconds=round(time.monotonic()-start, 3),
                           log=log.name, log_sha256=sha(log)))
        dump(work/'STAGES.json', stages)
        require(process.returncode == 0, name+' failed:\n'+log.read_text(errors='replace')[-5000:])
        print('PASS', name, stages[-1]['seconds'], flush=True)

    reuse = args.baseline799 is not None
    baseline = args.baseline799.resolve() if reuse else work/'baseline799'
    ancestor = args.ancestor741.resolve() if reuse else baseline/'ancestor'
    if not reuse:
        run('baseline799-cold', ROOT/'scripts/verify_frontier799.py', '--work', baseline)
    run('baseline741-coverage', HERE/'vendor/pr858/baseline_coverage.py', '--ancestor', ancestor, '--out', work/'BASELINE741-COVERAGE.json')
    run('baseline799-binding', ROOT/'scripts/verify_frontier799_bindings.py', '--ancestor', ancestor,
        '--native', baseline/'native', '--global', baseline/'global', '--independent', baseline/'INDEPENDENT-LOCAL.json',
        '--price', baseline/'INDEPENDENT-PRICE.json', '--out', work/'BASELINE-BINDING.json')
    run('native-u8', HERE/'vendor/pr870/construction/barch/reproduce_barch.py', '--main', ROOT,
        '--pr635', ROOT/'research/complex-sw4-frame8/vendor/pr635', '--jx-dir', baseline/'native', '--recipe', 'U8', '--out', work/'native')
    local = work/'native/local'
    run('independent-local', HERE/'vendor/pr870/independent/audit_local.py', '--word', work/'native/barch/FULL-WORD.json.gz',
        '--main', ROOT, '--output', work/'INDEPENDENT-LOCAL.json')
    run('build-owners', HERE/'build_owners.py', '--out', work/'owners')
    base = baseline/'global/global/base'
    run('build-parent', HERE/'build_parent.py', '--base', base, '--owners', work/'owners/OWNERS.json.gz',
        '--order', work/'owners/ORDER.json', '--out', work/'lift')
    run('check-parent', HERE/'check_parent.py', '--source', base/'split-centres/GLOBAL-TEMPLATE.json.gz',
        '--parent', work/'lift/GLOBAL-TEMPLATE.json.gz', '--out', work/'PARENT-CHECK.json')
    for label, replicas, owners, idle in [('t5', 5, HERE/'data/T5-OWNERS.json.gz', '{"48":1498,"6":1}'),
                                         ('t37', 37, work/'owners/OWNERS.json.gz', '{"48":11086,"1":6}')]:
        run('independent-'+label, HERE/'independent_check.py', '--baseline-parent', base/'split-centres/GLOBAL-TEMPLATE.json.gz',
            '--owners', owners, '--word', local/'CANONICAL-WORD.json.gz', '--replicas', replicas, '--expected-idle', idle,
            '--payload', 512 if replicas == 5 else 1024,
            *([] if replicas == 5 else ['--order', work/'owners/ORDER.json']),
            '--out', work/('INDEPENDENT-'+label.upper()+'.json'))
    run('owner-controls', HERE/'owner_controls.py', '--base', base, '--local', local, '--owners', work/'owners/OWNERS.json.gz', '--out', work/'OWNER-CONTROLS.json')
    run('source-adapters', HERE/'source_adapters.py', work/'runtime')
    spec, identities = runtime_spec(work/'lift/PLAN.json', work/'owners/OWNERS.json.gz')
    (work/'runtime/data').mkdir()
    dump(work/'runtime/data/SPEC.json', spec)
    dump(work/'RUNTIME-BINDING.json', identities)
    env['WITNESS_SPEC'] = str(work/'runtime/data/SPEC.json')
    shutil.copytree(baseline/'global/parent558', work/'parent')
    shutil.copyfile(work/'lift/GLOBAL-TEMPLATE.json.gz', work/'parent/complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    code, g = work/'runtime/code', work/'global'
    run('bind', code/'bind_providers_portable.py', '--baseline', work/'parent', '--provider', 'gauge44='+str(local), '--plan', work/'lift/PLAN.json', '--out', g)
    run('emit', code/'emit_allcold.py', '--base', g/'base', '--owners', work/'owners/OWNERS.json.gz', '--plan', g/'PLAN.json', '--out', g/'hosted')
    run('audit', code/'audit_allcold.py', g/'base', g/'hosted', g/'audit/ASYNC-AUDIT.json', '--mutation-controls')
    run('invoice', code/'invoice_allcold.py', '--base', g/'base', '--hosted', g/'hosted', '--audit', g/'audit', '--out', g/'audit',
        '--retained-invoice', SOURCE/'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json')
    run('assembly', code/'assemble.py', SOURCE, g, work/'ASSEMBLY.json')
    for name, script, filename in [('admission-controls', 'assembly_controls.py', 'ADMISSION-CONTROLS.json'),
                                    ('bit-controls', 'bit_supplier_controls.py', 'BIT-CONTROLS.json')]:
        run(name, code/script, '--source-package', SOURCE, '--owner', g/'audit/OWNERS-AND-PROFILE.json', '--invoice', g/'audit/PREFIX-AND-INVOICE.json', '--out', work/filename)
    run('payload-controls', HERE/'payload_controls.py', '--runtime', code, '--source-package', SOURCE,
        '--owner', g/'audit/OWNERS-AND-PROFILE.json', '--invoice', g/'audit/PREFIX-AND-INVOICE.json', '--out', work/'PAYLOAD-CONTROLS.json')
    run('independent-price', HERE/'price.py', '--profile', work/'INDEPENDENT-T37.json', '--out', work/'INDEPENDENT-PRICE.json')
    require(validate_pins() == pins, 'Package changed during verification')
    result = final_binding(work, stages, pins, reuse, baseline, ancestor)
    dump(work/'RESULT.json', result)
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
