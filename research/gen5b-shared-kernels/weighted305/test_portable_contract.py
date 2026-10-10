"""Subset witness, reused helpers, source and dynamic-case regression tests."""
from copy import deepcopy
from fractions import Fraction as F
from unittest.mock import patch
import hashlib,json,unittest
import source_data as src,witness,check_bridge,check_scalar_bounds,check_shared_banks

class PortableContractTests(unittest.TestCase):
 def test_all_source_pins(self):self.assertEqual(src.verify(),39)
 def test_exact_subset_witness_hashes(self):
  for case in ('154','156'):
   self.assertEqual(hashlib.sha256(witness.render(case)).hexdigest(),witness.case(case)['sha256'])
 def test_duplicate_subset_index_rejected(self):
  plan=witness.selection();plan['cases']['156']['entry_indices'][1]=plan['cases']['156']['entry_indices'][0]
  with patch.object(witness,'selection',lambda:plan):
   with self.assertRaises(AssertionError):witness.render('156')
 def test_switched_subset_order_rejected(self):
  plan=witness.selection();ids=plan['cases']['156']['entry_indices'];ids[0],ids[1]=ids[1],ids[0]
  with patch.object(witness,'selection',lambda:plan):
   with self.assertRaises(AssertionError):witness.render('156')
 def test_original104_failure_is_retained(self):
  import review_payload_cap
  r=review_payload_cap.run(438151,14104135,112)
  self.assertFalse(r['original_cap_satisfied']);self.assertTrue(r['explicit_candidate_cap_satisfied'])
  with self.assertRaises(AssertionError):review_payload_cap.run(438151,14104135,104)
 def test_norm_default_tracks_both_cases(self):
  try:
   for label,pairs in [('154',2541),('156',2545)]:
    check_bridge.configure(label);r=check_scalar_bounds.run()
    self.assertEqual(r['setup_restore_pairs'],pairs);self.assertEqual(r['actual_sink_redirects'],16)
  finally:check_bridge.configure('156')
 def test_auxiliary_cache_manifest_not_required(self):
  from pathlib import Path
  original=Path.read_bytes
  def no_auxiliary_manifest(path):
   if path.name=='PINS.json':raise FileNotFoundError('Auxiliary cache file deliberately unavailable')
   return original(path)
  check_bridge.configure('156')
  with patch.object(Path,'read_bytes',no_auxiliary_manifest):
   result=check_bridge.run()
  self.assertEqual(result['selected_pivots'],156)
 def test154_geometry_fallback(self):
  try:
   check_bridge.configure('154');r=check_bridge.run()
   self.assertEqual((r['selected_pivots'],r['selected_distinct_donors'],r['selected_streams']),(154,194,348))
   self.assertEqual(r['local_histogram_delta'],{1:194,2:278,3:-278,4:70,5:-70})
  finally:check_bridge.configure('156')
 def test_bank_stage_and_replica_factors(self):
  for label,stock in [('154',1229280),('156',1229275)]:
   r=check_shared_banks.run(witness.write_case(label))
   self.assertEqual(r['helper_roles'],15424);self.assertEqual(r['total_stage_assignments'],4627200)
   self.assertEqual(r['literal_stock'],stock);self.assertEqual(F(r['unreplicated_stock']),F(stock,60))
   self.assertEqual(stock,422400+5*r['banks_per_stage'])

if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 unittest.main()
