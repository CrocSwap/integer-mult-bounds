#!/usr/bin/env python3
"""Smoke tests for research/bit-hosted-digest-production."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/bit-hosted-digest-production"
PRODUCTION = (
    ROOT
    / "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage"
    / "vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py"
)
BASELINE = PACKAGE / "baseline.py"
OPTIMIZED_SHA256 = "9d0b44e37109128850192414bf0fefb1048bf96da2c78dff8e833980b20f61c7"
ORIGINAL_SHA256 = "57e558c80a2fea6e291587b04afd76dfaee3550729997798b61f33daf90b8ec9"


class BitHostedDigestProductionTests(unittest.TestCase):
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
        self.assertIn("PASS_BIT_HOSTED_DIGEST_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
