import unittest
from check_kernel70 import run as kernel
from check_kernel70_norm import run as bounds
from check_pr300_kernel70_composition import run as composition
class Candidate70Tests(unittest.TestCase):
 def test_exact_candidate(self):
  r=kernel();self.assertEqual((r['pivots'],r['distinct_donors'],r['setup_adds']),(70,87,601));self.assertTrue(r['formal_forward_and_inverse_equal'])
 def test_entrance_mutation(self):
  with self.assertRaises(AssertionError):kernel('bad_entrance')
 def test_response_mutation(self):
  with self.assertRaises(AssertionError):kernel('bad_relation')
 def test_missing_setup(self):
  with self.assertRaises(AssertionError):kernel('omit_setup')
 def test_missing_restore(self):
  with self.assertRaises(AssertionError):kernel('omit_restore')
 def test_payload_cap(self):
  r=bounds();self.assertEqual(r['payload_bits'],104);self.assertTrue(r['retained_payload_cap_2_to104'])
 def test_pr300_composition(self):
  r=composition();self.assertEqual(r['kernel70_streams'],157);self.assertTrue(r['paid_ledgers_additive'])
 def test_reject_pr300_kernel_overlap(self):
  with self.assertRaises(AssertionError):composition('kernel_overlap')
 def test_reject_pr300_final12_overlap(self):
  with self.assertRaises(AssertionError):composition('frame_overlap')
if __name__=='__main__':unittest.main()
