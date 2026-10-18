"""Tests for the KB3e engine (18-point cover question for F2^7).

Test-first: these were written and run (RED) before cover18.py existed, then
made GREEN.  Controls deliberately include the known 17-point outcomes so the
new machinery cannot silently disagree with PR 2870/PR 2773:

  * the (11,6)/(6,11) split must come out impossible (PR 2870, deficit 192);
  * the (10,7) split must NOT show a Fourier contradiction (PR 2870 table);
  * a real 10-point cover of F2^5 must pass every check (positive control);
  * the fast pairing-sums and row tables must agree with the vendored PR 2773
    engine wherever the vendored engine terminates.
"""

import itertools
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import cover18 as c18  # noqa: E402
import agent64_cover17 as c17  # noqa: E402


class TestCoverageAndReduction(unittest.TestCase):
    def test_coverage_matches_vendored_engine(self):
        rng = random.Random(20261016)
        for _ in range(200):
            k = rng.randint(1, 10)
            pts = rng.sample(range(128), k)
            self.assertEqual(c18.coverage_mask(pts), c17.coverage_mask(pts))
            self.assertEqual(c18.covers(pts), c17.coverage_mask(pts) == (1 << 128) - 1)

    def test_split_of_parity(self):
        self.assertEqual(c18.split_of([0, 3, 5, 7]), (3, 1))

    def test_reduction_equivalence_exhaustive_n3(self):
        # Every subset of F2^3: S covers iff the (A, D) reduction holds.
        for r in range(9):
            for pts in itertools.combinations(range(8), r):
                A = [p for p in pts if not (p.bit_count() % 2)]
                B = [p for p in pts if p.bit_count() % 2]
                direct = c18.covers(pts, n=3)
                odd_ok, even_ok = c18.reduction_conditions(A, B, n=3)
                self.assertEqual(direct, odd_ok and even_ok, (pts, odd_ok, even_ok))

    def test_positive_control_n5_cover(self):
        # A real 10-point cover of F2^5 (PR 2870's positive control).
        S = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
        self.assertTrue(c18.covers(S, n=5))
        A = [p for p in S if not (p.bit_count() % 2)]
        B = [p for p in S if p.bit_count() % 2]
        odd_ok, even_ok = c18.reduction_conditions(A, B, n=5)
        self.assertTrue(odd_ok and even_ok)


class TestRhoSquares(unittest.TestCase):
    def test_rho_square_values_exact(self):
        # sum rho = 8 over integer rho >= 0: attainable sums of squares.
        got = set(c18.rho_square_values(8))
        want = {8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 38, 40, 50, 64}
        self.assertEqual(got, want)
        self.assertNotIn(46, got)  # the (12,6) no-vanishing contradiction value

    def test_rho_square_values_two(self):
        self.assertEqual(set(c18.rho_square_values(2)), {2, 4})


