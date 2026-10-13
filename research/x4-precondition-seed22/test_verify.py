#!/usr/bin/env python3
"""Source-boundary and dirty-scratch controls, not performance tests."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("x4_precondition", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.programs, cls.checks = v.load_inputs()

    def test_changed_coefficient(self):
        word = copy.deepcopy(self.word)
        word["precondition"][1][3] = -1
        with self.assertRaisesRegex(ValueError, "triple shape"):
            v.pairs(word)

    def test_nonzero_frame(self):
        word = copy.deepcopy(self.word)
        word["start"][word["precondition"][0][1]] = 1
        with self.assertRaisesRegex(ValueError, "zero-frame"):
            v.pairs(word)

    def test_overlapping_pair(self):
        word = copy.deepcopy(self.word)
        word["precondition"][3:6] = word["precondition"][:3]
        with self.assertRaisesRegex(ValueError, "disjoint"):
            v.pairs(word)

    def test_missing_pair(self):
        word = copy.deepcopy(self.word)
        del word["precondition"][:3]
        with self.assertRaisesRegex(ValueError, "56 complete"):
            v.pairs(word)

    def test_archive_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / v.ARCHIVE
            path.parent.mkdir(parents=True)
            path.write_bytes(b"not the pinned archive")
            with self.assertRaisesRegex(ValueError, "source archive digest"):
                v.load_inputs(root)

    def test_dirty_coefficient_work_requires_first_clear(self):
        program = v.lower(["add", ["L", 0], ["L", 1], 1, 2])
        good, bad = v.Replay(2), v.Replay(2)
        for op in program:
            good.apply(op)
        for op in program[1:]:
            bad.apply(op)
        self.assertEqual(good.rows[("L", 0)], {0: v.Q(1), 1: v.Q(1, 2)})
        self.assertIn(10, bad.rows[("L", 0)])  # independent dirty W column
        self.assertFalse(good.rows[v.WORK])

    def test_six_operation_gatewise_comparison(self):
        x, y = ("L", 0), ("L", 1)
        candidates = {
            False: [("neg", x), ("half", x), ("double", x),
                    ("add", x, y, 1), ("half", x), ("add", y, x, -1)],
            True: [("neg", x), ("double", x), ("double", y),
                   ("add", y, x, -1), ("half", y), ("add", x, y, 1)],
        }
        for backward, gatewise in candidates.items():
            old, mid, new = v.Replay(2), v.Replay(2), v.Replay(2)
            for macro in v.expected_macros(0, 1, backward):
                for op in v.lower(macro):
                    old.apply(op)
            for op in gatewise:
                mid.apply(op)
            for op in v.replacement(0, 1, backward):
                new.apply(op)
            self.assertEqual([old.count, mid.count, new.count], [11, 6, 4])
            for r in (x, y):
                self.assertEqual(old.rows[r], mid.rows[r])
                self.assertEqual(old.rows[r], new.rows[r])


if __name__ == "__main__":
    unittest.main(verbosity=2)
