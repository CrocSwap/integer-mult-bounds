"""Independently authored regression checks. Upstream files remain inert data."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import check_bridge as bridge
import check_scalar_bounds as scalar
from check_scalar_bounds import run as norms
class Bridge156Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  bridge.configure('156');cls.r=bridge.run()
 def test_exact_full_alias_paths(self):
  self.assertEqual(len(self.r['selected_reused_donors']),102)
  self.assertEqual(len(self.r['selected_paths']),353)
  for z in self.r['selected_reused_donors']:
   self.assertLess(z['donor_last_order'],z['gauge_read_order']);self.assertLessEqual(z['gauge_read_order'],z['recipient_first_order']);self.assertEqual(z['dimensions'][-1],24)
 def test_literal_response_and_inverse(self):
  self.assertEqual(self.r['old_kernel_relations_and_cut_triples_reproduced'],1734);self.assertTrue(self.r['all_column_formal_composition_forward_inverse']);self.assertTrue(self.r['omitted_setup_and_restore_rejected']);self.assertEqual(self.r['all_column_dimension'],18952)
 def test_paid_demand(self):
  self.assertEqual(self.r['local_histogram_delta'],{1:197,2:283,3:-283,4:70,5:-70});self.assertEqual(self.r['residual_family_delta'],{24:-156,23:156})
 def test_scalar_bill_counts(self):
  self.assertEqual((self.r['setup_adds'],self.r['restore_adds'],self.r['removed_initial_unit_additions']),(2545,2545,1928))
 def test_explicit_new_payload_ceiling(self):
  r=norms();self.assertEqual(r['payload_bits'],110);self.assertFalse(r['retained_payload_cap_2_to104']);self.assertTrue(r['new_payload_cap_2_to112']);self.assertEqual(r['explicit_new_payload_cap_bits'],112)
 def test_no_final12_gain(self):
  self.assertEqual(len(self.r['direct_final12_endpoint_port_rejected']),12)
 def mutate_witness(self,fn):
  obj=json.loads(bridge.CAND.read_text());fn(obj)
  # Hash verification already passes on the untouched pinned witness in setUpClass.
  # These controls bypass only the witness hash to reach structural validation.
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'mutated.json';p.write_text(json.dumps(obj))
   with patch.object(bridge,'CAND',p),patch.object(bridge,'verify_sources',lambda:None):
    with self.assertRaises(AssertionError):bridge.run()
 def test_wrong_physical_mapping_rejected(self):
  self.mutate_witness(lambda x:x['entries'][0]['donors'].__setitem__(0,x['entries'][0]['donors'][0]+1))
 def test_wrong_relation_rejected(self):
  def change(x):
   e=x['entries'][0];e['donors'].pop();e['virtual_donors'].pop()
  self.mutate_witness(change)
 def test_invalid_entrance_line_rejected(self):
  self.mutate_witness(lambda x:x['entries'][0]['basis'][0].__setitem__(0,2))
 def test_premature_alias_reuse_rejected(self):
  recipient=self.r['selected_reused_donors'][0]['recipient_role'];oldread=bridge.read
  def changed_read(name):
   obj=oldread(name)
   if name=='gen5bit/selected/bit/word_p12.json.gz':obj['reads'][str(recipient)]=0
   return obj
  with patch.object(bridge,'read',changed_read):
   with self.assertRaises(AssertionError):bridge.run()
 def test_fresh_eight_sink_majorant(self):
  r=norms();self.assertEqual((r['sink_literal_words_verified'],r['actual_sink_redirects'],r['target_majorant_edges'],r['target_majorant_acyclic_vertices']),(8,16,684,912))
  self.assertEqual((r['forward']['inherited_bound'],r['inverse']['inherited_bound']),(86453,2766560))
  self.assertEqual((r['forward']['certified_new_bound'],r['inverse']['certified_new_bound']),(438151,14104135))
 def test_wrong_eighth_sink_target_rejected(self):
  oldread=scalar.read
  def changed_read(name):
   obj=oldread(name)
   if name=='sink-selection.json':
    z=next(z for z in obj['sinks']if z['role']==13115);z['targets'][0]+=1
   return obj
  with patch.object(scalar,'read',changed_read):
   with self.assertRaises(AssertionError):norms()
 def test_illegal_eighth_sink_source_use_rejected(self):
  oldread=scalar.read
  def changed_read(name):
   obj=oldread(name)
   if name=='gen5bit/selected/bit/word_p12.json.gz':obj['ops'][0][1]=13115
   return obj
  with patch.object(scalar,'read',changed_read):
   with self.assertRaises(AssertionError):norms()
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 unittest.main()
