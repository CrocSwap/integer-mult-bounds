"""Regression and failure controls for the self-contained complex bank ladder package.

The package vendors every input it reads by digest, so these checks need no network and no
contributor branch: they rebuild the whole ladder, re-derive both paid moments, the 47-constraint
assembly and the rungs' measurements, and then run the export harness.  They shell out rather
than import, because the package's modules deliberately shadow research module names
(`verify`, `suppliers`, `schedule`) -- which is exactly why the repository runs each test module
in its own interpreter.  The pin gate is the one exception: it is exercised in-process, so that
its comparison cannot be vacuous.
"""
import importlib
import json
import subprocess
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "complex-bank-run3"

# The reviewed result published in the repository root README (Dugongue's #186).  The rung's claim
# is compared against it here as well as inside the package's own certificate.
REVIEWED_KAPPA = Q(330942774629799, 5 * 10 ** 17)
RUNG_KAPPA = Q(1819302815717, 25 * 10 ** 14)
# The bit-side rung above it: #219's retained bit row banked a second time, which lands the
# assembly on #233's row's complex branch instead of on the bit leaf.
BIT_RUNG_KAPPA = Q(416977294469409, 5 * 10 ** 17)


def package_command(*argv):
    return subprocess.run([sys.executable, "-B", *argv], cwd=PACKAGE,
                          capture_output=True, text=True)


class ComplexBankRun3(unittest.TestCase):
    """The ladder, its three contracts and both rungs' measurements, rebuilt offline."""

    def test_verify_rebuilds_every_pinned_input(self):
        done = package_command("verify.py")
        self.assertEqual(done.returncode, 0, done.stdout[-3000:] + done.stderr[-3000:])
        self.assertIn("certificate.json matches a fresh rebuild", done.stdout)

    def test_all_three_export_contracts_are_executable(self):
        for contract in (None, "export-contract-bit.json", "export-contract-rank3.json"):
            argv = ["importer66.py"]
            if contract:
                argv += ["--contract", contract]
            done = package_command(*argv, "--self-test")
            self.assertEqual(done.returncode, 0, contract)
            self.assertIn("self-test: 13 checks, 0 failed", done.stdout)

    def test_the_gate_refuses_the_rung_while_its_bodies_are_absent(self):
        done = package_command("importer66.py", "--contract", "export-contract-rank3.json")
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("REFUSED: 10 of 10 required bodies are absent", done.stdout)
        partial = package_command("importer66.py", "--contract", "export-contract-rank3.json",
                                  "--partial")
        self.assertEqual(partial.returncode, 4, partial.stdout)
        self.assertIn("PARTIAL", partial.stdout)

    def test_the_rank3_rung_prices_above_the_reviewed_result(self):
        contract = json.loads((PACKAGE / "export-contract-rank3.json").read_text())
        point = contract["point"]
        self.assertEqual(Q(point["kappa"]), RUNG_KAPPA)
        self.assertEqual(point["binding"], "bit")
        self.assertTrue(Q(point["kappa"]) > REVIEWED_KAPPA, "the rung must beat the reviewed result")
        self.assertEqual(Q(contract["our_side"]["allowed_to_move"]["published_top_kappa"]),
                         Q(711599961413937, 10 ** 18))
        geometry = contract["rung"]["geometry"]
        self.assertEqual((geometry["banks"], geometry["blocks_per_bank"],
                          geometry["padding_registers"], geometry["banks_per_copy"]),
                         (4086, 22, 0, 1362))

    def test_the_bit_rung_lands_on_the_complex_branch(self):
        rung = json.loads((PACKAGE / "bitrung.json").read_text())
        point, leader = rung["point"], rung["leader"]
        self.assertEqual(Q(point["kappa"]), BIT_RUNG_KAPPA)
        self.assertEqual(point["binding"], "complex")
        self.assertTrue(Q(point["kappa"]) > RUNG_KAPPA, "the rung must beat the rank-3 rung")
        self.assertGreater(float(Q(point["gain_vs_the_rank3_rung"])), 0.14)
        self.assertTrue(Q(leader["leaf"]) > Q(point["complex_branch"]), "the leaf clears the branch")
        self.assertEqual(leader["ranks"], [7, 8, 20])
        self.assertEqual((rung["screen"]["rungs_priced"],
                          rung["screen"]["plateau"]["rungs_at_the_cap"]), (377, 108))
        self.assertEqual(len(rung["absorbable"]), 13)

    def test_the_rank4_rung_is_measured_negative(self):
        rung = json.loads((PACKAGE / "rank4-rung.json").read_text())
        schedule = rung["rung"]["padded_schedule"]
        self.assertFalse(schedule["saturated"])
        self.assertEqual((schedule["slack_slots"], schedule["slack_registers"]), (9, 36))
        self.assertFalse(rung["point"]["kappa_moved"])
        self.assertEqual(Q(rung["point"]["rank4_priced"]["kappa"]), RUNG_KAPPA)
        self.assertEqual(rung["head_dependence"]["heads_carrying_the_volume_criterion"],
                         ["109a857"])


class ComplexBankRun3PinGate(unittest.TestCase):
    """The digest gate is what makes every other claim reproducible, so it must fail closed."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PACKAGE))
        cls.verify = importlib.import_module("verify")

    def test_the_gate_accepts_the_vendored_bytes(self):
        self.assertEqual(self.verify.check_manifest(), self.verify.read_manifest())

    def test_a_recorded_digest_that_disagrees_is_rejected(self):
        recorded = dict(self.verify.read_manifest())
        recorded[sorted(recorded)[0]] = "0" * 64
        with patch.object(self.verify, "read_manifest", lambda: recorded):
            with self.assertRaises(AssertionError):
                self.verify.check_manifest()

    def test_a_missing_pinned_entry_is_rejected(self):
        recorded = dict(self.verify.read_manifest())
        recorded.pop(sorted(recorded)[0])
        with patch.object(self.verify, "read_manifest", lambda: recorded):
            with self.assertRaises(AssertionError):
                self.verify.check_manifest()

    def test_a_changed_byte_on_disk_is_rejected(self):
        recorded = self.verify.read_manifest()
        victim = Path(sorted(recorded)[0]).name
        digest = self.verify.pins.digest

        def corrupted(path):
            return "0" * 64 if Path(path).name == victim else digest(path)

        with patch.object(self.verify.pins, "digest", corrupted):
            with self.assertRaises(AssertionError):
                self.verify.check_manifest()


if __name__ == "__main__":
    unittest.main()
