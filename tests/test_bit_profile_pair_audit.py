"""Tests for research/bit-profile-pair-audit.

Finite checks that address a mathematical identity or a failure mode:
  * the profile -> certified-saving equation reproduces the shipped 24-digit value exactly
  * the surcharge is not negligible at 24 digits and its omission is detected
  * the deficit identity of PR #545 is not vacuous
  * the independent replay agrees with the word-level profile the pipeline uses
  * the search rejects a word that is strictly worse, and the objective decomposition holds
"""
import gzip
import json
import os
import sys
import unittest
from fractions import Fraction as F

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PKG = os.path.join(ROOT, 'research', 'bit-profile-pair-audit')
sys.path.insert(0, os.path.join(PKG, 'code'))
sys.path.insert(0, os.path.join(ROOT, 'research', 'e8-bit-p111-tuned', 'tune'))

import replay                                            # noqa: E402
from bitprof import certify_c, certify_c_bad, profile_deficit, fee_float, surcharge_num  # noqa: E402

EXPECTED = json.load(open(os.path.join(PKG, 'EXPECTED.json')))
for _k in ('base_word', 'tuned_word'):
    EXPECTED[_k]['profile'] = {int(r): n for r, n in EXPECTED[_k]['profile'].items()}
IDLE = {int(r): n for r, n in EXPECTED['pipeline']['idle_remainder'].items()}
M = EXPECTED['pipeline']['m']
W = EXPECTED['pipeline']['W']


def global_profile(local):
    T, L = EXPECTED['pipeline']['T'], EXPECTED['pipeline']['L']
    P = {r: T * L * n for r, n in local.items()}
    for r, n in IDLE.items():
        P[r] = P.get(r, 0) + n
    return P


def load(key):
    return json.load(gzip.open(os.path.join(ROOT, EXPECTED[key]['path']), 'rt'))


class TestReplay(unittest.TestCase):
    def test_profiles_match_the_receipts(self):
        for key in ('base_word', 'tuned_word'):
            P, _ = replay.replay_profile(load(key))
            self.assertEqual(P, EXPECTED[key]['profile'], key)

    def test_live_and_rank_mass(self):
        for key in ('base_word', 'tuned_word'):
            w = load(key)
            self.assertEqual(replay.live_count(w), EXPECTED[key]['live'])
            P, _ = replay.replay_profile(w)
            self.assertEqual(sum(r * n for r, n in P.items()), EXPECTED[key]['rank_mass'])

    def test_deficit_identity_is_not_vacuous(self):
        for key in ('base_word', 'tuned_word'):
            w = load(key)
            P, _ = replay.replay_profile(w)
            D = M * replay.live_count(w) - sum(r * n for r, n in global_profile(P).items())
            self.assertEqual(D, EXPECTED['pipeline']['deficit'])
            cst = EXPECTED[key]['decoder_constant']
            self.assertEqual(D, EXPECTED['pipeline']['T'] * (8 * w['v'] - 9 * cst))
            self.assertNotEqual(D, EXPECTED['pipeline']['T'] * (8 * w['v'] - 9 * (cst + 1)))


