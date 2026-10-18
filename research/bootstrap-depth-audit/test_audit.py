#!/usr/bin/env python3
"""Independent cost-exponent and CLI failure checks for the scoped audit.

Isaac Grannis (@BagMan9), with OpenAI Codex assistance. Apache-2.0.
"""

import importlib.util
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bootstrap_audit", ROOT / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class BootstrapAudit(unittest.TestCase):
    def test_varying_savings_against_original_cost_exponents(self):
        # This uses the three cost exponents, not audit.step. All 1,536
        # four-stage schedules are checked at every intermediate depth.
        schedules = 0
        for upper in (F(1, 64), F(31, 1024)):
            for initial in (F(0), upper / 2, 7 * upper / 8):
                choices = [i * upper / 4 for i in range(1, 5)]
                for schedule in itertools.product(choices, repeat=4):
                    old = initial
                    for depth, saving in enumerate(schedule, 1):
                        worst_cost_exponent = max(
                            1 - saving,
                            (1 - saving)**2 + saving * (1 - old),
                            saving,
                        )
                        # Keeping the previous completed supplier is permitted.
                        # Ignoring the logarithmic strict gap is optimistic.
                        old = max(old, 1 - worst_cost_exponent)
                        cap_n, cap_d = audit.cap_integer(initial, upper, depth)
                        self.assertLessEqual(old / (1 + old), F(cap_n, cap_d))
                    schedules += 1
        self.assertEqual(schedules, 1536)

    def test_monotonicity_domain_is_needed(self):
        # Outside u < 1/2, blindly maximizing s can lose the maximum.
        upper, saving = F(3, 4), F(1, 2)
        from_cost_exponent = 1 - ((1 - saving)**2 + saving)
        n, d = audit.cap_integer(F(0), upper, 1)
        self.assertGreater(from_cost_exponent / (1 + from_cost_exponent), F(n, d))

    def test_integer_cap_at_large_depth(self):
        # Cover j=0 and arbitrary a0 independently of the source witness.
        for initial, upper in ((F(0), F(1, 64)), (F(1, 1000), F(1, 50))):
            old = initial
            for depth in range(21):
                n, d = audit.cap_integer(initial, upper, depth)
                self.assertEqual(F(n, d), old / (1 + old))
                old = 1 - ((1 - upper)**2 + upper * (1 - old))

    def test_strict_grid_boundaries(self):
        for numerator in range(1, 41):
            for denominator in range(1, 21):
                for scale in (1, 10, 100):
                    point = F(audit.strict_grid(numerator, denominator, scale), scale)
                    value = F(numerator, denominator)
                    self.assertLess(point, value)
                    self.assertLessEqual(value, point + F(1, scale))

    def test_expected_receipt_in_optimized_isolated_process(self):
        with tempfile.TemporaryDirectory() as work:
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-O", str(ROOT / "verify.py"),
                 "--check", str(ROOT / "EXPECTED.json")],
                cwd=work, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("9 controls rejected", result.stdout)

    def test_tampered_receipt_rejected_under_optimization(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "receipt.json"
            receipt = json.loads((ROOT / "EXPECTED.json").read_text())
            receipt["five_round_exclusion_cross_product"] = "0"
            path.write_text(json.dumps(receipt))
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-O", str(ROOT / "verify.py"),
                 "--check", str(path)],
                cwd=work, capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stderr)

    def test_changed_source_rejected_under_optimization(self):
        with tempfile.TemporaryDirectory() as work:
            copy = Path(work) / "audit"
            shutil.copytree(ROOT, copy)
            path = copy / "sources/pr387/PARAMETERS.json"
            params = json.loads(path.read_text())
            params["bootstrap_rounds"] = 5
            path.write_text(json.dumps(params))
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-O", str(copy / "verify.py")],
                cwd=work, capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source SHA256", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
