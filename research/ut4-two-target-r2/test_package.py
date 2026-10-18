"""Focused tests for the r=2 two-target UT4 search (stdlib; run from anywhere)."""
import random, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import search as S


def direct_word(r, w):
    """CrocSwap/integer-mult-bounds#1662's direct word: (abcb)^2 on each target coordinate projector."""
    word = []
    for i in range(w):
        e = 1 << i
        word += [(g, e, e) for g in 'abcbabcb']
    return word


class Formal(unittest.TestCase):
    def test_group_has_64_elements_and_central_z(self):
        self.assertEqual(len(S.G), 64)
        z = S.idx[S.Z]
        for g in range(64):
            self.assertEqual(S.MUL[g][z], S.MUL[z][g])

    def test_formal_product_is_in_word_order(self):
        """On one role a factor is just [g]; the word (a, b) must give [a][b], not [b][a]."""
        a, b = S.GEN['a'], S.GEN['b']
        self.assertNotEqual(S.MUL[a][b], S.MUL[b][a])
        self.assertEqual(S.formal([('a', 1, 1), ('b', 1, 1)], 1), [[1 << S.MUL[a][b]]])

    def test_direct_sixteen_call_word_hits_target(self):
        self.assertTrue(S.formal_ok(direct_word(2, 2), 2, 2))

    def test_every_single_omission_fails(self):
        word = direct_word(2, 2)
        for i in range(len(word)):
            self.assertFalse(S.formal_ok(word[:i] + word[i + 1:], 2, 2))

    def test_pr1662_failed_twelve_call_trial_fails(self):
        trial = [('a', 1, 1), ('b', 1, 1), ('c', 1, 3), ('a', 3, 1), ('b', 1, 1), ('c', 1, 2)] * 2
        self.assertFalse(S.formal_ok(trial, 2, 2))


class Quotient(unittest.TestCase):
    def test_formal_hit_implies_quotient_hit(self):
        self.assertTrue(S.q_ok(direct_word(2, 2), 2, 2))

    def test_profile_formulas_match_direct_quotient_products(self):
        """The search's profile formulas assume zero a- and c-totals (the degree-one
        coefficients); compare them with direct quotient products in exactly that case."""
        rng = random.Random(1662)
        seen = {'a': 0, 'c': 0, 'both': 0}
        for _ in range(6000):
            nb = rng.randint(1, 6)
            bseq = [S.rank_one(rng.randint(1, 3), rng.randint(1, 3)) for _ in range(nb)]
            word = []
            for j in range(nb + 1):
                gap = [(rng.choice('ac'), rng.randint(1, 3), rng.randint(1, 3)) for _ in range(rng.randint(0, 3))]
                word += gap
                if j < nb:
                    word.append(('b',) + S.split(bseq[j]))
            coef = S.q_image(word, 2)
            P, Q = S.prefix_profile(word, 'a'), S.suffix_profile(word, 'c')
            ta, tc = coef.get('a', 0), coef.get('c', 0)
            if ta == 0:
                seen['a'] += 1
                self.assertEqual(S.side_coeffs(bseq, P), tuple(coef.get(m, 0) for m in ('ab', 'ba', 'aba', 'bab')))
            if tc == 0:
                seen['c'] += 1
                self.assertEqual(S.side_coeffs(bseq, Q), tuple(coef.get(m, 0) for m in ('cb', 'bc', 'cbc', 'bcb')))
            if ta == 0 and tc == 0:
                seen['both'] += 1
                self.assertEqual(S.cross_coeffs(bseq, P, Q), (coef.get('abc', 0), coef.get('cba', 0)))
        self.assertGreater(min(seen.values()), 50, seen)


class FastPath(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(14)

    def random_bseq(self):
        return [S.rank_one(self.rng.randint(1, 3), self.rng.randint(1, 3)) for _ in range(6)]

    def test_side_tables_match_side_coeffs(self):
        for _ in range(200):
            bseq = self.random_bseq()
            tab = S.side_tables(bseq)
            P = [self.rng.randrange(16) for _ in range(6)]
            ab, ba, aba, bab = S.side_coeffs(bseq, P)
            self.assertEqual(S.side_value(tab, P), ab | ba << 4 | aba << 8 | bab << 12)

    def test_key_cross_matches_cross_coeffs(self):
        for _ in range(500):
            bseq = self.random_bseq()
            P = [self.rng.randrange(16) for _ in range(6)]
            Q = [self.rng.randrange(16) for _ in range(6)]
            self.assertEqual(S.key_cross(S.key(bseq, P), S.key(bseq, Q)), S.cross_coeffs(bseq, P, Q))


    def test_indexed_key_pairs_equal_brute_force(self):
        hits = 0
        for _ in range(40):
            keys = {tuple(self.rng.randrange(64) for _ in range(4)) for _ in range(300)}
            brute = {(ka, kc) for ka in keys for kc in keys if S.key_cross(ka, kc) == (9, 9)}
            self.assertEqual(set(S.key_pairs(keys)), brute)
            hits += len(brute)
        self.assertGreater(hits, 0)


class Completeness(unittest.TestCase):
    def planted(self, rng):
        """Random (4,6,4) word on two roles with zero a- and c-totals."""
        while True:
            labels = list('aaaabbbbbbcccc')
            rng.shuffle(labels)
            word = [(g, rng.randint(1, 3), rng.randint(1, 3)) for g in labels]
            if not S.q_image(word, 2).get('a') and not S.q_image(word, 2).get('c'):
                return word

    def test_enumeration_regenerates_planted_words(self):
        rng = random.Random(964)
        for _ in range(2):
            word = self.planted(rng)
            bt = tuple(S.rank_one(x, y) for g, x, y in word if g == 'b')
            tab = S.side_tables(bt)
            P, Q = S.prefix_profile(word, 'a'), S.suffix_profile(word, 'c')
            want = (S.side_value(tab, P), S.side_value(tab, Q), S.key_cross(S.key(bt, P), S.key(bt, Q)))
            seen = []
            S.fast_search(bseqs=[bt], want=want, seen=seen)
            self.assertIn(word, seen)

    def test_quotient_map_is_multiplicative(self):
        self.assertEqual(S.check_quotient_homomorphism(), 4096)


class Driver(unittest.TestCase):
    def test_one_target_eight_calls_found_at_r1(self):
        sols = S.search(1, 1, (2, 4, 2))
        self.assertIn(tuple(direct_word(1, 1)), sols)

    def test_one_target_seven_calls_impossible_at_r1(self):
        self.assertEqual(S.search(1, 1, (2, 3, 2)), [])


if __name__ == '__main__':
    unittest.main()
