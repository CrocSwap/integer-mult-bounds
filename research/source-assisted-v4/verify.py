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
PR184_COMPLEX = Q(25667, 39062500)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


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
        run(SA / 'global/assemble_profiles.py', '--complex', profile,
            '--bit', SA / 'bit/source_aligned_profile.json', '--source', REPO, '--output', assembled)
        final = read(assembled)
        for branch in ('complex', 'bit'):
            final[branch].pop('numerical_root_for_discovery_only', None)
        kappa = Q(final['kappa'])
        complex_saving = Q(final['complex']['saving'])
        assert complex_saving < Q(final['bit']['effective_saving']), 'The complex supplier must bind'
        assert kappa > PR186_KAPPA, 'No gain over PR186'
        for name, check in profile_data['contract_checks'].items():
            assert check is not False, name
        return dict(
            status='PASS conditional finite witness',
            kappa=final['kappa'],
            complex_saving=final['complex']['saving'],
            bit_effective_saving=final['bit']['effective_saving'],
            gain_over_pr186=str(kappa / PR186_KAPPA - 1),
            complex_gain_over_pr184=str(complex_saving / PR184_COMPLEX - 1),
            witness_sha256=sha(witness),
            lift_certificate_sha256=sha(lift.with_suffix('.certificate.json.gz')),
            flow=flow_data, lift=lift_data, complex_profile=profile_data, assembly=final,
            scope='PR184 contract, finite bridge and bit supplier unchanged; the complex supplier is '
                  "PR184's source-parity local word and frame flow on PR168 v4's query modules and physical layer. "
                  'No new flattened bit transcript or full Clifford/router replay, as in PR184.')
    finally:
        shutil.rmtree(WORK, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Authoring only: rewrite certificate.json')
    args = parser.parse_args()
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    before = pins()
    result = build()
    assert pins() == before, 'Source closure changed during verification'
    target = PKG / 'certificate.json'
    if args.write:
        write(target, result)
    else:
        assert result == read(target), 'Canonical certificate does not reproduce'
    print('PASS source-assisted-v4 kappa = ' + result['kappa'] + ' (' + str(float(Q(result['kappa']))) + ')')


if __name__ == '__main__':
    main()
