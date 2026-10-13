#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Hao Yan (@FanPUYen)
"""Strict cold replay of T16 owner concentration on the accepted PR799 supplier.

Authored with substantial OpenAI Codex assistance. Credits include Jeremy
Kothe's PR799 provider, Chafik Boukhalfa's PR741 frames and owner map, the
PR514/PR484/PR507 controller lineage, and the retained PR589 bit supplier.

Default: --work NEW_DIRECTORY rebuilds PR799, its PR741 ancestry, and PR589.
Explicit reuse requires both --baseline799 and --ancestor741. The complete
maintainer binding checker always reruns before any baseline is consumed.
All outputs are outside the repository; no discovery mode is exposed.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
import os
import runpy
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/gauge44-frames-x'
SRC = ROOT/'research/complex-k492-owner-repair/vendor/multicold'
OLD_KAPPA = Fraction('0.001661634653669567')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_bytes((json.dumps(value, indent=2)+'\n').encode('utf-8'))


def canonical_sha(value):
    """Hash every JSON field, excluding only formatting, never proof data."""
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def semantic_identities(plan_path, owners_path):
    """Bind generated gzip by complete content, after checking literal references.

    Only two PLAN fields are container references. Their recorded bytes must
    first match the actual owner file. Replacing these two references by the
    already checked owner-content hash leaves every other PLAN field intact.
    This includes source pins, dispatch, widths, windows, profile, schedule,
    the full provider registry, and the exact lifted-parent content identity.
    """
    plan, owners = read(plan_path), read(owners_path)
    owner_file_sha = sha(owners_path)
    require(plan['assignment_sha256'] == owner_file_sha and
            plan['replica_lift']['owners_file_sha256'] == owner_file_sha,
            'Stale generated owner container reference')
    owner_content_sha = canonical_sha(owners)
    require(plan['assignment_content_sha256'] == owner_content_sha,
            'Stale generated owner content reference')
    normalized = copy.deepcopy(plan)
    normalized['assignment_sha256'] = owner_content_sha
    normalized['replica_lift']['owners_file_sha256'] = owner_content_sha
    return dict(owners_content_sha256=owner_content_sha,
                plan_semantic_sha256=canonical_sha(normalized))


def runtime_spec_value(frozen_spec_path, plan_path, owners_path):
    """Allow only derived file references and the same pinned pivot location."""
    frozen = read(frozen_spec_path)
    identities = semantic_identities(plan_path, owners_path)
    require(identities['owners_content_sha256'] == frozen['data']['owners_content_sha256'],
            'Generated owner semantic identity mismatch')
    require(identities['plan_semantic_sha256'] == frozen['data']['plan_semantic_sha256'],
            'Generated PLAN semantic identity mismatch')
    value = copy.deepcopy(frozen)
    value['data']['owners_sha256'] = sha(owners_path)
    value['data']['plan_sha256'] = sha(plan_path)
    # The upstream witness resolves this path relative to the SPEC package.
    # Moving SPEC into work/ must retain the original immutable recipe object.
    pivot = (HERE/frozen['pivot_swap']['recipe']).resolve()
    require(pivot.is_file() and sha(pivot) == frozen['pivot_swap']['sha256'],
            'Pinned runtime pivot recipe mismatch')
    value['pivot_swap']['recipe'] = str(pivot)
    return value, identities


def validate_runtime_spec(work, frozen_spec_path):
    """Reject every runtime-SPEC change other than the three derived fields."""
    expected, identities = runtime_spec_value(frozen_spec_path, work/'lift/PLAN.json',
                                              work/'owners/OWNERS.json.gz')
    actual = read(work/'runtime/data/SPEC.json')
    require(actual == expected, 'Runtime SPEC contains unapproved changes')
    return actual, identities


def validate_pins():
    """Validate every package byte and the explicit repository dependency set."""
    manifest_path = HERE/'MANIFEST.json'
    manifest = read(manifest_path)
    require(isinstance(manifest, dict) and manifest, 'Missing package manifest entries')
    actual = {path.relative_to(HERE).as_posix(): sha(path)
              for path in HERE.rglob('*')
              if path.is_file() and path != manifest_path and '__pycache__' not in path.parts}
    missing = sorted(set(manifest)-set(actual))
    extra = sorted(set(actual)-set(manifest))
    changed = sorted(key for key in set(actual) & set(manifest) if actual[key] != manifest[key])
    require(actual == manifest, 'Package manifest mismatch: missing=%s extra=%s changed=%s' %
            (missing, extra, changed))
    dependencies = read(HERE/'DEPENDENCY-PINS.json')
    require(isinstance(dependencies, dict) and dependencies, 'Missing dependency pins')
    for relative, expected in dependencies.items():
        path = (ROOT/relative).resolve()
        require(not Path(relative).is_absolute() and path.is_relative_to(ROOT), 'Dependency must be repository relative: '+relative)
        require(path.is_file() and sha(path) == expected, 'Dependency byte mismatch: '+relative)
    return dict(package_manifest_sha256=sha(manifest_path),
                dependency_manifest_sha256=sha(HERE/'DEPENDENCY-PINS.json'),
                package_files=len(manifest), dependency_files=len(dependencies))


def final_binding(work, baseline, ancestor, spec, package_pins, reuse, stages):
    """Bind the successful stages to one source/owner/local/invoice composition."""
    global_dir = work/'global'
    assembly = read(work/'ASSEMBLY.json')
    independent = read(work/'INDEPENDENT-T16.json')
    owner = read(global_dir/'audit/OWNERS-AND-PROFILE.json')
    audit = read(global_dir/'audit/ASYNC-AUDIT.json')
    invoice = read(global_dir/'audit/PREFIX-AND-INVOICE.json')
    binding = read(work/'BASELINE-BINDING.json')
    coverage = read(work/'BASELINE741-COVERAGE.json')
    coverage_check = runpy.run_path(str(HERE/'baseline_coverage.py'))['check']
    require(coverage == coverage_check(ancestor), 'Fresh ancestral coverage receipt binding')
    baseline_assembly = read(baseline/'global/ASSEMBLY.json')
    baseline_price = read(baseline/'INDEPENDENT-PRICE.json')
    baseline_owner = read(baseline/'global/global/audit/OWNERS-AND-PROFILE.json')
    bit = read(ancestor/'bit/RESULT9.json')
    admission = read(work/'ADMISSION-CONTROLS.json')
    bit_controls = read(work/'BIT-SUPPLIER-CONTROLS.json')
    construction = read(work/'owners/OWNER-CONSTRUCTION.json')
    parent_lift = read(work/'lift/PARENT-LIFT-RECEIPT.json')
    runtime_plan = read(global_dir/'PLAN.json')
    fresh_plan = read(work/'lift/PLAN.json')
    frozen_spec = read(spec)
    admitted_spec, artifact_identities = validate_runtime_spec(work, spec)
    require(binding['status'] == 'PASS_REBUILT_PR589_PR799_COMPOSITION' and
            Fraction(binding['kappa']) == OLD_KAPPA, 'Accepted PR799 baseline binding')
    require(Fraction(baseline_assembly['kappa']) == OLD_KAPPA, 'Baseline assembly exponent')
    require(assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY', 'New assembly status')
    require(independent['status'] == 'PASS_INDEPENDENT_T16_LITERAL_WINDOWS_CHARTS_PREFIX_ROW', 'Independent T16 audit status')
    require(owner['status'] == 'PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE', 'Whole-owner audit status')
    require(audit['status'] == 'PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS', 'Controller audit status')
    require(invoice['status'] == 'PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE', 'Finite invoice status')
    require(assembly['surcharge_model'] == {'complex': False, 'bit': True}, 'Retained surcharge models')
    bit_lower = Fraction(bit['bit_lower'])
    require(bit_lower == Fraction(assembly['bit_lower']) == Fraction(baseline_assembly['bit_lower']) ==
            Fraction(baseline_price['prices']['native']['outer_with_bit']['bit_c']), 'Fresh PR589 endpoint binding')
    profile = assembly['complex_profile']
    require(profile == independent['profile'] == owner['paid_profile'] == audit['complex_profile'] ==
            fresh_plan['profile'] == frozen_spec['expected']['global_profile'], 'Independent global profile agreement')
    require(runtime_plan['runtime_source_plan_sha256'] == sha(work/'lift/PLAN.json') == admitted_spec['data']['plan_sha256'], 'Fresh/frozen/runtime plan binding')
    require(sha(work/'owners/OWNERS.json.gz') == admitted_spec['data']['owners_sha256'] == construction['owners_sha256'], 'Fresh owner construction binding')
    require(construction['changed_roles'] == 11 and len(construction['omitted_edit_controls']) == 11, 'Explicit owner edit controls')
    require(parent_lift['T8_identity_control'] and parent_lift['T8_source_window_identity'] and
            parent_lift['actual_window_membership_checked'] == 72576, 'Parent lift source-window controls')
    expected_semantics = baseline_owner['provider_artifact_semantic_sha256']
    require(owner['provider_artifact_semantic_sha256'] == audit['provider_artifact_semantic_sha256'] ==
            expected_semantics, 'Unchanged fresh PR799 provider semantic identities')
    local = baseline/'native/local'
    provider = global_dir/'base/providers/gauge44'
    for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
                 'INDEPENDENT-LOCAL-REPLAY.json', 'RESIDUAL-ADAPTERS.json',
                 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json'):
        require(read(provider/name) == read(local/name), 'Fresh provider content binding: '+name)
    require(independent['roles'] == owner['hosted_residuals'] == audit['complex_hosted_residuals'] == 72576, 'Whole-helper role inventory')
    require(independent['calls'] == audit['complete_invocations'] == invoice['complete_invocation_sweeps'] == 144, 'Complete invocation inventory')
    require(independent['actual_73_axis_charts'] == owner['actual_73column_sigmas'] == audit['actual_orthogonal_73column_maps'], 'Independent 73-axis chart count')
    require(independent['prefix_bits'] == invoice['global_prefix_bits'] < invoice['charged_prefix_bits'] == 512, 'Independent global prefix reserve')
    require(independent['physical_row_coefficient'] == invoice['finite']['physical_row_coefficient'] <
            invoice['finite']['retained_row_coefficient'] == 20161, 'Independent physical-row reserve')
    require(independent['rank_mass'] == owner['rank_mass'] == 1041408 and
            independent['deficit'] == owner['deficit'] == 5120, 'Rank mass and deficit')
    require(all(invoice['strict_checks'].values()), 'Every finite invoice inequality')
    require(assembly['template_sha256'] == owner['template_sha256'] == invoice['template_sha256'], 'Template/invoice/assembly binding')
    require(invoice['owner_audit_sha256'] == sha(global_dir/'audit/OWNERS-AND-PROFILE.json') and
            invoice['controller_audit_sha256'] == sha(global_dir/'audit/ASYNC-AUDIT.json'), 'Invoice audit byte binding')
    require(len(assembly['outer']) == 47 and all(Fraction(value) > 0 for value in assembly['outer'].values()), 'All 47 strict outer margins')
    require(audit['mutation_controls_run'] and len(audit['mutations_rejected']) == 15, 'Controller mutation controls')
    require(not admission['discovery_accepted_controls'] and
            len(admission['rejected_controls']) == frozen_spec['expected']['assembly_controls_rejected'], 'Strict admission controls')
    require(bit_controls['status'] == 'PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS' and
            len(bit_controls['rejected_controls']) == 12 and bit_controls['derived_deficit'] == 10272, 'PR589 supplier controls')
    require(len(independent['controls_rejected']) == 6, 'Independent owner/window controls')
    kappa = Fraction(assembly['kappa'])
    require(kappa > OLD_KAPPA, 'The new construction must strictly improve accepted PR799')
    expected_stages = (['baseline799-cold'] if not reuse else []) + [
        'baseline741-coverage', 'baseline799-binding', 'source-adapters', 'build-owners', 'build-parent',
        'independent-t16', 'bind', 'emit', 'audit', 'invoice', 'assembly',
        'admission-controls', 'bit-supplier-controls']
    require([stage['name'] for stage in stages] == expected_stages, 'Complete ordered strict stage sequence')
    require(all(stage['log'] == stage['name']+'.log' and stage['exit_code'] == 0 and
                sha(work/stage['log']) == stage['log_sha256'] for stage in stages), 'Stage success and log binding')
    inputs = dict(package_pins, spec_sha256=sha(spec),
                  runtime_spec_sha256=sha(work/'runtime/data/SPEC.json'),
                  owners_content_sha256=artifact_identities['owners_content_sha256'],
                  plan_semantic_sha256=artifact_identities['plan_semantic_sha256'],
                  baseline_binding_sha256=sha(work/'BASELINE-BINDING.json'),
                  baseline741_coverage_sha256=sha(work/'BASELINE741-COVERAGE.json'),
                  source_plan_sha256=sha(SOURCE/'data/PLAN.json'), source_owners_sha256=sha(SOURCE/'data/OWNERS.json.gz'),
                  new_plan_sha256=sha(work/'lift/PLAN.json'), new_owners_sha256=sha(work/'owners/OWNERS.json.gz'),
                  new_parent_sha256=sha(work/'lift/GLOBAL-TEMPLATE.json.gz'),
                  fresh_local_word_sha256=sha(local/'CANONICAL-WORD.json.gz'),
                  fresh_bit_result_sha256=sha(ancestor/'bit/RESULT9.json'),
                  independent_t16_sha256=sha(work/'INDEPENDENT-T16.json'),
                  assembly_sha256=sha(work/'ASSEMBLY.json'))
    return dict(status='PASS_STRICT_T16_PR799_OWNER_CONCENTRATION',
                baseline_mode='explicitly_reused_and_rebound' if reuse else 'cold_rebuilt',
                kappa=str(kappa), kappa_decimal=assembly['kappa_decimal'],
                complex_lower=assembly['complex_lower'], bit_lower=assembly['bit_lower'],
                accepted_pr799_kappa=str(OLD_KAPPA), delta_kappa=str(kappa-OLD_KAPPA),
                global_profile=profile, roles=72576, complete_invocations=144,
                actual_73_axis_charts=independent['actual_73_axis_charts'],
                rank_mass=independent['rank_mass'], deficit=independent['deficit'],
                prefix_bits=independent['prefix_bits'], charged_prefix_bits=512,
                physical_row_coefficient=independent['physical_row_coefficient'], retained_row_coefficient=20161,
                controls=dict(omitted_owner_edits=11, independent_owner_windows=6, controller_mutations=15,
                              admission=len(admission['rejected_controls']), bit_supplier=12,
                              outer=len(assembly['controls']), strict_outer_margins=47),
                input_sha256=inputs, stages=len(stages),
                scope='Strict finite PR799/T16/PR589 composition with independent windows, charts, prefix and row checks. Inherited all-size/compiler, common-label/mutable-source, whole-call hosting, precision/tape and analytic hypotheses remain; no unconditional theorem or full Lean certification.')


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled; do not run verify.py with -O or PYTHONOPTIMIZE')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True, help='New output directory outside this repository')
    parser.add_argument('--baseline799', type=Path, help='Explicit completed verify_frontier799.py output to reuse')
    parser.add_argument('--ancestor741', type=Path, help='Complete PR741/PR589 ancestry corresponding to --baseline799')
    args = parser.parse_args()
    require((args.baseline799 is None) == (args.ancestor741 is None), 'Reuse requires both --baseline799 and --ancestor741')
    work = args.work.resolve()
    require(not work.exists(), 'Output directory must be new: '+str(work))
    require(not work.is_relative_to(ROOT), 'Output directory must be outside the repository')
    package_pins = validate_pins()
    spec = HERE/'data/SPEC.json'
    require(spec.is_file(), 'Missing strict data/SPEC.json')
    work.mkdir(parents=True)
    clean_env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
                     PYTHONINTMAXSTRDIGITS='0', PYTHON=sys.executable, SW4_FRAME8_PYTHON=sys.executable)
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC', 'MULTICOLD_SOURCE', 'GAIN_PR564_SOURCE'):
        clean_env.pop(key, None)
    strict_env = dict(clean_env, WITNESS_SPEC=str(spec), MULTICOLD_SOURCE=str(SRC), GAIN_PR564_SOURCE=str(SRC))
    stages = []

    def run(name, script, *arguments, strict=True):
        start = time.monotonic()
        log = work/(name+'.log')
        print('RUN', name, flush=True)
        command = [sys.executable, '-B', str(SRC/'code/run_portable.py'), str(script), *map(str, arguments)]
        with log.open('w', encoding='utf-8', newline='\n') as stream:
            process = subprocess.run(command, cwd=ROOT, env=strict_env if strict else clean_env,
                                     stdout=stream, stderr=subprocess.STDOUT)
        stage = dict(name=name, seconds=round(time.monotonic()-start, 3), exit_code=process.returncode,
                     log=log.name, log_sha256=sha(log))
        stages.append(stage)
        dump(work/'STAGES.json', stages)
        require(process.returncode == 0, '%s failed with exit %s; see %s\n%s' %
                (name, process.returncode, log, log.read_text(encoding='utf-8', errors='replace')[-6000:]))
        print('PASS', name, stage['seconds'], flush=True)

    reuse = args.baseline799 is not None
    if reuse:
        baseline, ancestor = args.baseline799.resolve(), args.ancestor741.resolve()
        require(baseline.is_dir() and ancestor.is_dir(), 'Both explicit reuse directories must exist')
    else:
        baseline, ancestor = work/'baseline799', work/'baseline799/ancestor'
        run('baseline799-cold', ROOT/'scripts/verify_frontier799.py', '--work', baseline, strict=False)
    run('baseline741-coverage', HERE/'baseline_coverage.py', '--ancestor', ancestor,
        '--out', work/'BASELINE741-COVERAGE.json', strict=False)
    run('baseline799-binding', ROOT/'scripts/verify_frontier799_bindings.py',
        '--ancestor', ancestor, '--native', baseline/'native', '--global', baseline/'global',
        '--independent', baseline/'INDEPENDENT-LOCAL.json', '--price', baseline/'INDEPENDENT-PRICE.json',
        '--out', work/'BASELINE-BINDING.json', strict=False)
    run('source-adapters', HERE/'source_adapters.py', work/'runtime')
    run('build-owners', HERE/'build_owners.py', '--source-plan', SOURCE/'data/PLAN.json',
        '--source-owners', SOURCE/'data/OWNERS.json.gz', '--out', work/'owners')
    old_base = baseline/'global/global/base'
    run('build-parent', HERE/'build_parent.py', '--base', old_base,
        '--source-plan', SOURCE/'data/PLAN.json', '--source-owners', SOURCE/'data/OWNERS.json.gz',
        '--owners', work/'owners/OWNERS.json.gz', '--out', work/'lift')
    runtime_spec, identities = runtime_spec_value(spec, work/'lift/PLAN.json', work/'owners/OWNERS.json.gz')
    runtime_spec_path = work/'runtime/data/SPEC.json'
    runtime_spec_path.parent.mkdir()
    dump(runtime_spec_path, runtime_spec)
    dump(work/'RUNTIME-SPEC-BINDING.json', dict(
        status='PASS_FROZEN_SEMANTIC_OWNER_AND_PLAN_RUNTIME_BINDING',
        frozen_spec_sha256=sha(spec), runtime_spec_sha256=sha(runtime_spec_path),
        owners_file_sha256=sha(work/'owners/OWNERS.json.gz'), plan_file_sha256=sha(work/'lift/PLAN.json'),
        semantic_identities=identities,
        rebound_fields=['data.owners_sha256', 'data.plan_sha256', 'pivot_swap.recipe'],
        scope='Complete owner and PLAN semantics match the frozen identities; only checked generated-container references and the identical immutable pivot location are rebound.'))
    strict_env['WITNESS_SPEC'] = str(runtime_spec_path)
    run('independent-t16', HERE/'independent_check.py',
        '--baseline-parent', old_base/'split-centres/GLOBAL-TEMPLATE.json.gz',
        '--owners', work/'owners/OWNERS.json.gz', '--word', baseline/'native/local/CANONICAL-WORD.json.gz',
        '--out', work/'INDEPENDENT-T16.json')
    shutil.copytree(baseline/'global/parent558', work/'parent')
    shutil.copyfile(work/'lift/GLOBAL-TEMPLATE.json.gz', work/'parent/complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    code, global_dir = work/'runtime/code', work/'global'
    run('bind', code/'bind_providers_portable.py', '--baseline', work/'parent',
        '--provider', 'gauge44='+str(baseline/'native/local'), '--plan', work/'lift/PLAN.json', '--out', global_dir)
    run('emit', code/'emit_allcold.py', '--base', global_dir/'base', '--owners', work/'owners/OWNERS.json.gz',
        '--plan', global_dir/'PLAN.json', '--out', global_dir/'hosted')
    run('audit', code/'audit_allcold.py', global_dir/'base', global_dir/'hosted',
        global_dir/'audit/ASYNC-AUDIT.json', '--mutation-controls')
    retained = SRC/'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json'
    run('invoice', code/'invoice_allcold.py', '--base', global_dir/'base', '--hosted', global_dir/'hosted',
        '--audit', global_dir/'audit', '--out', global_dir/'audit', '--retained-invoice', retained)
    run('assembly', code/'assemble.py', SRC, global_dir, work/'ASSEMBLY.json')
    run('admission-controls', code/'assembly_controls.py', '--source-package', SRC,
        '--owner', global_dir/'audit/OWNERS-AND-PROFILE.json', '--invoice', global_dir/'audit/PREFIX-AND-INVOICE.json',
        '--out', work/'ADMISSION-CONTROLS.json')
    run('bit-supplier-controls', code/'bit_supplier_controls.py', '--source-package', SRC,
        '--owner', global_dir/'audit/OWNERS-AND-PROFILE.json', '--invoice', global_dir/'audit/PREFIX-AND-INVOICE.json',
        '--out', work/'BIT-SUPPLIER-CONTROLS.json')
    require(validate_pins() == package_pins, 'Package or dependency inputs changed during replay')
    result = final_binding(work, baseline, ancestor, spec, package_pins, reuse, stages)
    dump(work/'RESULT.json', result)
    print(result['status'], result['kappa_decimal'], 'improvement='+result['delta_kappa'], flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        print('FAIL:', error, file=sys.stderr)
        raise SystemExit(1)
