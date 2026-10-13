"""Reissue the complete selected invoice for a certified primitive refinement.

No mathematical source or selected record is edited. Original native/phase/
wrapper/controller evidence is required and the unchanged assembly runs again.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
from fractions import Fraction
import importlib.util
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from lowering import sources, read, emit, require, canonical


def dump(path, data):
    path.write_bytes((json.dumps(data, indent=2) + '\n').encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, required=True)
    parser.add_argument('--ancestor', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(__debug__, 'Admission requires enabled assertions')
    pins = sources()
    expected = read(HERE / 'EXPECTED.json')
    require(set(expected) == {'status', 'base', 'predecessor', 'kappa',
                             'saved_selected_real_component_primitives', 'saved_coefficient_work_operations',
                             'global_prefix_bits', 'physical'}, 'Frozen result field domain')
    require(all(type(expected[k]) is int for k in ('saved_selected_real_component_primitives',
               'saved_coefficient_work_operations', 'global_prefix_bits', 'physical')),
            'Frozen result integer domain')
    replay, out = args.replay.resolve(), args.out.resolve()
    require(not out.exists() and not out.is_relative_to(ROOT), 'Fresh external output required')
    # Use the unchanged PR865 gate in an explicitly configured source context.
    # It checks complete coverage before calling the original mathematical binder.
    sys.path.insert(0, str(ROOT / 'scripts'))
    path = HERE / 'vendor/pr865/verify_replay_coverage.py'
    module_spec = importlib.util.spec_from_file_location('x4_required_coverage', path)
    coverage = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(coverage)
    coverage.ROOT = ROOT
    coverage.CONTRACT = HERE / 'vendor/pr865/pr741-sw4-v1.json'
    guarded = coverage.check_selected(replay, args.ancestor.resolve())
    binding = guarded['selected_binding']
    require(binding['kappa'] == '1661634653669567/1000000000000000000', 'Pinned selected result')
    out.mkdir(parents=True)
    local = replay / 'native/local'
    lowering = emit(local, out / 'lowering')
    baseline = replay / 'global/global'
    original_invoice = read(baseline / 'audit/PREFIX-AND-INVOICE.json')
    source = ROOT / 'research/gauge44-frames-x'
    multicold = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
    os.environ.update(WITNESS_SPEC=str(source / 'data/SPEC.json'),
                      GAIN_PR564_SOURCE=str(multicold))
    for key in ('WITNESS_DISCOVER', 'WITNESS_RECORD', 'PYTHONOPTIMIZE'):
        os.environ.pop(key, None)
    ns = runpy.run_path(str(source / 'code/invoice_allcold.py'), run_name='x4_invoice_refinement')
    run = ns['run']
    original_recount = run.__globals__['recount_provider']
    lowering_hash = sha256(canonical(lowering)).hexdigest()

    def refined_recount(directory, registry):
        provider = original_recount(directory, registry)
        # Original physical admission covers identical macro semantics. The
        # concrete lowering relation is independently required here, before any
        # numerical reduction is accepted into the complete invoice.
        for name, digest in lowering['source_artifacts'].items():
            require(sha256((directory / name).read_bytes()).hexdigest() == digest,
                    'Provider differs from audited lowering: ' + name)
        for orientation, row in provider['local'].items():
            proof = lowering['orientations'][orientation]
            require(row['real_component_primitives'] == proof['audit']['retained']['real_component_primitives'], 'Retained primitive count')
            row['real_component_primitives'] = proof['emitted']['real_component_primitives']
            row['coefficient_work_primitive_count'] -= proof['coefficient_work_operations_removed']
            require(row['coefficient_work_primitive_count'] >= 0, 'Coefficient bill')
            # Retain the larger inherited absolute-envelope bound. PR883's
            # complete primitive replay separately checks exact prefix growth.
            require(Fraction(row['prefix_l1']) >= Fraction(proof['emitted']['exact_prefix_row_l1']),
                    'Conservative magnitude reserve')
            require(proof['emitted']['exact_prefix_fraction_bits'] <=
                    proof['audit']['retained']['exact_prefix_fraction_bits'],
                    'Retained fractional grid reserve')
        provider['local_primitive_bound'] = max(z['real_component_primitives'] for z in provider['local'].values()) + provider['local_adapters'] * provider['compiler']
        provider['primitive_lowering'] = dict(receipt_sha256=lowering_hash,
                                              program_content_sha256=lowering['primitive_program_content_sha256'])
        return provider

    run.__globals__['recount_provider'] = refined_recount
    vendor = multicold / 'vendor/pr558/vendor/pr552/complex-global/vendor531'
    invoice = run(baseline / 'base', baseline / 'hosted', baseline / 'audit', out / 'invoice',
                  vendor / 'evidence/audit/PREFIX-AND-INVOICE.json')
    require(original_invoice['selected_real_component_primitives'] - invoice['selected_real_component_primitives'] == 72 * 784,
            'Complete selected primitive saving')
    require(invoice['global_prefix_bits'] == original_invoice['global_prefix_bits'] and invoice['physical'] == original_invoice['physical'],
            'Inherited prefix/stock must be retained')
    require(all(invoice['strict_checks'].values()), 'Finite inequalities')
    # Produce a separate candidate contract. Recompute and freeze only the
    # fields whose certified primitive implementation changed.
    candidate = out / 'candidate-package'
    shutil.copytree(source, candidate)
    spec = read(candidate / 'data/SPEC.json')
    for pid, provider in invoice['providers'].items():
        desc = spec['providers'][pid]
        desc['complete_contract'] = {k: v for k, v in provider.items() if k != 'artifacts'}
        for orientation, row in provider['local'].items():
            desc['expected_local'][orientation] = {k: row[k] for k in ('events', 'macros', 'real_component_primitives', 'prefix_l1', 'coefficient_work_primitive_count')}
    dump(candidate / 'data/SPEC.json', spec)
    assembly_input = out / 'assembly-input'
    (assembly_input / 'audit').mkdir(parents=True)
    (assembly_input / 'hosted').mkdir()
    shutil.copyfile(baseline / 'hosted/HOSTED.json', assembly_input / 'hosted/HOSTED.json')
    shutil.copyfile(baseline / 'audit/OWNERS-AND-PROFILE.json', assembly_input / 'audit/OWNERS-AND-PROFILE.json')
    shutil.copyfile(out / 'invoice/PREFIX-AND-INVOICE.json', assembly_input / 'audit/PREFIX-AND-INVOICE.json')
    environment = dict(os.environ, WITNESS_SPEC=str(candidate / 'data/SPEC.json'), PYTHONDONTWRITEBYTECODE='1')
    with (out / 'assembly.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([sys.executable, '-B', str(candidate / 'code/assemble.py'),
                                 str(multicold), str(assembly_input), str(out / 'ASSEMBLY.json')],
                                env=environment, stdout=log, stderr=subprocess.STDOUT)
    require(result.returncode == 0, 'Refined assembly failed: ' + (out / 'assembly.log').read_text()[-3000:])
    assembly = read(out / 'ASSEMBLY.json')
    require(assembly['kappa'] == binding['kappa'], 'Unexpected exponent change')
    summary = dict(status='PASS_X4_PRIMITIVE_GLOBAL_ADMISSION', base=pins['base'], predecessor=pins['pr883'],
                   kappa=assembly['kappa'], saved_selected_real_component_primitives=72*784,
                   saved_coefficient_work_operations=original_invoice['selected_coefficient_work_primitive_count']-invoice['selected_coefficient_work_primitive_count'],
                   global_prefix_bits=invoice['global_prefix_bits'], physical=invoice['physical'],
                   lowering_sha256=lowering_hash, invoice_sha256=sha256((out/'invoice/PREFIX-AND-INVOICE.json').read_bytes()).hexdigest(),
                   assembly_sha256=sha256((out/'ASSEMBLY.json').read_bytes()).hexdigest(),
                   scope='Fresh selected native/phase/wrapper/owner admission plus certified explicit primitive refinement and complete invoice/assembly. No new kappa; inherited all-size and analytic assumptions remain.')
    require(canonical({k: summary[k] for k in expected}) == canonical(expected),
            'Refined mathematical result differs from frozen expectation')
    require(sources() == pins, 'Consumed source bytes changed during admission')
    dump(out / 'RESULT.json', summary)
    print(summary['status'], 'saved=56448', 'kappa=' + assembly['kappa'])


if __name__ == '__main__':
    main()
