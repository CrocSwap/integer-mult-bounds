from fractions import Fraction as F
import unittest
import chart_bounds as c

class ChartTests(unittest.TestCase):
    def test_identity(self):
        r=c.factor([[1,0],[0,1]])
        self.assertEqual(r['count'],0);self.assertEqual(r['determinant'],1)
    def test_exact_nontrivial_factorization(self):
        r=c.factor([[1,2],[3,5]])
        self.assertEqual(r['determinant'],-1)
        self.assertGreater(r['count'],0)
    def test_singular_rejected(self):
        with self.assertRaises(StopIteration):c.factor([[1,2],[2,4]])
    def test_integer_nullspace(self):
        A=[[1,2,3],[2,4,6]];B=c.nullspace(A,3)
        self.assertEqual(len(B),2)
        self.assertTrue(all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B))
    def test_all_actual_charts(self):
        r=c.run();self.assertEqual(r['charts'],18)
        self.assertEqual(r['max_changed_chart_factors'],142)
        self.assertEqual(r['max_factor_numerator'],11)
        self.assertEqual(r['max_factor_denominator'],9)
        self.assertEqual(r['selector_calls_bound'],905994200400)

if __name__=='__main__':unittest.main(verbosity=2)
