#!/usr/bin/env python3
# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Behavioral tests against the actual replay CLI in private relocated copies."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


class ReplayTests(unittest.TestCase):
    def run_copy(self, mutate=None, optimized=False):
        with tempfile.TemporaryDirectory(prefix="mixed targets ") as directory:
            root = Path(directory)
            script = root / "verify.py"
            receipt = root / "RESULT.json"
            script.write_bytes((PACKAGE / "verify.py").read_bytes())
            value = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
            source = script.read_text(encoding="utf-8")
            if mutate is not None:
                source, value = mutate(source, value)
            script.write_text(source, encoding="utf-8")
            receipt.write_text(json.dumps(value), encoding="utf-8")
            before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in (script, receipt)]
            argv = [sys.executable, "-I", "-B"]
            if optimized:
                argv.append("-O")
            run = subprocess.run([*argv, str(script)], cwd=root.parent, capture_output=True,
                                 text=True, timeout=30, check=False)
            after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in (script, receipt)]
            self.assertEqual(before, after, "ordinary replay must be read-only")
            return run

    def test_relocated_positive_normal_and_optimized(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                run = self.run_copy(optimized=optimized)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn("PASS_MIXED_TARGET_REGISTER_COMPRESSION fixtures=6 controls=10", run.stdout)

    def check_receipt_fault(self, field, replacement):
        def mutate(source, value):
            value["fixtures"]["sharp"][field] = replacement
            return source, value

        for optimized in (False, True):
            run = self.run_copy(mutate, optimized)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("result receipt mismatch", run.stderr)
            self.assertNotIn("PASS_MIXED_TARGET", run.stdout)

    def test_false_bound(self):
        self.check_receipt_fault("role_bound", 5)

    def test_false_basis(self):
        self.check_receipt_fault("basis", [1, 2, 4])

    def test_false_restricted_operator(self):
        self.check_receipt_fault("restricted_projectors", [[0]])

    def test_missing_census(self):
        def mutate(source, value):
            value["census"].pop()
            return source, value

        run = self.run_copy(mutate, True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("result receipt mismatch", run.stderr)

    def test_unadapted_complement_mutant(self):
        def mutate(source, value):
            old = "action(projector, 1 << i) & ~active_mask"
            self.assertEqual(source.count(old), 1)
            return source.replace(old, "action(projector, 1 << i)"), value

        run = self.run_copy(mutate, True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("off-diagonal endpoint", run.stderr)


if __name__ == "__main__":
    unittest.main()
