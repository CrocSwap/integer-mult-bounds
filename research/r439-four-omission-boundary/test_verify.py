"""Independent finite oracles for the four-omission reduction. Apache-2.0."""
import copy
import importlib.util
import itertools
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("four_audit", Path(__file__).with_name("verify.py"))
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class FourOmissionTests(unittest.TestCase):
    def test_dense_complete_small_domain(self):
        result = audit.controls()
        self.assertEqual(result["dense_quartets"], 47880)
        self.assertEqual(result["literal_deletion_subsets"], 128)

    def test_all_short_literal_words(self):
        alphabet = [(a, b) for a in range(3) for b in range(3) if a != b]
        checked = 0
        for word in itertools.product(alphabet, repeat=3):
            factors = audit.factors_from_suffixes(word, 3)
            inverse = audit.replay(word[::-1], 3)
            for mask in range(8):
                omitted = [i for i in range(3) if (mask >> i) & 1]
                direct = audit.compose(audit.replay(word, 3, omitted), inverse)
                transported = [1, 2, 4]
                for i in omitted:
                    transported = audit.compose(audit.transvection_rows(factors[i], 3), transported)
                self.assertEqual(direct, transported)
                checked += 1
        self.assertEqual(checked, 1728)

    def test_noncommuting_orientation(self):
        factors = [(1, 2), (2, 4), (3, 4), (1, 6)]
        self.assertEqual(audit.four_census(factors)["neutral_four_rank_two"], 1)
        swapped = [factors[i] for i in (1, 0, 2, 3)]
        self.assertEqual(audit.four_census(swapped)["neutral_four_total"], 0)
        self.assertEqual(audit.dense_oracle(swapped, 3), [])

    def test_three_member_plane_and_transpose(self):
        factors = [(1, 2), (1, 4), (6, 6), (7, 6)]
        direct = audit.four_census(factors)
        dual = audit.four_census([(v, u) for u, v in factors])
        self.assertEqual(direct["three_member_image_planes"], 1)
        self.assertEqual(direct["neutral_four_total"], 1)
        self.assertEqual(dual["neutral_four_total"], 1)

    def test_strict_chronological_split(self):
        f = {"same": [(0, 1), (0, 2), (1, 2)]}
        self.assertEqual(audit.ordered_matches(f, [("same", 1, 3)])[0], 0)
        self.assertEqual(audit.ordered_matches(f, [("same", 2, 3)])[0], 1)
        self.assertEqual(audit.ordered_matches(f, [("same", 3, 4)])[0], 3)

    def test_all_two_dimensional_factor_subsets(self):
        factors = [(u, v) for u in range(1, 4) for v in range(1, 4)
                   if not audit.parity(u & v)]
        for size in range(len(factors) + 1):
            for subset in itertools.combinations(factors, size):
                result = audit.four_census(subset)
                self.assertEqual(result["neutral_four_total"], len(audit.dense_oracle(subset, 2)))

    def test_arbitrary_dirty_helper_is_observed(self):
        rows = audit.replay([(0, 2)], 3)
        self.assertEqual([r & 3 for r in rows[:2]], [1, 2])
        self.assertNotEqual(rows, [1, 2, 4])
        self.assertEqual(rows[0] & 4, 4)

    def test_source_factor_and_receipt_mutations(self):
        gates, width = audit.load_bound_word()
        factors = audit.factors_from_suffixes(gates, width)
        bad = factors.copy()
        u, v = bad[0]
        bad[0] = (u, v ^ 1)
        with self.assertRaisesRegex(ValueError, "incoming factor transport"):
            audit.check_factors(gates, width, bad)
        fixture = audit.four_census([(1, 2), (2, 4), (3, 4), (1, 6)])
        audit.check_certificate(fixture, copy.deepcopy(fixture))
        for key in ("pair_count", "neutral_four_total", "neutral_four_rank_two"):
            changed = copy.deepcopy(fixture)
            changed[key] += 1
            with self.assertRaisesRegex(ValueError, "certificate mismatch"):
                audit.check_certificate(fixture, changed)


if __name__ == "__main__":
    unittest.main()
