#!/usr/bin/env python3
"""Actual CLI source/receipt/relocation controls; standard library, Apache-2.0."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'


class PackageBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='charged-pure-')
        cls.export = Path(cls.temporary.name)/'export'
        cls.package = cls.export/'research/renamed-package'
        cls.package.mkdir(parents=True)
        source = cls.export/SOURCE
        source.parent.mkdir(parents=True)
        shutil.copyfile(ROOT/SOURCE, source)
        for name in ('verify.py', 'RESULT.json'):
            shutil.copyfile(HERE/name, cls.package/name)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B',
            str(self.package/'verify.py'), *map(str, args)], cwd=self.temporary.name,
            env=dict(os.environ, PYTHONOPTIMIZE='2'), capture_output=True,
            text=True, encoding='utf-8', timeout=180)

    def hashes(self):
        return {p.relative_to(self.export).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.export.rglob('*') if p.is_file()}

    def test_01_git_free_renamed_optimized_read_only_replay(self):
        before = self.hashes()
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('dual_conflicts=169', result.stdout)
        self.assertEqual(before, self.hashes())
        self.assertFalse((self.export/'.git').exists())

    def test_02_actual_source_corruption_rejects(self):
        path = self.export/SOURCE
        raw = path.read_bytes()
        try:
            path.write_bytes(raw+b' ')
            result = self.run_cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('prototype hash mismatch', result.stderr)
        finally:
            path.write_bytes(raw)

    def test_03_full_receipt_corruption_rejects(self):
        path = self.package/'RESULT.json'
        raw = path.read_bytes()
        try:
            receipt = json.loads(raw)
            receipt['fixtures'][-1]['pure_charge'] += 1
            path.write_text(json.dumps(receipt), encoding='utf-8')
            result = self.run_cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('full receipt mismatch', result.stderr)
        finally:
            path.write_bytes(raw)

    def test_04_regeneration_and_exclusive_output(self):
        out = Path(self.temporary.name)/'regenerated.json'
        result = self.run_cli('--out', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(out.read_text()), json.loads((HERE/'RESULT.json').read_text()))
        before = out.read_bytes()
        result = self.run_cli('--out', out)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FileExistsError', result.stderr)
        self.assertEqual(before, out.read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
