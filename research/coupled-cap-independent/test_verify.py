#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral and semantic rejection controls for the independent audit."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from array import array
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arithmetic import (
    catalogue,
    check_dual,
    check_primal,
    child_intervals,
    moment,
    power_interval,
)
from geometry import journal_edits, place, summarize
from verify import INVENTORY, LOCAL, PACKAGE, ROOT, check_providers, read, unique_object


class ArithmeticTests(unittest.TestCase):
    def test_square_root_enclosures_against_exact_powers(self):
        for x in (Fraction(73), Fraction(73, 48), Fraction(1)):
            low, high = power_interval(x, Fraction(1, 128))
            self.assertLessEqual(low**128, x)
            self.assertGreaterEqual(high**128, x)
            self.assertLess(high - low, Fraction(1, 10**40))
            self.assertEqual(power_interval(x, Fraction(0)), (1, 1))

    def test_nondyadic_exponent_monotonicity(self):
        lo, hi = power_interval(Fraction(73, 3), Fraction(1, 1000))
        self.assertLess(lo, hi)
        # Raising to the exact denominator independently checks both directions.
        self.assertLessEqual(lo**1000, Fraction(73, 3))
        self.assertGreaterEqual(hi**1000, Fraction(73, 3))

    def test_power_and_moment_domains(self):
        for x, b in [(Fraction(1, 2), Fraction(0)), (Fraction(74), Fraction(0)),
                     (Fraction(2), Fraction(-1)), (Fraction(2), Fraction(1))]:
            with self.assertRaisesRegex(ValueError, "power domain"):
                power_interval(x, b)
        with self.assertRaisesRegex(ValueError, "moment child"):
            moment({49: 1}, Fraction(1, 1000), 1)

    def test_complete_pattern_domain(self):
        patterns = catalogue()
        self.assertEqual(len(patterns), 2551)
        self.assertEqual(len(set(patterns)), 2551)
        self.assertIn((48, (12, 0, 0, 0, 0, 0), 0), patterns)
        self.assertIn((8, (0, 0, 0, 0, 0, 0), 8), patterns)

    def test_wrong_inventory_and_primal_amount_reject(self):
        cert = read(PACKAGE / "vendor/CAP.json")
        bad = copy.deepcopy(cert)
        bad["basis_patterns"][0]["count_per_replica"] = "671"
        with self.assertRaisesRegex(ValueError, "primal conservation"):
            check_primal(bad, INVENTORY, LOCAL)
        bad = copy.deepcopy(cert)
        bad["inventory_per_call"]["6"] += 1
        with self.assertRaisesRegex(ValueError, "inventory binding"):
            check_primal(bad, INVENTORY, LOCAL)

    def test_dual_sign_control(self):
        cert = read(PACKAGE / "vendor/CAP.json")
        patterns, basis, _, rhs = check_primal(cert, INVENTORY, LOCAL)
        intervals = child_intervals(Fraction(cert["cap_lower"]),
                                    Fraction(cert["cap_upper"]))
        tight, margin = check_dual(patterns, basis, rhs, intervals)
        self.assertEqual(len(tight), 12)
        self.assertGreater(margin, 0)
        # Exact linear costs make all feasible patterns dual-tight, contradicting
        # the claimed strict partition. This detects a dropped nonlinear charge.
        linear = {r: (Fraction(r), Fraction(r)) for r in range(1, 49)}
        with self.assertRaisesRegex(ValueError, "reduced cost"):
            check_dual(patterns, basis, rhs, linear)


