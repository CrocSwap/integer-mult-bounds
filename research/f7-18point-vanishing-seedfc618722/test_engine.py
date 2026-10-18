"""Tests for the KB3f vanishing-character classification engine.

All exact integer arithmetic.  The class-floor table asserted here was derived
by hand from the half-decomposition of the covering conditions (see vanish.py
module docstring); the tests are the machine check.  Conventions: E = even
coset of F2^n, isomorphic to F2^(n-1); a "character" is a nontrivial
character of E, represented by its F2^n index v in {1..2^n-2}, paired v ~
v + (2^n - 1) (both indices restrict to the same character of E); class
counts are at the character (pair) level unless a name says u-level.

Run: python3 -I -B test_engine.py      (expected: Ran N tests ... OK)
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vanish


class TestCharBasics(unittest.TestCase):
    def test_char_sum_and_split(self):
        # A = span{3, 5} = {0, 3, 5, 6} inside E = F2^5 (even-weight view).
        A = [0, 3, 5, 6]
        self.assertEqual(vanish.char_sum(A, 0), 4)
        # annihilator of A inside F2^5: v with base 7 and free bits 3, 4
        ann = {0, 7, 8, 15, 16, 23, 24, 31}
        for v in range(1, 32):
            cs = vanish.char_sum(A, v)
            if v in ann:
                self.assertEqual(cs, 4, v)
            else:
                self.assertEqual(cs, 0, v)
        van_u = vanish.vanishing_set_u(A, 5)
        self.assertEqual(len(van_u), 24)  # 30 u's off {0, 31} minus 6 annihilators
        self.assertEqual(van_u, {v for v in range(1, 31) if v not in ann})
        van_e = vanish.vanishing_set(A, 5)
        self.assertEqual(len(van_e), 12)  # character (pair) level

    def test_split_sizes(self):
        A = [0, 3, 5, 6]
        # v = 1 (bit 0): dots 1 on {3, 5}, 0 on {0, 6}
        self.assertEqual(vanish.split_sizes(A, 1, 5), (2, 2))
        self.assertEqual(vanish.split_sizes(A, 8, 5), (4, 0))


class TestHalfDecomposition(unittest.TestCase):
    def test_lemma_exhaustive_f2_3(self):
        """L2 (halving) and L3 (half-decomposition of coverage) hold for
        every (A, D) pair inside E = F2^3 (256 x 256 pairs)."""
        res = vanish.check_half_decomposition(3, exhaustive=True)
        self.assertTrue(res["ok"])
        self.assertEqual(res["pairs"], 256 * 256)

    def test_lemma_samples_f2_5(self):
        res = vanish.check_half_decomposition(5, exhaustive=False, samples=4000, seed=7)
        self.assertTrue(res["ok"])
        self.assertEqual(res["pairs"], 4000)

    def test_multi_vanishing_structure_exhaustive_f2_3(self):
        """L5: two simultaneous vanishings force the balanced grid."""
        res = vanish.check_multi_vanishing(3)
        self.assertTrue(res["ok"])
        self.assertGreater(res["checked"], 0)

    def test_tight_equality_exhaustive_f2_3(self):
        """L7: floor equality plus coverage forces Sidon cross sums."""
        res = vanish.check_tight_equality(3)
        self.assertTrue(res["ok"])
        self.assertGreater(res["checked"], 0)


class TestClassFloors(unittest.TestCase):
    """Exact class table: a vanishing character psi forces the vanishing
    side to split equally across ker(psi); even-mask coverage of the odd
    side of ker(psi) inside E forces a0*a1 + d0*d1 >= 2^(m-1) (m = 6 here:
    the 18-point problem's E = F2^6)."""

    def test_floor_values_12_6(self):
        tab = vanish.class_table(12, 6, m=6)
        surv = {(c["other_split"][0], c["other_split"][1]): c["verdict"] for c in tab["A_vanish"]}
        self.assertEqual(
            surv,
            {(6, 0): "survives", (5, 1): "survives", (4, 2): "survives", (3, 3): "survives"},
        )
        surv = {(c["other_split"][0], c["other_split"][1]): c["verdict"] for c in tab["D_vanish"]}
        self.assertEqual(
            surv,
            {
                (12, 0): "dead",
                (11, 1): "dead",
                (10, 2): "dead",
                (9, 3): "survives",
                (8, 4): "survives",
                (7, 5): "survives",
                (6, 6): "survives",
            },
        )

    def test_floor_values_10_8(self):
        tab = vanish.class_table(10, 8, m=6)
        surv = {(c["other_split"][0], c["other_split"][1]): c["verdict"] for c in tab["A_vanish"]}
        self.assertEqual(
            surv,
            {(8, 0): "dead", (7, 1): "survives", (6, 2): "survives", (5, 3): "survives", (4, 4): "survives"},
        )
        surv = {(c["other_split"][0], c["other_split"][1]): c["verdict"] for c in tab["D_vanish"]}
        self.assertEqual(
            surv,
            {
                (10, 0): "dead",
                (9, 1): "dead",
                (8, 2): "survives",
                (7, 3): "survives",
                (6, 4): "survives",
                (5, 5): "survives",
            },
        )
        tight = sorted(
            [c["other_split"] for c in tab["A_vanish"] + tab["D_vanish"] if c["tight"]]
        )
        self.assertEqual(tight, [(7, 1), (8, 2)])

    def test_dead_classes_have_witness(self):
        for (s, t) in ((12, 6), (10, 8)):
            for side in ("A_vanish", "D_vanish"):
                for c in vanish.class_table(s, t, m=6)[side]:
                    if c["verdict"] == "dead":
                        self.assertLess(c["floor_value"], c["floor_need"], c)
                    else:
                        self.assertGreaterEqual(c["floor_value"], c["floor_need"], c)

    def test_11_7_and_9_9_no_vanishing(self):
        for (s, t) in ((11, 7), (9, 9)):
            tab = vanish.class_table(s, t, m=6)
            self.assertEqual(tab["A_vanish"], [])
            self.assertEqual(tab["D_vanish"], [])
            self.assertFalse(tab["vanishing_possible"])


class TestFloorsSoundOnRealCovers(unittest.TestCase):
    def test_f2_4_census_consistent(self):
        rec = vanish.census_f4()
        for cov in rec["covers"]:
            self.assertTrue(vanish.covers_f2n(cov, 4))
        self.assertGreater(rec["covers_total"], 0)
        self.assertEqual(rec["dead_classes_hit"], [])

    def test_f2_5_subspace_example_classified(self):
        # recorded real 10-point cover of F2^5 (PR 2773 n5 control witness):
        # split (4, 6); A = span{3, 5} is a subspace, so A vanishes on every
        # character outside its annihilator; D = 1 + B vanishes on none.
        S = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
        rec = vanish.classify_cover(S, 5)
        self.assertEqual(rec["split"], (4, 6))
        self.assertEqual(rec["k_A"], 12)  # character level: 15 - 3 annihilator pairs
        self.assertEqual(rec["k_D"], 0)
        self.assertEqual(rec["dead_classes_hit"], [])
        # at every A-vanishing character L2 forces the A split (2, 2); the
        # D split must pass the class floor of F2^4 (need 8).
        self.assertEqual(len(rec["vanish_rows"]), 12)
        for (psi, side, a_sp, d_sp, verdict) in rec["vanish_rows"]:
            self.assertEqual(side, "A")
            self.assertEqual(a_sp, (2, 2))
            self.assertEqual(verdict, "survives")


class TestCensusF5(unittest.TestCase):
    def test_census_shard_smoke(self):
        rec = vanish.census_f5(shard=0, shards=16, keep_covers=5, max_combos=100000)
        self.assertIn(rec["status"], ("complete", "partial"))
        self.assertGreater(rec["combos"], 0)
        for cov in rec["covers"]:
            self.assertTrue(vanish.covers_f2n(cov, 5))
        self.assertEqual(rec["dead_classes_hit"], [])


class TestClassSearch(unittest.TestCase):
    def test_class_search_smoke(self):
        res = vanish.search_class(12, 6, side="A_vanish", other_split=(3, 3), restarts=2, seed=3, seconds=3.0)
        self.assertIn("found", res)
        if res["found"]:
            A, D = res["A"], res["D"]
            ok1, ok2 = vanish.cover_conditions(A, D, 6)
            self.assertTrue(ok1 and ok2)
            self.assertEqual(vanish.split_sizes(A, 1, 6), (6, 6))  # forced vanishing side


if __name__ == "__main__":
    unittest.main(verbosity=2)
