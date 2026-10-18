#!/usr/bin/env python3
"""Behavior and exact-arithmetic controls for the QQ16 certificate."""
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("qq16_moment", HERE / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Verifier import is unavailable")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def polynomial(x):
    return Q(85, 39)*x - Q(248, 169)*x*x + Q(48, 169)*x*x*x


def multiply(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(2))
             for j in range(2)] for i in range(2)]


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = verifier.report(verifier.ROOT)

    def test_literal_source_receipt(self):
        expected = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(self.actual, expected)
        self.assertEqual(self.actual["projector_moments_per_owner"],
                         ["24", "28", "109/3"])
        self.assertEqual(self.actual["necessary_integer_record_width"], 14)
        self.assertEqual(self.actual["semantic_controls_rejected"], 3)

    def test_factored_spectral_polynomial(self):
        self.assertEqual([polynomial(Q(x)) for x in (0, 1, 3)],
                         [Q(0), Q(505, 507), Q(1)])
        self.assertEqual(polynomial(Q(13, 12)), 1)
        for numerator in range(301):
            x = Q(numerator, 100)
            self.assertEqual(1-polynomial(x),
                             (1-Q(12, 13)*x)**2*(1-x/3))
            self.assertLessEqual(polynomial(x), 1)

    def test_sum_of_three_literal_projections(self):
        vectors = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(3, 5), Q(4, 5)))
        matrix = [[sum(v[i]*v[j] for v in vectors)
                   for j in range(2)] for i in range(2)]
        square = multiply(matrix, matrix)
        cube = multiply(square, matrix)
        moments = [sum(a[i][i] for i in range(2))
                   for a in (matrix, square, cube)]
        self.assertEqual(moments, [Q(3), Q(5), Q(9)])
        bound = Q(85, 39)*moments[0] - Q(248, 169)*moments[1] + Q(48, 169)*moments[2]
        self.assertEqual(bound, Q(297, 169))
        self.assertLessEqual(bound, 2)  # The two coordinate vectors span Q^2.

    def test_capacity_delta(self):
        bound = Q(self.actual["selected_defect_lower_per_owner"])
        self.assertEqual(bound, Q(176, 13))
        self.assertEqual(bound-Q(88, 7), Q(88, 91))
        self.assertEqual(bound-13, Q(7, 13))
        self.assertLess(bound-14, 0)  # No exclusion of width fourteen.

    def test_cli_positive(self):
        completed = subprocess.run(
            [sys.executable, "-I", "-B", str(HERE / "verify.py")],
            text=True, capture_output=True, timeout=30, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), verifier.MARKER +
                         " rank>=280|G|/13 defect>=176|G|/13 width>=14 no_new_kappa")

    def test_cli_rejects_changed_source(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            path = root / verifier.PACKET
            path.parent.mkdir(parents=True)
            path.write_bytes(b"not the pinned packet")
            completed = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                 "--repo", str(root)], text=True, capture_output=True,
                timeout=30, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("source pin:", completed.stderr)
            self.assertNotIn(verifier.MARKER, completed.stdout)

    def test_cli_rejects_changed_receipt(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            shutil.copyfile(HERE / "verify.py", root / "verify.py")
            bad = dict(self.actual)
            bad["necessary_integer_record_width"] = 15
            (root / "RESULT.json").write_text(json.dumps(bad), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(root / "verify.py"),
                 "--repo", str(verifier.ROOT)], text=True, capture_output=True,
                timeout=30, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("receipt mismatch", completed.stderr)
            self.assertNotIn(verifier.MARKER, completed.stdout)


if __name__ == "__main__":
    unittest.main()
