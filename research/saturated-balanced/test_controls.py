import sys
if sys.flags.optimize:raise ValueError('Verification requires assertions')
sys.dont_write_bytecode=True
import unittest,json,copy
from fractions import Fraction as Q
import verify as v
class Controls(unittest.TestCase):
 def test_missing_reflection_rejected(self):
  x=json.loads((v.HERE/'bit-ledger.json').read_text());x['complete_reflected_F2']=False
  with self.assertRaises(AssertionError):v.profile(x)
 def test_hidden_singleton_deletion_rejected(self):
  x=json.loads((v.HERE/'bit-ledger.json').read_text());x['histogram']['1']-=1
  with self.assertRaises(AssertionError):v.profile(x)
 def test_rank_preserving_fake_coalescence_rejected(self):
  x=json.loads((v.HERE/'bit-ledger.json').read_text());x['histogram']['1']-=2;x['histogram']['2']=x['histogram'].get('2',0)+1
  with self.assertRaises(AssertionError):v.profile(x)
 def test_wrong_basis_size_rejected(self):
  x=json.loads((v.HERE/'bit-ledger.json').read_text());x['formal_basis']-=1
  with self.assertRaises(AssertionError):v.profile(x)
 def test_overstated_kappa_rejected(self):
  x=json.loads((v.HERE/'certificate.json').read_text());x['kappa']='1/100'
  with self.assertRaises(AssertionError):v.arithmetic(x)
 def test_old_prefix_rejects_balanced_parameters(self):
  x=v.parent.rational(json.loads((v.HERE/'certificate.json').read_text()));f,_=v.parent.bridge()
  with self.assertRaises(v.parent.balanced.InvalidAssembly):v.parent.balanced.assembly(f,x['saving'],x['kappa'],beta=Q(1,10),h=Q(1,10**12),a_complex=Q(36926111,500000000000),original_prefix=True)
if __name__=='__main__':unittest.main()
