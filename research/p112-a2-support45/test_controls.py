"""Behavioral and rejecting controls for the shortening certificate."""

import json
import unittest
from pathlib import Path

import verify

PACKAGE = Path(__file__).resolve().parent


class Controls(unittest.TestCase):
    def test_ten_singletons_reduce_support(self):
        self.assertEqual(verify.singleton_budget(10), 20)
        self.assertEqual(verify.singleton_budget(9), 21)

    def test_optimized_guards_reject_invalid_counts(self):
        for value in (-1, 11, True, 1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verify.singleton_budget(value)

    def test_new_budget_excludes_the_old_equality(self):
        self.assertEqual(2 * (78 - 45), 3 * (12 + 10))
        self.assertGreater(
            2 * (78 - 45), 3 * max(map(verify.singleton_budget, range(11)))
        )

    def test_common_support46_needs_a_new_normalization(self):
        self.assertGreater(112 - (45 + 36), 30)
        self.assertEqual(112 - (46 + 36), 30)

    def test_binary_input_rejection(self):
        for values in ([512], [-1], [True], [0] * 121):
            with self.subTest(values=values[:3]), self.assertRaises(ValueError):
                verify.binary_span(values)

    def test_extra_full_root_rejects(self):
        geometry = verify.load_geometry()
        roots, _, _, coordinates = geometry.root_data()
        labels = [
            1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
            for row in coordinates
        ]
        receipt = json.loads((PACKAGE / "RESULT.json").read_text())
        support = next(iter(receipt["fibers"].values()))["witness_labels"]
        _, span = verify.binary_span(support)
        replacement = next(x for x in sorted(span) if x & 1 and x not in labels)
        removed = next(x for x in labels if x not in span)
        corrupted = [replacement if x == removed else x for x in labels]
        self.assertEqual(len(roots), 120)
        with self.assertRaisesRegex(ValueError, "adds a root"):
            verify.validate_tight(support, corrupted)

    def test_missing_or_duplicate_singletons_reject(self):
        labels = list(range(1, 241, 2))
        for support in (labels[:9], [labels[0]] * 10):
            with self.subTest(support=support), self.assertRaises(ValueError):
                verify.validate_tight(support, labels)

    def test_projective_fibers_ignore_sign_and_scale(self):
        self.assertEqual(verify.projective((4, -8)), (1, -2))
        self.assertEqual(verify.projective((-8, 16)), (1, -2))
        self.assertEqual(verify.projective((0, 0)), (0, 0))


if __name__ == "__main__":
    unittest.main()
