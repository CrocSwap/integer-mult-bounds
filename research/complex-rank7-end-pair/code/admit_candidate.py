"""Admit a fresh native candidate with unchanged predecessor predicates.

The prior full ancestor replay is reused only after its receipt is verified.
No source package is copied or edited; only candidate data are prepared.
"""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from prepare_candidate import add_native_arguments, selected_dispatch, selected_native_directories


HERE = Path(__file__).resolve().parent


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def need(value, message):
    if not value:
        raise ValueError(message)


def verify_manifest(package):
    actual = {p.relative_to(package).as_posix(): sha(p) for p in package.rglob('*')
              if p.is_file() and p != package / 'MANIFEST.json' and '__pycache__' not in p.parts}
    need(actual == read(package / 'MANIFEST.json'), 'Changed source package: ' + str(package))


def verify_receipt(directory):
    receipt = read(directory / 'RECEIPT.json')
    for name, expected in receipt['artifacts'].items():
        need(sha(directory / name) == expected, 'Changed replay artifact: ' + str(directory / name))
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('ancestor-package', 'ancestor-replay', 'dependency', 'checker-package', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    add_native_arguments(ap)
    ap.add_argument('--owners', type=Path, help='Specified gzipped owner rows for the fresh native widths')
    ap.add_argument('--comparison-record', type=Path, required=True,
                    help='Pinned selected-result record used for the strict improvement comparison')
    args = ap.parse_args()
    ancestor, replay, dep, checker, out = [getattr(args, name).resolve() for name in
        ('ancestor_package', 'ancestor_replay', 'dependency', 'checker_package', 'out')]
    natives = selected_native_directories(args)
    dispatch = selected_dispatch(args, natives)
    need(__debug__, 'Assertions must remain enabled')
    comparison_path = args.comparison_record.resolve()
    comparison_sha = sha(comparison_path)
    comparison = read(comparison_path)
    need(Fraction(comparison['kappa']) == Fraction(comparison['decimal']), 'Comparison record value')
    need(not out.exists(), 'Use a new output directory')
    need(not any(out.is_relative_to(p) for p in (ancestor, replay, dep, checker, *natives.values())),
         'Output must be separate from input artifacts and source packages')
    for package in (ancestor, dep, checker):
        verify_manifest(package)
    ancestor_receipt = verify_receipt(replay)
    need(ancestor_receipt['manifest_sha256'] == sha(ancestor / 'MANIFEST.json'), 'Ancestor source binding')
    need(read(replay / 'RESULT.json')['status'] ==
         'PASS_FRESH_SW4_EIGHT_FRAMES_COMPLETE_NATIVE_OWNER_AND_EXACT_GLOBAL_REPLAY', 'Full ancestor replay required')
    need(read(replay / 'ANCESTRAL-LINK.json')['status'] ==
         'PASS_FRESH_ANCESTRAL_INPUTS_MATCH_PINNED_BASELINE', 'Fresh ancestor semantic linkage required')
    need((ancestor / 'data/UPSTREAM-PINS.json').read_bytes() == (dep / 'data/UPSTREAM-PINS.json').read_bytes(),
         'Global ancestry differs from the replayed predecessor')
    for native in natives.values():
        verify_receipt(native)
        need(read(native / 'RESULT.json')['status'] == 'PASS_COMPLETE_NATIVE_REPLAY_UNCHANGED_CHECKERS',
             'Fresh native pipeline required')
        for key, package in (('ancestor_manifest', ancestor), ('dependency_manifest', dep)):
            need(read(native / 'RESULT.json')['input_sha256'][key] == sha(package / 'MANIFEST.json'), 'Native source binding')
    out.mkdir(parents=True)
    root = ancestor / 'vendor/main'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    for key in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)
    stages = []
    started = time.monotonic()
    dump(out / 'ANCESTRY-REUSE.json', {'status': 'PASS_HASH_VERIFIED_FRESH_ANCESTRY_REUSE',
         'ancestor_result_sha256': sha(replay / 'RESULT.json'),
         'ancestor_receipt_sha256': sha(replay / 'RECEIPT.json'),
         'ancestral_link_sha256': sha(replay / 'ANCESTRAL-LINK.json'),
         'upstream_pins_sha256': sha(dep / 'data/UPSTREAM-PINS.json'),
         'native_receipt_sha256': {pid: sha(n / 'RECEIPT.json') for pid, n in natives.items()},
         'source_manifests': {str(p): sha(p / 'MANIFEST.json') for p in (ancestor, dep, checker)},
         'scope': 'Unchanged ancestral circuits and literal geometry were freshly replayed once. The changed native word and full global admission are checked separately.'})

    def run(name, script, *arguments):
        print('RUN', name, flush=True)
        cmd = [sys.executable, '-B', str(script), *map(str, arguments)]
        log = out / (name + '.log')
        before = time.monotonic()
        with log.open('w') as stream:
            result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT, env=env)
        stages.append({'name': name, 'command': cmd, 'script_sha256': sha(script),
                       'exit_code': result.returncode, 'seconds': time.monotonic() - before,
                       'log_sha256': sha(log)})
        dump(out / 'STAGES.json', stages)
        if result.returncode:
            raise RuntimeError(name + ' failed:\n' + log.read_text()[-8000:])
        print('PASS', name, flush=True)

    witness = out / 'witness'
    owner_args = ['--owners', args.owners.resolve()] if args.owners else []
    if args.native:
        native_args = ['--native', args.native.resolve()]
    else:
        frozen_dispatch = out / 'DISPATCH.json'
        dump(frozen_dispatch, [[s, r, dispatch[s, r]] for s in range(9) for r in range(8)])
        native_args = [part for pid, path in sorted(natives.items())
                       for part in ('--native-provider', pid + '=' + str(path))]
        native_args += ['--dispatch', frozen_dispatch]
    run('prepare-data', HERE / 'prepare_candidate.py', '--dependency', dep, *native_args,
        '--out', witness, *owner_args)
    plan, owners, spec = [witness / 'data' / name for name in ('PLAN.json', 'OWNERS.json.gz', 'SPEC.json')]
    provider_args = [part for pid, path in sorted(natives.items())
                     for part in ('--provider', pid + '=' + str(path / 'local'))]
    global_args = ['--main', root, '--dependency', dep, '--plan', plan, '--owners', owners,
                   '--spec', spec, *provider_args]
    run('discovery', checker / 'verify_global.py', *global_args, '--work', out / 'discovery', '--discover')
    discovery_spec_sha = sha(spec)
    run('freeze-spec', checker / 'freeze_spec.py', '--spec', spec, '--discovery', out / 'discovery')
    frozen_spec_sha = sha(spec)
    need(discovery_spec_sha != frozen_spec_sha, 'Discovery values must be frozen before strict replay')
    run('strict-global', checker / 'verify_global.py', *global_args, '--work', out / 'global-replay')
    run('independent-owner-moment', checker / 'audit_owners.py', '--dependency', dep, '--plan', plan,
        '--owners', owners, '--spec', spec, *provider_args,
        '--output', out / 'INDEPENDENT-OWNERS.json')
    run('independent-two-engine-outer47', dep / 'independent/price_profile.py', '--main', root,
        '--profile', plan, '--output', out / 'INDEPENDENT-PRICE.json')
    need(sha(spec) == frozen_spec_sha, 'Frozen spec changed during strict verification')
    assembly = read(out / 'global-replay/ASSEMBLY.json')
    expected = read(spec)['expected']
    owner_audit = read(out / 'INDEPENDENT-OWNERS.json')
    price = read(out / 'INDEPENDENT-PRICE.json')
    kappa = expected['kappa']
    need(kappa == assembly['kappa'] == owner_audit['kappa'] == price['prices']['native']['outer_with_bit']['kappa'],
         'Independent kappa witnesses disagree')
    baseline_kappa = comparison['kappa']
    need(Fraction(kappa) > Fraction(baseline_kappa), 'A strictly improved kappa is required')
    need(len(owner_audit['negative_controls']) == 7 and owner_audit['roles'] == 36288, 'Independent owner census')
    for mode in ('native', 'conservative'):
        need(price['prices'][mode]['outer_with_bit']['strict_constraints_passed'] == 47, 'All outer constraints')
    admission = read(out / 'global-replay/ADMISSION-CONTROLS.json')
    discovery_controls = read(out / 'discovery/ADMISSION-CONTROLS.json')
    census = discovery_controls['rejected_controls'] + discovery_controls['discovery_accepted_controls']
    need(len(census) == len(set(census)) == expected['assembly_controls_rejected']
         and set(admission['rejected_controls']) == set(census)
         and len(admission['rejected_controls']) == len(census) and not admission['discovery_accepted_controls'],
         'Strict admission mutation census')
    bit = read(out / 'global-replay/BIT-SUPPLIER-CONTROLS.json')
    need(len(bit['rejected_controls']) == 12 and bit['derived_deficit'] == 10272, 'Bit controls')
    result = {'status': 'PASS_STRICTLY_IMPROVED_KAPPA_UNCHANGED_ADMISSION', 'kappa': kappa,
         'kappa_decimal': assembly['kappa_decimal'], 'baseline_kappa': baseline_kappa,
         'comparison_record_sha256': comparison_sha,
         'gain': str(Fraction(kappa) - Fraction(baseline_kappa)), 'complex_lower': assembly['complex_lower'],
         'bit_lower': assembly['bit_lower'], 'global_profile': assembly['complex_profile'],
         'seconds': time.monotonic() - started, 'stages': stages,
         'scope': 'Finite conditional native exact-complex witness. Hash-verified reuse of a fresh ancestral replay; full changed-native and global admission. Cited PR589 bit circuit is repriced with its surcharge and controls. All inherited all-size and analytic-transfer assumptions remain.'}
    need(sha(comparison_path) == comparison_sha, 'Comparison record changed during admission')
    dump(out / 'RESULT.json', result)
    retained = [p for p in out.rglob('*') if p.is_file() and p.name != 'RECEIPT.json']
    dump(out / 'RECEIPT.json', {'status': result['status'],
                              'native_receipt_sha256': {pid: sha(n / 'RECEIPT.json') for pid, n in natives.items()},
                              'artifacts': {p.relative_to(out).as_posix(): sha(p) for p in retained}})
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
