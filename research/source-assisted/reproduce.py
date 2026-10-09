#!/usr/bin/env python3
"""Reproduce the focused Round 13 increment without network access.

Prepared for icekylinx by GPT-6 Astra, 2026-10-09. Apache-2.0.
The immutable PR168 reference retains all original authorship and notices.
This driver writes only to the requested output directory.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PIN = ROOT/'public/pr168_fd25adb7'


def read(path):
    return json.loads(path.read_text())


def check_inputs():
    manifest = ROOT/'SHA256SUMS'
    checked = 0
    if manifest.is_file():
        for line in manifest.read_text().splitlines():
            expected, name = line.split('  ', 1)
            path = ROOT/name
            assert path.is_file(), name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
            checked += 1
    parent = read(PIN/'certificates/paired-cube-network.json')['source_sha256']
    for name, expected in parent.items():
        assert hashlib.sha256((PIN/name).read_bytes()).hexdigest() == expected, name
    return dict(package_files_checked=checked, parent_certificate_inputs_checked=len(parent))


def run(script, log, *args):
    with log.open('w') as stream:
        command = [sys.executable, str(ROOT/script), *map(str, args)]
        completed = subprocess.run(command, cwd=ROOT, stdout=stream,
                                   stderr=subprocess.STDOUT, check=False)
    if completed.returncode:
        raise RuntimeError(f'{script} failed; see {log}')
    print(f'PASS {script}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arithmetic-only', action='store_true',
                        help='Check recorded profile moments and all 47 constraints, without regenerating the physical construction.')
    parser.add_argument('--output', type=Path, default=ROOT/'reproduced')
    args = parser.parse_args()
    if sys.flags.optimize:
        raise ValueError('Assertions are part of the certificate: do not use Python -O.')
    # The byte-bound parent certificate contains explicit finite constants
    # with more than Python's default 4,300 decimal digits.
    sys.set_int_max_str_digits(0)
    started = time.monotonic()
    checked = check_inputs()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    cpath = ROOT/'decision/complex_source_aligned_profile.json'
    bpath = ROOT/'bit/source_aligned_profile.json'
    lifts = ROOT/'bit/source_aligned_lifts.json'
    if not args.arithmetic_only:
        run('decision/reproduce_complex.py', out/'complex.log',
            '--source', PIN, '--work', out/'complex')
        cpath = out/'complex/complex_source_aligned_profile.json'
        run('bit/common_frame_network.py', out/'bit_network.log',
            '--source', PIN, '--source-aligned', '--compact', '--output', out/'bit_profile.json')
        bpath = out/'bit_profile.json'
        actual, expected = read(bpath), read(ROOT/'bit/source_aligned_profile.json')
        for key in ('source_aligned_rewrite', 'combined_fixed_boundary_profile', 'source_sha256'):
            assert actual[key] == expected[key], key
        run('bit/source_aligned_lifts.py', out/'bit_lifts.log',
            '--source', PIN, '--output', out/'bit_lifts.json')
        lifts = out/'bit_lifts.json'
        assert read(lifts) == read(ROOT/'bit/source_aligned_lifts.json')
        run('public/kernel_matching_prefix.py', out/'kernel_matching.log',
            '--witness', out/'complex/aligned_parity_purified_flow.result.witness.json',
            '--profile', out/'complex/aligned_parity_purified_flow.result.json',
            '--output', out/'kernel_matching_prefix.json')
        prefix = read(out/'kernel_matching_prefix.json')['summary']
        assert prefix['selected_prefix_optimal'] is True
        assert prefix['all_new_prefixes_certified_by_equal_matching_and_vertex_cover'] is True
    run('global/assemble_profiles.py', out/'global_assembly.log',
        '--complex', cpath, '--bit', bpath, '--bit-lifts', lifts,
        '--output', out/'global_certificate.json')
    global_result = read(out/'global_certificate.json')
    expected = read(ROOT/'global/global_certificate.json')
    for key in ('kappa', 'kappa_decimal', 'reviewed_baseline', 'fixed_doubling_target'):
        assert global_result[key] == expected[key], key
    for branch in ('complex', 'bit'):
        assert global_result[branch]['saving'] == expected[branch]['saving']
        assert global_result[branch]['strict_gap_lower'] == expected[branch]['strict_gap_lower']
    assert len(global_result['assembly']['strict_constraints']) == 47
    result = dict(
        status='PASS arithmetic only' if args.arithmetic_only else 'PASS exact construction regeneration and global assembly',
        author='GPT-6 Astra', source_commit='fd25adb7fbaa12ee761d02c733c54d1d2a7687ee',
        kappa=global_result['kappa'], kappa_decimal=global_result['kappa_decimal'],
        ratio_to_reviewed_baseline=global_result['ratio_to_reviewed_baseline_decimal'],
        doubling_achieved=global_result['doubling_achieved'],
        strict_global_constraints=47, literal_global_program_exported=False,
        python_version=platform.python_version(), input_checks=checked,
        elapsed_seconds=time.monotonic()-started)
    (out/'reproduction_summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
