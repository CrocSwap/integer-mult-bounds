"""Failure controls for the direct corollary's bounded executable checks."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "scripts/verify_nov24_direct.py"
CHECKS = runpy.run_path(str(DRIVER))
CLAIM = json.loads((ROOT / "certificates/nov24-direct/CLAIM.json").read_bytes())


class ConstructionParameters(unittest.TestCase):
    def check(self, **changes):
        parameters = deepcopy(CLAIM["construction"])
        parameters.update(changes)
        return CHECKS["check_construction"](parameters, Fraction(4999, 10000))

    def test_published_parameters(self):
        self.check()

    def test_composite_prime_with_positive_scalar_slack_is_rejected(self):
        # 240009 is divisible by three, despite meeting the exponent inequality.
        prime = 240009
        margin = Fraction(40001, 80000) - Fraction(1, 2) - Fraction(3 * prime - 1, prime**2)
        self.assertGreater(margin, 0)
        with self.assertRaisesRegex(ValueError, "Odd interchange label prime"):
            self.check(interchange_label_prime=prime, interchange_label_margin=str(margin))

    def test_candidate_index_must_match_exponent(self):
        with self.assertRaisesRegex(ValueError, "Scheduler exponent"):
            self.check(scheduler_index=19999)

    def test_zero_recurrence_slack_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Strict construction exponent ordering"):
            self.check(interchange_intermediate_exponent=CLAIM["construction"]["fourier_log_exponent"])

    def test_nonpositive_prime_margin_is_rejected(self):
        prime = 7
        margin = Fraction(40001, 80000) - Fraction(1, 2) - Fraction(3 * prime - 1, prime**2)
        with self.assertRaisesRegex(ValueError, "Interchange label exponent margin"):
            self.check(interchange_label_prime=prime, interchange_label_margin=str(margin))

    def test_checks_cannot_be_relabelled_as_an_executed_multiplier(self):
        with self.assertRaisesRegex(ValueError, "do not materialize or execute"):
            self.check(multiplier_executed=True)


class CorollaryReplay(unittest.TestCase):
    def run_driver(self, root=ROOT, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(root / "scripts/verify_nov24_direct.py"),
                               *args], capture_output=True, text=True, cwd=root)

    def test_larger_fixed_witness_is_supported(self):
        result = self.run_driver(ROOT, "--kappa", "499999/1000000")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"kappa": "499999/1000000"', result.stdout)
        self.assertIn("PASS_NOV24_CONSTRUCTION_PARAMETERS", result.stdout)

    def test_strict_interval_controls(self):
        for witness in ("-1/10", "0", "1/2", "5001/10000"):
            with self.subTest(witness=witness):
                result = self.run_driver(ROOT, "--kappa", witness)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("PASS_NOV24_DIRECT_COROLLARY", result.stdout)

    def test_changed_upstream_proof_entry_fails(self):
        record = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
        manifest = json.loads((ROOT / record["source_manifest"]).read_bytes())
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name in {*manifest["files"], record["source_manifest"], "certificates/selected-result.json"}:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dest)
            proof = root / "research/nov24-direct-multiplication/source/Main.lean"
            proof.write_bytes(proof.read_bytes() + b"\n")
            result = self.run_driver(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("PASS_NOV24_DIRECT_COROLLARY", result.stdout)


if __name__ == "__main__":
    unittest.main()
