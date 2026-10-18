#!/usr/bin/env python3
"""Bounded package failures and read-only relocation, with optimized Python.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def replay(package):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package/"verify.py")],
                          cwd=package.parent, capture_output=True, text=True, timeout=60)


def hashes(package):
    return {p.relative_to(package).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in package.rglob("*") if p.is_file()}


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s3-output-test-")
        self.copy = Path(self.tmp.name)/"relocated"
        shutil.copytree(HERE, self.copy, ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self):
        for p in self.copy.rglob("*"):
            p.chmod(0o755 if p.is_dir() else 0o644)
        self.copy.chmod(0o755)
        self.tmp.cleanup()

    def test_read_only_relocation(self):
        before = hashes(self.copy)
        for p in self.copy.rglob("*"):
            p.chmod(0o555 if p.is_dir() else 0o444)
        self.copy.chmod(0o555)
        result = replay(self.copy)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn("PASS_S3_STANDARD_OUTPUT", result.stdout)
        self.assertEqual(hashes(self.copy), before)

    def test_changed_certificate_rejected(self):
        p = self.copy/"CERTIFICATE.json"
        data = json.loads(p.read_text())
        data["seed_fixture"]["saved_instructions"] += 1
        p.write_text(json.dumps(data))
        result = replay(self.copy)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("certificate differs", result.stderr)

    def test_changed_reference_rejected(self):
        p = self.copy/"references/PR1287-README.md"
        p.write_bytes(p.read_bytes()+b"\nchanged predecessor\n")
        result = replay(self.copy)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("predecessor source drift", result.stderr)

    def test_wrong_output_macro_rejected(self):
        p = self.copy/"model.py"
        source = p.read_text()
        old, new = "(add(1, 0, -1), neg(0)),", "(add(1, 0, 1), neg(0)),"
        self.assertEqual(source.count(old), 1)
        p.write_text(source.replace(old, new))
        result = replay(self.copy)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wrong output word", result.stderr)

    def test_emission_refuses_existing_certificate(self):
        target = self.copy/"CERTIFICATE.json"
        before = target.read_bytes()
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(self.copy/"verify.py"),
                                 "--emit", str(target)], capture_output=True, text=True, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
