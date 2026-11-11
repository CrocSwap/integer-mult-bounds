"""Portable path, pin, case-switch, closure, and bank binding controls."""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import hashlib,json,tempfile,unittest
import source_data as src
import check_bridge,check_scalar_bounds
import check_shared_banks
from cases import CASES

class PortableContractTests(unittest.TestCase):
 def test_all_input_pins(self):self.assertEqual(src.verify(),39)
 def test_modified_bytes_rejected(self):
  name='gen5bit/selected/bit/profile_p12.json'
  with self.assertRaises(AssertionError):src.validate(name,src.read_bytes(name)+b' ')
 def test_immutable_candidate_hashes(self):
  for case in CASES.values():self.assertEqual(hashlib.sha256((src.ROOT/case['file']).read_bytes()).hexdigest(),case['sha256'])
 def test_dynamic_norm_default_tracks_case(self):
  try:
   for name in ('70','166'):
    check_bridge.configure(name);r=check_scalar_bounds.run()
    self.assertEqual(r['setup_restore_pairs'],CASES[name]['pairs'])
    self.assertEqual(r['forward']['certified_new_bound'],CASES[name]['F'])
  finally:check_bridge.configure('166')
 def test_70_full_geometry_fallback(self):
  try:
   check_bridge.configure('70');r=check_bridge.run()
   self.assertEqual(len(r['selected_reused_donors']),2)
   self.assertEqual(r['local_histogram_delta'],CASES['70']['delta'])
   self.assertEqual(r['selected_streams'],157)
  finally:check_bridge.configure('166')
 def test_duplicate_bank_role_rejected(self):
  with self.assertRaisesRegex(AssertionError,'Missing or duplicated'):
   check_shared_banks.run(src.ROOT/CASES['166']['file'],mutation='duplicate_role')
 def test_replica_stage_units_both_cases(self):
  for case in CASES.values():
   b=check_shared_banks.run(src.ROOT/case['file'])
   self.assertEqual(b['literal_stock'],case['stock'])
   self.assertEqual(F(b['unreplicated_stock']),F(b['literal_stock'],60))
   self.assertEqual(b['literal_stock'],422400+5*b['banks_per_stage'])
   self.assertEqual(b['total_stage_assignments'],5*60*15425)
   self.assertEqual(b['assignment_sha256'],case['assignment_sha256'])
 def test_no_final12_endpoint_saving_in_inventory(self):
  b=check_shared_banks.run(src.ROOT/CASES['166']['file'])
  self.assertEqual((b['new_restorations'],b['reverted_old_restorations']),(0,0))
  self.assertEqual(b['retained_old_restorations'],440)
 def test_rounded_shared_donor_closure_charges_once(self):
  from search_expanded_lines import closure
  rows=[{'pivot':1,'donors':[3]},{'pivot':2,'donors':[3]}]
  # Two benefits2 versus one shared cost3: each alone loses, together gain1.
  dimensions={1:2,2:2,3:3};phi=lambda r:{0:0,1:5,2:7,3:9}[r]
  selected,profit=closure(rows,dimensions,phi)
  self.assertEqual(selected,rows);self.assertEqual(profit,10**9)
 def test_rounded_closure_rejects_losing_activation(self):
  from search_expanded_lines import closure
  selected,profit=closure([{'pivot':1,'donors':[3]}],{1:2,3:3},lambda r:{0:0,1:5,2:7,3:9}[r])
  self.assertEqual(selected,[]);self.assertEqual(profit,0)

if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 unittest.main()
