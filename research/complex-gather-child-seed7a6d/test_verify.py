"""Positive map and semantic failure controls for the C3 gather screen."""
import unittest
from fractions import Fraction as Q

import verify


class GatherControls(unittest.TestCase):
    def fixture_rows(self):
        return [
            {"operation": ["add", 5, 10, 1, 2, []], "old_frames": [(), (1,)],
             "deltas": [1, 0], "target": (1,)},
            {"operation": ["add", 5, 11, -1, 3, []], "old_frames": [(1,), (1,)],
             "deltas": [1, 1], "target": (2, 1)},
            {"operation": ["add", 5, 12, 2, 5, []], "old_frames": [(2, 1), (2, 1)],
             "deltas": [1, 1], "target": (4, 2, 1)},
        ]

    def test_positive_arbitrary_dirty_gather_and_inverse(self):
        candidate = {"coefficients": ["1/4", "-1/2", "3/7"]}
        self.assertTrue(verify.verify_gather_map(candidate))
        forward, inverse = verify.gather_matrices(candidate["coefficients"])
        dirty = [Q(17, 3), Q(-8, 5), Q(11, 7), Q(19, 4)]
        self.assertEqual(verify.matvec(inverse, verify.matvec(forward, dirty)), dirty)

    def test_candidate_conserves_source_and_destination_rank_mass(self):
        candidate = verify.candidate_from_rows("A", 40, self.fixture_rows())
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["frame_ranks"], [[1, 0], [1, 1], [1, 1]])
        self.assertEqual(candidate["positive_ranks"], [1, 1, 1, 1, 1])
        self.assertEqual(candidate["joint_rank"], 5)

    def test_duplicate_source_rejected(self):
        rows = self.fixture_rows()
        rows[2]["operation"][2] = 11
        self.assertIsNone(verify.candidate_from_rows("A", 0, rows))

    def test_destination_as_source_rejected(self):
        rows = self.fixture_rows()
        rows[2]["operation"][2] = 5
        self.assertIsNone(verify.candidate_from_rows("A", 0, rows))

    def test_fewer_than_two_positive_climbs_rejected(self):
        rows = self.fixture_rows()
        rows[0]["deltas"] = [1, 0]
        rows[1]["deltas"] = [0, 0]
        rows[2]["deltas"] = [0, 0]
        rows[0]["target"] = (1,)
        rows[1]["target"] = (1,)
        rows[2]["target"] = (1,)
        self.assertIsNone(verify.candidate_from_rows("A", 0, rows))

    def test_exact_interval_scheduler(self):
        candidates = [
            {"start": 0, "target_ranks": [1, 1, 1], "joint_rank": 3},
            {"start": 1, "target_ranks": [4, 4, 4], "joint_rank": 12},
            {"start": 3, "target_ranks": [1, 1, 1], "joint_rank": 3},
        ]
        weights = {0: Q(1), 1: Q(2), 3: Q(2)}
        total, chosen = verify.weighted_schedule(candidates, 6, weights)
        self.assertEqual(total, Q(3))
        self.assertEqual([row["start"] for row in chosen], [0, 3])

    def test_source_pinned_complete_census_and_negative_screen(self):
        certificate = verify.compute_certificate()
        self.assertEqual(sum(row["candidate_windows"]
                             for row in certificate["candidate_windows_by_section"].values()), 32)
        self.assertEqual(certificate["candidate_windows_by_section"]["A"]["candidate_windows"], 32)
        self.assertEqual(certificate["candidate_windows_by_section"]["B"]["candidate_windows"], 0)
        self.assertEqual(certificate["maximum_disjoint_window_count"], 16)
        self.assertEqual(certificate["max_saving_schedule_rank_mass"], 5586)
        self.assertGreater(Q(certificate["strict_margin_above_one"]), 0)
        self.assertFalse(certificate["screen_passes_five_percent"])
        self.assertLess(Q(certificate["max_saving_schedule_gain_percent"]), Q(5))


if __name__ == "__main__":
    unittest.main()
