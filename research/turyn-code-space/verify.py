#!/usr/bin/env python3
"""Reproduce exact code-space receipts and reject malformed fitting candidates."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
from model import build, require, candidate_labels, validate_labels
import quadratic


def check_manifest():
    manifest = ROOT / 'MANIFEST.json'
    require(manifest.is_file(), 'Package manifest is missing')
    for name, digest in json.loads(manifest.read_text()).items():
        path = ROOT / name
        require(path.resolve().is_relative_to(ROOT), 'Manifest path outside package')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, f'Package hash: {name}')


def run(args, output):
    check_manifest()
    state, receipt, affine = build(output)
    require(receipt == json.loads((ROOT / 'evidence/MODEL.json').read_text()), 'Regenerated model receipt')
    require(affine == json.loads((ROOT / 'evidence/AFFINE.json').read_text()), 'Regenerated affine certificate')
    result = dict(status='PASS_TURYN_CODE_SPACE', model=receipt['status'],
                  fitting_negative_controls=receipt['negative_controls'])
    if not args.geometry_only:
        result['quadratic'] = quadratic.run(state, output / 'quadratic', args.compiler)
        require(result['quadratic'] == json.loads((ROOT / 'evidence/QUADRATIC.json').read_text()),
                'Regenerated quadratic receipt')
    else:
        result['quadratic'] = 'NOT_REPLAYED_GEOMETRY_ONLY'
    if args.candidate is not None:
        candidate = json.loads(args.candidate.read_text())
        labels = candidate_labels(candidate, state['q'], state['p'])
        result['candidate'] = validate_labels(labels, state['adjacency'], args.maximum_dimension)
    (output / 'VERIFICATION.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Keep regenerated arrays, solution bases, and receipts here')
    parser.add_argument('--geometry-only', action='store_true', help='Skip the C++ quadratic-family replay')
    parser.add_argument('--compiler', help='C++ compiler executable; default c++, clang++, or g++')
    parser.add_argument('--candidate', type=Path, help='JSON explicit_quotient_labels or quadratic_radical candidate')
    parser.add_argument('--maximum-dimension', type=int, default=25)
    args = parser.parse_args()
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        run(args, args.output)
    else:
        with tempfile.TemporaryDirectory(prefix='turyn-code-space-') as temporary:
            run(args, Path(temporary))


if __name__ == '__main__':
    main()
