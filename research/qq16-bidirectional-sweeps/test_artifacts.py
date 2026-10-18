#!/usr/bin/env python3
"""CLI integrity and portability controls. Apache-2.0."""
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Artifacts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.package = self.root / 'export'
        self.package.mkdir()
        for source in HERE.iterdir():
            if source.is_file():
                shutil.copyfile(source, self.package / source.name)

    def tearDown(self):
        self.package.chmod(0o755)
        for path in self.package.iterdir():
            path.chmod(0o644)
        self.temporary.cleanup()

    def replay(self, success, diagnostic=''):
        result = subprocess.run(
            [sys.executable, '-I', '-B', '-O', '-Werror', str(self.package / 'verify.py')],
            cwd=self.root, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_git_free_read_only_export(self):
        before = {p.name: p.read_bytes() for p in self.package.iterdir()}
        for path in self.package.iterdir():
            path.chmod(0o444)
        self.package.chmod(0o555)
        self.replay(True, 'PASS_QQ16_BIDIRECTIONAL_SWEEPS')
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.package.iterdir()})

    def test_source_byte_corruption(self):
        path = self.package / 'source-word.json.gz'
        raw = gzip.decompress(path.read_bytes())
        changed = raw[:-1] + (b' ' if raw[-1:] != b' ' else b'\n')
        path.write_bytes(gzip.compress(changed, mtime=0))
        self.replay(False, 'source SHA256')

    def test_typed_result_corruption(self):
        path = self.package / 'RESULT.json'
        result = json.loads(path.read_text())
        result['scalar_invoice']['unit_adds'] = True
        path.write_text(json.dumps(result))
        self.replay(False, 'typed RESULT.json receipt')

    def test_direction_receipt_corruption(self):
        path = self.package / 'SCHEDULE.json'
        result = json.loads(path.read_text())
        result['L2'] = ('1' if result['L2'][0] == '0' else '0') + result['L2'][1:]
        path.write_text(json.dumps(result))
        self.replay(False, 'typed SCHEDULE.json receipt')

    def test_equivalent_recompression(self):
        path = self.package / 'source-word.json.gz'
        path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=42))
        self.replay(True, 'PASS_QQ16_BIDIRECTIONAL_SWEEPS')


if __name__ == '__main__':
    unittest.main()
