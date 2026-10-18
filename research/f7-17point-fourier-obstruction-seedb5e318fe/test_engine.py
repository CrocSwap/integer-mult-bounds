"""Tests for the KB3d Fourier/Parseval obstruction (fourier17.py).

RED first: the obstruction numbers (696 > 504, deficit 192) and the row
verdicts are the claim under test; they fail until fourier17.py exists.

Claim under test (KB3d): rows (5,1) and (6,0) of the (11,6)/(6,11) family of
PR 2542's "No 17-point set covers F2^7" question are structurally impossible:
for A in the even coset and B in the odd coset of F2^7 with sizes 11 and 6
(both orders), the 66 cross sums cannot cover the 64 odd masks.  The whole
(11,6)/(6,11) family is therefore excluded, and with PR 2542 and PR 2773 the
17-point cover question is complete.
"""

import hashlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import fourier17

# Concrete parity-split sets (A even-weight, B odd-weight) in F2^7.
A11 = [0, 3, 5, 6, 9, 17, 33, 58, 65, 92, 12]
B6 = [1, 2, 4, 8, 16, 31]

# Positive control: a real 10-point cover of F2^5, split (4, 6).
COVER5 = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
COVER5_A = [0, 3, 5, 6]
COVER5_B = [1, 2, 4, 8, 16, 31]


class TestVendoredPins(unittest.TestCase):
    """Vendored byte-exact from PR 2773's package (credit: Aaron Wang)."""

    def test_agent64_cover17_byte_pin(self):
        digest = hashlib.sha256((HERE / "vendor" / "agent64_cover17.py").read_bytes())
        self.assertEqual(
            digest.hexdigest(),
            "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654",
        )

    def test_agent64_search17_byte_pin(self):
        digest = hashlib.sha256((HERE / "vendor" / "agent64_search17.py").read_bytes())
        self.assertEqual(
            digest.hexdigest(),
            "9eb1bf79ffb99b0efcdaF57916c493bc781abd4a0096d584dc6bc6ca294bf674".lower(),
        )


class TestFourierIdentities(unittest.TestCase):
    """The exact identities the obstruction is built from."""

    def test_parity_split_fixtures(self):
        self.assertTrue(all(x.bit_count() % 2 == 0 for x in A11))
        self.assertTrue(all(x.bit_count() % 2 == 1 for x in B6))
        self.assertEqual((len(A11), len(B6)), (11, 6))

    def test_ft_convolution_identity_exact(self):
        # r = 1_A * 1_B on F2^7 satisfies r_hat(s) = f_hat(s) * g_hat(s).
        self.assertTrue(fourier17.ft_convolution_ok(A11, B6, 7))

    def test_ft_odd_coset(self):
        odd = [x for x in range(128) if x.bit_count() % 2 == 1]
        ft = fourier17.ft(odd, 7)
        self.assertEqual(ft[0], 64)
        self.assertEqual(ft[127], -64)
        for s in range(1, 127):
            self.assertEqual(ft[s], 0, s)

    def test_character_parities(self):
        f = fourier17.ft(A11, 7)
        g = fourier17.ft(B6, 7)
        self.assertTrue(all(v % 2 == 1 for v in f))  # |A| = 11 odd
        self.assertTrue(all(v % 2 == 0 for v in g))  # |B| = 6 even
        self.assertEqual(f[0], 11)
        self.assertEqual(g[0], 6)
        self.assertEqual(f[127], 11)   # A in the even coset
        self.assertEqual(g[127], -6)   # B in the odd coset

    def test_forced_odd_profile(self):
        # Odd excess 2 admits only the [1,1] profile (sigma = 2c even);
        # every rho with total 2 has |rho_hat| <= 2.
        self.assertEqual(fourier17.odd_profiles(2), [[1, 1]])
        for rho in fourier17.all_rho_shapes(2):
            for v in fourier17.rho_hat_values(rho, 6):
                self.assertLessEqual(abs(v), 2)


