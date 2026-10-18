#!/usr/bin/env python3
"""Failure and positive controls for the scoped verifier."""

import importlib.util
from pathlib import Path
import unittest


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r439_b509_minimality", PACKAGE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class LocalMinimumTests(unittest.TestCase):
    def test_full_certificate(self):
        result = VERIFY.verify()
        self.assertEqual(result["minimum"], 3)
        self.assertEqual(result["length3_words"], 3)

    def test_wrong_source_is_rejected(self):
        self.assertNotEqual(VERIFY.f2_rows(VERIFY.BAD_SOURCE_CONTROL), VERIFY.TARGET_ROWS)

    def test_two_gate_prefix_is_rejected(self):
        self.assertNotEqual(VERIFY.f2_rows(VERIFY.TWO_GATE_CONTROL), VERIFY.TARGET_ROWS)

    def test_two_gate_positive_control(self):
        self.assertEqual(VERIFY.f2_rows(VERIFY.POSITIVE_CONTROL), VERIFY.POSITIVE_CONTROL_ROWS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
