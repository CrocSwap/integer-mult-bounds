#!/usr/bin/env python3
"""Relocated source/receipt boundary tests; no Git or network required."""
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class ExportChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='p104-dual-precision-')
        cls.root = Path(cls.temporary.name)
        cls.package = cls.root / 'research/p104-dual-precision'
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns('__pycache__'))
        for pin in json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if pin['usage'] == 'input':
                destination = cls.root / pin['path']
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / pin['path'], destination)

    @classmethod
    def tearDownClass(cls):
        for path in cls.root.rglob('*'):
            if path.is_file():
                path.chmod(stat.S_IREAD | stat.S_IWRITE)
        cls.temporary.cleanup()

    def run_export(self):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package / 'verify.py')],
                              cwd=self.root, capture_output=True, text=True, encoding='utf-8', timeout=240)

    def hashes(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def test_01_read_only_git_free_export(self):
        before = self.hashes()
        files = [p for p in self.root.rglob('*') if p.is_file()]
        for path in files:
            path.chmod(stat.S_IREAD)
        try:
            result = self.run_export()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('PASS_P104_DUAL_PRECISION', result.stdout)
            self.assertEqual(before, self.hashes())
        finally:
            for path in files:
                path.chmod(stat.S_IREAD | stat.S_IWRITE)

    def source_mutation(self, path, diagnostic):
        original = path.read_bytes()
        path.write_bytes(original + b"\nraise RuntimeError('UNAUTHENTICATED_EXECUTION')\n")
        try:
            result = self.run_export()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ValueError: source SHA256: ' + diagnostic, result.stderr)
            self.assertNotIn('RuntimeError: UNAUTHENTICATED_EXECUTION', result.stderr)
        finally:
            path.write_bytes(original)

    def test_02_retained_executable_before_import(self):
        name = 'source/pr2479/verify.py'
        self.source_mutation(self.package / name, name)

    def test_03_live_executable_before_import(self):
        name = 'research/p104-native-channel/vendor/native_verify.py'
        self.source_mutation(self.root / name, name)

    def test_04_full_signed_receipt_not_just_constants(self):
        path = self.package / 'RESULT.json'
        original = path.read_bytes()
        receipt = json.loads(original)
        row = receipt['peaks']['absolute']['response']
        first = next(iter(row))
        row[first] = '987654321'
        path.write_text(json.dumps(receipt), encoding='utf-8')
        try:
            result = self.run_export()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ValueError: complete precision receipt mismatch', result.stderr)
        finally:
            path.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
