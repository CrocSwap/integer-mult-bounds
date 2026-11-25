#!/usr/bin/env python3
"""Verify PR200's bit word with cascade-optimized frames and completed banks, composed with PR193's complex supplier.

Adapted from this author's PR205 verify.py (itself from PR197's, Evan McKinney, Apache-2.0).
Prepared by Rohan Arun with Anthropic Claude assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, hashlib, json, os, subprocess, sys
if sys.flags.optimize: raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frames, packing, arithmetic, audit, controls

BIT_PACKAGE = 'research/paired-cube-diagonal-bit-168'


def serial(value):
    if isinstance(value, Q): return str(value)
    if isinstance(value, dict): return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [serial(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex-root', type=Path, required=True, help='Checkout of the pinned PR193 commit')
    parser.add_argument('--bit-root', type=Path, required=True, help='Checkout of the pinned PR200 commit')
    parser.add_argument('--full', action='store_true', help='Run the complex verifier, re-admit all frames and rebuild banks')
    parser.add_argument('--write', action='store_true', help='Regenerate certificate; requires --full')
    args = parser.parse_args(); assert not args.write or args.full
    ROOT = args.complex_root.resolve(); bit = args.bit_root.resolve()
    source = json.loads((HERE / 'SOURCE.json').read_text())
    assert subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip() == source['complex_commit']
    for name, expected in source['complex_files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, ('Changed source', name)
    inherited = json.loads((ROOT / 'research/source-assisted-v4/SOURCE.json').read_text())
    for name, expected in inherited['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, ('Changed complex dependency', name)
    assert subprocess.check_output(['git', '-C', str(bit), 'rev-parse', 'HEAD'], text=True).strip() == source['bit_commit']
    manifest_path = bit / BIT_PACKAGE / 'SOURCE.json'
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == source['bit_manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    for name, expected in list(manifest['files'].items()) + list(source['bit_files'].items()):
        assert hashlib.sha256((bit / name).read_bytes()).hexdigest() == expected, ('Changed bit dependency', name)
    assert hashlib.sha256((HERE / 'opframe-bases.json').read_bytes()).hexdigest() == source['frames_sha256']
    if args.full:
        subprocess.run([sys.executable, '-B', str(ROOT / 'research/source-assisted-v4/verify.py')], cwd=ROOT, check=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        admitted = serial(frames.admit(bit))
        physical = packing.build(bit, admitted['profile'])
    else:
        old = json.loads((HERE / 'certificate.json').read_text()); admitted = old['admitted']; physical = old['physical']
    result = arithmetic.build(ROOT, bit, physical, admitted)
    independent = audit.run(result, result['unpacked_profile'])
    record = dict(admitted=admitted, physical=physical, arithmetic=result, independent=independent,
                  bank_controls=controls.run(), pinned_bit_files=len(manifest['files']))
    out = serial(record)
    if args.write: (HERE / 'certificate.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else: assert out == json.loads((HERE / 'certificate.json').read_text()), 'Certificate differs'
    print('PASS PR200 frame/terminal/prime re-admission, exact charts and banks, two moment engines, finite leaf composition, 47 constraints')
    print('conditional kappa = ' + out['arithmetic']['after_packing']['kappa'])


if __name__ == '__main__': main()
