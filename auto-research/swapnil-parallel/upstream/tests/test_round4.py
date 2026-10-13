import importlib.util, pathlib, sys, unittest
from fractions import Fraction as Q

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'independent' / 'two-stage-bit'))
import moment
spec = importlib.util.spec_from_file_location('certificate_round3', ROOT / 'scripts' / 'certificate_round3.py')
r3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3)

A_C = Q(4079603, 25 * 10**10)   # fully batched PR #7 complex network with source frames, h=28


class Round4(unittest.TestCase):
    def test_bit_histogram_and_saving(self):
        c = moment.histogram(47, moment.R_of(47), True)
        self.assertEqual(sum(w * n for w, n in c['hist'].items()), c['s'])
        self.assertEqual(c['W'] * c['m'] - c['s'], c['v'] * (c['v'] - 4 * 47 * 47))
        a, _ = moment.certify(c)
        self.assertEqual(a, Q(10033, 10**9))

    def test_data_batching_needed(self):
        c = moment.histogram(47, moment.R_of(47), False)
        a, _ = moment.certify(c)
        self.assertLess(a, Q(10033, 10**9))

    def test_pr24_headline(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        import certificate_round4 as c4
        a, c = c4.pr24_bit_saving()
        self.assertEqual(a, Q(4788949, 4 * 10**11))
        r = r3.evaluate(a, A_C, Q(1, 1000), 'crude')
        self.assertTrue(r['ok'], r['bad'])
        self.assertEqual(r['kappa'], Q(59861145819, 5 * 10**15))
        self.assertGreater(r['kappa'], Q(119720853, 10**13))

    def test_kappa(self):
        r = r3.evaluate(Q(10033, 10**9), A_C, Q(1, 1000), 'crude')
        self.assertTrue(r['ok'], r['bad'])
        self.assertEqual(r['binding'], 'simultaneous butterflies')
        self.assertGreater(r['kappa'], Q(1, 2**17))


if __name__ == '__main__':
    unittest.main()
