#!/usr/bin/env python3
"""Public-CLI integrity and mathematical failure controls in isolated exports."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


class Controls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='coxeter-control-')
        self.root = Path(self.tmp.name)
        self.pkg = self.root/'research'/PACKAGE.name
        shutil.copytree(PACKAGE, self.pkg, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((PACKAGE/'SOURCES.json').read_text())
        for item in sources['files']:
            if item['usage'] == 'input':
                path = self.root/item['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/item['path'], path)

    def tearDown(self):
        for path in self.root.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        self.tmp.cleanup()

    def run_verifier(self, succeeds, expected='', script='verify.py'):
        run = subprocess.run([sys.executable, '-I', '-O', '-B', str(self.pkg/script)],
                             cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode == 0, succeeds, run.stdout+run.stderr)
        self.assertIn(expected, run.stdout+run.stderr)

    def snapshot(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_readonly_git_free_export(self):
        before = self.snapshot()
        for p in self.root.rglob('*'):
            p.chmod(0o555 if p.is_dir() else 0o444)
        self.run_verifier(True, 'PASS_COXETER_ROOT_TARIFF')
        self.run_verifier(True, 'PASS_INDEPENDENT_COXETER_ROOT_TARIFF', 'independent.py')
        self.assertEqual(before, self.snapshot())

    def test_dropped_source_pin(self):
        path = self.pkg/'SOURCES.json'
        data = json.loads(path.read_text())
        data['files'] = [x for x in data['files'] if x['path'] !=
                         'research/symmetric-adjacent-cut-bound/PROOF.md']
        path.write_text(json.dumps(data))
        self.run_verifier(False, 'source inventory mismatch')

    def test_changed_source_bytes(self):
        path = self.root/'research/symmetric-adjacent-cut-bound/PROOF.md'
        path.write_bytes(path.read_bytes()+b'\ncorrupted source\n')
        self.run_verifier(False, 'source drift')

    def test_typed_receipt(self):
        path = self.pkg/'RESULT.json'
        original = path.read_text()
        for replacement in ('boolean', 'float', 'wrong count'):
            with self.subTest(replacement=replacement):
                data = json.loads(original)
                if replacement == 'boolean':
                    data['no_new_kappa'] = 1
                elif replacement == 'float':
                    data['finite_systems']['A2']['order'] = 6.0
                else:
                    data['finite_systems']['A2']['order'] = 7
                path.write_text(json.dumps(data))
                self.run_verifier(False, 'receipt mismatch')

    def test_duplicate_receipt_field(self):
        path = self.pkg/'RESULT.json'
        path.write_text(path.read_text().replace('{', '{"no_new_kappa":true,', 1))
        self.run_verifier(False, 'duplicate JSON key')

    def test_rank_undercharging_mutation(self):
        path = self.pkg/'verify.py'
        source = path.read_text()
        self.assertEqual(source.count('return len(basis)'), 1)
        path.write_text(source.replace('return len(basis)', 'return min(1, len(basis))'))
        self.run_verifier(False, 'rank-two undercharging control')


if __name__ == '__main__':
    unittest.main(verbosity=2)
