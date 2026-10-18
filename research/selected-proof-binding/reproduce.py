#!/usr/bin/env python3
"""Reproduce the primary-proof provenance gap and its repair offline.

This is an exact metadata/fixture check, not a supplier or mathematical replay.
Mihir Srivastava, with substantial OpenAI assistance. Apache-2.0.
"""
import importlib.util
from fractions import Fraction
from hashlib import sha1
import json
from pathlib import Path
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE_BLOB = '4f0e4bded003a48b5122cbff597af4282f4d6329'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    baseline_path = PACKAGE / 'vendor/verify_selected_result.py'
    payload = baseline_path.read_bytes()
    blob = sha1(b'blob ' + str(len(payload)).encode('ascii') + b'\0' + payload).hexdigest()
    require(blob == BASE_BLOB, 'Pinned baseline Git blob changed')
    baseline = load('pinned_selected_checker', baseline_path)
    tests = load('selected_proof_regressions', ROOT / 'tests/test_selected_proof_binding.py')
    patched = tests.checker
    positive = 0
    negative = 0
    for modern in (False, True):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            record = tests.fixture(root, modern)
            for target in ('supplier/PROOF.md', 'supplement.md', 'supplier/../supplier/./PROOF.md'):
                for impl in (baseline, patched):
                    require(impl.check(dict(record, proof=target), root) == Fraction(1, 1000),
                            'Valid proof rejected')
                positive += 1
            # A byte-identical file at another unverified path is not source provenance.
            (root / 'copy.md').write_bytes((root / record['proof']).read_bytes())
            targets = ['decoy.md', 'review.md', 'validation.json', 'certificate.json', 'copy.md']
            if not modern:
                (root / 'PROOF.md').write_bytes((root / record['proof']).read_bytes())
                targets.append('PROOF.md')
            for target in targets:
                changed = dict(record, proof=target)
                require(baseline.check(changed, root) == Fraction(1, 1000),
                        'Baseline no longer demonstrates the pinned gap')
                try:
                    patched.check(changed, root)
                except ValueError as exc:
                    require(str(exc) == 'Selected primary proof is not covered by a verified digest',
                            'Mutation rejected for the wrong reason: ' + str(exc))
                else:
                    raise ValueError('Detached primary proof accepted: ' + target)
                negative += 1
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    outcome = unittest.TextTestRunner(verbosity=1).run(suite)
    require(outcome.wasSuccessful(), 'Regression tests failed')
    result = dict(base_commit='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',
                  baseline_git_blob=blob, inventory_layouts=2,
                  valid_primary_proof_cases=positive,
                  baseline_false_acceptances=negative, repaired_rejections=negative,
                  regression_tests=outcome.testsRun)
    expected = json.loads((PACKAGE / 'EXPECTED.json').read_text(encoding='utf-8'))
    require(result == expected, 'Evidence differs from EXPECTED.json')
    print(json.dumps(result, sort_keys=True, indent=2))
    print('PASS_SELECTED_PROOF_BINDING 11 reproduced gaps; 11 repaired rejections; 12 tests')


if __name__ == '__main__':
    main()
