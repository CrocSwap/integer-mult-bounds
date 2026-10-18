#!/usr/bin/env python3
"""Smoke tests for research/hpe-transport-integer-production."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/hpe-transport-integer-production"
PRODUCTION = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_and_transport.py"
BASELINE = PACKAGE / "baseline.py"
OPTIMIZED_SHA256 = "d777db4abe316594df5cd3dc1269b42f4af4a8c87d4d0df500d32655e3775b87"
ORIGINAL_SHA256 = "c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3"


class HpeTransportIntegerProductionTests(unittest.TestCase):
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
        self.assertIn("PASS_HPE_TRANSPORT_INTEGER_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
