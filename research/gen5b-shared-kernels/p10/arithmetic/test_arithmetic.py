"""Focused portable numerical and rejection checks; supplied-source programs never run."""
from fractions import Fraction as F
import unittest
import reproduce_p10 as b
import price_candidate as p
from finite_invoice import bill
class ArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.base=p.baseline()
    def test_baseline(self):
        self.assertEqual(self.base['assembly']['kappa'],F(384599485948493,500000000000000000))
        self.assertEqual(self.base['assembly']['strict_constraint_count'],47)
        r=self.base['bit_root_bracket'];self.assertLess(r['lower_moment'][1],1);self.assertGreater(r['upper_moment'][0],1)
    def test_zero_delta(self):self.assertEqual(p.price({},{})['kappa_delta'],0)
    def test_complex_root(self):self.assertEqual(self.base['complex_certificate']['bad_envelope_root']['lower'],b.COMPLEX)
    def test_complex_cap(self):self.assertEqual(p.price({1:-10000,2:5000},{})['assembly']['binding'],'complex')
    def test_reject_nonexact(self):
        for value in ({1:1.0},{True:1},{'01':1},{21:1}):
            with self.assertRaises(ValueError):p.price(value,{})
    def test_reject_unbalanced(self):
        with self.assertRaises(ValueError):p.price({1:1},{})
    def test_reject_negative(self):
        with self.assertRaises(ValueError):p.price({1:-10**9},{20:-50000000})
    def test_candidate15(self):self.assertEqual(p.price({1:17,2:30,3:-30,4:2,5:-2},{20:-15,19:15})['assembly']['kappa'],F(192302177781107,250000000000000000))
    def test_weighted_finite_formula(self):
        r=bill(658905,249085,334771,336691,R=8221)
        self.assertEqual(r['coefficient'],25415456130362201)
        self.assertEqual(r['coefficient_terms']['bank_selectors'],295858082400)
if __name__=='__main__':unittest.main(verbosity=2)
