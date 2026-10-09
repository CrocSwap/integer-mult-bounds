#!/usr/bin/env python3
"""Regenerate the PR184 source-assisted complex supplier on PR168 v4 modules and assemble kappa.

Usage from the repository root, with Python assertions enabled:

    python3 -m pip install -r research/source-assisted/requirements-round13.txt
    python3 -B research/source-assisted-v4/verify.py

The script checks SOURCE.json, rebuilds the complex word in a scratch
directory inside this package, runs the unchanged PR184 flow, exact lift and
global assembly, runs this package's copy of the PR184 contract checker, and
compares the canonical result with certificate.json. --write is authoring
mode: it rewrites certificate.json instead of comparing.

Prepared by Avi Eisenberg with Claude (Anthropic) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

PKG = Path(__file__).resolve().parent
REPO = PKG.parents[1]
SA = REPO / 'research/source-assisted'
WORK = PKG / '.work'
PR186_KAPPA = Q(330942774629799, 500000000000000000)
PR191_KAPPA = Q(6626307, 10**10)
PR193_KAPPA = Q(103873, 156250000)
PR184_COMPLEX = Q(25667, 39062500)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def canon(value):
    # Binary floats are discovery diagnostics; round them so that last-digit
    # libm differences between platforms cannot change the comparison.
    if isinstance(value, float):
        return format(value, '.12e')
    if isinstance(value, dict):
        return {k: canon(v) for k, v in value.items()}
    if isinstance(value, list):
        return [canon(v) for v in value]
    return value


def differences(actual, expected, limit=24):
    found = []

    def show(value):
        text = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        return text if len(text) <= 240 else text[:237] + '...'

    def walk(a, e, path='$'):
        if len(found) >= limit:
            return
        if isinstance(a, dict) and isinstance(e, dict):
            for key in sorted(set(a) | set(e)):
                if len(found) >= limit:
                    break
                child = path + '.' + str(key)
                if key not in a:
                    found.append((child, '<missing>', show(e[key])))
                elif key not in e:
                    found.append((child, show(a[key]), '<missing>'))
                else:
                    walk(a[key], e[key], child)
        elif isinstance(a, list) and isinstance(e, list):
            if len(a) != len(e):
                found.append((path + '.length', str(len(a)), str(len(e))))
            for i, (av, ev) in enumerate(zip(a, e)):
                if len(found) >= limit:
                    break
                walk(av, ev, path + '[' + str(i) + ']')
        elif a != e:
            found.append((path, show(a), show(e)))

    walk(actual, expected)
    return found


def rel(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def run(*args):
    result = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=REPO,
                            capture_output=True, text=True)
    if result.returncode:
        raise SystemExit('FAILED: ' + ' '.join(map(str, args)) + '\n'
                         + result.stdout[-4000:] + result.stderr[-4000:])
    return result.stdout


def strip(path):
    # Elapsed times are the only nondeterministic fields of these receipts.
    data = read(path)
    data.pop('seconds', None)
    write(path, data)
    return data


def pins():
    manifest = read(PKG / 'SOURCE.json')
    actual = {name: sha(REPO / name) for name in manifest['files']}
    assert actual == manifest['files'], 'Pinned source or input bytes changed'
    return actual


def build():
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    try:
        base, aligned = WORK / 'base', WORK / 'aligned'
        run(REPO / 'scripts/paired_cube_producer.py', '--work-dir', base, '--output', WORK / 'producer.json')
        run(PKG / 'source_aligned_local_v4.py', '--tree', REPO, '--cache', base, '--out', aligned,
            '--pairs', PKG / 'data/physical-pairs.json')
        flow = WORK / 'flow.json'
        run(SA / 'decision/complex_frame_flow.py', '--tree', aligned, '--cache', aligned / 'cache',
            '--out', flow, '--witness', '--purify-source-donors', '--recycle-kernels',
            '--kernel-pairs', PKG / 'data/kernel-pairs.json')
        flow_data = strip(flow)
        witness = flow.with_suffix('.witness.json')
        lift = WORK / 'lift.json'
        run(SA / 'decision/exact_complex_flow_lift.py', '--witness', witness, '--profile', flow, '--out', lift)
        lift_data = strip(lift)
        # PR184's lift records paths relative to its own package; record them
        # relative to the repository so the receipt is portable.
        lift_data.update(certificate_path=rel(lift.with_suffix('.certificate.json.gz')),
                         witness_path=rel(witness),
                         checker_path=rel(SA / 'decision/exact_complex_flow_lift.py'))
        write(lift, lift_data)
        profile = WORK / 'complex-profile.json'
        run(PKG / 'contract_v4.py', '--tree', aligned, '--cache', aligned / 'cache', '--witness', witness,
            '--flow-profile', flow, '--lift-profile', lift, '--out', profile)
        profile_data = strip(profile)
        assembled = WORK / 'global.json'
        run(PKG / 'assemble.py', '--complex', profile, '--output', assembled)
        final = read(assembled)
        for branch in ('complex', 'bit'):
            final[branch].pop('numerical_root_for_discovery_only', None)
        kappa = Q(final['kappa'])
        complex_saving = Q(final['complex']['saving'])
        bit_saving = Q(final['bit']['effective_saving'])
        assert kappa > PR193_KAPPA > PR191_KAPPA > PR186_KAPPA, 'No gain over PR193'
        for name, check in profile_data['contract_checks'].items():
            assert check is not False, name
        return canon(dict(
            status='PASS conditional finite witness',
            kappa=final['kappa'],
            complex_saving=final['complex']['saving'],
            bit_effective_saving=final['bit']['effective_saving'],
            binding_supplier='bit' if bit_saving < complex_saving else 'complex',
            gain_over_pr186=str(kappa / PR186_KAPPA - 1),
            gain_over_pr191=str(kappa / PR191_KAPPA - 1),
            gain_over_pr193=str(kappa / PR193_KAPPA - 1),
            complex_gain_over_pr184=str(complex_saving / PR184_COMPLEX - 1),
            witness_sha256=sha(witness),
            lift_certificate_sha256=sha(lift.with_suffix('.certificate.json.gz')),
            flow=flow_data, lift=lift_data, complex_profile=profile_data, assembly=final,
        scope='PR184 contract and finite bridge unchanged; the bit supplier is PR189 after 102 exact endpoint-frame lowerings (verified by its own verify.py), then the PR185 depth-2 finite ordinary-leaf bootstrap; the complex supplier is '
              "PR184's source-parity local word and frame flow on PR168 v4's query modules and physical layer, "
                  'with donor/recipient pairs that avoid parity purification. '
                  'No new flattened bit transcript or full Clifford/router replay, as in PR184.'))
    finally:
        shutil.rmtree(WORK, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Authoring only: rewrite certificate.json')
    parser.add_argument('--candidate-output', type=Path,
                        help='Write the regenerated canonical certificate here before comparison')
    args = parser.parse_args()
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    before = pins()
    result = build()
    assert pins() == before, 'Source closure changed during verification'
    if args.candidate_output:
        write(args.candidate_output, result)
    target = PKG / 'certificate.json'
    if args.write:
        write(target, result)
    else:
        expected = read(target)
        if result != expected:
            for path, generated, saved in differences(result, expected):
                print('Certificate mismatch at ' + path + ': generated=' + generated + ' saved=' + saved)
            raise AssertionError('Canonical certificate does not reproduce')
    print('PASS source-assisted-v4 kappa = ' + result['kappa'] + ' (' + str(float(Q(result['kappa']))) + ')')


if __name__ == '__main__':
    main()