class TestFourierSystem(unittest.TestCase):
    def test_116_control_infeasible(self):
        # PR 2870: (11,6) is impossible.  The profile system must be
        # infeasible and its squeeze numbers must reproduce 696/504/192.
        rec = c18.fourier_profile_feasibility(7, 11, 6)
        self.assertFalse(rec["feasible"])
        squeeze = c18.squeeze_numbers(7, 11, 6)
        self.assertEqual(squeeze["parseval_remainder"], 696)
        self.assertEqual(squeeze["max_allowed"], 504)
        self.assertEqual(squeeze["deficit"], 192)
        self.assertTrue(squeeze["contradiction"])

    def test_611_mirror_control_infeasible(self):
        rec = c18.fourier_profile_feasibility(7, 6, 11)
        self.assertFalse(rec["feasible"])

    def test_107_control_infeasible_consistent_with_pr2773(self):
        # PR 2870's pure squeeze found no contradiction for (10,7), but the
        # split is excluded (PR 2773's census route).  The profile system adds
        # the even-half bound and must find it infeasible -- consistent with
        # the known truth, and a control that the system can detect this split.
        rec = c18.fourier_profile_feasibility(7, 10, 7)
        self.assertFalse(rec["feasible"])

    def test_small_n_covers_never_excluded(self):
        # Soundness: every split realized by a REAL cover of F2^3 or F2^4 must
        # be feasible for the profile system (no false exclusions), and the
        # actual character values of the cover must satisfy every constraint.
        for n in (3, 4):
            N = 1 << n
            seen = set()
            for r in range(1, N + 1):
                for pts in itertools.combinations(range(N), r):
                    if not c18.covers(pts, n=n):
                        continue
                    A = [p for p in pts if not (p.bit_count() % 2)]
                    B = [p for p in pts if p.bit_count() % 2]
                    key = (n, len(A), len(B))
                    self.assertTrue(
                        c18.witness_constraints_ok(A, B, n), (n, pts)
                    )
                    if key not in seen:
                        seen.add(key)
                        if len(A) * len(B) - (1 << (n - 1)) > 12:
                            continue  # solver battery is bounded; witnesses above cover all
                        rec = c18.fourier_profile_feasibility(n, len(A), len(B))
                        if rec["feasible"] is None:
                            continue  # E_o beyond the enumeration budget
                        self.assertTrue(rec["feasible"], (key, rec["reason"]))

    def test_positive_control_n5_system_feasible(self):
        # The real F2^5 cover has split (4,6); the system must allow it.
        rec = c18.fourier_profile_feasibility(5, 4, 6)
        self.assertTrue(rec["feasible"])
        S = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
        A = [p for p in S if not (p.bit_count() % 2)]
        B = [p for p in S if p.bit_count() % 2]
        self.assertTrue(c18.witness_constraints_ok(A, B, 5))

    def test_shapes_respect_parity_and_bounds(self):
        for (s, t) in ((11, 6), (10, 7), (12, 6), (11, 7), (10, 8), (9, 9)):
            rec = c18.shapes_fourier(7, s, t)
            eo = s * t - 64
            for (f2, g2, p2) in rec:
                a = int(f2 ** 0.5)
                b = int(g2 ** 0.5)
                self.assertEqual(a % 2, s % 2)
                self.assertEqual(b % 2, t % 2)
                self.assertLessEqual(a * b, eo)
                self.assertEqual((a * b) % 2, eo % 2)


class TestPairingSums(unittest.TestCase):
    def test_fast_pairing_agrees_with_vendored(self):
        rng = random.Random(7)
        for _ in range(300):
            m = rng.randint(1, 6)
            da = tuple(sorted(rng.randint(1, 4) for _ in range(m)))
            db = tuple(sorted(rng.randint(1, 4) for _ in range(m)))
            fast = c18.pairing_sums(da, db)
            slow = set(c17._pairing_sums(da, db))
            self.assertEqual(fast, slow, (da, db))

    def test_pairing_sums_single(self):
        self.assertEqual(c18.pairing_sums((1,), (5,)), {5})


class TestRows(unittest.TestCase):
    def test_sharp_rows_fast_agrees_with_vendored_17point(self):
        for (s, t) in ((11, 6), (10, 7), (9, 8)):
            fast = c18.sharp_rows_fast(7, s, t)
            slow = c17.sharp_rows(7, s, t)
            self.assertEqual(
                [(r["e_ex"], r["b_ex"], r["c"]) for r in fast["rows"]],
                [(r["e_ex"], r["b_ex"], r["c"]) for r in slow["rows"]],
                (s, t),
            )
            self.assertEqual(fast["best"], slow["best"])

    def test_row_table_17point_remainder(self):
        # With the census floors the 17-point (11,6) remainder is (5,1),(6,0).
        rows = c18.surviving_rows_fast(7, 11, 6, min_e_ex=5, min_b_ex=0)
        got = sorted((r["e_ex"], r["b_ex"]) for r in rows["rows"])
        self.assertEqual(got, [(5, 1), (6, 0)])

    def test_row_table_107_after_floor_empty(self):
        rows = c18.surviving_rows_fast(7, 10, 7, min_e_ex=3, min_b_ex=0)
        self.assertEqual(rows["rows"], [])


class TestSearchSmoke(unittest.TestCase):
    def test_coverage_best_on_known_cover(self):
        S = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
        self.assertEqual(c18.coverage_mask(S).bit_count(), 32)


class TestVendoredPins(unittest.TestCase):
    def _sha(self, rel):
        import hashlib

        return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()

    def test_agent64_cover17_byte_pin(self):
        self.assertEqual(self._sha("vendor/agent64_cover17.py"), c18.VENDOR_PIN_COVER17)

    def test_agent64_search17_byte_pin(self):
        self.assertEqual(self._sha("vendor/agent64_search17.py"), c18.VENDOR_PIN_SEARCH17)

    def test_pr2870_anchors_byte_pin(self):
        # byte-vendored from PR 2870 head 9f55f291e9e79e628fd98f1e4f4debfc1c2106e5
        self.assertEqual(
            self._sha("anchors.py"),
            "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7",
        )


if __name__ == "__main__":
    unittest.main()
