#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Positive fixture and premise-removal controls for the frame-508 cut lemma."""

import unittest
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("frame508_verify", Path(__file__).with_name("verify.py"))
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class Frame508InverseCutTests(unittest.TestCase):
    def test_source_pinned_frame508_obstruction(self):
        cert = verify.verify()
        self.assertEqual(cert["status"], "PASS_R439_FRAME508_INVERSE_CUT")
        self.assertEqual(cert["inverse_column_support"], [19, 35, 66, 89, 97, 466])
        self.assertEqual(cert["inverse_column_vector_bits_in_register_order"], 1861)
        self.assertTrue(cert["cut_witness"]["source_forced_to_full_frame"])

    def test_low_donor_positive_control(self):
        # A two-wire shear can be completed entirely in a proper low subspace;
        # the cut lemma correctly does not reject it.
        shear = [0b01, 0b11]
        support = [0, 1]  # column 0 of the inverse is the same shear column
        self.assertEqual(verify.inverse_column_support(shear, 0), support)
        self.assertFalse(verify.cut_obstruction(support, {0, 1}, True))

    def test_full_frame_donor_premise_is_necessary(self):
        support = [0, 1]
        # If the second coordinate is incorrectly allowed in the low phase,
        # there is no contradiction. The actual source pin excludes it because
        # register 466 enters at F itself.
        self.assertFalse(verify.cut_obstruction(support, {0, 1}, True))
        self.assertTrue(verify.cut_obstruction(support, {0}, True))

    def test_reaching_full_frame_removes_the_cut_hypothesis(self):
        self.assertFalse(verify.cut_obstruction([0, 1], {0}, False))

    def test_singular_map_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "singular frame-508 matrix"):
            verify.inverse_column_support([0b01, 0b01], 0)


if __name__ == "__main__":
    unittest.main()
