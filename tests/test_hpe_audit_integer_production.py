#!/usr/bin/env python3
"""unittest entry for research/hpe-audit-integer-production."""
import unittest
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HpeAuditIntegerProductionTests(unittest.TestCase):
    def test_verify(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "research/hpe-audit-integer-production/verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("PASS_HPE_AUDIT_INTEGER_PRODUCTION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
