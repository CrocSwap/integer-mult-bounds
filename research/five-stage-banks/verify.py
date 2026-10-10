#!/usr/bin/env python3
"""Verify completed width-120 entrance banks on PR234's five-stage bit supplier.

Usage (repository root, assertions enabled):
    python3 -B research/five-stage-banks/verify.py --pr234-root <checkout of PR234 @ af3fe33> [--full] [--write]

--full first runs PR234's own fresh verifier (all six mandatory stages) into a new temporary directory and
uses its freshly computed mathematics; without it, PR234's pinned expected-math.json is used.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tempfile
if sys.flags.optimize: raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import packing5, arithmetic5

PKG = 'research/five-stage-source-bound-v8'


def serial(x):
    if isinstance(x, Q): return str(x)
    if isinstance(x, dict): return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [serial(v) for v in x]
    return x


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr234-root', type=Path, required=True)
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args(); assert not a.write or a.full
    P = a.pr234_root.resolve(); source = json.loads((HERE / 'SOURCE.json').read_text())
    head = subprocess.check_output(['git', '-C', str(P), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == source['pr234_commit'], 'wrong PR234 checkout'
    for name, digest in source['pr234_files'].items():
        assert hashlib.sha256((P / name).read_bytes()).hexdigest() == digest, ('changed PR234 input', name)
    expected = json.loads((P / PKG / 'expected-math.json').read_text())['mathematics']
    if a.full:
        with tempfile.TemporaryDirectory(prefix='pr234-fresh-') as tmp:
            out = Path(tmp) / 'run'
            subprocess.run([sys.executable, '-B', 'verify.py', '--output', str(out)], cwd=P / PKG, check=True)
            fresh = json.loads((out / 'certificate.json').read_text())
        for key in ('bit_profile', 'complex_profile', 'kappa', 'assembly'):
            assert fresh[key] == expected[key], ('PR234 fresh mathematics differ', key)
        pr234 = fresh
    else:
        pr234 = expected
    R = pr234['bit_profile']['W'] - 4 * 1760
    physical = packing5.build(P, R)
    result = arithmetic5.build(P, pr234, physical)
    record = serial(dict(pr234_commit=head, pr234_fresh_run=a.full, physical=physical, arithmetic=result))
    path = HERE / 'certificate.json'
    if a.write: path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    else:
        old = json.loads(path.read_text()); old['pr234_fresh_run'] = a.full
        assert record == old, 'certificate differs'
    print('PASS 231 exact charts, 177179 width-120 banks with a proper 60-colouring, paid moments, 3 leaf levels, 47 constraints')
    print('conditional kappa = ' + record['arithmetic']['kappa'])


if __name__ == '__main__': main()
