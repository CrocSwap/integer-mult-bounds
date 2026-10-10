"""Fresh focused arithmetic and rejection regression suite for this experiment."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,unittest
CODE=Path(__file__).resolve().parent;sys.path.insert(0,str(CODE.parent));import support
P=support.OUTPUT;import reproduce_p10 as b;import price_candidate as p
import check_second_moment as second
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.baseline=p.baseline()
 def test_new_baseline(self):
  x=self.baseline;self.assertEqual(x['assembly']['kappa'],F(769553898621543,10**18));self.assertEqual(x['profile']['kernel']['entries'],1047);self.assertEqual(x['inventory']['literal_stock'],658290)
 def test_zero_delta(self):self.assertEqual(p.price({},{})['kappa_delta'],0)
 def test_full_price(self):
  d=json.loads((P/'matching/weighted890-delta.json').read_text());x=p.price(d['histogram_delta'],d['residual_delta']);self.assertEqual(x['assembly']['kappa'],F(769997773182046,10**18));self.assertEqual(x['banked_calls'],250045);self.assertEqual(x['assembly']['strict_constraint_count'],47);self.assertTrue(all(v>0 for v in x['assembly']['strict_constraints'].values()))
 def test_reject_noninteger(self):
  for d in ({1:1.0},{True:1},{'01':1},{21:1}):
   with self.assertRaises(ValueError):p.price(d,{})
 def test_reject_unbalanced(self):
  with self.assertRaises(ValueError):p.price({1:1},{})
 def test_reject_negative(self):
  with self.assertRaises(ValueError):p.price({1:-10**9},{20:-50000000})
 def test_bank_modulus_rejection(self):
  with self.assertRaises(ValueError):p.pack_residuals({3:1})
 def test_second_engine_exact_identity(self):
  self.assertEqual(second.log_interval(F(1)),(0,0));self.assertEqual(second.exp_interval(0,0),(1,1))
 def test_second_engine_monotonic_enclosure(self):
  for x in [F(2),F(3),F(100),F(100,19)]:
   a,c=second.log_interval(x);lo,hi=second.exp_interval(a/10,c/10);self.assertLessEqual(lo**10,x);self.assertGreaterEqual(hi**10,x)
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 unittest.main(verbosity=2)
