#!/usr/bin/env python3
"""Independent pins for verify.py of research/four-swap-balanced-j3-layer.

The algebraic expectations here were derived by hand (2x2 matrix products over
F2 and the expansion of ([a]+1)([b]+1)([a]+1)) before verify.py existed, so a
failure indicates a bug in the checker, not in the expectation. Stdlib only.
"""
import importlib.util
import itertools
import pathlib
import random
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("j3verify", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class AlgebraPins(unittest.TestCase):
    def setUp(self):
        V.build()

    def test_involution_squares_vanish(self):
        for g in (V.A, V.B, V.S):
            x = V.gplus(g)
            self.assertEqual(V.rmul(x, x), 0)

    def test_one_swap_word_at_r1(self):
        # The three-call word aba at r=1 (N = [1]) equals [s] exactly:
        # each factor I + ([g]+1) collapses to [g] in dimension one.
        labels = (V.A, V.B, V.A)
        word = V.word_value(1, labels, (V.idem(1, 1, 1),) * 3)
        self.assertEqual(word, (1 << V.idx(V.S),))

    def test_xyx_pin(self):
        # Hand expansion: ([a]+1)([b]+1)([a]+1) = [aba] + [ab] + [ba] + [b]
        # with NO identity term (the two [1] summands cancel over F2).
        x, y = V.gplus(V.A), V.gplus(V.B)
        got = V.rmul(V.rmul(x, y), x)
        ab = V.idx(V.mm2(V.A, V.B))
        ba = V.idx(V.mm2(V.B, V.A))
        want = (1 << V.idx(V.S)) ^ (1 << ab) ^ (1 << ba) ^ (1 << V.idx(V.B))
        self.assertEqual(got, want)

    def test_layer_expansion_identity(self):
        # prod(1+eps_i) == 1 + sum eps_i + sum_{i<j} eps_i eps_j  (mod J^3),
        # in the exact quotient for seeded random words.
        rng = random.Random(20261014)
        idems = V.rank_one_idempotents(4)
        lab = (V.A, V.B)
        for _ in range(50):
            q = rng.randrange(1, 8)
            labels = tuple(lab[rng.randrange(2)] for _ in range(q))
            mats = tuple(rng.choice(idems) for _ in range(q))
            self.assertTrue(V.layer_expansion_holds(4, labels, mats))


class WordControls(unittest.TestCase):
    def setUp(self):
        V.build()

    def test_direct_words_hit_targets(self):
        for r, labels, mats, k in V.direct_control_words():
            self.assertEqual(V.word_value(r, labels, mats), V.target(r, k),
                             "direct word must realize the target")

    def test_mutated_words_fail(self):
        for r, labels, mats, k, mut in V.mutation_controls():
            self.assertNotEqual(V.word_value(r, labels, mats), V.target(r, k),
                                "mutation control must fail: " + mut)

    def test_conjugation_closure(self):
        rng = random.Random(7)
        idems = V.rank_one_idempotents(4)
        gl = V.gl_elements(4)
        for _ in range(50):
            n = rng.choice(idems)
            u = rng.choice(gl)
            c = V.conjugate(4, u, n)
            self.assertIn(c, idems)


class SearchControls(unittest.TestCase):
    def setUp(self):
        V.build()

    def test_search_finds_known_small_instances(self):
        # Smallest falsifying instances first: where a balanced word is known
        # to exist, the search must actually find one.
        r1 = V.search(1, 3, 1, 1, samples=2000, seed=11)
        self.assertIsNotNone(r1["full_witness"], "r=1, q=3, 1a2b must find bab")
        r2 = V.search(2, 6, 3, 2, samples=20000, seed=12)
        self.assertIsNotNone(r2["full_witness"], "r=2, q=6, 3a3b must find aba|bab")

    def test_layer_is_a_strict_relaxation(self):
        # Honesty control: a word that passes the J^3 layer check but fails
        # full formal equality must exist at a known-solvable instance.
        r2 = V.search(2, 6, 3, 2, samples=20000, seed=12)
        self.assertGreater(r2["layer_hits"], 0)
        self.assertIsNotNone(r2["layer_only_witness"])
        labels, mats = r2["layer_only_witness"]
        self.assertTrue(V.layer_value_ok(2, labels, mats, 2))
        self.assertNotEqual(V.word_value(2, labels, mats), V.target(2, 2))


class RestoredRoleSignQuotient(unittest.TestCase):
    """Regression control for the review follow-up on
    https://github.com/CrocSwap/integer-mult-bounds/pull/1755.

    At r = 5 with endpoint diag([S],[S],[S],[S],1) the fifth role is restored
    with the identity boundary: its target augmentation is zero, so the sign
    quotient forces sum N_i = diag(I_4, 0), not I_5.  Conditioning on I_5
    would exclude every solution to that endpoint.  Hand derivation: rho([g])
    = 1 + sign(g) z is the sign quotient F2[G] -> F2[z]/(z^2) with z^2 = 0,
    every paid factor 1 + ([g]+1) N reduces to 1 + z N (a and b are odd), so
    the word reduces to 1 + z sum N_i while the endpoint reduces to
    1 + z diag(I_4, 0); comparing z-coefficients gives sum N_i = diag(I_4,0).
    """

    def setUp(self):
        V.build()

    def test_sign_quotient_is_permutation_sign(self):
        # The quotient is determined by the permutation sign of GL_2(F2) on
        # the three nonzero vectors: even elements (identity, the two
        # 3-cycles) reduce to 0, odd ones (the three transpositions, incl.
        # a, b, S) to z.  This must agree with the J^2 = J^3 reduction.
        for g in V.ELEMS:
            self.assertEqual(V.RED[V.gplus(g)] == 0, V.perm_sign(g) == 0)
        self.assertEqual([V.perm_sign(g) for g in (V.A, V.B, V.S)], [1, 1, 1])
        self.assertEqual(V.perm_sign(V.IDE), 0)

    def test_fifth_role_target_augmentation_is_zero(self):
        zt = V.zcoef_mR(5, V.target(5, 4))
        self.assertEqual(zt, V.diag_m(5, 4), "endpoint z-coefficient is diag(I_4,0)")
        self.assertEqual((zt >> 24) & 1, 0, "fifth role's augmentation must be zero")
        self.assertNotEqual(zt, V.ident_m(5), "I_5 must not be the forced condition")
        self.assertEqual(zt ^ V.ident_m(5), 1 << 24, "they differ only in the (5,5) entry")
        # The retained r = 4 statement is unchanged: all four roles swapped.
        self.assertEqual(V.zcoef_mR(4, V.target(4, 4)), V.ident_m(4))

    def test_endpoint_witness_and_i5_overconstraint(self):
        labels = (V.A, V.B, V.A) * 2 + (V.B, V.A, V.B) * 2
        mats = (V.idem(5, 1, 1),) * 3 + (V.idem(5, 2, 2),) * 3 + \
               (V.idem(5, 4, 4),) * 3 + (V.idem(5, 8, 8),) * 3
        self.assertEqual(V.word_value(5, labels, mats), V.target(5, 4),
                         "12-call disjoint word must realize the endpoint")
        total = 0
        for n in mats:
            total ^= n
        self.assertEqual(total, V.diag_m(5, 4))
        self.assertNotEqual(total, V.ident_m(5),
                            "I_5 conditioning would reject this solution")
        self.assertTrue(V.layer_value_ok(5, labels, mats, 4))
        # Forcing the total to I_5 must break the endpoint layer equation.
        self.assertEqual(total ^ V.idem(5, 16, 16), V.ident_m(5))
        self.assertFalse(V.layer_value_ok(5, labels + (V.A,),
                                          mats + (V.idem(5, 16, 16),), 4))

    def test_layer_iff_sum_is_diag_i4_zero(self):
        rng = random.Random(20261016)
        idems = V.rank_one_idempotents(5)
        zt = V.diag_m(5, 4)
        for _ in range(200):
            q = rng.randrange(2, 8)
            labels = tuple((V.A, V.B)[rng.randrange(2)] for _ in range(q))
            mats = tuple(rng.choice(idems) for _ in range(q))
            total = 0
            for n in mats:
                total ^= n
            self.assertEqual(V.layer_value_ok(5, labels, mats, 4), total == zt,
                             "r=5 layer check must be equivalent to sum N_i = diag(I_4,0)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
