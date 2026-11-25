#!/usr/bin/env python3
"""Smoke tests for research/frame-pair-enumeration-production."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/frame-pair-enumeration-production"
PRODUCTION = ROOT / "research/complex-frame-pair-decoders/verify.py"
BASELINE = PACKAGE / "baseline.py"
OPTIMIZED_SHA256 = "f7a9a39659c179853af3220f83a11b4c3cf52c8f3bccc0911a5629add10fbaff"
ORIGINAL_SHA256 = "bdf7ee497dc04dfc634ee5b7848f6a2b39b0169668fb1a60a9715111dbd15395"


class FramePairEnumerationProductionTests(unittest.TestCase):
    def test_production_differs_from_baseline_and_matches_digest(self):
        self.assertEqual(sha256(BASELINE.read_bytes()).hexdigest(), ORIGINAL_SHA256)
        self.assertEqual(sha256(PRODUCTION.read_bytes()).hexdigest(), OPTIMIZED_SHA256)
        self.assertNotEqual(PRODUCTION.read_bytes(), BASELINE.read_bytes())
        self.assertIn("neighbors = [sum(bool(IP[g][f])", PRODUCTION.read_text(encoding="utf-8"))

    def test_verify_script(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS_FRAME_PAIR_ENUMERATION_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
