import importlib.util, pathlib, sys, unittest
from fractions import Fraction as Q

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'independent' / 'two-stage-bit'))
import certificate_round5 as c5
import certificate_round3 as r3

A_C = Q(4079603, 25 * 10**10)


class Round5(unittest.TestCase):
    def test_flag_histogram_and_saving(self):
        a, c = c5.bit_saving(side=False)
        self.assertEqual(c['R'], 403248)
        self.assertEqual(sum(w * n for w, n in c['hist'].items()), c['s'])
        self.assertEqual(a, Q(3369, 250000000))   # flag basis and data runs, side roles as singletons

    def test_side_lemma_saving(self):
        a, c = c5.bit_saving(side=True)
        self.assertEqual(sum(w * n for w, n in c['hist'].items()), c['s'])
        self.assertEqual(a, Q(15479, 10**9))
        r = r3.evaluate(a, A_C, Q(1, 1000), 'crude')
        self.assertTrue(r['ok'], r['bad'])
        self.assertEqual(r['kappa'], Q(309575208081, 2 * 10**16))
        self.assertGreater(r['kappa'], Q(1, 2**16))

    def test_flag_beats_singleton_corners(self):
        # same histogram with the h corner transpositions charged as singletons is strictly worse
        import moment
        c = c5.flag_histogram(47, 403248)
        h, A = 47, None
        a_flag, _ = moment.certify(c)
        base = moment.histogram(47, 403248, True)
        a_base, _ = moment.certify(base)
        self.assertGreater(a_flag, a_base)

    def test_kappa(self):
        r = r3.evaluate(Q(13341, 10**9), A_C, Q(1, 1000), 'crude')
        self.assertTrue(r['ok'], r['bad'])
        self.assertEqual(r['kappa'], Q(333520550497, 25 * 10**15))


if __name__ == '__main__':
    unittest.main()
