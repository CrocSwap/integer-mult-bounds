import pathlib, sys, unittest
from fractions import Fraction as Q

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'independent' / 'deferred-readout'))
import certificate_round7 as c7
import deferred as dr


class Round7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S, cls.rk, cls.ylev, cls.xd = c7.build(c7.WITNESSES[0])

    def test_schedule_shape(self):
        S = self.S
        self.assertEqual((S.h, S.R, len(S.readout), len(S.vstart)), (23, 28866, 11565, 11374))
        self.assertEqual(S.readout, sorted(S.readout, key=lambda s: (S.f[s], s)))    # readouts by dim sigma
        dv = {s: len(B) for s, B in S.vstart.items()}
        self.assertEqual(S.late_v, sorted(S.late_v, key=lambda s: (dv[s], s)))      # deferred V gates by dim s_i
        self.assertTrue(all(sum(x) == S.h - 1 for x in self.xd))

    def test_chain_ranks_are_corner_ranks(self):
        S = self.S
        self.assertEqual(sum(r * c for r, c in self.rk.items()), sum(S.h - S.f[s] for s in range(S.R)))

    def test_savings(self):
        for key, _, corner in c7.CORNERS:
            a, c = c7.saving(self.S, self.rk, self.ylev, self.xd, corner(self.S.h))
            self.assertEqual(sum(w * n for w, n in c['hist'].items()), c['s'])
            self.assertEqual(c['s'], c['W'] * c['m'] - c['N'] + c['L'])
            self.assertEqual(a, c7.WITNESSES[0][key][0])

    def test_kappa(self):
        for key in ('plain', 'staircase'):
            a, k = c7.WITNESSES[0][key]
            r = c7.kappa(a)
            self.assertTrue(r['ok'], r['bad'])
            self.assertEqual(r['kappa'], k)
            self.assertGreater(r['kappa'], Q(1, 2**14))

    def test_wrong_readout_level_breaks_rank_sum(self):
        # a deferred slot whose recorded sigma is one dimension smaller no longer re-partitions the budget
        S = self.S; s = S.readout[0]; S.f[s] -= 1
        try:
            c = dr.histogram(S, self.rk, self.ylev, self.xd)
            self.assertNotEqual(sum(w * n for w, n in c['hist'].items()), c['s'])
        finally:
            S.f[s] += 1


if __name__ == '__main__':
    unittest.main()
