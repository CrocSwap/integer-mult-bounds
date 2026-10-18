#!/usr/bin/env python3
"""Focused tests for the Q8 all-register central-minus-one result."""
import unittest
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("q8_any_r_verify", Path(__file__).with_name("verify.py"))
verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify)


class Q8CentralMinusOneTests(unittest.TestCase):
    def test_formal_group_and_augmentation_quotient(self):
        self.assertEqual(len(verify.GROUP_MUL), 8)
        self.assertEqual(verify.q8_axioms(), verify.build_certificate()["algebra"]["group_table_sha256"])
        quotient = verify.augmentation_quotient()
        self.assertEqual(quotient, {"dim_J": 7, "dim_J2": 5, "dim_J_over_J2": 2})

    def test_all_rank_one_pair_controls(self):
        for r, count in ((3, 28), (4, 120)):
            Ns = verify.idempotents(r)
            self.assertEqual(len(Ns), count)
            decompositions, checked = verify.pair_projection_controls(r, Ns)
            self.assertEqual(checked, (r * (r - 1) // 2) * 6)
            self.assertEqual(decompositions, [6] * (r * (r - 1) // 2))

    def test_direct_words_and_negative_controls(self):
        receipt = verify.build_certificate()
        controls = receipt["finite_controls"]
        self.assertEqual(controls["central_targets_each_width"], 12)
        self.assertEqual(controls["direct_full_group_algebra_replays"], 24)
        self.assertEqual(set(controls["negative_controls"].values()), {"rejected"})
        self.assertEqual(receipt["theorem"]["exact_minimum_calls"], 4)

    def test_source_pins_and_saved_certificate(self):
        self.assertEqual(verify.source_pins(), 10)
        self.assertEqual(verify.verify(write=False)["cost"]["new_kappa"], False)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Q8CentralMinusOneTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
