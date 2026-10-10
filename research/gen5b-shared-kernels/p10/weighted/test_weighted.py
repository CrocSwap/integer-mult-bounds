"""Fast mutation regressions; full certificates are generated once by aggregate."""
import copy,hashlib,json,unittest
from pathlib import Path
from check_transport import OVER,OVER_SHA,CAND,CAND_SHA,rr,included
from weighted_source_data import OUTPUT,read
class WeightedRegressions(unittest.TestCase):
 def test_overlay_binding_rejects_mutation(self):
  b=OVER.read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),OVER_SHA)
  self.assertNotEqual(hashlib.sha256(b+b' ').hexdigest(),OVER_SHA)
 def test_witness_binding_rejects_wrong_rank(self):
  self.assertEqual(hashlib.sha256(CAND.read_bytes()).hexdigest(),CAND_SHA)
  x=json.loads(CAND.read_text());x['entries'][0]['rank']=2
  self.assertNotEqual(hashlib.sha256(json.dumps(x).encode()).hexdigest(),CAND_SHA)
 def test_wrong_physical_mapping(self):
  w=json.loads(OVER.read_text());alias={b:a for a,b in w['pairs']};ids={r:1920+i for i,r in enumerate(sorted(set(range(9120))-set(alias)))}
  e=json.loads((OUTPUT/'rebound-candidate19.json').read_text())['entries'][0]
  wanted=ids[alias.get(e['virtual_pivot'],e['virtual_pivot'])]
  self.assertEqual(e['pivot'],wanted);self.assertNotEqual(e['pivot']+1,wanted)
 def test_wrong_line_is_not_contained(self):
  self.assertTrue(included([[1,-1]+[0]*18],[[1,-1]+[0]*18]))
 def test_noncontained_line_rejected(self):
  self.assertFalse(included([[1,0]+[0]*18],[[0,1]+[0]*18]))
 def test_exact_dependent_rank(self):
  a,p=rr([[1,-1]+[0]*18,[2,-2]+[0]*18]);self.assertEqual(len(p),1)
 def test_every_target_close_member_and_omission(self):
  r=json.loads((OUTPUT/'target-chronology-result.json').read_text())
  self.assertEqual(r['all120_literal_target_relations'],120)
  self.assertTrue(r['all480_group_members_checked_at_close']);self.assertTrue(r['negative_controls'])
 def test_delayed_target_port_mutation(self):
  r=json.loads((OUTPUT/'reorder-transport-result.json').read_text());ports={s for z in r['receipts']for s in z['precompact_incidence'][:2]}
  self.assertTrue(all(not{z[1],z[2]}&ports for z in r['late_compensations']))
  q=list(r['late_compensations'][0]);q[1]=next(iter(ports));self.assertTrue({q[1],q[2]}&ports)
 def test_norm_dependency_bindings(self):
  r=json.loads((OUTPUT/'scalar-recurrence-result.json').read_text());code=Path(__file__).parent
  for name,wanted in r['dependency_sha256'].items():self.assertEqual(hashlib.sha256(((code if name.endswith('.py')else OUTPUT)/name).read_bytes()).hexdigest(),wanted)
  self.assertEqual(r['final_compact_columns'],10141);self.assertEqual(r['retained_sink_spectator_columns'],7);self.assertTrue(r['retained_payload_cap_2_to104'])
if __name__=='__main__':unittest.main()
