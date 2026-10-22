#!/usr/bin/env python3
"""Rejecting controls for verify.py."""
import math
import unittest
from fractions import Fraction as Q

import verify as v


class Controls(unittest.TestCase):
    def test_old_atom_fails_adapter_for_4470(self):
        c = v.CASES["pr4470"]
        a = v.ordinary_saving(c["C1"], Q(3, 1000))
        self.assertLessEqual(Q(3, 1000), a)

    def test_literal_h0003_bound_false_at_atom_0004(self):
        # h^.004 L^2.008 <= C h^.003 L^3 fails once h^.001 > C L^.992
        logC, L = 2 * v.CASES["pr4470"]["log2N"] + 64, 10.0 ** 18
        logh = 0.99 * L
        lhs = 0.004 * logh + 2.008 * math.log2(L)
        rhs = logC + 0.003 * logh + 3 * math.log2(L)
        self.assertGreater(lhs, rhs)

    def test_beta_predicate_passes_broken_atom(self):
        atom = Q(99999, 100000)
        a = v.ordinary_saving(v.CASES["pr4470"]["C1"], atom)
        self.assertGreater(v.CASES["pr4470"]["beta"] * (1 - atom), 0)
        self.assertFalse(atom < 1 - a)

    def test_omitting_high_matrix_lift_underreserves(self):
        N, q, w, B, S, D = 2, 3, 2, 5, 7, 3
        full = B * v.gl_order(N, q) * q ** (N * N * (w - 1))
        wrong = B * v.gl_order(N, q)
        R = wrong ** D * S
        levels = 0
        while R % full == 0 and R >= full:
            R //= full
            levels += 1
        self.assertLess(levels, D)

    def test_max_instead_of_product_underreserves(self):
        bit, cx = 12 ** 3, 48 ** 2
        self.assertLess(max(bit, cx), bit * cx)

    def test_omitted_carry_breaks_high_row(self):
        p, m = 3, 9
        g, S = ((2, 7), (4, 5)), ((1, 1), (1, 0))
        h = v.mat_mul(g, S, m)
        g0 = [[x % p for x in r] for r in g]
        G1 = [[(x - y) // p for x, y in zip(r, s)] for r, s in zip(g, g0)]
        no_carry = tuple(tuple(sum(G1[i][k] * S[k][j] for k in range(2)) % p for j in range(2)) for i in range(2))
        self.assertNotEqual(tuple(tuple(x // p for x in r) for r in h), no_carry)

    def test_stock_threshold_fails_below(self):
        c = v.CASES["pr4359"]
        Le = 1.5 * c["log2N"]
        k = v.log2_k(Le, float(c["delta"]), float(c["log2N"]))
        self.assertTrue(k is None or k + 1 >= Le)


if __name__ == "__main__":
    unittest.main()
