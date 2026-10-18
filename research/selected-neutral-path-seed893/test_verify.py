#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Positive and negative controls for the selected neutral-path witness."""
import importlib.util
from fractions import Fraction
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("neutral_path_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)


class NeutralPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify.check_pins()
        cls.result = verify.build()
        cls.one, cls.ceiling, cls.fixture = verify.load_fixture()
        cls.base = cls.fixture["model"]
        cls.first = cls.one.relocate(cls.base, verify.NEUTRAL_INDEX, verify.NEUTRAL_DEST)
        cls.final = cls.one.relocate(cls.first, verify.STRICT_INDEX, verify.STRICT_DEST)

    def test_neutral_move_preserves_full_idle_histogram(self):
        self.assertEqual(verify.idle_hist(self.base, self.one),
                         verify.idle_hist(self.first, self.one))
        self.assertEqual(self.base.bins[verify.NEUTRAL_SOURCE].remainder, 0)
        self.assertEqual(self.base.bins[verify.NEUTRAL_DEST].remainder, 7)
        self.assertEqual(self.first.bins[verify.NEUTRAL_SOURCE].remainder, 7)
        self.assertEqual(self.first.bins[verify.NEUTRAL_DEST].remainder, 0)

    def test_strict_move_fails_before_but_fits_after_neutral_move(self):
        role = self.base.roles[verify.STRICT_INDEX]
        self.assertIsNone(self.base.rejection(role, verify.STRICT_DEST))
        with self.assertRaisesRegex(ValueError, "destination capacity"):
            self.one.relocate(self.base, verify.STRICT_INDEX, verify.STRICT_DEST)
        self.assertIsNone(self.first.rejection(self.first.roles[verify.STRICT_INDEX],
                                               verify.STRICT_DEST))
        self.assertEqual(verify.idle_hist(self.final, self.one),
                         {1: 2275, 3: 377, 7: 6, 8: 1, 48: 4866})

    def test_final_map_passes_full_owner_audit_and_rejects_family_mutation(self):
        idle = verify.idle_hist(self.final, self.one)
        audit = self.fixture["audit"]
        result = audit.audit(self.base.geo, self.fixture["widths"], self.fixture["local"],
                             self.final.roles, self.fixture["plan"], idle, 16)
        self.assertEqual(result["rank_mass"], 1041408)
        self.assertEqual(result["deficit"], 5120)
        self.assertEqual(result["roles"], 69120)
        mutant = [dict(role) for role in self.final.roles]
        mutant[0]["family"] += 1
        with self.assertRaises(audit.Reject) as caught:
            audit.audit(self.base.geo, self.fixture["widths"], self.fixture["local"],
                        mutant, self.fixture["plan"], idle, 16)
        self.assertTrue(str(caught.exception).startswith("R3:"))

    def test_wrong_window_is_negative_control(self):
        role = self.base.roles[verify.NEUTRAL_INDEX]
        source = verify.NEUTRAL_SOURCE
        width = role["width"]
        bad = next(key for key, item in self.base.bins.items()
                   if key != source and item.remainder >= width
                   and self.base.rejection(role, key) == "outside_strict_source_event_window")
        self.assertEqual(self.base.rejection(role, bad), "outside_strict_source_event_window")
        with self.assertRaisesRegex(ValueError, "illegal relocation"):
            self.one.relocate(self.base, verify.NEUTRAL_INDEX, bad)

    def test_uniform_majorization_sign_and_certified_endpoint_gain(self):
        self.assertEqual(self.one.compare(0, 7, 7), 0)
        self.assertEqual(self.one.compare(1, 7, 7), -1)
        before = tuple(map(Fraction, self.result["pricing"]["moment_root_before"]))
        after = tuple(map(Fraction, self.result["pricing"]["moment_root_after"]))
        self.assertGreater(after[0], before[1])
        self.assertEqual(self.result["pricing"]["root_gain_certified_lower"],
                         str(after[0] - before[1]))
        self.assertFalse(self.result["interpretation"]["new_supplier_or_kappa"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