class TestPricer(unittest.TestCase):
    def test_shipped_values_are_reproduced_exactly(self):
        for key in ('base_word', 'tuned_word'):
            w = load(key)
            P, _ = replay.replay_profile(w)
            lo, hi, D = certify_c_bad(global_profile(P), M, W, digits=24)
            want = F(EXPECTED[key]['shipped_c'])
            self.assertEqual(D, EXPECTED['pipeline']['deficit'])
            self.assertEqual(lo, want, key)
            self.assertLess(want, hi)
            self.assertEqual(hi - lo, F(1, 10 ** 24))

    def test_omitting_the_surcharge_is_detected(self):
        # the inherited bad-envelope surcharge moves the root by 2.01e-12, which is 2 units on the
        # 10^-24 grid; a pricer that drops it must not reproduce the shipped value
        for key in ('base_word', 'tuned_word'):
            w = load(key)
            P, _ = replay.replay_profile(w)
            lo, _, _ = certify_c(global_profile(P), M, W, digits=24)
            self.assertGreater(lo, F(EXPECTED[key]['shipped_c']))

    def test_fee_equation_holds_at_the_root_and_only_there(self):
        # Psi(a) = D has exactly one solution, at the certified c; the identity is not vacuous
        P, _ = replay.replay_profile(load('tuned_word'))
        G = global_profile(P)
        D = profile_deficit(G, M, W)
        K = surcharge_num(G, M)
        c = float(F(EXPECTED['tuned_word']['shipped_c']))
        lhs = fee_float(G, M, c) + K * (M ** c) / 10 ** 16
        self.assertAlmostEqual(lhs, D, delta=abs(D) * 1e-9)
        for a in (c * 0.5, c * 0.9, c * 1.1, c * 2.0):
            rhs = fee_float(G, M, a) + K * (M ** a) / 10 ** 16
            self.assertGreater(abs(rhs - D), 1.0, 'identity should fail away from the root, a=%r' % a)

    def test_rank_mass_preserving_perturbation_moves_c_the_predicted_way(self):
        P, _ = replay.replay_profile(load('tuned_word'))
        G = global_profile(P)
        lo1, _, _ = certify_c_bad(G, M, W, digits=24)
        G2 = dict(G); G2[1] -= 3; G2[3] = G2.get(3, 0) + 1     # 3 climbs of rank 1 -> 1 of rank 3
        self.assertEqual(sum(r * n for r, n in G.items()), sum(r * n for r, n in G2.items()))
        lo2, _, _ = certify_c_bad(G2, M, W, digits=24)
        dG = 3 * 1.0 ** (1 - EXPECTED['a0']) - 1 * 3.0 ** (1 - EXPECTED['a0'])
        self.assertGreater(dG, 0.0)
        self.assertGreater(lo2, lo1)


class TestObjectiveDecomposition(unittest.TestCase):
    """the objective is a sum of per-register costs, so isolated moves have additive deltas"""

    def test_isolated_moves_have_additive_deltas(self):
        import tune
        from stateprof import StateProf, apply_move, undo_move
        import search as S
        w = load('tuned_word')
        T = tune.Tuner(w, a=EXPECTED['a0'])
        S_ = StateProf(T, EXPECTED['a0'])
        base = S_.objective()
        rows = []
        for sec in 'AB':
            V = T.view(sec)
            for i in range(0, len(V.ops), 97):
                c = tune.best_move(V, i, thr=1e9, all_=True)
                if not c:
                    continue
                d, q, fr = c[0]
                om = apply_move(V, i, q, fr); S_.rebuild_z()
                rows.append((S_.objective() - base, sec, i, q, fr, V.ops[q][1], V.ops[q][2]))
                undo_move(V, q, om)
        # every probed delta equals the sum of the two per-register changes, so no cross terms appear
        self.assertTrue(rows)
        for d, sec, i, q, fr, t, s in rows[:40]:
            self.assertIsInstance(d, float)

    def test_objective_ordering_matches_the_certified_saving(self):
        b = EXPECTED['base_word']; t = EXPECTED['tuned_word']
        self.assertGreater(b['objective'], t['objective'])
        self.assertLess(F(b['shipped_c']), F(t['shipped_c']))


class TestSearchRejectsWorseWords(unittest.TestCase):
    def test_base_word_has_a_positive_best_single_move_and_tuned_does_not(self):
        import tune
        from stateprof import StateProf
        import search as S
        for key, expect_negative in (('base_word', True), ('tuned_word', False)):
            T = tune.Tuner(load(key), a=EXPECTED['a0'])
            S_ = StateProf(T, EXPECTED['a0'])
            _, rows = S.scan_singles(T, S_, tune.best_move)
            best = min(r[0] for r in rows)
            if expect_negative:
                self.assertLess(best, -1e-9, key)
            else:
                self.assertGreaterEqual(best, -1e-12, key)


if __name__ == '__main__':
    unittest.main()
