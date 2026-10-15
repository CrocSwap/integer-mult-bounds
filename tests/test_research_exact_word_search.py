"""Failure-sensitive controls for the reusable exact-search tooling in
research/kb2-alt13-noncommuting-tooling/exact_search.py.

Run: python -B -m unittest tests.test_research_exact_word_search -v
"""

import hashlib
import importlib.util
import itertools
import pathlib
import random
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "research" / "kb2-alt13-noncommuting-tooling" / "exact_search.py"


def load():
    spec = importlib.util.spec_from_file_location("exact_search", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ES = load()


class TestGroups(unittest.TestCase):
    def test_gl2f2_relations(self):
        g = ES.gl2f2()
        self.assertEqual(g.n, 6)
        e, a, b, s = g.identity, g.A, g.B, g.S
        self.assertEqual(g.mul(a, a), e)
        self.assertEqual(g.mul(b, b), e)
        self.assertEqual(g.mul(g.mul(a, b), a), s)
        self.assertEqual(g.mul(g.mul(b, a), b), s)

    def test_q8_relations(self):
        g = ES.q8()
        self.assertEqual(g.n, 8)
        e, x, y, z = g.identity, g.X, g.Y, g.Z
        self.assertEqual(g.mul(x, x), z)
        self.assertEqual(g.mul(y, y), z)
        self.assertEqual(g.mul(g.mul(g.mul(x, y), x), y), z)
        self.assertNotEqual(g.mul(x, y), g.mul(y, x))


class TestAlphabets(unittest.TestCase):
    def test_rank_one_idempotent_counts(self):
        self.assertEqual(len(ES.rank_one_idempotents(2)), 6)
        self.assertEqual(len(ES.rank_one_idempotents(3)), 28)
        self.assertEqual(len(ES.rank_one_idempotents(5)), 496)
        t = 5
        eye = tuple(1 << i for i in range(t))
        for u, v in ES.rank_one_idempotents(t):
            n = ES.proj_rows(t, u, v)
            self.assertEqual(ES.mat_mul(t, n, n), n)
            self.assertEqual(ES.mat_add(n, eye), ES.mat_add(eye, n))


class TestWordModel(unittest.TestCase):
    def setUp(self):
        self.g = ES.gl2f2()
        self.ga = ES.GroupAlgebra(self.g)

    def test_direct_words_reach_target(self):
        for t in (1, 3, 5):
            labels = [self.g.A, self.g.B, self.g.A] * t
            projs = [ES.coord_proj(t, i // 3) for i in range(3 * t)]
            self.assertEqual(
                ES.word_product(self.ga, self.g, t, labels, projs),
                ES.ring_target(self.ga, t, self.g.S), t)

    def test_mutated_word_fails(self):
        t = 5
        labels = [self.g.A, self.g.B, self.g.A] * 5
        labels[1] = self.g.A
        projs = [ES.coord_proj(t, i // 3) for i in range(15)]
        self.assertNotEqual(
            ES.word_product(self.ga, self.g, t, labels, projs),
            ES.ring_target(self.ga, t, self.g.S))

    def test_sign_quotient_sum_rule(self):
        rng = random.Random(7)
        t = 3
        for _ in range(50):
            labels, projs = ES.random_tuple(self.g, t, 7, rng)
            m0, m1 = ES.sign_quotient_word(self.g, t, labels, projs)
            eye = tuple(1 << i for i in range(t))
            want1 = ES.proj_sum(t, [ES.proj_rows(t, u, v) for u, v in projs])
            self.assertEqual(m0, eye)
            self.assertEqual(m1, want1)

    def test_sign_natural_equivalent_to_endpoint(self):
        rng = random.Random(11)
        t = 3
        agree = 0
        for _ in range(200):
            labels, projs = ES.random_tuple(self.g, t, 6, rng)
            full = ES.endpoint_check(self.ga, self.g, t, labels, projs)
            quot = (ES.sign_check(self.g, t, labels, projs)
                    and ES.natural_check(self.g, t, labels, projs))
            self.assertEqual(full, quot)
            agree += full
        # structured near-misses so both outcomes occur
        labels = [self.g.A, self.g.B, self.g.A] * 3
        projs = [ES.coord_proj(3, i // 3) for i in range(9)]
        self.assertTrue(ES.endpoint_check(self.ga, self.g, 3, labels, projs))
        projs[0] = ES.coord_proj(3, 1)
        self.assertFalse(ES.endpoint_check(self.ga, self.g, 3, labels, projs))

    def test_c_invariant_equivalent_to_endpoint(self):
        rng = random.Random(13)
        t = 3
        for _ in range(200):
            labels, projs = ES.random_tuple(self.g, t, 6, rng)
            full = ES.endpoint_check(self.ga, self.g, t, labels, projs)
            cok = ES.c_conditions_ok(t, labels, projs)
            self.assertEqual(full, cok)


class TestClassificationLemmas(unittest.TestCase):
    def test_t_summands_over_f2_3_are_dual_frames(self):
        # k = t rank-one idempotents summing to I_t are automatically a dual
        # frame (V^T U is an invertible idempotent, hence I).
        t = 3
        projs = ES.rank_one_idempotents(t)
        eye = tuple(1 << i for i in range(t))
        checked = 0
        for comb in itertools.combinations(range(len(projs)), 3):
            rows = [ES.proj_rows(t, projs[i][0], projs[i][1]) for i in comb]
            if ES.proj_sum(t, rows) != eye:
                continue
            checked += 1
            for i, j in itertools.combinations(comb, 2):
                ui, vi = projs[i]
                uj, vj = projs[j]
                self.assertEqual(ES.dot(vi, uj), 0)
                self.assertEqual(ES.dot(vj, ui), 0)
        self.assertGreater(checked, 0)

    def test_more_than_t_summands_need_not_commute(self):
        # the dual-frame collapse is exactly k = t: at k = t + 2 there are
        # noncommuting summand sets (this is what makes d >= 7 tuples open).
        t = 3
        projs = ES.rank_one_idempotents(t)
        eye = tuple(1 << i for i in range(t))
        found = False
        for comb in itertools.combinations(range(len(projs)), 5):
            rows = [ES.proj_rows(t, projs[i][0], projs[i][1]) for i in comb]
            if ES.proj_sum(t, rows) != eye:
                continue
            for i, j in itertools.combinations(comb, 2):
                ui, vi = projs[i]
                uj, vj = projs[j]
                if ES.dot(vi, uj) or ES.dot(vj, ui):
                    found = True
                    break
            if found:
                break
        self.assertTrue(found)

    def test_four_summands_never_reach_identity_f2_3(self):
        t = 3
        projs = ES.rank_one_idempotents(t)
        eye = tuple(1 << i for i in range(t))
        for comb in itertools.combinations(range(len(projs)), 4):
            rows = [ES.proj_rows(t, projs[i][0], projs[i][1]) for i in comb]
            self.assertNotEqual(ES.proj_sum(t, rows), eye)


class TestBruteForceBaseline(unittest.TestCase):
    def test_t2_length6_is_exact_minimum(self):
        g = ES.gl2f2()
        ga = ES.GroupAlgebra(g)
        t = 2
        alphabet = ES.rank_one_idempotents(t)
        target = ES.ring_target(ga, t, g.S)
        labels = [g.A, g.B, g.A, g.B, g.A, g.B]
        # length 4: exhaustive negative
        found4 = 0
        for tup in itertools.product(alphabet, repeat=4):
            if ES.word_product(ga, g, t, labels[:4],
                               [ES.proj_rows(t, u, v) for u, v in tup]) == target:
                found4 += 1
        self.assertEqual(found4, 0)
        # length 6: the direct word is a witness
        direct = [ES.coord_proj(t, 0), ES.coord_proj(t, 0), ES.coord_proj(t, 0),
                  ES.coord_proj(t, 1), ES.coord_proj(t, 1), ES.coord_proj(t, 1)]
        self.assertEqual(ES.word_product(ga, g, t, labels, direct), target)


class TestFastEval(unittest.TestCase):
    def test_signature_expansion_matches_generic(self):
        rng = random.Random(17)
        g = ES.gl2f2()
        ga = ES.GroupAlgebra(g)
        t = 5
        for _ in range(8):
            labels, projs = ES.random_tuple(g, t, 13, rng)
            # split into frame classes + free projector to exercise both paths
            slow = ES.word_product(ga, g, t, labels, projs)
            fast = ES.expanded_word_product(ga, g, t, labels, projs)
            self.assertEqual(slow, fast)

    def test_frame_plus_extra_eval_matches_generic(self):
        rng = random.Random(23)
        g = ES.gl2f2()
        ga = ES.GroupAlgebra(g)
        t = 5
        labels = ES.alt_labels(g, 13)
        alphabet = ES.rank_one_idempotents(t)
        for _ in range(10):
            m = rng.randrange(1, 5)
            w_pos = sorted(rng.sample(range(13), m))
            w_u, w_v = alphabet[rng.randrange(len(alphabet))]
            assign = [rng.randrange(t) for _ in range(13)]
            h = [[g.identity] * (m + 1) for _ in range(t)]
            projs = []
            seg = 0
            for i in range(13):
                if i in w_pos:
                    projs.append((w_u, w_v))
                    seg += 1
                else:
                    projs.append(ES.coord_proj(t, assign[i]))
                    h[assign[i]][seg] = g.mul(h[assign[i]][seg], labels[i])
            slow = ES.word_product(ga, g, t, labels, projs)
            fast = ES.sig_eval(ga, g, t, [labels[i] for i in w_pos],
                               h, w_u, w_v)
            self.assertEqual(slow, fast)
            # mutation control: corrupting one segment product must change it
            h[0][0] = g.mul(h[0][0], g.A)
            mutated = ES.sig_eval(ga, g, t, [labels[i] for i in w_pos],
                                  h, w_u, w_v)
            self.assertNotEqual(slow, mutated)

    def test_gl_conjugation_invariance(self):
        rng = random.Random(19)
        g = ES.gl2f2()
        ga = ES.GroupAlgebra(g)
        t = 5
        labels = [g.A, g.B, g.A] * 5
        projs = [ES.coord_proj(t, i // 3) for i in range(15)]
        eye = ES.ring_target(ga, t, g.S)
        self.assertEqual(ES.word_product(ga, g, t, labels, projs), eye)
        p, pinv = ES.random_gl(t, rng)
        conj = [ES.proj_conj(t, u, v, p, pinv) for u, v in projs]
        self.assertEqual(ES.word_product(ga, g, t, labels, conj), eye)


class TestLayerBalls(unittest.TestCase):
    def test_q8_layer_calibration(self):
        g = ES.q8()
        ga = ES.GroupAlgebra(g)
        t = 2
        alphabet = [ES.proj_rows(t, u, v) for u, v in ES.rank_one_idempotents(t)]
        gens = [ES.call_matrix(ga, g, t, lbl, n)
                for lbl in (g.X, g.Y) for n in alphabet]
        layers = ES.layer_ball_sizes(ga, gens, 3)
        self.assertEqual(layers, [1, 12, 110, 936])


class TestBatchSplit(unittest.TestCase):
    def test_shards_partition_and_are_stable(self):
        items = list(range(1000))
        s1 = ES.shard_split(items, 7)
        s2 = ES.shard_split(items, 7)
        self.assertEqual(s1, s2)
        self.assertEqual(len(s1), 7)
        flat = [x for sh in s1 for x in sh["items"]]
        self.assertEqual(sorted(flat), items)
        for sh in s1:
            self.assertEqual(sh["sha256"],
                             hashlib.sha256(
                                 ",".join(map(str, sh["items"])).encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
