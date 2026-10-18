#!/usr/bin/env python3
"""Independent matrix checks and isolated rejection controls for seed 67.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("composite_height_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def matrix_rank(matrix, prime):
    """Dense elimination, separate from the checker's Bezout polynomial route."""
    a = [[x % prime for x in row] for row in matrix]
    rank = 0
    for column in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][column], -1, prime)
        a[rank] = [x * inverse % prime for x in a[rank]]
        for i in range(rank + 1, len(a)):
            c = a[i][column]
            if c:
                a[i] = [(x - c * y) % prime for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank


def sylvester(r, prime, shifted_reciprocal=False):
    # Independently evaluate each whole tail, not the backward recurrence.
    coefficients = []
    for j in range(r):
        product = 1
        for s in range(j + 1, r):
            product = product * (1 - (-1) ** s) % prime
        coefficients.append(product)
    reciprocal = coefficients[::-1]
    if shifted_reciprocal:
        reciprocal = [0] * (r - 2) + [1, 2]
    n = r - 1
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for shift in range(n):
        for j in range(r):
            out[j + shift][shift] = coefficients[j]
            out[j + shift][n + shift] = reciprocal[j]
    return out


class AuditTests(unittest.TestCase):
    def test_all_lifting_matrices_by_dense_rank(self):
        cases = audit.audit_lifting()["cases"]
        self.assertEqual(len(cases), 19)
        for case in cases:
            r, p = case["r"], case["p"]
            with self.subTest(r=r, p=p):
                self.assertEqual(matrix_rank(sylvester(r, p), p), 2 * (r - 1))

    def test_singular_lifting_controls(self):
        self.assertLess(matrix_rank(sylvester(6, 3), 3), 10)
        self.assertLess(matrix_rank(sylvester(10, 5, shifted_reciprocal=True), 5), 18)

    def test_seed_budget_and_ratio(self):
        self.assertEqual(audit.Q(134, len(audit.units(134))), audit.Q(67, 33))
        row = audit.bound(8978)
        self.assertEqual(row["phi"], 4422)
        self.assertEqual(row["old_coarse_gap_bits"], 356393327561)
        self.assertEqual(row["gap_bits"], 28312479536)
        self.assertEqual(row["inverse_norm_bits"], 56624968052)
        # Independent totient formula for every seeded exponent.
        for a in range(1, 9):
            self.assertEqual(audit.bound(2 * 67 ** a)["phi"], 66 * 67 ** (a - 1))

    def clone_fixture(self, temp):
        root = Path(temp)
        package = root / "research" / HERE.name
        package.parent.mkdir(parents=True)
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for row in sources["files"]:
            if row["usage"] == "input":
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)
        return root, package

    def run_fixture(self, package, *args):
        return subprocess.run([sys.executable, "-I", "-O", "-B",
                               str(package / "verify.py"), *args],
                              text=True, capture_output=True, timeout=30)

    def test_relocated_normal_and_optimized_receipt(self):
        with tempfile.TemporaryDirectory(prefix="height-audit67-") as temp:
            _, package = self.clone_fixture(temp)
            result = self.run_fixture(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            proposal = Path(temp) / "recomputed.json"
            result = self.run_fixture(package, "--write", str(proposal))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(proposal.read_bytes(), (package / "EXPECTED.json").read_bytes())
            normal = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py")],
                                    text=True, capture_output=True, timeout=30)
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertEqual(normal.stdout, result.stdout)

    def test_reject_corrupt_receipt(self):
        with tempfile.TemporaryDirectory(prefix="height-audit67-") as temp:
            _, package = self.clone_fixture(temp)
            path = package / "EXPECTED.json"
            value = json.loads(path.read_text())
            value["budgets"]["seed_family"][1]["gap_bits"] -= 1
            path.write_text(json.dumps(value))
            result = self.run_fixture(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)

    def test_reject_source_drift(self):
        with tempfile.TemporaryDirectory(prefix="height-audit67-") as temp:
            root, package = self.clone_fixture(temp)
            path = root / "research/prime-power-cyclic-inverse/PROOF.md"
            path.write_bytes(path.read_bytes() + b"\nchanged source\n")
            result = self.run_fixture(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source drift", result.stderr)

    def test_reject_missing_totient_cancellation_factor(self):
        with tempfile.TemporaryDirectory(prefix="height-audit67-") as temp:
            _, package = self.clone_fixture(temp)
            path = package / "verify.py"
            original = path.read_text()
            needle = "3 * n * r * (ell + 1) ** 2 // 2"
            self.assertEqual(original.count(needle), 1)
            path.write_text(original.replace(needle, "3 * n * (ell + 1) ** 2 // 2"))
            result = self.run_fixture(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("totient cancellation", result.stderr)

    def test_refuse_silent_expected_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="height-audit67-") as temp:
            _, package = self.clone_fixture(temp)
            target = package / "EXPECTED.json"
            original = target.read_bytes()
            result = self.run_fixture(package, "--write", str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("proposed receipt", result.stderr)
            self.assertEqual(original, target.read_bytes())


if __name__ == "__main__":
    unittest.main()
