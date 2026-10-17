"""Mathematical and failure controls for the analytic A5 frame bound."""

import sys
import unittest
from collections import Counter
from itertools import combinations, combinations_with_replacement
from unittest.mock import patch

import verify as v


class ShorteningChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots = v.root_inventory()
        cls.values, cls.costs, cls.variances = v.evaluations(cls.roots)
        cls.receipt = v.read_json(v.PACKAGE / "RESULT.json")

    def test_integer_variance_and_unequal_pair_bound(self):
        for values in combinations_with_replacement(range(-2, 3), 6):
            cost = 6 - max(Counter(values).values())
            variance6 = 6 * sum(x * x for x in values) - sum(values) ** 2
            pair_sum = sum((x - y) ** 2 for x, y in combinations(values, 2))
            self.assertEqual(variance6, pair_sum)
            if cost == 1:
                self.assertGreaterEqual(variance6, 5)
            elif cost >= 2:
                self.assertGreaterEqual(variance6, 8)

    def test_parseval_and_low_cost_frame_coordinate(self):
        frame = self.receipt["witness"]["frame"]
        self.assertEqual(sum(self.variances[i] for i in frame), 60)
        counts = Counter(self.costs[i] for i in frame)
        self.assertEqual(2 * counts[0] + counts[1], 2)
        self.assertEqual(v.frame_identity(v.ATTAINING_FRAME)[0][0], 8)

    def test_symbolic_signature_consequence(self):
        receipt = v.signature_receipt()
        self.assertEqual(receipt["signatures"], 165)
        self.assertEqual(receipt["minimum_floor_at_30"], 122)
        self.assertEqual(v.scalar_receipt()["integer_patterns"], 210)

    def test_sharp_witness_is_an_orthogonal_frame(self):
        witness = self.receipt["witness"]
        frame, cuts = witness["frame"], witness["cuts"]
        self.assertEqual(len(set(frame)), 8)
        self.assertEqual(len(set(cuts)), 30)
        self.assertFalse(set(frame) & set(cuts))
        self.assertTrue(
            all(
                v.inner(self.roots[i], self.roots[j]) == 0
                for i, j in combinations(frame, 2)
            )
        )
        self.assertEqual(
            sum(
                c for i, c in enumerate(self.costs) if i not in frame and i not in cuts
            ),
            122,
        )

    def test_unstructured_cuts_lose_strictness(self):
        order = sorted(range(120), key=lambda i: -self.costs[i])
        self.assertEqual(sum(self.costs[i] for i in order[38:]), 120)
        self.assertTrue(
            any(
                v.inner(self.roots[i], self.roots[j])
                for i, j in combinations(order[:8], 2)
            )
        )

    def test_thirty_one_is_a_failed_proof_boundary(self):
        frame = self.receipt["witness"]["frame"]
        costs = sorted(c for i, c in enumerate(self.costs) if i not in frame)
        self.assertEqual(sum(costs[:81]), 120)
        self.assertEqual(self.receipt["root_floor_at_31"], 120)

    def test_analytic_formula_rejects_false_frames(self):
        for costs in ((2,) * 8, (3,) * 8):
            with self.assertRaisesRegex(ValueError, "Parseval"):
                v.analytic_floor(costs, 30)
        for costs, cuts in (((0,) * 7, 30), ((0,) * 8, 32), ((4,) * 8, 30)):
            with self.assertRaises(ValueError):
                v.analytic_floor(costs, cuts)

    def test_incomplete_geometry_rejects(self):
        with self.assertRaisesRegex(ValueError, "frame shape"):
            v.frame_identity(v.ATTAINING_FRAME[:-1])
        with self.assertRaisesRegex(ValueError, "spectrum"):
            v.evaluations(self.roots[:-1])
        with self.assertRaisesRegex(ValueError, "not orthogonal"):
            v.frame_identity((self.roots[0],) * 8)

    def test_source_mutation_rejects(self):
        original = v.Path.read_bytes

        def altered(path):
            raw = original(path)
            return raw + b"\n" if path.name == "mixed.py" else raw

        with patch.object(v.Path, "read_bytes", altered):
            with self.assertRaisesRegex(ValueError, "input hash"):
                v.bind_sources()

    def test_mixed_premise_mutation_rejects(self):
        original = v.read_json

        def altered(path):
            data = original(path)
            if (
                path.parent.name == "p112-six-vertex-budget"
                and path.name == "RESULT.json"
            ):
                data["mixed"]["minimum_after_30_cuts"] = 120
            return data

        with patch.object(v, "read_json", altered):
            with self.assertRaisesRegex(ValueError, "mixed premise"):
                v.bind_sources()

    def test_separate_cost_algorithm(self):
        independent = []
        for root in self.roots:
            values = [0] + [root[0] + root[j] for j in range(1, 6)]
            independent.append(6 - max(values.count(x) for x in values))
        self.assertEqual(tuple(independent), self.costs)
        self.assertEqual(sum(independent), 216)

    def test_output_stays_outside_repository(self):
        argv = ["verify.py", "--output", str(v.PACKAGE / "unexpected-output.json")]
        with (
            patch.object(sys, "argv", argv),
            patch.object(v, "build", return_value=self.receipt),
        ):
            with self.assertRaisesRegex(ValueError, "external output only"):
                v.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
