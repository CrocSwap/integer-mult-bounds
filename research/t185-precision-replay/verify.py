#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded exact replay of T185 precision parameters and release bindings.

This command checks the changed arithmetic, source derivation and recorded
complete release. reproduce_all.py separately performs the complete cold run.
Prepared for digitalis-p with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True

def need(test, why):
    if not test:
        raise ValueError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_bytes())

def authenticate():
    pins = read(HERE / 'PACKAGE-MANIFEST.json')
    actual = {}
    for p in HERE.rglob('*'):
        need(not p.is_symlink(), 'package symlink')
        if p.is_file() and p != HERE / 'PACKAGE-MANIFEST.json':
            actual[p.relative_to(HERE).as_posix()] = sha(p)
    need(actual == pins, 'complete package inventory and bytes')
    return pins

def run(work):
    need(not sys.flags.optimize, 'assertions must be enabled')
    pins = authenticate()
    deps = read(HERE / 'DEPENDENCIES.json')
    base = HERE / 'inputs/pr2863'
    need(sha(base / 'MANIFEST.json') == deps['original_manifest_sha256'], 'pinned predecessor manifest')
    upstream = read(base / 'MANIFEST.json')
    for name, digest in deps['subset_sha256'].items():
        need(sha(base / name) == digest, 'exact predecessor subset: ' + name)
        if name != 'MANIFEST.json':
            need(upstream[name] == digest, 'predecessor manifest member: ' + name)
    old = read(base / 'CLAIM.json')
    claim = read(HERE / 'CLAIM.json')
    need(claim['status'] == 'PASS_COMPLETE_PRECISION_ONLY_RELEASE', 'complete release status required')
    need(claim['baseline_head'] == deps['baseline_head'], 'exact comparison head')
    profile = {int(r): n for r, n in read(base / 'data/PROFILE.json').items()}
    need(profile == {int(r): n for r, n in old['paid_profile'].items()}, 'actual baseline profile')
    need(profile == {int(r): n for r, n in claim['paid_profile'].items()}, 'unchanged paid profile')
    native = read(HERE / 'evidence/SHARED-NATIVE-RESULT.json')
    baseline = read(HERE / 'evidence/BASELINE-RESULT.json')
    result = read(HERE / 'evidence/CANDIDATE-RESULT.json')
    release = read(HERE / 'evidence/CANDIDATE-RELEASE.json')
    need(baseline['status'] == 'PASS_T185_PORTABLE_COMPLETE_REPLAY', 'fresh baseline complete replay')
    baseline_admission = read(HERE / 'evidence/BASELINE-CANDIDATE-RESULT.json')
    baseline_release = read(HERE / 'evidence/BASELINE-RELEASE.json')
    need(sha(HERE / 'evidence/BASELINE-CANDIDATE-RESULT.json') == baseline['candidate_result_sha256'], 'cold baseline admission binding')
    need(sha(HERE / 'evidence/BASELINE-RELEASE.json') == baseline_admission['release_receipt_sha256'] and baseline_release['status'] == 'PASS_RELEASE', 'cold baseline strict release binding')
    need(sha(HERE / 'evidence/BASELINE-MANIFEST.json') == baseline_admission['package_manifest_sha256'] == baseline_release['manifest_sha256'], 'cold baseline supplier manifest')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete candidate admission')
    need(release['status'] == 'PASS_RELEASE', 'strict release')
    need(sha(HERE / 'evidence/CANDIDATE-RELEASE.json') == result['release_receipt_sha256'] == claim['release_receipt_sha256'], 'release receipt binding')
    need(result['package_manifest_sha256'] == release['manifest_sha256'], 'full derived supplier manifest')
    supplier_manifest = HERE / 'evidence/CANDIDATE-MANIFEST.json'
    need(sha(supplier_manifest) == release['manifest_sha256'], 'actual complete supplier manifest')
    supplier_pins = read(supplier_manifest)
    for path in (HERE / 'inputs/admitted-outer').rglob('*'):
        if path.is_file():
            name = path.relative_to(HERE / 'inputs/admitted-outer').as_posix()
            need(sha(path) == supplier_pins[name], 'actual admitted outer bytes: ' + name)
    need(result['native_receipt_sha256'] == native['native_receipt_sha256'] == claim['native_receipt_sha256'], 'shared fresh native binding')
    native_receipt = read(HERE / 'evidence/NATIVE-RECEIPT.json')
    need(sha(HERE / 'evidence/NATIVE-RECEIPT.json') == result['native_receipt_sha256'], 'actual native receipt')
    need(native_receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE', 'native cache admission status')
    need(sha(HERE / 'evidence/OVERLAY-MANIFEST.json') == native_receipt['manifest_sha256'] == deps['new_native_overlay_manifest_sha256'], 'native source manifest binding')
    need(sha(HERE / 'evidence/SOURCE-MANIFEST.json') == deps['full_source_manifest_sha256'], 'original source manifest binding')
    need(baseline['native_receipt_sha256'] == result['native_receipt_sha256'], 'same native evidence as cold baseline')
    need(baseline['fresh_retained_bootstrap'] is True and baseline['explicit_retained_reuse'] is False and baseline['fresh_changed_native_chains'] == 2, 'cold baseline freshness')
    need(result['comparison_head'] == deps['baseline_head'] and Q(result['comparison_kappa']) == Q(old['kappa']) and result['comparison_claim_sha256'] == sha(base / 'CLAIM.json'), 'complete admission comparison provenance')
    need({int(r): n for r, n in result['profile'].items()} == profile, 'complete admission unchanged paid profile')
    need(Q(baseline['kappa']) == Q(old['kappa']), 'reproduced exact baseline')
    need(Q(result['kappa']) == Q(release['kappa_decimal']) == Q(claim['kappa']), 'same complete outer headline')
    need(Q(claim['kappa']) - Q(old['kappa']) == Q(claim['gain']) > 0, 'strict rational gain')
    # Execute authenticated source bytes directly; no timestamp-valid pyc can
    # substitute for the source checked by the package inventory.
    source = HERE / 'endpoint_refiner.py'
    refiner = types.ModuleType('authenticated_endpoint_refiner')
    exec(compile(source.read_bytes(), str(source), 'exec'), refiner.__dict__)
    coarse = Q(old['kappa']) + Q(1, 10**46) + Q(1, 10**70)
    C = refiner.refine(profile, 73, old['live'], coarse, False, 40)
    need(C == Q(claim['complex_lower']), 'regenerated fine native endpoint')
    conservative = read(HERE / 'inputs/conservative40.json')
    bad = refiner.refine(profile, 73, old['live'], Q(conservative['coarse']), True, 40)
    need(bad == Q(conservative['fine']) == Q(claim['conservative_lower']), 'regenerated conservative endpoint')
    need(Q(claim['kappa']) == C-Q(1, 10**62)-Q(1, 10**86), 'fixed-grid outer equality')
    precision = work / 'precision'
    (precision / 'screen40').mkdir(parents=True)
    shutil.copyfile(HERE / 'inputs/screen40.json', precision / 'screen40/RESULT.json')
    shutil.copyfile(HERE / 'inputs/conservative40.json', precision / 'conservative40.json')
    shutil.copyfile(HERE / 'build_precision_driver.py', precision / 'build_precision_driver.py')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX=str(work / 'fresh-pycache'), FINE_ENGINE_WORKERS='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for key in ['PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD']:
        env.pop(key, None)
    stages = []
    def execute(label, args):
        command = [sys.executable, '-B', *map(str, args)]
        log = work / (label + '.log')
        with log.open('wb') as output:
            proc = subprocess.run(command, cwd=work, env=env, stdout=output, stderr=subprocess.STDOUT)
        stages.append(dict(stage=label, command=command, exit_code=proc.returncode, log_sha256=sha(log)))
        need(proc.returncode == 0, label + ' failed; inspect ' + str(log))
    execute('derive-driver', [HERE / 'build_precision_driver.py', '--package', base, '--out', precision / 'driver40'])
    need(sha(precision / 'driver40/admit_precision.py') == claim['admission_driver_sha256'], 'identical frozen admission driver')
    execute('independent-optimum', [HERE / 'audit/check_optimum.py', base, work / 'optimum'])
    execute('independent-precision', [HERE / 'audit/check_precision.py', base, precision, work / 'independent', HERE / 'inputs/source-assembler.py'])
    independent = read(work / 'independent/RESULT.json')
    need(Q(independent['kappa']) == Q(claim['kappa']) and Q(independent['gain']) == Q(claim['gain']), 'independent exact gain')
    staged = work / 'outer'
    shutil.copytree(HERE / 'inputs/admitted-outer', staged)
    spec = read(staged / 'new/SPEC.json')
    need(Q(spec['expected']['complex_lower']) == C and Q(spec['expected']['conservative_complex_lower']) == bad, 'actual admitted SPEC endpoints')
    need(spec['expected']['global_profile'] == old['paid_profile'] and spec['expected']['live'] == old['live'], 'actual admitted normalization/profile')
    for script in ['check_ledger.py', 'independent_check.py']:
        execute('outer-' + script, [staged / 'outer' / script])
    ledger = read(staged / 'outer/LEDGER.json')
    row = ledger['rows']['struct_boundary_radix_union']
    need(Q(row['kappa']['rational']) == Q(claim['kappa']), 'fresh exact outer kappa')
    need(len(row['strict_checks']) == 63 and all(Q(v['rational']) > 0 for v in row['strict_checks'].values()), '63 strict outer inequalities')
    need(len(ledger['rejecting_controls']['struct_boundary_radix_union']) == 17, '17 outer rejecting controls')
    need(authenticate() == pins, 'immutable package after replay')
    report = dict(status='PASS_BOUNDED_PRECISION_AND_RELEASE_BINDING', kappa=claim['kappa'], gain=claim['gain'], stages=stages,
                  scope='Fresh exact arithmetic, independent fixed-model proof and driver audit, and authenticated complete-release receipts. Full native/owner/outer cold replay is reproduce_all.py; all inherited asymptotic assumptions remain.')
    (work / 'RESULT.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], 'gain=' + claim['gain'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if args.work:
        need(not args.work.resolve().is_relative_to(HERE), 'work must be outside immutable package')
        need(not args.work.exists(), 'fresh work directory required')
        args.work.mkdir(parents=True)
        run(args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='t185-precision-') as temp:
            run(Path(temp))

if __name__ == '__main__':
    main()
