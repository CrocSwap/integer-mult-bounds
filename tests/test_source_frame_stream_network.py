"""Independent source relocation, moment, and complete assembly boundaries."""
from dataclasses import replace
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import source_frame_stream_network as network


class SourceFrameStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.complex_result=network.complex_certificate()

    def test_independent_rank_masses_and_exponent_boundary(self):
        h,R=30,13056812;v,m=comb(h,5),h**3
        W=2*v*v*(v+R)
        s=W*m-v**3+6*v*v*comb(h,2)*(h-2)
        rows=[(v*v*R,m-4*h),(2*v**3,m-2*h*h-2*h+2),(v*v*R,m-2*h)]
        masses=[s-sum(c*r for c,r in rows)]+[c*r for c,r in rows]
        actual=network.bit_certificate()
        self.assertEqual(actual['counts']['W'],W)
        self.assertEqual(actual['counts']['rank_sum'],s)
        self.assertEqual(sum(masses),s)
        self.assertEqual(actual['counts']['new_exit_rank'],m-h)
        self.assertEqual(actual['counts']['removed_entrance_rank']+(m-h*h),m-h)
        expected=sum((Q(mass,W*m)/(1-network.BIT_SAVING*ell)
                      for mass,ell in zip(masses,actual['logarithm_upper_bounds'])),Q(0))
        self.assertEqual(actual['moment_upper'],expected)
        self.assertLess(expected,1)
        with self.assertRaisesRegex(ValueError,'Unsupported source-frame'):
            network.bit_certificate(network.BIT_SAVING+Q(1,10**12))
        with self.assertRaisesRegex(ValueError,'Unsupported source-frame'):
            network.bit_certificate(roles=17515487)

    def test_all_constraints_and_independent_margins(self):
        p=network.parameters();actual=network.assembly(self.complex_result)
        expected=dict(g1=1-p.epsilon*(1+p.c),g2=p.epsilon*p.c*(1-p.tau),
                      g3=p.epsilon*(1-p.lamp),g4=(1-p.epsilon)*(1-p.tau),
                      g5=1-p.delta-2*p.epsilon,g6=1-p.delta-p.epsilon,g7=p.epsilon)
        self.assertEqual(actual['margins'],expected)
        self.assertEqual(len(actual['constraints']),29)
        self.assertTrue(all(x>0 for x in actual['constraints'].values()))
        self.assertEqual(actual['minimum_margin'],Q(538339170276524048839,5*10**26))
        self.assertEqual(actual['absorption_gap'],Q(170276524048839,5*10**26))
        self.assertEqual(actual['factor_over_aligned'],Q(538339,812))
        self.assertGreater(actual['dyadic_gap'],0)
        self.assertGreater(actual['factor_over_PR13'],Q(139,100))
        with self.assertRaisesRegex(ValueError,'absorption gap'):
            network.assembly(self.complex_result,replace(p,kappa=actual['minimum_margin']))
        with self.assertRaisesRegex(ValueError,'guard mismatch'):
            network.assembly(self.complex_result,replace(p,C1=Q(11999,10000)))
        with self.assertRaisesRegex(ValueError,'gaussian_cost'):
            network.assembly(self.complex_result,replace(p,delta=1-2*p.epsilon))

    def test_complex_headroom_is_real(self):
        result=self.complex_result
        self.assertEqual(result['complex_saving'],network.COMPLEX_SAVING)
        self.assertLess(result['moment_upper'],1)
        self.assertGreaterEqual(result['next_grid_moment'],1)
        self.assertGreater(result['complex_saving'],network.BIT_SAVING)
        self.assertLess(result['guard']['path_moment_upper'],Q(999,1000))
        self.assertGreater(network.BIT_SAVING,Q(18,10**7))


if __name__=='__main__':unittest.main()
