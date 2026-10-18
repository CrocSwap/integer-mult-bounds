"""Tamper/mutation checks for proof-relevant failures, not a second full replay."""

from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import exact
from oracles import Gaussian as G, gaussian_norm2
import verify


class PackageTests(unittest.TestCase):
    def test_pinned_source_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(verify.ROOT / "vendor", root / "vendor")
            shutil.copy2(verify.ROOT / "SOURCES.json", root / "SOURCES.json")
            self.assertEqual(verify.source_check(root), 8)
            source = root / "vendor/pr803-PROOF.md"
            source.write_bytes(source.read_bytes() + b"changed\n")
            with self.assertRaisesRegex(AssertionError, "source SHA256"):
                verify.source_check(root)

    def test_git_blob_pin_is_independently_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(verify.ROOT / "vendor", root / "vendor")
            sources = json.loads((verify.ROOT / "SOURCES.json").read_text())
            sources["files"][0]["git_blob"] = "0" * 40
            (root / "SOURCES.json").write_text(json.dumps(sources))
            with self.assertRaisesRegex(AssertionError, "source git blob"):
                verify.source_check(root)

    def test_changed_witness_receipt_is_rejected(self):
        result = json.loads((verify.ROOT / "EXPECTED.json").read_text())
        bad = deepcopy(result)
        bad["primary_witness"]["inverse_norm_floor"] -= 1
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "EXPECTED.json"
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(AssertionError, "receipt mismatch"):
                verify.check_receipt(result, path)

    def test_changed_domain_digest_is_rejected(self):
        result = json.loads((verify.ROOT / "EXPECTED.json").read_text())
        result["domain_sha256"] = "0" * 64
        with self.assertRaisesRegex(AssertionError, "receipt mismatch"):
            verify.check_receipt(result, verify.ROOT / "EXPECTED.json")

    def test_dropping_power_factor_is_detected_by_dense_oracle(self):
        def mutant(permutation, weights):
            result = exact.power_certificate(permutation, weights)
            if result["K2"] is not None:
                result["K2"] = F(1)
            return result
        with patch.object(verify, "power_certificate", mutant):
            with self.assertRaisesRegex(AssertionError, "dense power supremum"):
                verify.power_oracle()

    def test_edge_only_factor_is_detected(self):
        def mutant(permutation, weights):
            result = exact.power_certificate(permutation, weights)
            if result["K2"] is not None:
                result["K2"] = max(F(re) ** 2 + F(im) ** 2 for re, im in weights)
            return result
        with patch.object(verify, "power_certificate", mutant):
            with self.assertRaisesRegex(AssertionError, "max_edge_is_not_max_path"):
                verify.admission_controls()

    def test_wrong_weight_order_is_detected_by_dense_inverse(self):
        def mutant(a, weights, rhs):
            return exact.cyclic_solve(a, weights[1:] + weights[:1], rhs)
        with patch.object(verify, "cyclic_solve", mutant):
            with self.assertRaisesRegex(AssertionError, "affine vs dense inverse"):
                verify.small_resolvents({"eta_exponents": [4], "half_lengths": [2],
                                         "delta_multipliers": ["1/2"]})

    def test_optimistic_perturbation_guard_is_detected(self):
        def mutant(coefficients, eta, bound):
            return F(0), F(bound)
        with patch.object(verify, "perturbation_bound", mutant):
            with self.assertRaisesRegex(AssertionError, "polynomial error bound"):
                verify.polynomial_guards({"roots": ["3/2"], "degree_range": [1, 1],
                                          "eta": ["1/64"], "dimension": 4})

    def test_optimized_python_keeps_failure_detection(self):
        code = ("import verify; verify.admission_controls(); "
                "verify.require(False, 'deliberate failure')")
        result = subprocess.run([sys.executable, "-B", "-O", "-c", code],
                                cwd=verify.ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AssertionError: deliberate failure", result.stderr)

    def test_missing_cycle_denominator_is_detected(self):
        def mutant(a, length, lower, upper):
            bound, weights = exact.sharp_inverse_bound(a, length, lower, upper)
            return bound * (1 - a ** -length), weights
        with patch.object(verify, "sharp_inverse_bound", mutant):
            with self.assertRaisesRegex(AssertionError, "sharp bound attained"):
                verify.sharp_inverses({"lengths": [3], "eta": ["1/16"],
                                      "delta_multipliers": ["1/2"]})

    def test_norm_oracle_rejects_irrational_ratios(self):
        with self.assertRaisesRegex(ValueError, "irrational magnitude ratios"):
            gaussian_norm2([[G(1), G(1, 1)], [G(0), G(1)]])


if __name__ == "__main__":
    unittest.main()
