#!/usr/bin/env python3
"""Read-only relocation, source/receipt corruption and exact-kernel tests.

Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as audit


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="signed prefix relocation ")
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "research" / audit.PACKAGE.name
        shutil.copytree(audit.PACKAGE, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in audit.INPUTS:
            dest = cls.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(audit.ROOT / name, dest)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def command(self, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(self.package / "verify.py"), *args],
                              cwd="/tmp", text=True, capture_output=True, timeout=120)

    def test_strict_bit_boundary(self):
        for value, expected in [(Q(1), 1), (Q(2), 2), (Q(3, 2), 1), (Q(1, 2), 0),
                                (Q(131072), 18), (Q(131088), 18), (Q(1154896), 21)]:
            self.assertEqual(audit.strict_bits(value), expected)

    def test_dense_cancellation_and_alias_free_copy(self):
        engine = audit.DenseDyadic(3)
        engine.step(["copy", ["C", 0], ["L", 0]])
        engine.step(["add", ["L", 0], ["L", 1], -3, 8])
        engine.step(["scale", ["L", 1], 1, -2])
        engine.step(["add", ["L", 0], ["L", 1], -3, 4])
        engine.compare(("L", 0), {0: Q(1)})
        engine.compare(("C", 0), {0: Q(1)})
        engine.step(["clear", ["L", 0]])
        engine.compare(("L", 0), {})

    def test_read_only_relocation(self):
        files = [p for p in self.root.rglob("*") if p.is_file()]
        before = {str(p.relative_to(self.root)): audit.digest(p.read_bytes()) for p in files}
        try:
            for path in files:
                path.chmod(0o444)
            result = self.command()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS_COMPLEX_SIGNED_PREFIX_AUDIT", result.stdout)
            after = {str(p.relative_to(self.root)): audit.digest(p.read_bytes())
                     for p in self.root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
        finally:
            for path in files:
                path.chmod(0o644)

    def test_source_corruption(self):
        path = self.root / audit.LOCAL_CHECKER
        original = path.read_bytes()
        try:
            path.write_bytes(original + b"\n# corruption control\n")
            result = self.command()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash:", result.stderr)
        finally:
            path.write_bytes(original)

    def test_missing_input_pin(self):
        path = self.package / "SOURCES.json"
        original = path.read_bytes()
        try:
            value = json.loads(original)
            value["files"] = [r for r in value["files"] if r["path"] != audit.LOCAL_CHECKER]
            path.write_text(json.dumps(value))
            result = self.command()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("mandatory source inventory", result.stderr)
        finally:
            path.write_bytes(original)

    def test_receipt_corruption(self):
        path = self.package / "EXPECTED.json"
        original = path.read_bytes()
        try:
            value = json.loads(original)
            value["orientations"]["backward"]["exact_peak"] = "1154895"
            path.write_text(json.dumps(value))
            result = self.command()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("committed receipt mismatch", result.stderr)
        finally:
            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
