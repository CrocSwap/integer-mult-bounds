#!/usr/bin/env python3
"""Adverse controls for exact arithmetic, independent inputs and frame screens."""
from fractions import Fraction as Q
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit
from triangular_obstruction import inverse, matrix, multiply, rejection


class ExactAuditTests(unittest.TestCase):
    def test_log_enclosures_against_longer_series(self):
        for x in (Q(1), Q(6, 5), Q(2), Q(3), Q(66), Q(72, 22)):
            lo, hi = audit.log_interval(x)
            y, power = x, 0
            while y >= 2:
                y /= 2
                power += 1
            l, u = audit.atanh_log(y, terms=65)
            l2, u2 = audit.atanh_log(Q(2), terms=65)
            self.assertLessEqual(lo, l + power * l2)
            self.assertGreaterEqual(hi, u + power * u2)
            self.assertLessEqual(hi - lo, Q(2, audit.GRID))

    def test_checkpoint_corruption_rejected(self):
        original = json.loads((audit.HERE / "inputs/complex-pr193.json").read_text())
        for field in ("rank", "loss"):
            changed = json.loads(json.dumps(original))
            changed["profile"][field] -= 1
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "inputs").mkdir()
                (root / "inputs/complex-pr193.json").write_text(json.dumps(changed))
                with patch.object(audit, "HERE", root), self.assertRaises(ValueError):
                    audit.checkpoint("complex-pr193")

    def test_cube_kernel_beyond_frozen_controls(self):
        result = audit.local_identity(9)
        self.assertEqual(result["B_rank"], 256)
        self.assertEqual(result["opposite_parity_source_rank"], 9)

    def test_infinite_tail_excludes_target(self):
        result = audit.family_screen()
        self.assertLess(Q(result["strict_arbitrary_local_chains_a_ceiling"]), Q(1, 100))
        self.assertEqual(result["best_arbitrary_local_chains_case"]["p"], 13)
        self.assertEqual(result["best_arbitrary_local_chains_case"]["degree"], 5)

    def test_common_flag_need_not_commute(self):
        upper = [matrix([[1, 1], [0, 0]]), matrix([[0, 2], [0, 1]])]
        basis = matrix([[1, 1], [1, 2]])
        inv = inverse(basis)
        frames = [multiply(multiply(basis, a), inv) for a in upper]
        self.assertFalse(rejection(frames)["rejected"])
        self.assertTrue(rejection(frames, basis)["rejected"])
        with self.assertRaises(ValueError):
            rejection(frames, [[1, 0], [0, 1]])

    def test_commuting_without_rational_eigenbasis(self):
        rotation = [[0, -1], [1, 0]]
        translated = [[1, -1], [1, 1]]
        self.assertTrue(rejection([rotation, translated])["rejected"])
        with self.assertRaises(ValueError):
            rejection([rotation], [[1, 0], [0, 1]])

    def test_nontriangular_family_is_only_inconclusive(self):
        frames = [[[1, 0], [0, 0]], [[Q(1, 2), Q(1, 2)], [Q(1, 2), Q(1, 2)]]]
        self.assertFalse(rejection(frames)["rejected"])
        with self.assertRaises(ValueError):
            rejection(frames, [[1, 0], [0, 1]])


if __name__ == "__main__":
    unittest.main()
