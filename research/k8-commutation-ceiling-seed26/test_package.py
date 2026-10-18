# SPDX-License-Identifier: Apache-2.0
"""Controls for the commutation-class ceiling (about 40 s).

Run: python3 -I -B -m unittest discover -s research/k8-commutation-ceiling-seed26 -p test_package.py -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model as Mo  # noqa: E402
import toy  # noqa: E402
import verify as V  # noqa: E402

I = Mo.load_1671()
W = Mo.Word(I)
LO1, HI1 = W.intervals('chrono')
LO2, HI2 = W.intervals('trace')
G = [('G', i) for i in range(len(W.ops))]
RESULT = json.loads((HERE / 'RESULT.json').read_text())


class Model(unittest.TestCase):
    def test_commutation_rule_matches_exact_composition(self):
        pairs, agree = V.commute_exact(W)
        self.assertEqual((pairs, agree), (109388, 109388))

    def test_a_wrong_rule_disagrees_with_exact_composition(self):
        saved = Mo.commute
        try:
            Mo.commute = lambda e, g: True if e[0] == 'add' and g[0] == 'add' else saved(e, g)   # ignores t1 == s2
            pairs, agree = V.commute_exact(W)
            self.assertLess(agree, pairs)
        finally:
            Mo.commute = saved

    def test_chronological_mode_is_pr1671(self):
        self.assertTrue(all(LO1[g] == W.chrono['lo'][g] and HI1[g] == W.chrono['hi'][g] for g in G))

    def test_trace_intervals_contain_chronological_and_the_word(self):
        self.assertTrue(all(LO2[g] & ~LO1[g] == 0 and HI1[g] & ~HI2[g] == 0 for g in G))
        self.assertEqual(sum(LO2[g] == HI2[g] for g in G), 2979)

    def test_given_word_profile(self):
        self.assertEqual(Mo.given_word_profile(W), Mo.PROFILE)

    def test_subspace_counts(self):
        self.assertEqual([len(Mo.subspaces_rref(I, 1, V._span(I, k))) for k in range(5)], [1, 2, 5, 16, 67])


class Bounds(unittest.TestCase):
    def test_certificate_excludes_the_class_at_the_gate(self):
        lam, fac = V.load_lambda('LAMBDA.json', W, LO2, HI2)
        b, _ = Mo.bound(W, LO2, HI2, fac * Mo.BASE_HI, lam)
        self.assertGreater(b, 1)

    def test_without_coupling_the_bound_does_not_reject(self):
        b, _ = Mo.bound(W, LO2, HI2, Mo.A_STAR)
        self.assertLess(b, 1)

    def test_multiplier_on_a_forced_gate_is_refused(self):
        forced = next(i for i, e in enumerate(W.ops) if e[0] == 'add' and LO2[('G', i)] == HI2[('G', i)])
        d = json.loads((HERE / 'LAMBDA.json').read_text())
        d['lam'][str(forced)] = 5
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'L.json'
            p.write_text(json.dumps(d))
            saved = V.HERE
            try:
                V.HERE = Path(t)
                with self.assertRaisesRegex(V.Reject, 'free ADD gates'):
                    V.load_lambda('L.json', W, LO2, HI2)
            finally:
                V.HERE = saved

    def test_wrong_word_digest_refused(self):
        d = json.loads((HERE / 'LAMBDA.json').read_text())
        d['word_sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / 'L.json').write_text(json.dumps(d))
            saved = V.HERE
            try:
                V.HERE = Path(t)
                with self.assertRaisesRegex(V.Reject, 'certificate header'):
                    V.load_lambda('L.json', W, LO2, HI2)
            finally:
                V.HERE = saved

    def test_recorded_results(self):
        self.assertTrue(all(float(v['bill_lower_minus_one']) > 0 for v in RESULT['stage2'].values()))
        self.assertLess(float(RESULT['stage1']['trace']), 1)
        self.assertGreater(float(RESULT['stage1']['chronological']), 1)


class Toy(unittest.TestCase):
    def test_toy_bound_is_sound(self):
        done, multi = toy.run(2, 60)
        self.assertEqual(done, 60)
        self.assertGreater(multi, 0)

    def test_invalid_charging_is_caught(self):
        with self.assertRaises(AssertionError):
            toy.run(1, 150, mutated=True)


if __name__ == '__main__':
    unittest.main()
