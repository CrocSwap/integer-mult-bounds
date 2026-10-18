"""Behavioral and mathematical failure controls for the deletion proof."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import verify
from vendor import geometry


class ProofControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots, cls.points, cls.labels, _ = geometry.root_data()
        cls.star, cls.costs, _ = verify.root_star(cls.roots)

    def test_explicit_star_and_root_class_formula(self):
        star = []
        for j in range(1, 6):
            row = [0] * 8
            row[0] = row[j] = 2
            star.append(tuple(row))
        spectrum = Counter()
        for root in self.roots:
            values = [0] + [
                sum(x * y for x, y in zip(root, v, strict=True)) for v in star
            ]
            minimum = min(sum(value != zero for value in values) for zero in values)
            spectrum[minimum] += 1
        self.assertEqual(spectrum, verify.closed_form_spectrum())
        self.assertEqual(spectrum, Counter(self.costs))

    def test_winning_invoice_and_losing_old_edge_bound(self):
        invoice = verify.support_invoice(self.costs)
        self.assertEqual(
            (invoice["endpoint_lower"], invoice["endpoint_allowance"]), (132, 120)
        )
        self.assertEqual(
            (invoice["coordinate_lower"], invoice["coordinate_upper"]), (795, 784)
        )
        self.assertGreaterEqual(9 * 24 + 5 * 120, 795)

    def test_puncture_charge_cannot_be_omitted(self):
        self.assertEqual(sum(sorted(self.costs)[:96]), 148)
        self.assertEqual(sum(sorted(self.costs)[: 96 - 8]), 132)

    def test_rank_five_capacity_cannot_be_relaxed_to_sixteen(self):
        with self.assertRaisesRegex(ValueError, "root-only"):
            verify.support_invoice(self.costs, small_support=32)

    def test_quotient_boundary_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "quotient"):
            verify.support_invoice(self.costs, small_support=33)

    def test_support_bill_must_be_strict(self):
        with self.assertRaisesRegex(ValueError, "endpoint budget"):
            verify.support_invoice([1] * 120)

    def test_invalid_budget_and_costs(self):
        for small, cap in ((True, 20), (-1, 20), (24, 113), (24, 20.0)):
            with self.subTest(small=small, cap=cap), self.assertRaises(ValueError):
                verify.support_invoice(self.costs, small, cap)
        with self.assertRaisesRegex(ValueError, "cost domain"):
            verify.support_invoice(self.costs[:-1])

    def test_actual_historical_profile(self):
        history = verify.original_survivors()
        self.assertEqual(len(history["profiles"]), 17)
        self.assertIn((5, 5) + (6,) * 6 + (7,), history["profiles"])
        self.assertEqual(history["target_excess"], 35)

    def test_receipt_rejects_altered_claim(self):
        expected = verify.read_json(verify.PACKAGE / "RESULT.json")
        changed = json.loads(json.dumps(expected))
        changed["invoice"]["endpoint_lower"] = 133
        with self.assertRaisesRegex(ValueError, "receipt mismatch"):
            verify.compare_receipt(changed, expected)

    def test_coordinate_source_order(self):
        with self.assertRaisesRegex(ValueError, "source order"):
            verify.bind_input(self.points[::-1], self.labels)

    def test_changed_source_and_retained_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research/p112-five-five-slice"
            shutil.copytree(verify.PACKAGE, package)
            # Exports may be read-only; only these disposable copies are made writable.
            for path in package.rglob("*"):
                path.chmod(0o700 if path.is_dir() else 0o600)
            package.chmod(0o700)
            source = root / "research/one-sided-six-multisets/data/data.txt"
            source.parent.mkdir(parents=True)
            original = verify.ROOT / source.relative_to(root)
            source.write_bytes(original.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "live input"):
                verify.check_sources(root, package)
            source.write_bytes(original.read_bytes())
            (package / "vendor/geometry.py").write_text("raise RuntimeError('changed')")
            with self.assertRaisesRegex(ValueError, "retained source"):
                verify.check_sources(root, package)

    def test_original_filter_incomplete_and_child_failures(self):
        with (
            patch(
                "verify.subprocess.run",
                return_value=SimpleNamespace(stdout="6 3 17 1\n", stderr=""),
            ),
            self.assertRaisesRegex(ValueError, "count mismatch"),
        ):
            verify.predecessor_control()
        for error in (
            subprocess.TimeoutExpired("control", 45),
            subprocess.CalledProcessError(1, "control"),
        ):
            with (
                self.subTest(error=type(error).__name__),
                patch("verify.subprocess.run", side_effect=error),
                self.assertRaises(type(error)),
            ):
                verify.predecessor_control()

    def test_output_location_and_overwrite_controls(self):
        env = dict(os.environ)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing.json"
            path.write_text("preserved")
            outputs = (
                (path, "overwrite"),
                (verify.PACKAGE / "must-not-exist.json", "outside"),
            )
            for output, message in outputs:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-O",
                        "-B",
                        str(verify.PACKAGE / "verify.py"),
                        "--output",
                        str(output),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                    env=env,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
            self.assertEqual(path.read_text(), "preserved")
            self.assertFalse((verify.PACKAGE / "must-not-exist.json").exists())


if __name__ == "__main__":
    unittest.main()
