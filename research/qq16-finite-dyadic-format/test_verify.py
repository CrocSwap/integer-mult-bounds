#!/usr/bin/env python3
"""Exercise the exported CLI, source/receipt integrity and finite boundaries."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import verify  # noqa: E402


class ArtifactTests(unittest.TestCase):
    def invoke(self, directory, *arguments, success=True):
        completed = subprocess.run(
            [sys.executable, "-Werror", "-I", "-O", "-B", str(directory / "verify.py"), *arguments],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if success:
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PASS_QQ16_FINITE_DYADIC_FORMAT", completed.stdout)
        else:
            self.assertNotEqual(completed.returncode, 0)
            self.assertNotIn("PASS_QQ16_FINITE_DYADIC_FORMAT", completed.stdout)
        return completed

    def export(self, parent):
        destination = Path(parent) / "export"
        shutil.copytree(PACKAGE, destination, ignore=shutil.ignore_patterns("__pycache__"))
        return destination

    def snapshot(self, directory):
        return {
            str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*")
            if p.is_file()
        }

    def test_read_only_git_free_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            exported = self.export(temporary)
            before = self.snapshot(exported)
            for path in exported.rglob("*"):
                path.chmod(0o555 if path.is_dir() else 0o444)
            exported.chmod(0o555)
            try:
                self.invoke(exported)
                self.assertEqual(before, self.snapshot(exported))
            finally:
                exported.chmod(0o755)
                for path in exported.rglob("*"):
                    path.chmod(0o755 if path.is_dir() else 0o644)

    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            exported = self.export(temporary)
            path = exported / "source/WORD.json"
            path.write_bytes(path.read_bytes() + b"\n")
            failed = self.invoke(exported, success=False)
            self.assertIn("source hash mismatch", failed.stderr)

    def test_typed_receipt_and_cut_corruption(self):
        for field in ("line_cases", "cut"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                exported = self.export(temporary)
                path = exported / "RESULT.json"
                receipt = json.loads(path.read_text())
                if field == "line_cases":
                    receipt[field] = True
                else:
                    receipt["grid_certificate"]["cut_rows"][371][2][0] += 1
                path.write_text(json.dumps(receipt))
                self.assertIn("typed receipt mismatch", self.invoke(exported, success=False).stderr)

    def test_overwrite_and_unknown_argument(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "existing.json"
            target.write_text("preserve me\n")
            self.invoke(PACKAGE, "--emit-result", str(target), success=False)
            self.assertEqual(target.read_text(), "preserve me\n")
        self.invoke(PACKAGE, "--unknown", success=False)

    def test_signed_rounding_and_integer_limits(self):
        for value in range(-31, 32):
            for shift in range(7):
                actual = verify.rounded_integer(value, shift, 8)
                expected = verify.rational_round(verify.F(value), verify.F(1 << shift)) / (
                    1 << shift
                )
                self.assertEqual(actual, expected)
        self.assertEqual(verify.signed(-128, 8), -128)
        self.assertEqual(verify.signed(127, 8), 127)
        self.assertEqual(
            verify.integer_line([(1, -1), (0, 1)], 1, [0], 1, 22, 64),
            [(1, -1), (0, 1)],
        )
        with self.assertRaisesRegex(ValueError, "overflow"):
            verify.signed(-129, 8)
        with self.assertRaisesRegex(ValueError, "direction"):
            verify.integer_line([(0, 0), (0, 0)], 1, [2], 1, 22, 64)


if __name__ == "__main__":
    unittest.main()
