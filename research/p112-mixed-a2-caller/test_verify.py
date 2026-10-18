"""Behavioral and original-source controls, including optimized replay."""

import contextlib
import io
import json
import sys
import unittest
from itertools import combinations_with_replacement, permutations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def load_verify():
    sys.path.insert(0, str(PACKAGE))
    import verify

    return verify


verify = load_verify()


class Controls(unittest.TestCase):
    def test_actual_application(self):
        result = verify.application()
        self.assertEqual(result["small"], (5, 5, 5))
        self.assertEqual(result["retained_code_dimension"], 2)
        self.assertEqual(result["bound"]["ranks"], (5, 5, 6))
        self.assertEqual(result["bound"]["required_twice_residual_union"], 84)

    def test_classification_boundary(self):
        self.assertTrue(verify.mixed_bound(37)["excluded"])
        boundary = verify.mixed_bound(38)
        self.assertFalse(boundary["A2_classification_valid"])
        self.assertFalse(boundary["excluded"])
        # Both classification and the singleton count stop at this boundary.
        self.assertEqual(
            boundary["required_twice_residual_union"],
            boundary["incidence_plus_singletons_cap"],
        )

    def test_rank_permutation(self):
        for ranks in set(permutations((5, 5, 6))):
            self.assertTrue(verify.mixed_bound(37, ranks)["excluded"])

    def test_deletion_controls(self):
        for count in (3, 5):
            with self.assertRaises(ValueError):
                verify.application(count)

    def test_old_uniform_bound_loses(self):
        self.assertFalse(verify.mixed_bound(36, (6, 6, 6))["excluded"])

    def test_invalid_boundaries(self):
        for support in (-1, 113, True, 2.5):
            with self.assertRaises(ValueError):
                verify.mixed_bound(support)
        with self.assertRaises(ValueError):
            verify.mixed_bound(36, (5, 5, 7))

    def test_literal_original_filters(self):
        sys.path.insert(0, str(PACKAGE / "vendor"))
        with contextlib.redirect_stdout(io.StringIO()) as output:
            import bk2b
        table = [tuple(map(int, row.split())) for row in output.getvalue().splitlines()]
        self.assertEqual(len(table), 24)
        self.assertIn((6, 4, 69, 1), table)
        checked = 0
        survivors = []
        for n in range(6, 11):
            for weights in combinations_with_replacement(range(2, 8), n):
                expected = (
                    sum(w - 2 for w in weights) < 36
                    and bk2b.feasible(weights, 6)
                    and not bk2b.killed(weights, 6)
                )
                self.assertEqual(verify.historical_survivor(weights), expected)
                checked += 1
                if expected:
                    survivors.append(list(weights))
        result = json.loads((PACKAGE / "RESULT.json").read_text())
        self.assertEqual(survivors, result["historical_cell_survivors"])
        self.assertEqual(checked, 7546)

    def test_capacity_source_receipts(self):
        five = json.loads((PACKAGE / "vendor/RANK5-RESULT.json").read_text())
        six = json.loads((PACKAGE / "vendor/RANK6-RESULT.json").read_text())
        self.assertEqual(five["p112_five_flats"]["maximum"], 12)
        self.assertEqual([r["maximum"] for r in six["live_flat_capacities"]], [12, 20])


if __name__ == "__main__":
    unittest.main()
