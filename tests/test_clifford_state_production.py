#!/usr/bin/env python3
"""Smoke tests for research/clifford-state-production."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/clifford-state-production"
PRODUCTION = (
    ROOT
    / "research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py"
)
BASELINE = PACKAGE / "baseline.py"
OPTIMIZED_SHA256 = "9b360d58055de706a27abe5211a14115225e47f0c6096e4fb8818e99a4772abd"
ORIGINAL_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"


class CliffordStateProductionTests(unittest.TestCase):
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
        self.assertIn("PASS_CLIFFORD_STATE_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
