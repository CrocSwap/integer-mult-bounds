#!/usr/bin/env python3
"""Semantic, endpoint, corruption and portable replay controls. Apache-2.0."""
from fractions import Fraction as Q
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import census
import interval_oracle
import verify


def rational_execution(c, target, guards=2):
    """Small independent scalar fixture interpreter; never used for the census."""
    x, m, t = Q(5, 8), 1, 6
    while True:
        scale = 2 ** t
        prefix = Q((c * scale).__floor__(), scale)
        u = Q((prefix * x * scale).__floor__(), scale)
        x = Q((x * (2 - u) * scale).__floor__(), scale)
        if m == target:
            return x
        m = min(m * 2, target)
        t = m + guards


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((HERE / "CERTIFICATE.json").read_text())

    def test_strict_endpoints_all_seven_intervals(self):
        bound = Q(1, 65536)
        for f in self.receipt["rows"][-1]["failures"]:
            lo, hi, x = Q(f["lo"]), Q(f["hi"]), Q(f["output"])
            self.assertTrue(f["lo_closed"] and f["hi_closed"])
            self.assertLess(lo, hi)
            for c in (lo, (lo + hi) / 2, hi):
                self.assertEqual(rational_execution(c, 15), x)
                self.assertGreaterEqual(1 - c * x, bound)
            self.assertEqual(1 - hi * x, bound)
            self.assertGreater(1 - lo * x, bound)
            # Inside the very same prefix cell, just beyond the rational
            # equality endpoint, the strict contract is satisfied.
            cell_end = Q(f["cell"] + 1, 2 ** 17)
            probe = (hi + cell_end) / 2
            self.assertEqual(rational_execution(probe, 15), x)
            self.assertLess(abs(1 - probe * x), bound)
        first = self.receipt["rows"][-1]["failures"][0]
        self.assertEqual(first["lo"], "127379/65536")
        self.assertEqual(first["hi"], "26214/13487")
        self.assertEqual(1 - Q(first["lo"]) * Q(first["output"]) - bound,
                         Q(655, 8589934592))  # PR1655's credited witness.

    def test_lower_guards_and_equality_only_failures(self):
        for guards, first in ((0, 2), (1, 3)):
            for p in range(1, first + 1):
                row = census.grid_census(p, guards)
                self.assertEqual(row, interval_oracle.interval_census(p, guards))
                self.assertEqual(bool(row["failures"]), p == first)
        singletons = [f for f in census.grid_census(3, 1)["failures"] if f["lo"] == f["hi"]]
        self.assertEqual(len(singletons), 3)
        for f in singletons:
            self.assertTrue(f["lo_closed"] and f["hi_closed"])
            self.assertEqual(abs(1 - Q(f["lo"]) * rational_execution(Q(f["lo"]), 3, 1)), Q(1, 16))

    def test_rounding_and_schedule_mutants_are_distinguished(self):
        def truncate_incoming(c, a, b, t):
            if b > t:
                a, b = a >> (b - t), t
            return census.rounded_step(c, a, b, t)

        def stale_prefix(c, a, b, t):
            if t > 6:
                c = (c >> (t - 6)) << (t - 6)
            return census.rounded_step(c, a, b, t)

        def exact_inner(c, a, b, t):
            return a * ((2 << t) * (1 << b) - c * a) // (1 << (2 * b))

        def ceil_output(c, a, b, t):
            u = c * a // (1 << b)
            return (a * ((2 << t) - u) + (1 << b) - 1) // (1 << b)

        for p, mutant in ((2, truncate_incoming), (5, stale_prefix), (2, exact_inner), (2, ceil_output)):
            with self.subTest(mutant=mutant.__name__):
                self.assertNotEqual(census.grid_census(p, step=mutant)["outputs_sha256"],
                                    self.receipt["rows"][p - 1]["outputs_sha256"])
        for broken in ([4, 6, 10, 17], [6, 4, 6, 10], [6, 4, 6, 10, 18]):
            with patch.object(census, "schedule", return_value=broken):
                self.assertNotEqual(census.grid_census(15), self.receipt["rows"][-1])
        original = interval_oracle.interval_census

        def wrong_stream(*args, **kwargs):
            row, outputs = original(*args, **kwargs)
            # Leave every receipt field, including its digest, unchanged.
            # Direct stream equality must still reject the changed output.
            return row, bytes([outputs[0] ^ 1]) + outputs[1:]

        with patch.object(interval_oracle, "interval_census", side_effect=wrong_stream):
            with self.assertRaisesRegex(ValueError, "exact output-stream disagreement"):
                verify.compute_checked()

    def test_excluded_right_endpoint_is_not_a_failure(self):
        # x=3/4 on [1,3/2): residual approaches -1/8 only at excluded 3/2.
        x, lo, hi, bound = Q(3, 4), Q(1), Q(3, 2), Q(1, 8)
        self.assertEqual(1 - hi * x, -bound)
        for c in ((lo + hi) / 2, hi - Q(1, 2 ** 30)):
            self.assertGreater(1 - c * x, -bound)
        # A real routine fixture also has zero *positive* endpoint slack at
        # one guard, p=3; equality is retained as an actual singleton above.

    def test_interval_coverage_and_domains_fail_closed(self):
        for pieces in ([(Q(1), Q(3, 2), Q(5, 8))],
                       [(Q(1), Q(5, 4), Q(5, 8)), (Q(3, 2), Q(2), Q(5, 8))],
                       [(Q(1), Q(7, 4), Q(5, 8)), (Q(3, 2), Q(2), Q(5, 8))],
                       [(Q(1), Q(2), Q(0))]):
            with self.assertRaises(ValueError):
                interval_oracle.advance(pieces, 6)
        for bad in (0, 16, True, 2.5):
            with self.assertRaises(ValueError):
                census.grid_census(bad)
            with self.assertRaises(ValueError):
                interval_oracle.interval_census(bad)

    def test_readonly_relocation_and_actual_corruption_controls(self):
        with tempfile.TemporaryDirectory(prefix="reciprocal audit ") as tmp:
            root = Path(tmp) / "export"
            destination = root / "research" / HERE.name
            shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns("__pycache__"))
            original_input = HERE.parents[1] / "upstream/build/sections/09-exact-arithmetic.tex"
            copied_input = root / "upstream/build/sections/09-exact-arithmetic.tex"
            copied_input.parent.mkdir(parents=True)
            shutil.copy2(original_input, copied_input)
            for file in root.rglob("*"):
                if file.is_file():
                    file.chmod(0o444)
            for directory in sorted((d for d in root.rglob("*") if d.is_dir()), reverse=True):
                directory.chmod(0o555)
            root.chmod(0o555)

            def run(*args):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(destination / "verify.py"), *args],
                                      cwd=tmp, env={**os.environ, "PYTHONOPTIMIZE": "2"},
                                      text=True, capture_output=True, timeout=120)

            try:
                positive = run()
                self.assertEqual(positive.returncode, 0, positive.stderr)
                self.assertIn("independent_partition=PASS", positive.stdout)
                receipt_file = destination / "CERTIFICATE.json"
                for mutation in (lambda d: d["rows"][-1]["failures"].pop(),
                                 lambda d: d["rows"][-1]["failures"][0].update(hi_closed=False)):
                    original = receipt_file.read_bytes()
                    altered = json.loads(original)
                    mutation(altered)
                    receipt_file.chmod(0o644)
                    receipt_file.write_text(json.dumps(altered))
                    receipt_file.chmod(0o444)
                    result = run()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("certificate disagrees", result.stderr)
                    receipt_file.chmod(0o644)
                    receipt_file.write_bytes(original)
                    receipt_file.chmod(0o444)
                for source in (copied_input, destination / "vendor/PR1655-README.md"):
                    original = source.read_bytes()
                    source.chmod(0o644)
                    source.write_bytes(original + b"\ncorrupt\n")
                    source.chmod(0o444)
                    result = run()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("source digest", result.stderr)
                    source.chmod(0o644)
                    source.write_bytes(original)
                    source.chmod(0o444)
                preserved = Path(tmp) / "occupied.json"
                preserved.write_bytes(b"retain this output")
                result = run("--write", str(preserved))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("refusing to overwrite", result.stderr)
                self.assertEqual(preserved.read_bytes(), b"retain this output")
            finally:
                root.chmod(0o755)
                for directory in root.rglob("*"):
                    if directory.is_dir():
                        directory.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
