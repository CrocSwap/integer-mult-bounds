#!/usr/bin/env python3
"""Behavioral rejection controls for the scoped cut-method certificate."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Behavior(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='s4-cut-envelope-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / 'research' / HERE.name
        shutil.copytree(HERE, self.package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        for row in sources['files']:
            if row['usage'] == 'input':
                target = self.root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], target)

    def call(self, script='verify.py', optimized=False):
        return subprocess.run([sys.executable, '-I', *(['-O'] if optimized else []),
                               '-B', str(self.package / script)],
                              capture_output=True, text=True, timeout=30, cwd=self.root)

    def test_git_free_read_only_normal_and_optimized(self):
        def inventory():
            return {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.root.rglob('*') if p.is_file()}
        before = inventory()
        for optimized in (False, True):
            for script in ('verify.py', 'independent.py'):
                result = self.call(script, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS_', result.stdout)
        self.assertEqual(before, inventory())

    def test_corrupted_receipt(self):
        path = self.package / 'RESULT.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        data['sharp_cut_alpha_gamma'] = [12, 9]
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('receipt mismatch', result.stderr)
        result = self.call('independent.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invoice control', result.stderr)

    def test_changed_external_source(self):
        path = self.root / 'research/symmetric-adjacent-cut-bound/PROOF.md'
        path.write_bytes(path.read_bytes() + b'\nchanged\n')
        result = self.call()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('changed external source', result.stderr)

    def test_changed_public_predecessor(self):
        path = self.package / 'predecessor/PROOF.md'
        path.write_bytes(path.read_bytes() + b'\nchanged\n')
        result = self.call(optimized=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('changed public predecessor', result.stderr)

    def test_actual_implementation_mutants(self):
        path = self.package / 'verify.py'
        original = path.read_text(encoding='utf-8')
        mutants = [
            ('cost = outer[g] + (i != 1)', 'cost = outer[g] + 1'),
            ('cut_values[g] = (inv, outer)', 'cut_values[g] = (inv, outer + 1)'),
            ('if v >> i & 1:', 'if u >> i & 1:'),
            ('signed * (1 - signed) <= 0', 'signed * (1 + signed) <= 0'),
        ]
        for old, new in mutants:
            with self.subTest(mutation=old):
                self.assertEqual(original.count(old), 1)
                path.write_text(original.replace(old, new), encoding='utf-8')
                result = self.call(optimized=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ValueError', result.stderr)
                self.assertNotIn('receipt mismatch', result.stderr)
        path.write_text(original, encoding='utf-8')

    def test_independent_orientation_control(self):
        path = self.package / 'independent.py'
        original = path.read_text(encoding='utf-8')
        old = 'inverse_points = [tuple(p.index(i) + 1 for i in range(1, 5)) for p in points]'
        self.assertEqual(original.count(old), 1)
        path.write_text(original.replace(old, 'inverse_points = points'), encoding='utf-8')
        result = self.call('independent.py')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('five-point matrix disagreement', result.stderr)


if __name__ == '__main__':
    unittest.main()
