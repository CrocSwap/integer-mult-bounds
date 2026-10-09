#!/usr/bin/env python3
"""Verify the served diagonal bit supplier, packed with PR205's banks, against PR193's complex supplier.

PR205's verify.py (Rohan Arun; adapted from PR197's, Evan McKinney, Apache-2.0) with two added steps:
patch.py re-derives the served word from PR200's frozen word, and bit/served_prove.py checks the served word
completely (F2 identity, integer decoder, exact frames, chains, terminal sinks and paid moment).
"""
from pathlib import Path
import argparse, gzip, hashlib, json, os, subprocess, sys, tempfile
if sys.flags.optimize: raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import packing, arithmetic, audit, controls
from fractions import Fraction as Q

BIT_PACKAGE = 'research/paired-cube-diagonal-bit-168'
SERVED = HERE / 'selected/served'
SERVED_FILES = ('word_p12.json.gz', 'kchron_p12.json', 'profile_p12.json')


def serial(value):
    if isinstance(value, Q): return str(value)
    if isinstance(value, dict): return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [serial(v) for v in value]
    return value


def run(root, script, *args):
    subprocess.run([sys.executable, '-B', str(root / script), *args], cwd=root, check=True,
                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))


def capture(script, *args):
    """Run one of this package's scripts and parse the JSON record on its last stdout line."""
    out = subprocess.run([sys.executable, '-B', str(script), *args], check=True, capture_output=True, text=True,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')).stdout
    return json.loads(out.strip().splitlines()[-1])


def rederive(bit):
    """patch.py must reproduce the frozen served word, schedule and profile from PR200's frozen word.

    The gzip container is compared after decompression: its deflate bytes depend on the zlib build."""
    with tempfile.TemporaryDirectory() as tmp:
        stats = capture(HERE / 'patch.py', str(bit / BIT_PACKAGE), tmp)
        for name in SERVED_FILES:
            new, old = (Path(tmp) / name).read_bytes(), (SERVED / name).read_bytes()
            if name.endswith('.gz'): new, old = gzip.decompress(new), gzip.decompress(old)
            assert new == old, ('patch.py does not reproduce the frozen file', name)
    assert stats == dict(served=373, deleted_roles=373, deleted_ops=373), stats
    return dict(stats, reproduced=list(SERVED_FILES))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex-root', type=Path, required=True, help='Checkout of the pinned PR193 commit')
    parser.add_argument('--bit-root', type=Path, required=True, help='Checkout of the pinned PR200 commit')
    parser.add_argument('--full', action='store_true',
                        help='Run both inherited verifiers, re-derive and prove the served word, then rebuild charts and banks')
    parser.add_argument('--write', action='store_true', help='Regenerate certificate; requires --full')
    args = parser.parse_args(); assert not args.write or args.full
    ROOT = args.complex_root.resolve()
    source = json.loads((HERE / 'SOURCE.json').read_text())
    head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == source['complex_commit'], 'Wrong complex checkout commit'
    for name, expected in source['complex_files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, ('Changed source', name)
    inherited = json.loads((ROOT / 'research/source-assisted-v4/SOURCE.json').read_text())
    for name, expected in inherited['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, ('Changed complex dependency', name)
    bit = args.bit_root.resolve()
    head = subprocess.check_output(['git', '-C', str(bit), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == source['bit_commit'], 'Wrong bit checkout commit'
    manifest_path = bit / BIT_PACKAGE / 'SOURCE.json'
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == source['bit_manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest['files'].items():
        assert hashlib.sha256((bit / name).read_bytes()).hexdigest() == expected, ('Changed bit dependency', name)
    for name, expected in source['bit_files'].items():
        assert hashlib.sha256((bit / name).read_bytes()).hexdigest() == expected, ('Changed bit word', name)
    for name, expected in source['served_files'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, ('Changed served file', name)
    if args.full:
        run(ROOT, 'research/source-assisted-v4/verify.py')
        run(bit, BIT_PACKAGE + '/verify.py')
        derivation = rederive(bit)
        served = capture(HERE / 'bit/served_prove.py', str(bit / BIT_PACKAGE), str(SERVED))
        physical = packing.build(bit, SERVED, served['profile'])
    else:
        frozen = json.loads((HERE / 'certificate.json').read_text())
        derivation, served, physical = frozen['derivation'], frozen['served'], frozen['physical']
    assert served['status'] == 'PASS' and served['served_operations'] == 373
    result = arithmetic.build(ROOT, bit, physical, served)
    independent = audit.run(result, result['unpacked_profile'])
    record = dict(derivation=derivation, served=served, physical=physical, arithmetic=result, independent=independent,
                  bank_controls=controls.run(), pinned_bit_files=len(manifest['files']))
    out = serial(record)
    if args.write: (HERE / 'certificate.json').write_bytes((json.dumps(out, indent=2, sort_keys=True) + '\n').encode())
    else: assert out == json.loads((HERE / 'certificate.json').read_text()), 'Certificate differs'
    print('PASS served word (re-derived and fully checked), exact charts and banks, two moment engines, '
          'finite leaf composition, 47 constraints and seven margins')
    print('conditional kappa = ' + out['arithmetic']['after_packing']['kappa'])


if __name__ == '__main__': main()
