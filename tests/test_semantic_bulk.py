"""Failure-oriented integration checks for the changed analytic interface."""
import importlib.util
from pathlib import Path
from fractions import Fraction as Q
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('semantic_composition',ROOT/'research/semantic-bulk/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class SemanticBulk(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  old,_=v.pinned_inputs();cls.f=v.finite_bridge(old)
 def test_changed_guard_and_exposure_are_necessary(self):
  for kwargs in ({'old_guard':True},{'old_exposures':True}):
   with self.assertRaises(AssertionError):v.assembly(self.f,**kwargs)
 def test_next_unreached_milestone_is_rejected(self):
  with self.assertRaises(AssertionError):v.assembly(self.f,kappa=Q(1,2**16))
 def test_independent_exact_balance_and_stock(self):
  x=v.assembly(self.f);p=x['parameters'];a=Q(11,10**6);h=Q(1,10**8)
  # Eliminate c and epsilon directly to obtain the minimum.
  minimum=a*(1-2*h)*(1-h)/(1+a*(1-2*h)*(2+h))
  self.assertEqual(minimum,x['minimum_margin'])
  self.assertGreater(minimum-v.KAPPA,Q(9,10**9))
  self.assertEqual(self.f['rows']['coefficient'],43*494+41*544)
  self.assertGreater(89000*25,51*(43*494+41*544))
  self.assertGreater(v.KAPPA,Q(1,2**17))
 def test_near_parent_semantic_induction_including_tails(self):
  f=self.f;m=f['complex']['m'];r=f['complex']['maxchild'];B=f['semantic']['B'];s=f['complex']['s'];E=f['semantic']['E']
  for n in (1,2,3,10,100):
   for tail in (0,1,m-1):self.assertLessEqual(2*B*r*n+s*n+E,2*B*(m*n+tail))
  # A full-width recursive child destroys this induction's strict gap.
  self.assertGreater(2*B*m+s+E,2*B*m)
if __name__=='__main__':unittest.main()
