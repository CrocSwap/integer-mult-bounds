import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
import unittest,copy,json
from fractions import Fraction as Q
import verify as v
class Controls(unittest.TestCase):
 def test_old_prefix_rejected_at_balanced_parameters(self):
  c=v.rational(v.upstream.read(v.HERE/'certificate.json'));f,_=v.bridge()
  with self.assertRaises(v.balanced.InvalidAssembly):v.balanced.assembly(f,c['bit']['saving'],c['balanced_interface']['kappa'],beta=Q(1,10),h=Q(1,10**12),a_complex=Q(36926111,500000000000),original_prefix=True)
 def test_changed_scalar_charge_rejected(self):
  f,_=v.bridge();f['complex']['scalar_group_upper']-=1
  with self.assertRaises(v.balanced.InvalidAssembly):v.balanced.validate_bridge(f)
 def test_inadequate_row_stock_rejected(self):
  f,_=v.bridge();f['rows']['degree']=1
  with self.assertRaises(v.balanced.InvalidAssembly):v.balanced.validate_bridge(f)
 def test_zero_backoff_rejected(self):
  c=v.rational(v.upstream.read(v.HERE/'certificate.json'));f,_=v.bridge()
  with self.assertRaises(v.balanced.InvalidAssembly):v.balanced.assembly(f,c['bit']['saving'],c['balanced_interface']['kappa'],h=Q(),a_complex=Q(36926111,500000000000))
 def test_too_large_stopped_leaf_rejected(self):
  c=v.rational(v.upstream.read(v.HERE/'certificate.json'));f,_=v.bridge()
  with self.assertRaises(v.balanced.InvalidAssembly):v.balanced.assembly(f,c['bit']['saving'],c['balanced_interface']['kappa'],beta=Q(1,2),h=Q(1,10**12),a_complex=Q(36926111,500000000000))
 def test_overstated_exponent_rejected(self):
  c=v.upstream.read(v.HERE/'certificate.json');c['balanced_interface']['kappa']='1/100'
  with self.assertRaises(AssertionError):v.exact(c)
if __name__=='__main__':unittest.main()
