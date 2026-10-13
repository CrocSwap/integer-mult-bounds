#!/usr/bin/env python3
"""Regenerate exact research receipts and reject targeted corruptions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))

import numpy as np
from binary_labels import inverse
from leech_geometry import require, verify
from verify_norm6_basis import integer_full_rank


def negative_controls(output):
    vectors = np.load(output / 'minimal_vectors.npy')
    words = np.load(output / 'golay_words.npy')
    rejected = []
    for name in ('norm', 'duplicate', 'octad_sign_parity'):
        altered = vectors.copy()
        if name == 'norm':
            altered[0, 0] += 1
        elif name == 'duplicate':
            altered[1] = altered[0]
        else:
            index = 1104
            coordinate = int(np.flatnonzero(altered[index])[0])
            altered[index, coordinate] *= -1
        try:
            verify(altered, words, 1)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError(f'Corruption accepted: {name}')
    for name, action in [
            ('singular_binary_basis', lambda: inverse(np.zeros((2, 2), dtype=np.uint8))),
            ('dependent_cubic_basis', lambda: integer_full_rank(
                np.array([[1, 2], [1, 2]], dtype=np.int64), block_size=2))]:
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError(f'Corruption accepted: {name}')
    return rejected


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    manifest = ROOT / 'MANIFEST.json'
    if manifest.exists():
        for name, digest in json.loads(manifest.read_text()).items():
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                    f'Artifact hash differs: {name}')
    stages = [
        ('leech_geometry.py', ['--output', str(output)]),
        ('binary_labels.py', ['--output', str(output)]),
        ('center_supports.py', ['--output', str(output)]),
        ('dyadic_factor.py', ['--output', str(output)]),
        ('norm6_centers.py', ['--output', str(output), '--rank']),
        ('verify_norm6_basis.py', ['--output', str(output)]),
        ('turyn_checks.py', ['--outputdir', str(output)]),
        ('screen.py', ['--out', str(output / 'SCREEN.json')]),
    ]
    optimize = ['-O'] if not __debug__ else []
    for script, arguments in stages:
        result = subprocess.run([sys.executable, *optimize, str(ROOT / 'code' / script),
                                 *arguments], capture_output=True, text=True)
        (output / f'{script}.log').write_text(result.stdout + result.stderr)
        require(result.returncode == 0, f'{script} failed; see {output / (script + ".log")}')
        print(f'PASS {script}', flush=True)
    evidence = sorted((ROOT / 'evidence').glob('*.json'))
    require(len(evidence) >= 12, 'Incomplete evidence package')
    for expected in evidence:
        actual = output / expected.name
        require(actual.exists(), f'Missing regenerated receipt: {expected.name}')
        require(json.loads(actual.read_text()) == json.loads(expected.read_text()),
                f'Regenerated receipt differs: {expected.name}')
    rejected = negative_controls(output)
    result = {'status': 'PASS_EXACT_LEECH_AND_TURYN_RESEARCH',
              'deterministic_receipts_checked': len(evidence),
              'turyn_ordered_pairs_checked': 23040**2,
              'negative_controls_rejected': rejected,
              'new_kappa_claimed': False,
              'scope': 'Exact geometry, factors, frame fits, equivalence, and scoped '
                       'moment experiments. No new complete supplier or outer certificate.'}
    expected = ROOT / 'VERIFICATION.json'
    if expected.exists():
        require(json.loads(expected.read_text()) == result, 'Verification receipt differs')
    (output / 'VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output:
        run(args.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='leech-turyn-') as directory:
            run(Path(directory))


if __name__ == '__main__':
    main()
