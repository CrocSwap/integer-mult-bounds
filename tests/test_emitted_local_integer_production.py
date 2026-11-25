#!/usr/bin/env python3
"""Smoke tests for research/emitted-local-integer-production."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/emitted-local-integer-production"
PRODUCTION = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_local.py"
BASELINE = PACKAGE / "baseline.py"
OPTIMIZED_SHA256 = "cbf68feab9fcf57d8d5ed8a525a8f8cd5d79b2a61faf98cff672e137a3bcf99f"
ORIGINAL_SHA256 = "6bd9a1e279c9c9e4f3767d9f82e537b559292906feb2ddab02f380fb6523a810"


class EmittedLocalIntegerProductionTests(unittest.TestCase):
    def test_production_differs_from_baseline_and_matches_digest(self):
        self.assertEqual(sha256(BASELINE.read_bytes()).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(sha256(PRODUCTION.read_bytes()).hexdigest(), OPTIMIZED_SHA256)
        self.assertNotEqual(PRODUCTION.read_bytes(), BASELINE.read_bytes())

    def test_verify_script(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS_EMITTED_LOCAL_INTEGER_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
