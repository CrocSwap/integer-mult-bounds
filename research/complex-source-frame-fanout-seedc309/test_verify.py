"""Meaningful positive and negative controls for the scoped C3 screen."""
import unittest
from fractions import Fraction as Q

import verify


class C3Controls(unittest.TestCase):
    def test_positive_arbitrary_dirty_fanout_map(self):
        candidate = {"coefficients": ["1/4", "-1/2", "3/7"]}
        self.assertTrue(verify.verify_fanout_map(candidate))
        forward, inverse = verify.fanout_matrices(candidate["coefficients"])
        self.assertEqual(forward[1][0], Q(1, 4))
        self.assertEqual(inverse[2][0], Q(1, 2))

    def test_duplicate_target_rejected(self):
        rows = [
            {"operation": ["add", 4, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 0], "target": ()},
            {"operation": ["add", 5, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 0], "target": ()},
            {"operation": ["add", 5, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 0], "target": ()},
        ]
        self.assertIsNone(verify.candidate_from_rows("A", 0, rows))

    def test_source_write_rejected(self):
        rows = [
            {"operation": ["add", 9, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 0], "target": ()},
            {"operation": ["add", 5, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 0], "target": ()},
            {"operation": ["add", 6, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 0], "target": ()},
        ]
        self.assertIsNone(verify.candidate_from_rows("A", 0, rows))

    def test_source_frame_change_rejected(self):
        rows = [
            {"operation": ["add", 4, 9, 1, 1, []], "old_frames": [(), ()], "deltas": [1, 1], "target": (1,)},
            {"operation": ["add", 5, 9, 1, 1, []], "old_frames": [(1,), ()], "deltas": [1, 0], "target": (1,)},
            {"operation": ["add", 6, 9, 1, 1, []], "old_frames": [(1,), ()], "deltas": [1, 0], "target": (1,)},
        ]
        self.assertIsNone(verify.candidate_from_rows("A", 0, rows))

    def test_exact_interval_scheduler_never_overlaps(self):
        candidates = [
            {"start": 0, "target_ranks": [1, 1, 1], "joint_rank": 3},
            {"start": 1, "target_ranks": [4, 4, 4], "joint_rank": 12},
            {"start": 3, "target_ranks": [1, 1, 1], "joint_rank": 3},
        ]
        weights = {0: Q(1), 1: Q(2), 3: Q(2)}
        total, chosen = verify.weighted_schedule(candidates, 6, weights)
        self.assertEqual(total, Q(3))
        self.assertEqual([x["start"] for x in chosen], [0, 3])

    def test_source_pinned_census_and_profile(self):
        result = verify.compute_certificate()
        self.assertEqual(sum(x["candidate_windows"] for x in result["candidate_windows_by_section"].values()), 32)
        self.assertEqual(result["maximum_disjoint_window_count"], 25)
        self.assertGreater(Q(result["strict_margin_above_one"]), 0)
        self.assertEqual(result["max_weight_schedule_rank_mass"], 5586)
        self.assertLess(Q(result["max_weight_schedule_gain_percent_upper"]), Q(5))


if __name__ == "__main__":
    unittest.main()
