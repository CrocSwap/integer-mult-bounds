#!/usr/bin/env python3
"""Independent small-matrix and adversarial checks for this scoped audit."""

import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("cover_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def brute_matrices(n, check_cross_terms=True):
    """Enumerate all 2^(n*n) matrices, independently of prefix pruning."""
    count = 0
    for columns in itertools.product(range(1 << n), repeat=n):
        gram = [[sum(((u >> k) & 1) * ((v >> k) & 1) for k in range(n)) % 2
                 for v in columns] for u in columns]
        pairs = itertools.product(range(n), repeat=2) if check_cross_terms else ((i, i) for i in range(n))
        if all(gram[i][j] == int(i == j) for i, j in pairs):
            count += 1
            if check_cross_terms:
                image = 0
                for v in columns:
                    image ^= v
                if image != (1 << n) - 1:
                    raise ValueError("isometry moved characteristic vector")
    return count


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.run(ROOT)
        _, cls.invoice, cls.owners = audit.load_sources(ROOT)

    def test_full_matrix_enumeration(self):
        for n in range(1, 5):
            with self.subTest(n=n):
                self.assertEqual(brute_matrices(n), self.result["enumeration"][n-1]["complete_bases"])

    def test_norms_alone_are_not_isometry(self):
        # Unit columns can be duplicated and need not be pairwise orthogonal.
        self.assertEqual(brute_matrices(3, check_cross_terms=False), 64)
        self.assertEqual(brute_matrices(3), 6)

    def test_odd_characteristic_vector_cannot_start_a_basis(self):
        for row in self.result["enumeration"]:
            if row["dimension"] in (3, 5, 7):
                self.assertEqual(row["characteristic_vector_completions"], 0)
                self.assertEqual(row["first_column_completion_histogram"]["0"], 1)

    def test_actual_group_order_mutation_is_detected(self):
        original = audit.symplectic_order
        # Drop a factor 2 in every positive-dimensional group computation.
        with mock.patch.object(audit, "symplectic_order", side_effect=lambda n: original(n) // (2 if n else 1)):
            with self.assertRaisesRegex(ValueError, "enumeration/order disagreement"):
                audit.run(ROOT)

    def test_actual_row_cost_mutation_is_detected(self):
        original = audit.invoice_metrics

        def omit_prefix_reserve(*args):
            result = original(*args)
            result["finite"]["physical_row_coefficient"] -= 1024
            return result

        with mock.patch.object(audit, "invoice_metrics", side_effect=omit_prefix_reserve):
            with self.assertRaisesRegex(ValueError, "finite receipt mismatch"):
                audit.run(ROOT)

    def test_strict_row_boundary_and_gl_substitution(self):
        g = audit.dot_group_order(73)
        for t, row, accepted in ((1846, 20159, True), (1847, 20161, False), (1848, 20163, False)):
            measured = audit.invoice_metrics(g << t, self.invoice, self.owners)
            self.assertEqual(measured["finite"]["physical_row_coefficient"], row)
            self.assertEqual(all(measured["strict_checks"].values()), accepted)
        self.assertEqual(self.result["negative_controls"]["use_all_invertible_matrices"]["failed_guards"], ["row"])

    def test_invalid_dimensions_and_orders(self):
        for n in (True, -1, 0, 1.5):
            with self.assertRaises(ValueError):
                audit.dot_group_order(n)
        for n in (True, -2, 1, 2.5):
            with self.assertRaises(ValueError):
                audit.symplectic_order(n)
        for n in (0, 8, True):
            with self.assertRaises(ValueError):
                audit.enumerate_bases(n)
        for g in (0, -1, True):
            with self.assertRaises(ValueError):
                audit.invoice_metrics(g, self.invoice, self.owners)

    def test_relocation_optimized_execution_and_corruption(self):
        pins = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="orthogonal audit with spaces ") as tmp:
            root = Path(tmp)
            target = root / "research" / HERE.name
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            for name in pins["sha256"]:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            command = [sys.executable, "-I", "-B", "-O", str(target / "verify.py")]
            passed = subprocess.run(command, capture_output=True, text=True, cwd=tmp, timeout=30)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn("PASS_ORTHOGONAL_COVER_INVOICE_AUDIT", passed.stdout)
            for source in (audit.INVOICE, audit.CODE + "invoice_allcold.py"):
                path = root / source
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                failed = subprocess.run(command, capture_output=True, text=True, cwd=tmp, timeout=30)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn("source hash mismatch", failed.stderr)
                path.write_bytes(original)
            certificate = target / "CERTIFICATE.json"
            changed = json.loads(certificate.read_text())
            changed["dimension_73"]["finite"]["router_bits"] -= 1
            certificate.write_text(json.dumps(changed))
            failed = subprocess.run(command, capture_output=True, text=True, cwd=tmp, timeout=30)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("certificate mismatch", failed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
