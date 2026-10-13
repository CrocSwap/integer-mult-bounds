import pathlib, sys, unittest
from fractions import Fraction as Q

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import certificate_round6 as c6
import certificate_round3 as r3

A_C = Q(36926111, 5 * 10**11)   # two-stage complex interchange, h = 24
M_C, S_C = 576, 119453132304


class Round6(unittest.TestCase):
    def test_copied_bit_saving(self):
        a, c = c6.bit_saving()
        self.assertEqual((c['R'], c['W'] * c['m'] - c['s']), (52788, 2415000))
        self.assertEqual(a, Q(34919, 10**9))

    def test_retained_totals_saving(self):
        a, c = c6.retained_saving()
        self.assertEqual((c['R'], c['s']), (40077, 78410006675))
        self.assertEqual(a, Q(36667, 10**9))

    def test_kappa(self):
        r = r3.evaluate(Q(36667, 10**9), A_C, Q(1, 1000), 'crude', m_c=M_C, s_c=S_C)
        self.assertTrue(r['ok'], r['bad'])
        self.assertEqual(r['kappa'], Q(3666565558019, 10**17))
        self.assertGreater(r['kappa'], Q(1, 2**15))


if __name__ == '__main__':
    unittest.main()
