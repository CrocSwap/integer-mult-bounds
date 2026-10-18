#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the composed allocation, tariff and release boundary."""

import copy
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import verify


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geometry = verify.retained("geometry")
        cls.moment = verify.retained("moment")
        cls.data = verify.allocation()
        cls.plan = verify.read(verify.SOURCE / "vendor/PLAN.json.gz")
        cls.template = verify.read(verify.SOURCE / "vendor/TEMPLATE.json.gz")
        cls.providers = verify.read(verify.PACKAGE / "vendor/pr3015/PROVIDERS.json")

    def check(self, order, fill, routes):
        dispatch = {(stage, owner): name for stage, owner, name in routes}
        return self.geometry.check(order, fill, dispatch, self.plan, self.template, self.providers)

    def test_complete_candidate_and_paid_remainder(self):
        _, _, _, order, _, fill, routes = self.data
        result = self.check(order, fill, routes)
        self.assertEqual(result["profile"], verify.EXPECTED)
        self.assertEqual((result["roles"], result["physical"], result["rank_mass"]),
                         (543456, 133117, 9633024))
        self.assertEqual(result["idle"][32], 1)
        self.assertNotIn(14, result["idle"])

    def test_unknown_retained_module_rejects(self):
        with self.assertRaisesRegex(ValueError, "module name"):
            verify.retained("../verify")

    def test_stale_journal_rejects(self):
        journal = verify.read(verify.PACKAGE / "vendor/PR3022-EXCHANGE.json")
        with self.assertRaisesRegex(ValueError, "preimage"):
            verify.apply(self.data[5], journal, 86)

    def test_duplicate_journal_rejects(self):
        journal = copy.deepcopy(verify.read(verify.PACKAGE / "vendor/PR3022-EXCHANGE.json"))
        journal["edits"][1] = journal["edits"][0]
        with self.assertRaisesRegex(ValueError, "preimage"):
            verify.apply(self.data[4], journal, 86)

    def test_missing_role_rejects(self):
        _, _, _, order, _, fill, routes = self.data
        with self.assertRaisesRegex(ValueError, "role count"):
            self.check(order, {**fill, "rows": fill["rows"][:-1]}, routes)

    def test_wrong_dispatch_rejects(self):
        _, _, _, order, _, fill, routes = self.data
        wrong = [*routes[:-1], routes[0]]
        with self.assertRaisesRegex(ValueError, "dispatch count"):
            self.check(order, fill, wrong)

    def test_undercharged_idle_rejects(self):
        profile = dict(verify.EXPECTED)
        del profile[32]
        with self.assertRaisesRegex(ValueError, "rank mass"):
            verify.root(profile, 148, self.moment)

    def test_exact_doubling_has_no_gain(self):
        doubled = {rank: 2 * count for rank, count in verify.BASELINE.items()}
        self.assertEqual(verify.root(verify.BASELINE, 74, self.moment),
                         verify.root(doubled, 148, self.moment))

    def test_strict_rational_gain(self):
        old = verify.root(verify.BASELINE, 74, self.moment)
        new = verify.root(verify.EXPECTED, 148, self.moment)
        self.assertGreater(new[0] - old[1], Fraction(1133, 10**12))
        self.assertLess(new[1] - old[0], Fraction(1134, 10**12))

    def test_paid_profile_packing_cap(self):
        local = {"1": 2443, "2": 707, "3": 232, "4": 108, "5": 18, "8": 8}
        bounds = verify.general_ceiling(self.moment, local)
        self.assertEqual(bounds, (Fraction(439088585719, 250000000000000),
                                  Fraction(1756354342877, 1000000000000000)))
        with self.assertRaisesRegex(ValueError, "actual paid profile"):
            verify.general_ceiling(self.moment, {**local, "1": 2445})

    def test_actual_stock_and_prefix_increase(self):
        old, new = verify.stock(74), verify.stock(148)
        self.assertEqual((old["physical"], new["physical"]), (66813, 133117))
        self.assertEqual((old["stock_l2_bits"], new["stock_l2_bits"]), (1322, 1323))
        self.assertEqual((old["required_reserve_bits"], new["required_reserve_bits"]),
                         (1510, 1511))
        self.assertEqual(new["retained_payload_bits"], 2048)

    def test_outside_replica_domain_rejects(self):
        with self.assertRaisesRegex(ValueError, "replica domain"):
            verify.stock(740)

    def test_source_drift_rejects_without_touching_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "input.txt"
            source.write_bytes(b"original\n")
            sources = {"files": [{"path": "input.txt", "usage": "input",
                                   "sha256": verify.digest(source)}]}
            (root / "SOURCES.json").write_bytes(verify.canonical(sources))
            (root / "VENDOR.json").write_bytes(b"[]\n")
            verify.authenticate(root, root)
            source.write_bytes(b"changed\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                verify.authenticate(root, root)


if __name__ == "__main__":
    unittest.main()