class TestObstruction(unittest.TestCase):
    """The exact obstruction: Parseval remainder 696 > allowed 504."""

    def test_116_obstruction_exact(self):
        res = fourier17.obstruction(7, 11, 6)
        self.assertTrue(res["contradiction"])
        self.assertEqual(res["odd_excess"], 2)
        self.assertEqual(res["bounded_side"], "B")
        self.assertEqual(res["parseval_remainder"], 696)
        self.assertEqual(res["max_allowed"], 504)
        self.assertEqual(res["deficit"], 192)
        self.assertEqual(res["character_values"], [-2, 0, 2])

    def test_611_mirror_obstruction_exact(self):
        res = fourier17.obstruction(7, 6, 11)
        self.assertTrue(res["contradiction"])
        self.assertEqual(res["bounded_side"], "A")
        self.assertEqual(res["parseval_remainder"], 696)
        self.assertEqual(res["max_allowed"], 504)
        self.assertEqual(res["deficit"], 192)

    def test_not_vacuous_on_other_17point_splits(self):
        # (10,7)/(7,10)/(9,8)/(8,9) are excluded by other machinery
        # (PR 2542 rows; PR 2773 census floor); the Fourier bound alone
        # does not fire there, so this checker is not vacuously contradicting.
        for split in ((10, 7), (7, 10), (9, 8), (8, 9)):
            res = fourier17.obstruction(7, *split)
            self.assertFalse(res["contradiction"], (split, res))

    def test_positive_control_real_cover_n5(self):
        # A real 10-point cover of F2^5 must pass every check (no false
        # contradiction), and its multiplicity profile must match exactly.
        self.assertEqual(
            fourier17.sumset_mask(COVER5, 5), (1 << 32) - 1
        )
        split = fourier17.split_of(COVER5, 5)
        self.assertEqual(split, (4, 6))
        self.assertTrue(fourier17.ft_convolution_ok(COVER5_A, COVER5_B, 5))
        info = fourier17.cross_info(COVER5_A, COVER5_B, 5)
        self.assertTrue(info["covers_odd"])
        self.assertEqual(info["odd_excess"], 8)
        res = fourier17.obstruction(5, 4, 6)
        self.assertFalse(res["contradiction"])


class TestRowRemainder(unittest.TestCase):
    """The recorded remainder rows (5,1),(6,0) and their verdict."""

    def test_row_remainder_reproduced_from_vendored_rows(self):
        import agent64_cover17 as c17

        sharp = c17.sharp_rows(7, 11, 6)
        self.assertTrue(sharp["feasible"])
        self.assertEqual(
            {(r["e_ex"], r["b_ex"]) for r in sharp["rows"]},
            {(e, 6 - e) for e in range(7)},
        )
        for r in sharp["rows"]:
            self.assertEqual((r["shared"], r["c"]), (1, 1))
        # PR 2773's recorded k = 11 census floor e_ex >= 5 leaves exactly
        # the two remainder rows (5,1) and (6,0) -- the KB3d object.
        survivors = {(r["e_ex"], r["b_ex"]) for r in sharp["rows"] if r["e_ex"] >= 5}
        self.assertEqual(survivors, {(5, 1), (6, 0)})
        # Both verdicts: impossible (the obstruction kills the family).
        for row in sorted(survivors):
            self.assertTrue(fourier17.obstruction(7, 11, 6)["contradiction"], row)
        mirror = c17.sharp_rows(7, 6, 11)
        self.assertEqual(
            {(r["e_ex"], r["b_ex"]) for r in mirror["rows"] if r["e_ex"] >= 5},
            {(5, 1), (6, 0)},
        )

    def test_odd_translation_mirror(self):
        # S -> S + u (u odd) swaps the (11,6)/(6,11) splits and preserves S+S.
        S = sorted(A11 + B6)
        self.assertEqual(fourier17.split_of(S, 7), (11, 6))
        T = [x ^ 1 for x in S]
        self.assertEqual(fourier17.split_of(T, 7), (6, 11))
        self.assertEqual(fourier17.sumset_mask(S, 7), fourier17.sumset_mask(T, 7))


if __name__ == "__main__":
    unittest.main(verbosity=2)
