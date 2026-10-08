"""Scalar stage compression, dirty restoration and basis-placement caveats."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from experiments import ternary_depth_exchange as td


class ScalarIdentities(unittest.TestCase):
    def test_only_characteristic_three_merges_these_two_stages(self):
        self.assertTrue(td.operate(3, "merged-final-stages"))
        for p in (2, 5, 7):
            self.assertFalse(td.operate(p, "merged-final-stages"))

    def test_direct_exchange_restores_all_dirty_basis_inputs(self):
        for p in (2, 3, 5, 7):
            with self.subTest(field=p):
                got = td.operate(p, "exchange-with-reflection")
                self.assertTrue(got["exact_exchange"])
                self.assertTrue(got["scratch_restored"])
                self.assertEqual(got["reflection_is_identity"], p == 2)

    def test_signed_transvection_is_square_zero_only_at_required_characteristic(self):
        m = [[1, -1], [1, 0]]
        for p in (2, 3, 5, 7):
            shifted = [[(m[i][j] + int(i == j)) % p for j in range(2)] for i in range(2)]
            self.assertEqual(td.mul(shifted, shifted, p) == [[0, 0], [0, 0]], p == 3)


class OnePassScope(unittest.TestCase):
    def test_bitplane_elimination_matches_dense_elimination(self):
        for values in product(range(3), repeat=6):
            matrix = [list(values[:3]), list(values[3:])]
            planes = [(sum(1 << i for i, x in enumerate(row) if x == 1),
                       sum(1 << i for i, x in enumerate(row) if x == 2)) for row in matrix]
            self.assertEqual(td.ternary_bitplane_rank(planes), td.rank(matrix, 3))

    def test_one_pass_noise_and_basis_caveat(self):
        got = td.one_pass_and_basis_controls()
        self.assertEqual(got["noise_rank"], got["source_dimension"])
        self.assertEqual(got["arbitrary_target_blocks_checked"], 81)
        self.assertTrue(got["basis_can_zero_decoder_noise"])
        self.assertTrue(got["early_basis_does_not_fix_post_swap_noise"])

    def test_basis_change_commutes_with_load_but_not_swap(self):
        # Coordinates are X, source-slot u, remaining dirty role w.
        p = 3
        u = [[1, 0, 0], [0, 1, -1], [0, 0, 1]]
        load = [[1, 0, 0], [1, 1, 0], [0, 0, 1]]
        swap = [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
        self.assertEqual(td.mul(u, load, p), td.mul(load, u, p))
        self.assertNotEqual(td.mul(u, swap, p), td.mul(swap, u, p))

    def test_trivial_decoder_passes_necessary_condition(self):
        # The obstruction is deliberately scoped: A=S has no dirty noise.
        v = [[1, 0], [0, 1], [0, 0]]
        s = [[1, 0, 0], [0, 1, 0]]
        self.assertEqual(td.mul(s, v, 3), td.eye(2))
        vs = td.mul(v, s, 3)
        complement = [[int(i == j) - vs[i][j] for j in range(3)] for i in range(3)]
        self.assertEqual(td.mul(s, complement, 3), [[0, 0, 0], [0, 0, 0]])


class ResearchArtifacts(unittest.TestCase):
    def test_shared_bank_guard_exact_exponent_and_headroom(self):
        self.assertLess(22120 ** 1000, 21952 ** 1001)
        beta, rho, zeta = Q(1, 1000), Q(1001, 1000), Q(1, 10000)
        c1 = beta + (1 - beta) * rho + zeta
        self.assertEqual(c1, Q(1001099, 10 ** 6))
        self.assertLess(Q(4999, 10000) * c1, 1)
        self.assertEqual((1 - beta) * Q(39, 10 ** 9), Q(38961, 10 ** 12))

    def test_standalone_certificate(self):
        saved = json.loads((ROOT / "certificates/ternary-depth.json").read_text())
        self.assertEqual(saved, td.certificate())


if __name__ == "__main__":
    unittest.main()
