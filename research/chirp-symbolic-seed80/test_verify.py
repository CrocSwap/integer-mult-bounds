#!/usr/bin/env python3
"""Check the algebra engine, scope boundaries, and failure-sensitive entrypoint."""
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("chirp_symbolic_verifier", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class VerificationTests(unittest.TestCase):
    def test_ring_by_independent_integer_evaluation(self):
        x, y, z = (V.Poly.var(name) for name in ("x", "y", "z"))
        expressions = [
            ((x+y+z)**3, lambda a, b, c: (a+b+c)**3),
            ((x-y)*(y-z)*(z-x), lambda a, b, c: (a-b)*(b-c)*(c-a)),
            (x*(y+1)**2-x*y*y, lambda a, b, c: a*(b+1)**2-a*b*b),
            ((2*x-3*y+7)*(z-4), lambda a, b, c: (2*a-3*b+7)*(c-4)),
            ((x+y)**0, lambda a, b, c: 1),
        ]
        for values in itertools.product(range(-2, 3), repeat=3):
            assignment = dict(zip(("x", "y", "z"), values))
            for polynomial, oracle in expressions:
                self.assertEqual(polynomial.evaluate(assignment), oracle(*values))
        self.assertEqual(((x+y)**2-x*x-2*x*y-y*y).terms, {})
        self.assertNotEqual(((x+y)**2-x*x-x*y-y*y).terms, {})
        self.assertEqual((x*y-y*x).terms, {})

    def test_guard_and_modulus_cannot_be_assumed_silently(self):
        q = V.Modulus()
        V.Poly.context = q
        j, t = V.Poly.var("j"), V.Poly.var("t")
        with self.assertRaisesRegex(V.Failure, "unproved branch guard"):
            _ = j+1 < t
        with self.assertRaisesRegex(V.Failure, "changed symbolic modulus"):
            _ = j % V.Modulus()
        with self.assertRaisesRegex(V.Failure, "changed symbolic modulus"):
            _ = j % 8
        q.guards[(j+1-t).key()] = True
        self.assertTrue(j+1 < t)
        self.assertFalse(t < t)
        self.assertEqual(len(q.used_guards), 1)

    def test_all_faults_have_concrete_state_or_flag_witnesses(self):
        source, _ = V.source_bytes()
        rows = V.controls(source)
        self.assertEqual(len(rows), 16)
        self.assertEqual(sum(row["symbolic_rejection"] is not None for row in rows), 10)
        for row in rows:
            witness = row["concrete_witness"]
            differs = witness["expected"] != witness["actual"]
            if witness["stage"] == "advance":
                differs |= witness["continues"] != witness["expected_continues"]
                differs |= witness["metrics"] != witness["expected_metrics"]
            self.assertTrue(differs, row["mutation"])
        # Congruence alone cannot certify canonical residues or initialization.
        nonsymbolic = {row["mutation"] for row in rows if row["symbolic_rejection"] is None}
        self.assertEqual(nonsymbolic, {"positive_initial_phase", "half_modulus",
                                     "zero_initial_difference", "unreduced_phase",
                                     "unreduced_value", "unreduced_difference"})

    def test_complete_small_numeric_domain_and_wide_endpoints(self):
        source, _ = V.source_bytes()
        result = V.finite_checks(V.implementation(source))
        self.assertEqual(result["exact_state_transitions"], 8605)
        self.assertEqual(result["small_boxes"], 129)
        self.assertEqual(result["wide_transitions"], 21)
        # Independent arithmetic: all 2x4x8 ranks decode in lexicographic order.
        points = list(itertools.product(range(2), range(4), range(8)))
        self.assertEqual([V.unrank(k, (2, 4, 8)) for k in range(64)], points)
        self.assertEqual([V.rank_of(point, (2, 4, 8)) for point in points], list(range(64)))

    def test_nontrivial_equivalent_source_rewrites_pass(self):
        source, _ = V.source_bytes()
        self.assertEqual(len(V.equivalent_controls(source)), 2)

    def copy_package(self, directory):
        root = Path(directory) / "independent package with spaces"
        shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def run_cli(self, root, *args):
        return subprocess.run([sys.executable, "-B", "-I", "-O", str(root / "verify.py"), *args],
                              cwd=root.parent, text=True, capture_output=True, check=False)

    def test_relocated_optimized_receipt_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_package(directory)
            ok = self.run_cli(root)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertIn("PASS_CHIRP_SYMBOLIC_INVARIANTS", ok.stdout)
            expected = json.loads((root / "EXPECTED.json").read_text())
            expected["finite"]["exact_state_transitions"] += 1
            (root / "EXPECTED.json").write_text(V.canonical(expected))
            bad = self.run_cli(root)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("expected receipt mismatch", bad.stderr)

    def test_source_drift_and_incomplete_pin_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_package(directory)
            source = root / "vendor/stream.py"
            original = source.read_bytes()
            source.write_bytes(original+b"\n# changed bytes\n")
            bad = self.run_cli(root)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source SHA-256 mismatch", bad.stderr)
            source.write_bytes(original)
            pins = json.loads((root / "SOURCES.json").read_text())
            del pins["files"]["vendor/PROOF.md"]
            (root / "SOURCES.json").write_text(V.canonical(pins))
            bad = self.run_cli(root)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("incomplete source closure", bad.stderr)

    def test_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.copy_package(directory)
            destination = root.parent / "existing.json"
            destination.write_text("preserve me\n")
            bad = self.run_cli(root, "--write", str(destination))
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(destination.read_text(), "preserve me\n")


if __name__ == "__main__":
    unittest.main()
