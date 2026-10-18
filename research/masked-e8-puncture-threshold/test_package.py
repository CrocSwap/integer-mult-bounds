#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded on-disk rejection and relocation controls for the research package."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def invoke(directory, script, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(directory / script), *map(str, args)],
                          cwd=directory.parent, capture_output=True, text=True, timeout=600)


class PackageControls(unittest.TestCase):
    def copy(self, temporary):
        directory = Path(temporary) / "minimal source with spaces"
        shutil.copytree(HERE, directory)
        return directory

    def test_complete_support_sets_agree(self):
        primary = json.loads((HERE / "CERTIFICATE.json").read_text())
        independent = json.loads((HERE / "INDEPENDENT.json").read_text())
        self.assertEqual(primary["census"]["rank6_supports_sha256"],
                         independent["e7"]["rank6_supports_sha256"])
        self.assertEqual(primary["witness"]["deleted_indices"], independent["witness"]["deleted_indices"])

    def test_primary_and_independent_reject_corrupted_receipts(self):
        for script, receipt in (("verify.py", "CERTIFICATE.json"), ("independent.py", "INDEPENDENT.json")):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temporary:
                directory = self.copy(temporary)
                path = directory / receipt
                value = json.loads(path.read_text())
                value["first_failure_deletions"] = 26
                path.write_text(json.dumps(value))
                before = path.read_bytes()
                result = invoke(directory, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source/receipt drift", result.stderr)
                self.assertEqual(path.read_bytes(), before)

    def test_primary_and_independent_reject_source_drift(self):
        for script in ("verify.py", "independent.py"):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temporary:
                directory = self.copy(temporary)
                with (directory / script).open("a") as out:
                    out.write("\n# deliberate changed implementation control\n")
                result = invoke(directory, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source/receipt drift", result.stderr)

    def test_custom_independent_receipt_rejects_false_geometry(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "false-result.json"
            value = json.loads((HERE / "INDEPENDENT.json").read_text())
            value["e7"]["max_flat_size"] = 37
            path.write_text(json.dumps(value))
            result = invoke(HERE, "independent.py", "--check", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("independent receipt differs", result.stderr)

    def test_no_overwrite(self):
        for script in ("verify.py", "independent.py"):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "retained.json"
                path.write_bytes(b"retained evidence\n")
                result = invoke(HERE, script, "--write", path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("overwrite", result.stderr)
                self.assertEqual(path.read_bytes(), b"retained evidence\n")

    def test_minimal_relocated_read_only_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = self.copy(temporary)
            before = {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                      for f in directory.iterdir() if f.is_file()}
            for script in ("verify.py", "independent.py"):
                result = invoke(directory, script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after = {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                     for f in directory.iterdir() if f.is_file()}
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
