#!/usr/bin/env python3
"""Verify completed width-120 banks on PR234's five-stage cover with PR210's newest 493-source helper.

Usage (repository root, assertions enabled, sympy==1.14.0):
    python3 -B research/five-stage-banks-493/verify.py --pr210-root <PR210 @ 1331149> --pr234-root <PR234 @ af3fe33> [--full] [--write]

Always: assemble PR210's package with PR234's pinned PR200 base inputs, prepare the 493-source helper with PR210's
own code, run its F2 / majorant / both defining-integer replays and 17 controls, the physical telescope, an
independent literal projection and inverse, PR234's five-stage global lowering and exact geometry (constants
rebound), all used-basis determinants, the finite bill, 231 charts, 176,915 width-120 banks with a proper
60-colouring, paid moments, three leaf levels and PR234's outer-47 assembly.
--full additionally runs PR234's own fresh verifier (for its complex supplier) and requires its mathematics to
match its pinned expected values. Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tempfile, time
if sys.flags.optimize: raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import helper493, packing5, arithmetic5

V8 = 'research/five-stage-source-bound-v8'


def serial(x):
    if isinstance(x, Q): return str(x)
    if isinstance(x, dict): return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)): return [serial(v) for v in x]
    return x


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr210-root', type=Path, required=True)
    ap.add_argument('--pr234-root', type=Path, required=True)
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args(); assert not a.write or a.full
    t0 = time.monotonic(); say = lambda s: print(f'{time.monotonic()-t0:7.1f}s  {s}', flush=True)
    src = json.loads((HERE / 'SOURCE.json').read_text())
    for key, root in (('pr210', a.pr210_root), ('pr234', a.pr234_root)):
        head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        assert head == src[key]['commit'], ('wrong checkout', key)
        for name, digest in src[key]['files'].items():
            assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, ('changed input', key, name)
    say('source pins passed')
    expected = json.loads((a.pr234_root / V8 / 'expected-math.json').read_text())['mathematics']
    if a.full:
        with tempfile.TemporaryDirectory(prefix='pr234-fresh-') as tmp:
            subprocess.run([sys.executable, '-B', 'verify.py', '--output', str(Path(tmp) / 'run')], cwd=a.pr234_root / V8, check=True)
            fresh = json.loads((Path(tmp) / 'run/certificate.json').read_text())
        for key in ('complex_profile', 'complex_moment_interval', 'assembly'):
            assert fresh[key] == expected[key], ('PR234 fresh mathematics differ', key)
        say('PR234 fresh verifier passed')
    raw, checks = helper493.build(a.pr210_root, a.pr234_root, say)
    R = raw['physical_R']
    physical = packing5.build(a.pr234_root, R); say('charts, banks and colouring passed')
    math234 = dict(expected); math234['bit_profile'] = raw['five_stage_profile']
    result = arithmetic5.build(a.pr234_root, math234, physical); say('moments, bootstrap and outer-47 assembly passed')
    record = serial(dict(pr210_commit=src['pr210']['commit'], pr234_commit=src['pr234']['commit'], pr234_fresh_run=a.full,
                         helper=raw, checks=checks, physical=physical, arithmetic=result))
    path = HERE / 'certificate.json'
    if a.write: path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    else:
        old = json.loads(path.read_text()); old['pr234_fresh_run'] = a.full
        assert record == old, 'certificate differs'
    print('PASS 493-source helper (all columns, telescope, five-stage lowering, geometry, primes, finite bill), banks, 47 constraints')
    print('conditional kappa = ' + record['arithmetic']['kappa'])


if __name__ == '__main__': main()
