"""Focused tests for the fifteen-call r=2 two-target UT4 search (stdlib; run from anywhere)."""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fifteen as F  # noqa: E402
import pr1690_search as S  # noqa: E402


def planted(rng, counts):
    """Random word with the given label counts on two roles and zero a-, b- and c-totals
    (the degree-one coefficients every endpoint word has)."""
    na, nb, nc = counts
    while True:
        labels = list('a' * na + 'b' * nb + 'c' * nc)
        rng.shuffle(labels)
        word = [(g, rng.randint(1, 3), rng.randint(1, 3)) for g in labels]
        q = S.q_image(word, 2)
        if not q.get('a') and not q.get('b') and not q.get('c'):
            return word


class Screen(unittest.TestCase):
    """The trie screen returns exactly the profiles PR1690's formulas accept, under PR1690's keys."""

    def test_screen_matches_side_value_and_key(self):
        rng = random.Random(15)
        for counts in F.SPLITS:
            na, nb, nc = counts
            F._init(counts)
            for _ in range(3):
                bt = tuple(S.rank_one(rng.randint(1, 3), rng.randint(1, 3)) for _ in range(nb))
                tab, kt = S.side_tables(bt), F.key_tables(bt)
                for trie, n in ((F._CTX['TA'], na), (F._CTX['TC'], nc)):
                    profs = S.profiles(nb, n, F._CTX['seqs'])
                    want = S.side_value(tab, profs[rng.randrange(len(profs))])
                    got = F.screen(trie, tab, kt, want)
                    brute = {}
                    for P in profs:
                        if S.side_value(tab, P) == want:
                            brute.setdefault(S.key(bt, P), []).append(P)
                    self.assertEqual({k: sorted(v) for k, v in got.items()}, brute)

    def test_key_cross_matches_direct_cross_coefficients(self):
        rng = random.Random(77)
        for nb in (6, 7):
            for _ in range(300):
                bt = [S.rank_one(rng.randint(1, 3), rng.randint(1, 3)) for _ in range(nb)]
                P = [rng.randrange(16) for _ in range(nb)]
                Q = [rng.randrange(16) for _ in range(nb)]
                self.assertEqual(F.key_cross(S.key(bt, P), S.key(bt, Q)), S.cross_coeffs(bt, P, Q))

    def test_key_pairs_equal_brute_force_seven_bits(self):
        rng = random.Random(7)
        hits = 0
        for _ in range(30):
            ka = {tuple(rng.randrange(128) for _ in range(4)) for _ in range(200)}
            kc = {tuple(rng.randrange(128) for _ in range(4)) for _ in range(200)}
            brute = {(a, c) for a in ka for c in kc if F.key_cross(a, c) == F.TARGET_CROSS}
            self.assertEqual(set(F.key_pairs(7, ka, kc)), brute)
            hits += len(brute)
        self.assertGreater(hits, 0)


class Completeness(unittest.TestCase):
    """For random words of each split, every pipeline stage keeps the word: its profiles pass
    the trie screen under their keys with the word's own screen values, the key pairing emits
    that key pair, and the expansion of that profile pair regenerates the word. (Orbit coverage
    of the canonical middle sequences is checked in verify.py.)"""

    def test_planted_words_survive_every_stage(self):
        rng = random.Random(1515)
        for counts in F.SPLITS:
            na, nb, nc = counts
            F._init(counts)
            for _ in range(3):
                word = planted(rng, counts)
                bt = tuple(S.rank_one(x, y) for g, x, y in word if g == 'b')
                tab, kt = S.side_tables(bt), F.key_tables(bt)
                P, Q = S.prefix_profile(word, 'a'), S.suffix_profile(word, 'c')
                kP, kQ = S.key(bt, P), S.key(bt, Q)
                ga = F.screen(F._CTX['TA'], tab, kt, S.side_value(tab, P))
                gc = F.screen(F._CTX['TC'], tab, kt, S.side_value(tab, Q))
                self.assertIn(tuple(P), ga.get(kP, []), counts)
                self.assertIn(tuple(Q), gc.get(kQ, []), counts)
                self.assertIn((kP, kQ), set(F.key_pairs(nb, ga, gc, F.key_cross(kP, kQ))), counts)
                seen, st = [], dict(words=0)
                S.expand(bt, tuple(P), tuple(Q), na, nc, F._CTX['seqs'], 2, 2, st, [], seen)
                self.assertIn(word, seen, counts)


class Symmetry(unittest.TestCase):
    def test_a_c_swap_automorphism(self):
        """psi(g) = J g^{-T} J (J antidiagonal) is an automorphism of UT4(F2) with psi(a)=c,
        psi(b)=b, psi(c)=a, psi(z)=z, so (5,6,4) and (4,6,5) are equivalent splits; the
        verifier still searches both."""
        def psi(M):
            n = 4
            inv = next(h for h in S.G if S.mmul4(M, h) == S.mat(0))
            out = [0] * n
            for i in range(n):
                for j in range(n):
                    # (J inv^T J)_{ij} = inv_{3-j, 3-i}
                    if inv[3 - j] >> (3 - i) & 1:
                        out[i] |= 1 << j
            return tuple(out)
        P = [S.idx[psi(g)] for g in S.G]
        self.assertEqual(sorted(P), list(range(64)))
        for g in range(64):
            for h in range(64):
                self.assertEqual(P[S.MUL[g][h]], S.MUL[P[g]][P[h]])
        self.assertEqual((P[S.GEN['a']], P[S.GEN['b']], P[S.GEN['c']]),
                         (S.GEN['c'], S.GEN['b'], S.GEN['a']))
        self.assertEqual(P[S.idx[S.Z]], S.idx[S.Z])


class Controls(unittest.TestCase):
    def test_sixteen_call_word_found_by_reference_driver_at_r1(self):
        word = tuple((g, 1, 1) for g in 'abcbabcb')
        self.assertIn(word, S.search(1, 1, (2, 4, 2)))


if __name__ == '__main__':
    unittest.main()
