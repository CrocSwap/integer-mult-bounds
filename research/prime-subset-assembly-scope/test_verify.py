"""Focused failure controls for the historical assembly-scope reconciliation.

Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0.
This suite verifies the new receipt; it does not replay a supplier or bridge.
"""
from copy import deepcopy
from contextlib import contextmanager
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("prime_subset_scope_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


@contextmanager
def scratch_directory():
    # Keep writes inside the package in restricted Windows environments, and
    # verify the resolved cleanup target before TemporaryDirectory removes it.
    with tempfile.TemporaryDirectory(prefix=".review-test-", dir=HERE) as directory:
        path = Path(directory).resolve()
        if path.parent != HERE.resolve():
            raise RuntimeError("temporary directory escaped package")
        yield path


class ScopeReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = verify.read_json(verify.ROOT / verify.CERTIFICATE)
        cls.manifest = verify.read_json(HERE / "SOURCES.json")
        cls.result = verify.calculate()

    def test_log_series_anchors_and_domain(self):
        self.assertEqual(verify.log_unit_bounds(Q(1)), (Q(0), Q(0)))
        self.assertEqual(verify.log_unit_bounds(Q(2), 1), (Q(1, 2), Q(3, 4)))
        self.assertEqual(verify.log_unit_bounds(Q(2), 2), (Q(5, 8), Q(17, 24)))
        # Known 25-decimal brackets, independent of either implemented series.
        for n, low, high in (
            (2, "0.6931471805599453094172321", "0.6931471805599453094172322"),
            (3, "1.0986122886681096913952452", "1.0986122886681096913952453"),
        ):
            with self.subTest(n=n):
                lo, hi = verify.log_integer_bounds(n)
                self.assertLess(Q(low), lo)
                self.assertLess(lo, hi)
                self.assertLess(hi, Q(high))
        for value in (Q(1, 2), Q(3), 2, 2.0, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verify.log_unit_bounds(value)
        for terms in (0, -1, True, 1.0):
            with self.subTest(terms=terms), self.assertRaises(ValueError):
                verify.log_unit_bounds(Q(2), terms)
        for n in (0, 1, True, 2.0, Q(2)):
            with self.subTest(integer_domain=n), self.assertRaises(ValueError):
                verify.log_integer_bounds(n)

    def test_coverage_and_receipt(self):
        self.assertEqual(verify.prime_powers(32),
                         [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 29, 31, 32])
        self.assertEqual(self.result["finite_case_count"], 626)
        self.assertEqual(self.result["positive_case_count"], 301)
        self.assertEqual(sum(self.result["finite_cases_by_q"].values()), 626)
        verify.same(self.result, verify.read_json(HERE / "RESULT.json"), "receipt replay")

    def test_conversion_bracket_and_reduced_control(self):
        winner = self.result["winner"]
        self.assertEqual((winner["q"], winner["h"]), (3, 29))
        self.assertEqual(Q(winner["eta_upper"]), Q(237, 599335286))
        a_lo, a_hi = (Q(winner["bit_envelope"][key]) for key in ("lower", "upper"))
        b_lo, b_hi = (Q(winner["balanced_envelope"][key]) for key in ("lower", "upper"))
        self.assertLess(a_hi / 5, Q(1, 2**26))
        self.assertLess(Q(1, 2**25), b_lo)
        self.assertLess(b_hi, Q(1, 2**24))
        exact_enclosure = verify.family(3, 29)
        self.assertLess(b_lo, exact_enclosure["lower"] / (1 + exact_enclosure["lower"]))
        self.assertLess(exact_enclosure["upper"] / (1 + exact_enclosure["upper"]), b_hi)
        control = self.result["reduced_diagnostic"]
        a, epsilon, gain, target, h = (Q(control[key]) for key in
                                      ("a", "epsilon", "gain", "target", "backoff"))
        self.assertLess(a, Q(control["ideal_rate_lower"]))
        self.assertLess(a / 5, target)
        self.assertLess(target, gain)
        self.assertLess(target, 1 - epsilon)
        self.assertEqual(1 - epsilon - gain, h)

    def test_tail_gap_is_real_and_family_tail_is_sufficient(self):
        lo65, hi65 = verify.log_integer_bounds(65**3)
        generic_lower = Q(1, 4 * 65**3 - 1) / hi65
        # Even the lower enclosure, after balanced conversion, exceeds 2^-24.
        self.assertGreater(generic_lower / (1 + generic_lower), Q(1, 2**24))
        tailored_upper = Q(1, 14 * 65**3 - 1) / lo65
        best_lower = Q(self.result["winner"]["bit_envelope"]["lower"])
        self.assertLess(tailored_upper, best_lower)
        self.assertLessEqual(tailored_upper, Q(self.result["tail"]["bound_at_65"]))
        # An adjacent exact check supports, but does not replace, the analytic
        # proof that both positive denominator factors increase for all h>=65.
        lo66, hi66 = verify.log_integer_bounds(66**3)
        self.assertLess(Q(1, 14 * 66**3 - 1) / lo66,
                        Q(1, 14 * 65**3 - 1) / hi65)

    def test_corrupted_archived_coverage_and_arithmetic_rejected(self):
        first_positive = next(i for i, row in enumerate(self.certificate["envelope"]["cases"])
                              if row["positive_deficit"])
        mutations = {
            "missing": lambda x: x["envelope"]["cases"].pop(),
            "reordered": lambda x: x["envelope"]["cases"].reverse(),
            "boolean_flag": lambda x: x["envelope"]["cases"][0].__setitem__("positive_deficit", 0),
            "eta": lambda x: x["envelope"]["cases"][first_positive].__setitem__("eta_upper", "1/100"),
            "side_roles": lambda x: x["envelope"]["cases"][first_positive].__setitem__("side_role_floor", 1),
            "log_envelope": lambda x: x["envelope"]["cases"][first_positive].__setitem__("bit_saving_upper", "1/100"),
        }
        for label, mutate in mutations.items():
            with self.subTest(mutation=label):
                changed = deepcopy(self.certificate)
                mutate(changed)
                with self.assertRaises(ValueError):
                    verify.reconcile(changed)

    def test_source_inventory_omission_and_extension_rejected(self):
        for action in ("omit", "extend"):
            changed = deepcopy(self.manifest)
            if action == "omit":
                changed["files"].pop(verify.SOURCE_PATHS[0])
            else:
                changed["files"]["unexpected.py"] = {"sha256": "0" * 64, "git_blob": "0" * 40}
            with self.subTest(action=action), self.assertRaisesRegex(ValueError, "source inventory"):
                verify.check_sources(manifest=changed)

    def test_missing_and_drifted_source_bytes_rejected(self):
        # Only the first file is needed: its absence/drift must stop the check.
        with scratch_directory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "missing source"):
                verify.check_sources(root=root, manifest=self.manifest)
            target = root / verify.SOURCE_PATHS[0]
            target.parent.mkdir(parents=True)
            target.write_bytes((verify.ROOT / verify.SOURCE_PATHS[0]).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source digest"):
                verify.check_sources(root=root, manifest=self.manifest)

    def test_git_blob_pin_is_checked_in_addition_to_sha256(self):
        changed = deepcopy(self.manifest)
        changed["files"][verify.SOURCE_PATHS[0]]["git_blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Git blob differs"):
            verify.check_sources(manifest=changed)

    def test_historical_dependency_omission_rejected(self):
        changed = deepcopy(self.certificate)
        changed["source_sha256"].pop(next(iter(changed["source_sha256"])))
        with patch.object(verify, "check_sources", return_value=self.manifest), \
             patch.object(verify, "read_json", return_value=changed):
            with self.assertRaisesRegex(ValueError, "historical pin set"):
                verify.calculate()

    def test_receipt_type_corruption_rejected_by_cli_check(self):
        changed = deepcopy(self.result)
        changed["conversions"]["historical_excludes_2_to_minus26"] = 1
        with patch.object(verify, "calculate", return_value=self.result), \
             patch.object(verify, "read_json", return_value=changed), \
             patch.object(sys, "argv", [str(HERE / "verify.py")]):
            with self.assertRaisesRegex(ValueError, "committed receipt"):
                verify.main()

    def test_duplicate_json_keys_rejected(self):
        with scratch_directory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"tail": {"factor": 14, "factor": 4}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                verify.read_json(path)

    def test_failed_calculation_preserves_output_and_creates_nothing(self):
        with scratch_directory() as directory:
            existing = Path(directory) / "existing.json"
            absent = Path(directory) / "absent.json"
            existing.write_bytes(b"review sentinel\n")
            for target in (existing, absent):
                with self.subTest(target=target.name), \
                     patch.object(verify, "calculate", side_effect=ValueError("source drift")), \
                     patch.object(sys, "argv", [str(HERE / "verify.py"), "--output", str(target)]):
                    with self.assertRaisesRegex(ValueError, "source drift"):
                        verify.main()
            self.assertEqual(existing.read_bytes(), b"review sentinel\n")
            self.assertFalse(absent.exists())

    def test_existing_output_is_never_overwritten(self):
        with scratch_directory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_bytes(b"review sentinel\n")
            with patch.object(verify, "calculate", return_value=self.result), \
                 patch.object(sys, "argv", [str(HERE / "verify.py"), "--output", str(path)]):
                with self.assertRaises(FileExistsError):
                    verify.main()
            self.assertEqual(path.read_bytes(), b"review sentinel\n")

    def test_optimized_cli_positive_and_corrupt_receipt(self):
        command = [sys.executable, "-B", "-O", str(HERE / "verify.py")]
        checked = subprocess.run(command, capture_output=True, text=True, timeout=120)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertIn("PASS_PRIME_SUBSET_ASSEMBLY_SCOPE_NO_NEW_KAPPA", checked.stdout)
        # Copy just the verifier: its original ROOT remains the pinned repo,
        # while HERE points to a corrupt temporary receipt and original pins.
        with scratch_directory() as directory:
            copied = Path(directory)
            shutil.copy2(HERE / "verify.py", copied / "verify.py")
            shutil.copy2(HERE / "SOURCES.json", copied / "SOURCES.json")
            changed = deepcopy(self.result)
            changed["tail"]["below_finite_winner"] = 1
            (copied / "RESULT.json").write_text(json.dumps(changed), encoding="utf-8")
            script = (
                "import importlib.util; from pathlib import Path; "
                f"s=importlib.util.spec_from_file_location('scoped',{str(copied / 'verify.py')!r}); "
                "v=importlib.util.module_from_spec(s); s.loader.exec_module(v); "
                f"root=Path({str(verify.ROOT)!r}); "
                "original=v.calculate; v.calculate=lambda: original(root=root); v.main()"
            )
            rejected = subprocess.run([sys.executable, "-B", "-O", "-c", script],
                                      capture_output=True, text=True, timeout=120)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("committed receipt differs", rejected.stderr)
            self.assertNotIn("PASS_PRIME_SUBSET", rejected.stdout)


if __name__ == "__main__":
    unittest.main()
