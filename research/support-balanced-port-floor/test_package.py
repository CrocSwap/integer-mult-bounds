#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""End-to-end integrity controls for the scoped verifier."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root/'research/support-balanced-port-floor'
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__'))
        pins = json.loads((HERE/'SOURCES.json').read_text())['files']
        self.inputs = [p['path'] for p in pins if p['usage'] == 'input']
        for path in self.inputs:
            target = self.root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/path, target)

    def run_verify(self, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package/'verify.py'), *args],
                              cwd=self.temp.name, capture_output=True, text=True, timeout=30)

    def test_git_free_readonly_export(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = self.run_verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_source_corruption_rejected_before_parse(self):
        path = self.root/'research/kport-group-scalar-endpoint-audit/fixtures/PR2041-CANDIDATE.json'
        path.write_text('{invalid json')
        result = self.run_verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source SHA256:', result.stderr)
        self.assertNotIn('JSONDecodeError', result.stderr)

    def test_typed_receipt_corruption(self):
        path = self.package/'RESULT.json'
        data = json.loads(path.read_text())
        data['no_new_kappa'] = 1
        path.write_text(json.dumps(data))
        result = self.run_verify()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('complete typed result mismatch', result.stderr)

    def test_overwrite_refusal_preserves_bytes(self):
        target = self.root/'existing.json'
        target.write_text('keep these bytes')
        result = self.run_verify('--write', str(target))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FileExistsError', result.stderr)
        self.assertEqual(target.read_text(), 'keep these bytes')


if __name__ == '__main__':
    unittest.main()
