"""Behavioral controls for the actual profile and deletion boundary."""

import json
import tempfile
import unittest
from itertools import combinations_with_replacement
from pathlib import Path

import verify


def sigma_survivor(weights):
    """Separate descending-sigma implementation of bk1b with subset-sum bins."""
    sigma = tuple(sorted((w - 2 for w in weights), reverse=True))
    caps = (2, 4, 8, 12, 20, 36)
    if sum(sigma) >= 42:
        return False
    for deleted in range(7):
        tail, level = sigma[deleted:], 7 - deleted
        global_cap = sum(caps[x] for x in tail)
        target = sum(32 if x == 5 else caps[x] for x in tail)
        if level == 1 and max(target - 53, global_cap - 73) < 0:
            return False
        if level == 2 and max(target - 78, global_cap - 82) < 0:
            return False
        if level >= 3 and global_cap < verify.DISTANCE[level]:
            return False
    small = sorted(weights)[: len(weights) - 7]
    if sum(caps[w - 2] for w in small) >= 53:
        return True
    if sum(small) <= 7:
        return False
    reachable = {0}
    for weight in small:
        reachable |= {value + weight for value in reachable}
    return not any(value <= 6 and sum(small) - value <= 6 for value in reachable)


class ApplicationTests(unittest.TestCase):
    def test_literal_profile(self):
        row = verify.application()
        self.assertEqual((row["common_support_cap"], row["edge_support_cap"]), (26, 66))
        self.assertEqual(row["retained_code_dimension_lower_bound"], 3)
        self.assertFalse(row["older_support22_applies"])

    def test_independent_historical_filter(self):
        count = 0
        for size in range(7, 12):
            for weights in combinations_with_replacement(range(2, 8), size):
                first = verify.historical_survivor(weights)
                self.assertEqual(first, sigma_survivor(weights), weights)
                count += first
        self.assertEqual(count, 154)

    def test_three_deletions_leave_illegal_endpoint(self):
        with self.assertRaisesRegex(ValueError, "endpoint rank"):
            verify.application(deleted=3)

    def test_five_deletions_lose_required_dimension(self):
        with self.assertRaisesRegex(ValueError, "code dimension"):
            verify.application(deleted=5)

    def test_weaker_initial_dimension_fails(self):
        with self.assertRaisesRegex(ValueError, "code dimension"):
            verify.application((2, 3) + (6,) * 4 + (7,) * 4, dimension=6)

    def test_common_support_boundary(self):
        weights = (3, 4) + (6,) * 5 + (7,) * 4
        with self.assertRaisesRegex(ValueError, "common support"):
            verify.application(weights)

    def test_weight_and_order_boundaries(self):
        for weights in (
            tuple(reversed(verify.PROFILE)),
            (1,) + verify.PROFILE[1:],
            (True,) + verify.PROFILE[1:],
        ):
            with self.assertRaises(ValueError):
                verify.historical_survivor(weights)

    def test_changed_retained_source(self):
        manifest = json.loads((verify.PACKAGE / "SOURCES.json").read_text())
        manifest["files"] = []
        manifest["retained_files"] = [{"local_path": "source", "sha256": "0" * 64}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "SOURCES.json").write_text(json.dumps(manifest))
            (path / "source").write_text("changed")
            with self.assertRaisesRegex(ValueError, "retained source"):
                verify.authenticate(path)


if __name__ == "__main__":
    unittest.main()
