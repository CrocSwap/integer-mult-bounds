#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks of the published CLI and meaningful failure controls."""

import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRIMARY = runpy.run_path(str(PACKAGE / 'verify.py'))


def run(package, script='verify.py', optimized=True):
    argv = [sys.executable, '-I', '-Werror', '-B']
    if optimized:
        argv.append('-O')
    return subprocess.run(argv + [str(package / script)], check=False,
                          capture_output=True, text=True, timeout=30, cwd=package.parent)


def export(destination):
    target = destination / 'research' / PACKAGE.name
    target.mkdir(parents=True)
    files = [p for p in PACKAGE.iterdir() if p.is_file()]
    if len(files) > 12:
        raise ValueError('bounded package export')
    for path in files:
        shutil.copyfile(path, target / path.name)
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            path = destination / row['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['path'], path)
    return target


class EndpointSupportTests(unittest.TestCase):
    def test_published_receipt_and_independent_cli(self):
        for optimized in (False, True):
            completed = run(PACKAGE, optimized=optimized)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload, marker = completed.stdout.rsplit('\nPASS_', 1)
            result = json.loads(payload)
            self.assertEqual(marker.strip(),
                             'P104_ENDPOINT_SUPPORT required=4656 capacity=30 rejected=406 control=400')
            self.assertEqual([r['support_total'] for r in result['profiles']], [2459, 2465, 4663])
            self.assertEqual([r['support_rows_pass'] for r in result['profiles']], [False, False, True])
            self.assertEqual(result['profiles'][2]['moment_upper'], '0.999729278053145')
        independent = run(PACKAGE, 'independent.py')
        self.assertEqual(independent.returncode, 0, independent.stderr)
        self.assertEqual(independent.stdout.strip(),
                         'PASS_INDEPENDENT_ENDPOINT_SUPPORT orientations=2 endpoints=208 required=4656 cap=30')

    def test_history_boundary_and_asymmetric_cases(self):
        weights = PRIMARY['history_weights']
        for jumps, expected in [([1, 7, 1], (1, 1)), ([1] * 9, (30, 30)),
                                ([1, 1, 6, 1], (2, 30)), ([1, 6, 1, 1], (30, 2)),
                                ([8, 1], (0, 0)), ([1, 8], (0, 0)),
                                ([1, 1, 7], (0, 30)), ([7, 1, 1], (30, 0))]:
            self.assertEqual(weights(jumps), expected)
        for invalid in ([], [0, 9], [1, 7], [1.0, 7, 1], [True, 7, 1]):
            with self.assertRaisesRegex(ValueError, 'positive composition'):
                weights(invalid)

    def test_git_free_read_only_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = export(Path(temporary))
            files = [p for p in Path(temporary).rglob('*') if p.is_file()]
            before = {str(p): p.read_bytes() for p in files}
            for path in files:
                path.chmod(0o444)
            try:
                for script in ('verify.py', 'independent.py'):
                    completed = run(package, script)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual({str(p): p.read_bytes() for p in files}, before)
                self.assertFalse(any(p.name == '__pycache__' for p in Path(temporary).rglob('*')))
            finally:
                for path in files:
                    path.chmod(0o644)

    def test_sources_and_typed_receipt_reject(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = export(Path(temporary))
            engine = Path(temporary) / 'research/complex-local-word-ceiling/ceiling.py'
            original = engine.read_bytes()
            engine.write_bytes(b'raise RuntimeError("SHOULD_NOT_EXECUTE")\n')
            failed = run(package)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source hash', failed.stderr)
            self.assertNotIn('SHOULD_NOT_EXECUTE', failed.stderr)
            engine.write_bytes(original)
            receipt = package / 'RESULT.json'
            result = json.loads(receipt.read_bytes())
            result['profiles'][0]['support_rows_pass'] = 0
            receipt.write_text(json.dumps(result))
            failed = run(package)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('typed receipt equality', failed.stderr)

    def test_affine_only_and_phantom_arrival_mutants_reject(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = export(Path(temporary))
            path = package / 'verify.py'
            original = path.read_text()
            for before, after in [('min(1 << (dimension - 1), 30)', '1 << (dimension - 1)'),
                                  ('if after == 8:', 'if after == 9:')]:
                self.assertEqual(original.count(before), 1)
                path.write_text(original.replace(before, after))
                completed = run(package)
                self.assertNotEqual(completed.returncode, 0)
                self.assertNotIn('PASS_P104_ENDPOINT_SUPPORT', completed.stdout)
            path.write_text(original)
            completed = run(package)
            self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == '__main__':
    unittest.main()
