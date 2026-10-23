"""Focused controls for the independently authored p10 candidate15 checker."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import support
from unittest.mock import patch
import unittest,tempfile,json,copy,hashlib
import check_bridge as b
import check_scalar_bounds as n
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.bridge=b.run();cls.norm=n.run()
 def candidate_failure(self,change):
  obj=json.loads(b.CAND.read_text());change(obj)
  with tempfile.TemporaryDirectory()as td:
   p=Path(td)/'candidate.json';p.write_text(json.dumps(obj));s=hashlib.sha256(p.read_bytes()).hexdigest()
   with patch.object(b,'CAND',p),patch.object(b,'CAND_SHA',s):
    with self.assertRaises(AssertionError):b.run()
 def test_pinned_census_and_payload(self):
  r=self.bridge;q=self.norm
  self.assertEqual((r['selected_pivots'],r['selected_distinct_donors'],r['setup_adds']),(15,17,40))
  self.assertEqual(r['local_histogram_delta'],{1:17,2:30,3:-30,4:2,5:-2})
  self.assertEqual(r['old_kernel_relations_and_cut_triples_reproduced'],775)
  self.assertEqual(len(r['selected_reused_donors']),2)
  self.assertEqual((q['forward']['certified_new_bound'],q['inverse']['certified_new_bound']),(49937,1194200))
  self.assertTrue(q['retained_payload_cap_2_to104']);self.assertEqual(q['payload_bits'],94)
 def test_omitted_relation_donor_rejected(self):
  def mutate(c):c['entries'][0]['donors'].pop();c['entries'][0]['virtual_donors'].pop()
  self.candidate_failure(mutate)
 def test_wrong_common_cut_rejected(self):
  self.candidate_failure(lambda c:c['entries'][0]['cut_read'].__setitem__(0,960))
 def test_wrong_entrance_line_rejected(self):
  self.candidate_failure(lambda c:c['entries'][0].__setitem__('basis',[[1,-1]+[0]*18]))
 def test_alias_overlap_rejected(self):
  original=b.read;recipient=self.bridge['selected_reused_donors'][0]['recipient_role']
  def read(name):
   z=original(name)
   if name.endswith('word_p10.json.gz'):z['reads'][str(recipient)]=0
   return z
  with patch.object(b,'read',read):
   with self.assertRaises(AssertionError):b.run()
 def test_reorder_crossing_prefix_rejected(self):
  original=b.read
  def read(name):
   z=original(name)
   if name=='reorder-selection.json':z['moves'][0]['anchor']=1
   return z
  with patch.object(b,'read',read):
   with self.assertRaises(AssertionError):b.run()
 def test_wrong_sink_target_rejected(self):
  original=n.read
  def read(name):
   z=original(name)
   if name=='sink-selection.json':z['sinks'][-1]['targets'][0]+=1
   return z
  with patch.object(n,'read',read):
   with self.assertRaises(AssertionError):n.run()
 def test_inherited_raw_crossings_are_explicit(self):
  x=self.bridge['reorder_transport'];self.assertTrue(x['original_raw_crossing_contract_inherited'])
  self.assertFalse(x['all133_raw_crossings_independently_replayed'])
  self.assertLess(x['raw_prefix_upper'],x['minimum_entire_interval_start'])
if __name__=='__main__':unittest.main()
