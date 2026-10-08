#!/usr/bin/env python3
"""Portable finite verifier; historical compatibility is deliberately weaker evidence."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RR = ROOT / 'experiments/round7-review'


def main():
    if not __debug__:
        raise RuntimeError('Checks require assertions: optimized Python is unsupported')
    ap = argparse.ArgumentParser()
    ap.add_argument('--full', action='store_true')
    args = ap.parse_args()
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    for name, digest in manifest['sha256'].items():
        actual = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if actual != digest:
            raise RuntimeError('Changed package input or checker: ' + name)
    provenance = json.loads((ROOT/'PROVENANCE.json').read_text())
    for name, expected in provenance['binary_git_blobs'].items():
        raw = (RR/'vendor/certificates/round7'/name).read_bytes()
        git_id = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if git_id != expected:
            raise RuntimeError('Pinned upstream Git blob mismatch: '+name)
    print('Immutable package and upstream Git blob hashes: PASS', flush=True)
    subprocess.run([sys.executable, str(ROOT/'experiments/saturation-review/review.py')], check=True)
    spec = importlib.util.spec_from_file_location('portable_arithmetic', RR/'check_arithmetic.py')
    ar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ar)
    candidate = json.loads((RR/'saturation-results.json').read_text())['Z']['histogram']
    lo, hi = ar.exact_moment(candidate, Fraction(3999182181,62500000000000))
    if hi >= 1:
        raise RuntimeError('Moment fails the strict saving certificate')
    compatibility = json.loads((ROOT/'historical/saturated-balanced-compatibility.json').read_text())
    # A sanity check of saved values, NOT regeneration of Chen's assembly.
    if not all(Fraction(v)>0 for v in compatibility['assembly']['strict_constraints'].values()):
        raise RuntimeError('Saved PR97-compatible slack is nonpositive')
    if not all(Fraction(v)>Fraction(compatibility['kappa']) for v in compatibility['assembly']['margins'].values()):
        raise RuntimeError('Saved PR97-compatible margin is too small')
    out = ROOT/'verification'
    out.mkdir(exist_ok=True)
    review_path = ROOT/'experiments/saturation-review/results.json'
    review = json.loads(review_path.read_text())
    review['source_hashes'] = {str(Path(p).relative_to(ROOT)) if Path(p).is_absolute() else p:v for p,v in review['source_hashes'].items()}
    (out/'exact-frame-review.json').write_text(json.dumps(review,indent=2)+'\n')
    review_path.unlink()
    result = dict(status='PASS',package_manifest_verified=True,exact_changed_frame_review=True,
                  moment_lower_float=float(lo),moment_upper_float=float(hi),moment_gap_lower_float=float(1-hi),
                  moment_comparison_used_exact_rationals=True,
                  historical_compatibility_slacks_positive=True,
                  pr97_assembly_regenerated=False,full_finite_checks_executed=args.full,
                  full_theorem_proved=False)
    if args.full:
        subprocess.run([sys.executable,str(RR/'check_candidate_frames.py'),str(RR/'saturated-Z.json.gz')],check=True)
        subprocess.run([sys.executable,str(RR/'scalar_engine.py'),'--data',str(RR/'saturated-Z.json.gz'),'--output',str(out/'scalar-results.json')],check=True)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Exact frame delta, moment and historical slack sanity checks: PASS',flush=True)
    print('Full theorem / global optimality: NOT CLAIMED',flush=True)


if __name__ == '__main__':
    main()
