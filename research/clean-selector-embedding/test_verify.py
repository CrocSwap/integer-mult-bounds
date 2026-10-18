#!/usr/bin/env python3
"""Actual no-Git, optimized, source/receipt corruption and output controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


class ExportChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, self.package)
        sources = json.loads((PACKAGE / "SOURCES.json").read_text())
        for row in sources["files"]:
            dest = self.root / row["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], dest)

    def run_check(self, *args, optimized=False):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        command += [str(self.package / "verify.py"), *args]
        return subprocess.run(command, cwd=self.root, text=True, capture_output=True, timeout=30)

    def rejected(self, result, text):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(text, result.stderr)

    def test_no_git_normal_and_optimized(self):
        self.assertFalse((self.root / ".git").exists())
        for mode in (False, True):
            result = self.run_check(optimized=mode)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_CLEAN_SELECTOR_EMBEDDING", result.stdout)

    def test_source_corruption(self):
        path = self.root / "research/selector-batching/README.md"
        path.write_bytes(path.read_bytes() + b"\nchanged source\n")
        self.rejected(self.run_check(optimized=True), "changed pinned source")

    def test_receipt_number_corruption(self):
        path = self.package / "CERTIFICATE.json"
        receipt = json.loads(path.read_text())
        receipt["native_d6_counts"][1] += 1
        path.write_text(json.dumps(receipt))
        self.rejected(self.run_check(optimized=True), "certificate mismatch")

    def test_receipt_boolean_alias(self):
        path = self.package / "CERTIFICATE.json"
        receipt = json.loads(path.read_text())
        self.assertEqual(receipt["fixtures"][0]["n"], 1)
        receipt["fixtures"][0]["n"] = True
        path.write_text(json.dumps(receipt))
        self.rejected(self.run_check(optimized=True), "certificate mismatch")

    def test_new_output_and_occupied_output(self):
        path = self.root / "new.json"
        result = self.run_check("--output", str(path), optimized=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(path.read_text()),
                         json.loads((self.package / "CERTIFICATE.json").read_text()))
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        self.rejected(self.run_check("--output", str(path)), "FileExistsError")
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
