#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed receipt and portable replay controls, in disposable copies only."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


@contextmanager
def isolated():
    with tempfile.TemporaryDirectory(prefix='a8-one-pair-') as temporary:
        package = Path(temporary) / 'relocated'
        package.mkdir()
        for name in ('verify.py', 'independent.py', 'CERTIFICATE.json'):
            shutil.copyfile(HERE / name, package / name)
        try:
            yield package
        finally:
            package.chmod(0o755)
            for path in package.iterdir():
                path.chmod(0o644)


def replay(package, script, optimized=False):
    flags = ['-I', '-B'] + (['-O'] if optimized else [])
    return subprocess.run([sys.executable, *flags, str(package / script)],
                          cwd=package.parent, text=True, capture_output=True, timeout=120)


def mutate_receipt(package, change):
    path = package / 'CERTIFICATE.json'
    receipt = json.loads(path.read_text())
    change(receipt)
    path.write_text(json.dumps(receipt))


def tree_hashes(package):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir()}


class PackageTests(unittest.TestCase):
    def assert_rejected(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('PASS_A8_', result.stdout)
        self.assertIn(reason, result.stderr)

    def test_missing_and_malformed_receipts(self):
        for contents, reason in [(None, 'FileNotFoundError'), ('{', 'JSONDecodeError')]:
            with self.subTest(reason=reason), isolated() as package:
                path = package / 'CERTIFICATE.json'
                if contents is None:
                    path.unlink()
                else:
                    path.write_text(contents)
                self.assert_rejected(replay(package, 'verify.py'), reason)

    def test_false_copy_cost(self):
        with isolated() as package:
            mutate_receipt(package, lambda c: c.update(sharp_copy_cost=70))
            self.assert_rejected(replay(package, 'verify.py', optimized=True),
                                 'certificate differs from exact replay')

    def test_missing_anchor(self):
        with isolated() as package:
            mutate_receipt(package, lambda c: c['anchors'].pop())
            self.assert_rejected(replay(package, 'verify.py'),
                                 'certificate differs from exact replay')

    def test_changed_frame_coverage(self):
        with isolated() as package:
            mutate_receipt(package, lambda c: c['frame_partition'].update(
                one_pair_orbit_sha256='0' * 64))
            self.assert_rejected(replay(package, 'independent.py', optimized=True),
                                 'frame census receipt: one_pair_orbit_sha256')

    def test_optimized_read_only_relocated_replay(self):
        with isolated() as package:
            before = tree_hashes(package)
            for path in package.iterdir():
                path.chmod(0o444)
            package.chmod(0o555)
            for script, marker in [('verify.py', 'PASS_A8_ONE_PAIR_FRAME_FLOOR'),
                                   ('independent.py', 'PASS_A8_ONE_PAIR_SECOND_CHECK')]:
                result = replay(package, script, optimized=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(marker, result.stdout)
            self.assertEqual(before, tree_hashes(package), 'default replay wrote to its input tree')


if __name__ == '__main__':
    unittest.main(verbosity=2)
