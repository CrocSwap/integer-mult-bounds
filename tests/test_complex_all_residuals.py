"""Residual accounting, convex guard, and exact moment controls."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from experiments.complex_all_residuals import counts, guard, moment_data, moment, sqrt_upper


class AllResiduals(unittest.TestCase):
    def test_physical_small_network_matches_independent_rank_identity(self):
        for h in (8,10):
            n=counts(h)
            v=comb(h,3); r=n['roles']+h+1
            expected_width=2*v*v*(v+r)
            expected_rank=expected_width*h**3-2*v**3+6*v*v*h*(h+1)
            self.assertEqual(n['W'],expected_width)
            self.assertEqual(n['s'],expected_rank)
            histogram=n['residual_histogram']
            self.assertEqual(sum(a*c for a,c in histogram.items()),expected_rank)
            self.assertEqual(histogram[h**3-2*h],v*v*r)
            self.assertEqual(histogram[h**3-h*h],v*v*r)
            self.assertTrue(all(0<a<h**3 for a in histogram))

    def test_sqrt_enclosures(self):
        for x in (Q(1,1000000),Q(1,7),Q(3,4),Q(1),Q(100)):
            upper=sqrt_upper(x)
            self.assertGreater(upper*upper,x)
            self.assertLessEqual((upper-Q(1,10**12))**2,x)

    def test_convex_partition_extremum_controls(self):
        # Integer squares give an independent exact convex special case.
        # Exhaust all feasible three-child partitions of small path budgets.
        for cap in range(2,8):
            for budget in range(cap+1,2*cap):
                bound=cap**2+(budget-cap)**2
                for a in range(cap+1):
                    for b in range(cap+1):
                        for c in range(cap+1):
                            if a+b+c<=budget:
                                self.assertLessEqual(a*a+b*b+c*c,bound)
        n=dict(h=28,m=21952,W=2085111546336,s=45772350635112192,
               residual_histogram={21896:1})
        g=guard(n)
        self.assertEqual(g['path_moment_upper'],Q(27921787004127,28000000000000))
        self.assertLess(g['path_moment_upper'],g['theta_upper'])
        self.assertEqual(g['C1'],Q(3749,2500))
        self.assertLess(Q(1,2)*g['C1'],1)
        with self.assertRaises(AssertionError):
            guard(n|dict(residual_histogram={21952:1}))

    def test_whole_residual_moment_preserves_rank_and_improves_entropy(self):
        n=counts(8)
        w,logs=moment_data(n)
        self.assertEqual(sum(w),1-n['eta'])
        a=Q(1,10**6)
        # A uniform singleton comparison with the same rank mass.
        from search_network import log_integer_bounds
        log_m=log_integer_bounds(n['m'])[1]
        self.assertLess(moment(a,w,logs),sum(w)/(1-a*log_m))
        self.assertEqual(moment(Q(0),w,logs),sum(w))
        with self.assertRaises(AssertionError):
            moment(Q(1),w,logs)


if __name__=='__main__': unittest.main()
