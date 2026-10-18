#!/usr/bin/env python3
"""Reproduce all exact receipts and independent corruption controls offline."""
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from accelerator import accelerated_screen, load_original, receipt


def same_json(left, right):
    # Preserve JSON types: Python considers True == 1 and 1 == 1.0.
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def evidence():
    original = load_original()
    complete = receipt(original, 'reference')
    if not same_json(complete, receipt(original, 'accelerated')):
        raise ValueError('Complete certificate differs')
    expected = json.loads((PACKAGE.parents[1]/'certificates/sparse-fusion-audit.json').read_text())
    if not same_json(complete, expected):
        raise ValueError('Original certificate no longer matches committed certificate')
    screens = {}
    for h in (22, 25, 28):
        reference = original.central_gate_screen(h)
        accelerated = accelerated_screen(original, h)
        if not same_json(original.serializable(reference), original.serializable(accelerated)):
            raise ValueError(f'Complete central screen differs at h={h}')
        screens[str(h)] = {'receipt': original.serializable(reference),
                          'original_unary_rank_calls': 64*comb(h, 3),
                          'accelerated_unary_rank_calls': 64*8,
                          'frames': 64, 'joint_pairs': 4096}
    return {'status': 'PASS_SPARSE_FUSION_ORBITS', 'seed': 91,
            'base_commit': 'f567884aeb8851b6e794af1184119a3bfbe1e631',
            'source_manifest_sha256': sha256((PACKAGE/'SOURCES.json').read_bytes()).hexdigest(),
            'complete_certificate': complete, 'screens': screens, 'kappa': 'unchanged'}


def main():
    actual = evidence()
    expected = json.loads((PACKAGE/'EXPECTED.json').read_text())
    if not same_json(actual, expected):
        raise ValueError('Frozen evidence receipt differs')
    suite = unittest.defaultTestLoader.discover(str(PACKAGE), pattern='test_orbits.py')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun == 0:
        raise SystemExit(1)
    print(f"PASS_SPARSE_FUSION_ORBITS frames=64 joint_pairs=4096 h=22,25,28 tests={result.testsRun} kappa=unchanged")


if __name__ == '__main__':
    main()