class GeometryTests(unittest.TestCase):
    def fixture(self):
        windows = [[(16, -1, 2)] * 18]
        return windows, {0: 0}, array("Q", [0]) * 2016, array("I", [0]) * 2016

    def test_place_positive_and_prefix(self):
        windows, families, occupied, signatures = self.fixture()
        place([0, 0, 0, 0, 0, 0], 4, 0, windows, families,
              occupied, signatures, set())
        place([1, 0, 0, 0, 0, 4], 5, 1, windows, families,
              occupied, signatures, set())
        idle, _ = summarize(windows, occupied, signatures)
        self.assertEqual(idle[7], 1)
        self.assertEqual(idle[16], 2015)

    def test_capacity_window_family_and_overlap_controls(self):
        windows, families, occupied, signatures = self.fixture()
        for row, width, time, reason in [
                ([0, 0, 0, 0, 0, 13], 4, 0, "capacity"),
                ([3, 0, 0, 0, 0, 0], 4, 3, "source availability"),
                ([0, 0, 1, 0, 0, 0], 4, 0, "bounds")]:
            with self.assertRaisesRegex(ValueError, reason):
                place(row, width, time, windows, families,
                      occupied, signatures, set())
        place([0, 0, 0, 0, 0, 0], 4, 0, windows, families,
              occupied, signatures, set())
        with self.assertRaisesRegex(ValueError, "family exclusion"):
            place([0, 1, 0, 0, 0, 4], 4, 0, windows, families,
                  occupied, signatures, {0})
        with self.assertRaisesRegex(ValueError, "disjoint bin"):
            place([1, 0, 0, 0, 0, 3], 4, 1, windows, families,
                  occupied, signatures, set())

    def test_unpaid_hole_rejects(self):
        windows, families, occupied, signatures = self.fixture()
        place([0, 0, 0, 0, 0, 1], 4, 0, windows, families,
              occupied, signatures, set())
        with self.assertRaisesRegex(ValueError, "compact paid prefix"):
            summarize(windows, occupied, signatures)

    def test_journal_controls(self):
        base = read(PACKAGE / "vendor/FILL.json.gz")["rows"]
        journal = read(PACKAGE / "vendor/EXCHANGE.json")
        self.assertEqual(len(journal_edits(base, journal)), 145)
        for field, reason in [("preimage", "preimage"), ("duplicate", "unique"),
                              ("identity", "fixed call"), ("missing", "complete")]:
            bad = copy.deepcopy(journal)
            if field == "preimage":
                bad["edits"][0][1][0] += 1
            elif field == "duplicate":
                bad["edits"][1] = copy.deepcopy(bad["edits"][0])
            elif field == "identity":
                bad["edits"][0][2][1] += 1
            else:
                bad["edits"].pop()
            with self.assertRaisesRegex(ValueError, reason):
                journal_edits(base, bad)

    def test_inherited_profile_binding(self):
        providers = read(PACKAGE / "vendor/PROVIDERS.json")
        check_providers(providers)
        bad = copy.deepcopy(providers)
        bad["extra"]["widths"][0] = 8
        with self.assertRaisesRegex(ValueError, "width inventory"):
            check_providers(bad)
        bad = copy.deepcopy(providers)
        bad["extra"]["actual_paid_profile"]["1"] -= 1
        with self.assertRaisesRegex(ValueError, "paid profile"):
            check_providers(bad)


class BoundaryTests(unittest.TestCase):
    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            json.loads('{"a":1,"a":2}', object_pairs_hook=unique_object)

    def test_git_free_readonly_export_and_corrupt_input(self):
        with tempfile.TemporaryDirectory(prefix="independent-cap-export-") as directory:
            root = Path(directory)
            package = root / PACKAGE.relative_to(ROOT)
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for row in read(PACKAGE / "SOURCES.json")["files"]:
                if row["usage"] == "input":
                    dest = root / row["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / row["path"], dest)
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            command = [sys.executable, "-I", "-O", "-Werror", "-B",
                       str(package / "verify.py")]
            positive = subprocess.run(command, capture_output=True, text=True,
                                      timeout=120, check=False)
            self.assertEqual(positive.returncode, 0, positive.stderr)
            self.assertIn("PASS_INDEPENDENT_COUPLED_CAP", positive.stdout)
            target = package / "vendor/EXCHANGE.json"
            target.chmod(0o644)
            target.write_bytes(target.read_bytes() + b" ")
            negative = subprocess.run(command, capture_output=True, text=True,
                                      timeout=20, check=False)
            self.assertNotEqual(negative.returncode, 0)
            self.assertIn("source bytes:", negative.stderr)

    def test_actual_optimized_cli(self):
        result = subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(PACKAGE / "verify.py")],
            capture_output=True, text=True, timeout=120, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_INDEPENDENT_COUPLED_CAP roles=2717280", result.stdout)


if __name__ == "__main__":
    unittest.main()
