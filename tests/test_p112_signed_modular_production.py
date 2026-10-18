"""Thin admission test for production P112 signed modular wiring."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "research/p112-signed-modular-production/verify.py"


class P112SignedModularProduction(unittest.TestCase):
    def test_verify_passes(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(VERIFY)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("PASS_P112_SIGNED_MODULAR_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
