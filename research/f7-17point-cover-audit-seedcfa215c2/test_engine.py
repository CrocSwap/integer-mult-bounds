"""Tests for the 17-point cover audit engine (cover17.py).

RED first: these assertions encode the sharp 17-point split table derived
in the CLAIM card (collision-multiplicity identity), and the exact small
controls (n = 5).  They fail until cover17.py exists.
"""

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import cover17
import hashlib


class TestVendoredEngine(unittest.TestCase):
    def test_pr2542_engine_byte_pin(self):
        digest = hashlib.sha256((HERE / "vendor" / "pr2542_engine.py").read_bytes())
        self.assertEqual(
            digest.hexdigest(),
            "82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4",
        )


class TestSharpRows(unittest.TestCase):
    """The pair-representation identity extended to every 17-point split."""

    def test_pr2542_rows_reproduced(self):
        # PR 2542's contradiction, re-derived: best_sum_AB=1 need=4.
        for s, t in ((9, 8), (8, 9)):
            rows = cover17.sharp_rows(7, s, t)
            self.assertFalse(rows["feasible"], (s, t))
            self.assertEqual(rows["best"], 1, (s, t))
            self.assertEqual(rows["need"], 4, (s, t))

    def test_17point_split_table(self):
        feasible = {
            (s, t): cover17.sharp_rows(7, s, t)["feasible"]
            for s in range(1, 17)
            for t in (17 - s,)
        }
        counted = {k: v for k, v in feasible.items() if v or k in ((9, 8), (8, 9))}
        # Counting-feasible 17-point splits are exactly these six:
        self.assertEqual(
            sorted(k for k in feasible if cover17.counting_ok(7, *k)),
            [(6, 11), (7, 10), (8, 9), (9, 8), (10, 7), (11, 6)],
        )
        # PR 2542's table kills (9,8)/(8,9); the four others survive the
        # closed-form identity (that is the recorded overreach).
        self.assertTrue(feasible[(10, 7)])
        self.assertTrue(feasible[(7, 10)])
        self.assertTrue(feasible[(11, 6)])
        self.assertTrue(feasible[(6, 11)])
        self.assertFalse(feasible[(9, 8)])
        self.assertFalse(feasible[(8, 9)])

    def test_extremal_107_profile(self):
        # (10,7): odd excess 6; integer collision profiles force c in {3,4,5,6,8}.
        self.assertEqual(cover17.profile_c_values(7, 10, 7), [3, 4, 5, 6, 8])
        self.assertEqual(cover17.profile_c_values(7, 7, 10), [3, 4, 5, 6, 8])
        # The extremal (e_ex=b_ex=0) row admits only c = 3 (six doubled masks).
        self.assertEqual(cover17.attainable_c(7, 10, 7, 0, 0), {3})

    def test_116_reduces_to_one_row(self):
        # (11,6): odd excess 2 forces c = 1 and e_ex + b_ex = 6, shared = 1.
        self.assertEqual(cover17.profile_c_values(7, 11, 6), [1])
        sharp = cover17.sharp_rows(7, 11, 6)
        self.assertTrue(sharp["feasible"])
        self.assertEqual(
            {(r["e_ex"], r["b_ex"], r["c"]) for r in sharp["rows"]},
            {(e, 6 - e, 1) for e in range(7)},
        )
        for r in sharp["rows"]:
            self.assertEqual(r["shared"], 1)

    def test_min_excess_census_kills_107(self):
        # Census (SIDON-RECEIPT.json): min pair-sum excess of 10-sets in F2^6
        # is >= 3 (k=10 budgets 0,1,2 all empty through {0,3}, GL-complete).
        # With e_ex >= 3 the (10,7) rows all die: shared = 3 - e - b <= 0.
        self.assertEqual(cover17.surviving_rows(7, 10, 7, 3, 0)["rows"], [])
        self.assertEqual(cover17.surviving_rows(7, 7, 10, 0, 3)["rows"], [])
        self.assertFalse(cover17.surviving_rows(7, 10, 7, 3, 0)["feasible"])

    def test_min_excess_census_narrows_116(self):
        # Census (SIDON-RECEIPT.json, raw {0,3} domain complete): min excess
        # of 11-sets in F2^6 is >= 5 (k=11 budget-4 walk: zero leaves across
        # all 62 sub-shards).  The surviving (11,6) rows are then (5,1),(6,0).
        rows = cover17.surviving_rows(7, 11, 6, 3, 0)
        self.assertEqual(
            {(r["e_ex"], r["b_ex"], r["c"]) for r in rows["rows"]},
            {(3, 3, 1), (4, 2, 1), (5, 1, 1), (6, 0, 1)},
        )
        rows = cover17.surviving_rows(7, 11, 6, 5, 0)
        self.assertEqual(
            {(r["e_ex"], r["b_ex"], r["c"]) for r in rows["rows"]},
            {(5, 1, 1), (6, 0, 1)},
        )

    def test_odd_translation_mirror(self):
        # S+S is translation-invariant; an odd translation swaps the E/O
        # parts, so (s,t) and (t,s) are the same set-level question.
        pts = [0, 3, 5, 9, 17, 30, 33, 65, 102, 21, 42]
        shifted = [p ^ 1 for p in pts]
        self.assertEqual(cover17.coverage_mask(pts), cover17.coverage_mask(shifted))
        even = sum(1 for p in pts if p.bit_count() % 2 == 0)
        even_shifted = sum(1 for p in shifted if p.bit_count() % 2 == 0)
        self.assertEqual(even, len(pts) - even_shifted)

    def test_odd_profile_parity(self):
        # sigma = sum j(j+1)/2 must be even (= 2c); e.g. a single triple
        # (j=2, sigma=3) can never absorb odd excess 2 at (11,6).
        self.assertEqual(cover17.odd_profiles(2), [[1, 1]])


class TestCoveragePrimitives(unittest.TestCase):
    def test_dual_predicate_agrees(self):
        pts = [0, 1, 3, 7, 15, 31, 32]
        self.assertEqual(
            cover17.coverage_mask(pts), cover17.coverage_mask_dual(pts)
        )

    def test_self_sum_gives_zero_only(self):
        pts = [0, 5, 9]
        mask = cover17.coverage_mask(pts)
        self.assertTrue(mask & 1)  # zero covered via a = b
        self.assertEqual(bin(mask).count("1"), 4)  # 0, 5, 9, 12


class TestSmallControls(unittest.TestCase):
    def test_n5_nine_point_no_cover_max29(self):
        # Community fact reproduced by PR 2542's census: no nine-point set
        # of F2^5 covers; the maximum is 29/32.
        covers, max_cov = cover17.brute_force_set_census(5, 9)
        self.assertEqual(covers, 0)
        self.assertEqual(max_cov, 29)

    def test_n5_ten_point_covers_exist(self):
        # Non-vacuity: 99,200 ten-point covers of F2^5 (pinned community
        # census reproduced by PR 2542's control).
        covers, max_cov = cover17.brute_force_set_census(5, 10)
        self.assertEqual(covers, 99200)
        self.assertEqual(max_cov, 32)


if __name__ == "__main__":
    unittest.main()
