"""Independent h30 rank-mass and strict-assembly boundary controls."""
from dataclasses import replace
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import dimension30_stream_network as network


class Dimension30Network(unittest.TestCase):
    def test_h30_mass_identity_and_exact_logarithms(self):
        h, roles = 30, network.ROLES
        v, m = comb(h, 5), h**3
        N, copies, W = v**3, v*v*roles, 2*v*v*(v+roles)
        loss = 3*v*v*comb(h, 2)*(h-2)
        s = W*m-N+2*loss
        chunks = [m-4*h, m-2*h*h, m-2*h*h-2*h+2, h*h]
        multiplicities = [copies, copies, 2*N, copies]
        masses = [s-sum(a*b for a, b in zip(chunks, multiplicities))]
        masses += [a*b for a, b in zip(chunks, multiplicities)]
        result = network.bit_certificate()
        logs = result['logarithm_upper_bounds']
        self.assertEqual(logs, [Q(2040718429, 200000000), Q(4454351, 10**9),
                               Q(8624109, 125000000), Q(8912139, 125000000),
                               Q(1700598691, 500000000)])
        self.assertEqual(sum(masses), s)
        self.assertEqual(result['counts']['W'], W)
        self.assertEqual(result['counts']['original_rank_sum'], s)
        expected = sum((Q(mass, W*m)/(1-network.BIT_SAVING*ell)
                        for mass, ell in zip(masses, logs)), Q(0))
        self.assertEqual(result['moment_upper'], expected)
        self.assertLess(expected, 1)
        with self.assertRaisesRegex(ValueError, 'Unsupported h30 bit saving'):
            network.bit_certificate(a=network.BIT_SAVING+Q(1, 10**12))
        with self.assertRaisesRegex(ValueError, 'Unsupported h30 bit saving'):
            network.bit_certificate(roles=17515487)  # PR #12's separate producer.

    def test_complete_assembly_and_independent_margins(self):
        p = network.parameters()
        result = network.assembly()
        expected = dict(g1=1-p.epsilon*(1+p.c), g2=p.epsilon*p.c*(1-p.tau),
                        g3=p.epsilon*(1-p.lamp), g4=(1-p.epsilon)*(1-p.tau),
                        g5=1-p.delta-2*p.epsilon, g6=1-p.delta-p.epsilon,
                        g7=p.epsilon)
        self.assertEqual(result['margins'], expected)
        self.assertEqual(len(result['constraints']), 29)
        self.assertTrue(all(value > 0 for value in result['constraints'].values()))
        self.assertEqual(result['minimum_margin'], Q(84239485748905098429, 5*10**26))
        self.assertEqual(result['absorption_gap'], Q(485748905098429, 5*10**26))
        self.assertGreater(result['factor_over_aligned'], 103)
        self.assertEqual(result['guard']['h'], 28)  # Complex guard is unchanged.
        with self.assertRaisesRegex(ValueError, 'absorption gap'):
            network.assembly(replace(p, kappa=result['minimum_margin']))
        with self.assertRaisesRegex(ValueError, 'Bulk guard mismatch'):
            network.assembly(replace(p, C1=Q(6, 5)))
        with self.assertRaisesRegex(ValueError, 'gaussian_cost'):
            network.assembly(replace(p, delta=1-2*p.epsilon))


if __name__ == '__main__':
    unittest.main()
