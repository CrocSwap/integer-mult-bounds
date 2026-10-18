#!/usr/bin/env python3
"""Focused positive and semantic negative controls for the exact E6 screen."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import solve_family


class E6CoordinateBilinearFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = solve_family()

    def test_exact_domain_and_constraint_rank(self):
        self.assertEqual(self.result["root_counts"], {
            "E8_lines": 120,
            "E6_lines": 36,
            "ordered_orthogonal_pairs": 540,
        })
        self.assertEqual(self.result["constraint_rank_Q"], 35)
        self.assertEqual(self.result["kernel_dimension_Q"], 1)

    def test_gram_positive_control_and_rank_obstruction(self):
        self.assertTrue(self.result["kernel_equals_gram_line"])
        self.assertEqual(self.result["kernel_generator_rank_Q"], 6)
        self.assertEqual(set(self.result["decoder_diagonal_scaled"]), {"8/1"})

    def test_zero_and_mutated_form_negative_controls(self):
        self.assertEqual(self.result["negative_controls"], 2)
        self.assertGreater(self.result["mutant_orthogonal_pair_violations"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
