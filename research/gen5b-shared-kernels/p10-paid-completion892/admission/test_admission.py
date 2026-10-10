"""Independent bindings and mutation regressions for weighted892 admission."""
from pathlib import Path
import hashlib,json,subprocess,sys,unittest
from functools import lru_cache
from collections import defaultdict
from weighted_source_data import read,verify,HEAD,OUTPUT
from admission_config import OVER,OVER_SHA
from check_transport import rr,included
HERE=Path(__file__).resolve().parent
@lru_cache(None)
def data():
 w=json.loads(OVER.read_text());old=read('bitword/selected/bit/word_p10.json.gz')
 ga={e['role']for e in w['gauges']};alias={b:a for a,b in w['pairs']};ids={r:1920+i for i,r in enumerate(sorted(set(range(9120))-set(alias)))};sid=lambda r:ids[alias.get(r,r)]
 phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];g=read('graph.json');adj=[{}for _ in range(9120)]
 for root,r in zip(g['roots'],w['rootroles']):
  for t in root['targets']:adj[r][t]=adj[r].get(t,0)+1
 for i in reversed(order):
  a,b,_=w['ops'][i]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 response={sid(r):sum(1<<t for t,c in adj[r].items()if c%2)for r in range(9120)if r not in ga};last={};index=0
 for r in range(9120):
  if r in ga:continue
  for t,c in adj[r].items():
   if c%2:last[sid(r)]=(index,[960+t,sid(r),-c]);index+=1
 return w,old,response,last
class AdmissionRegressions(unittest.TestCase):
 def test_all_inert_pins(self):verify()
 def test_candidate_hash_mutation(self):
  b=OVER.read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),OVER_SHA);self.assertNotEqual(hashlib.sha256(b+b' ').hexdigest(),OVER_SHA)
 def test_all_literal_kernel_and_omission_controls(self):
  _,_,response,_=data();es=json.loads((OUTPUT/'rebound-kernel-entries.json').read_text())['entries'];self.assertEqual(len(es),1047)
  for e in es:
   p=response[e['pivot']];s=p
   for d in e['donors']:s^=response[d]
   self.assertEqual(s,0);self.assertNotEqual(s^p,0)
 def test_all_literal_cut_and_mutation_controls(self):
  _,_,_,last=data();es=json.loads((OUTPUT/'rebound-kernel-entries.json').read_text())['entries']
  for e in es:
   wanted=max((last[s]for s in[e['pivot']]+e['donors']),key=lambda z:z[0]);self.assertEqual((e['cut_index'],e['cut_read']),wanted)
   bad=e['cut_read'][:];bad[2]-=2;self.assertNotEqual(bad,wanted[1])
 def test_wrong_basis_rank(self):
  e=json.loads((OUTPUT/'rebound-kernel-entries.json').read_text())['entries'][0];self.assertEqual(len(rr(e['basis'])[0]),e['rank']);self.assertNotEqual(len(rr(e['basis'])[0]),e['rank']+1)
 def test_noncontained_line(self):
  self.assertFalse(included([[1,0]+[0]*18],[[0,1]+[0]*18]));self.assertTrue(included([[1,-1]+[0]*18],[[2,-2]+[0]*18]))
 def test_role_map_mutation(self):
  m=json.loads((OUTPUT/'virtual-physical-map.json').read_text())['rows'];self.assertEqual(len(m),9120)
  changed=[r for r in m if r['old_physical']!=r['new_physical']];self.assertTrue(changed)
  for r in changed:self.assertNotEqual(r['old_physical'],r['new_physical'])
 def test_checked_code_and_dependency_binding(self):
  for f,code in [('transport-result.json','check_transport.py'),('target-chronology-result.json','check_target_chronology.py'),('scalar-recurrence-result.json','check_scalar_recurrence.py'),('reorder-transport-result.json','check_reorder_transport.py'),('source-target-geometry-result.json','check_source_target_geometry.py'),('reorder-controls-result.json','check_reorder_controls.py')]:
   d=json.loads((OUTPUT/f).read_text());self.assertEqual(d['head'],HEAD);self.assertEqual(d['overlay_sha256'],OVER_SHA);self.assertEqual(hashlib.sha256((HERE/code).read_bytes()).hexdigest(),d['checker_sha256'])
   for name,h in d.get('dependency_sha256',{}).items():self.assertEqual(hashlib.sha256(((HERE if name.endswith('.py')else OUTPUT)/name).read_bytes()).hexdigest(),h)
 def test_scalar_payload_and_omission_receipts(self):
  d=json.loads((OUTPUT/'scalar-recurrence-result.json').read_text());self.assertTrue(d['all_kernel_setup_and_restore_omission_controls_rejected']);self.assertEqual(d['final_compact_columns'],10141)
  self.assertEqual(d['payload_bound'],64*d['forward']['max_row_l1']**3*d['inverse']['max_row_l1']**2);self.assertLess(d['payload_bound'],2**104)
 def test_target_close_negative_control(self):
  d=json.loads((OUTPUT/'target-chronology-result.json').read_text());self.assertEqual(d['all120_literal_target_relations'],120);self.assertTrue(d['all480_group_members_checked_at_close']);self.assertTrue(d['negative_controls'])
 def test_reorder_port_mutation(self):
  d=json.loads((OUTPUT/'reorder-transport-result.json').read_text());ports={s for e in d['receipts']for s in e['new_precompact_incidence'][:2]};self.assertEqual(len(d['receipts']),133)
  self.assertTrue(all(not{e[1],e[2]}&ports for e in d['late_compensations']))
  bad=list(d['late_compensations'][0]);bad[1]=next(iter(ports));self.assertTrue({bad[1],bad[2]}&ports)
 def test_assertions_disabled_rejected(self):
  r=subprocess.run([sys.executable,'-O','-c','from weighted_source_data import verify; verify()'],cwd=HERE,capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertIn('Assertions must be enabled',r.stderr)
 def test_all_source_target_final_geometry(self):
  d=json.loads((OUTPUT/'source-target-geometry-result.json').read_text());self.assertEqual(d['source_columns'],960);self.assertEqual(d['target_columns'],960);self.assertEqual(d['partner_pairs'],480);self.assertTrue(d['source_line_identities_and_partner_chains_exact']);self.assertTrue(d['all_terminal_targets_in_declared_cap']);self.assertEqual(len(d['paths']),1920);self.assertEqual(d['new_gauge_omission_controls_rejected'],[9118,9119])
 def test_all133_reorder_injected_event_controls(self):
  d=json.loads((OUTPUT/'reorder-controls-result.json').read_text());self.assertEqual(d['moves_checked'],133)
  for k in ['noncommuting_insertions_rejected','commuting_extra_anchor_insertions_rejected','disjoint_positive_controls_accepted']:self.assertEqual(d[k],133)
  self.assertEqual(hashlib.sha256((OUTPUT/'reorder-transport-result.json').read_bytes()).hexdigest(),d['reorder_receipt_sha256'])
 def test_exact892_matching_contract(self):
  d=json.loads((OUTPUT/'transport-result.json').read_text());self.assertEqual(d['new_pairs'],892);self.assertEqual(d['old_pairs'],890);self.assertEqual(d['preserved_pairs'],819);self.assertEqual(d['changed_role_count'],205);self.assertEqual(d['kernel_entries_touching_changed_roles'],77);self.assertEqual(d['representatives_removed'],[9118,9119]);self.assertEqual(d['representatives_added'],[]);self.assertEqual(d['retained_representative_ids_changed'],0)
 def test_authored_and_immutable_input_provenance(self):
  import support
  self.assertEqual(support.HEAD,HEAD);self.assertEqual(support.WORD_SHA,OVER_SHA)
  self.assertEqual(hashlib.sha256(support.INPUT_MANIFEST.read_bytes()).hexdigest(),'98e5e469faab4230cf791b5777a5b324f1aaf9153c6adf1caedfe4afb45a3c03')
  self.assertTrue(support.verify_dependencies())
  self.assertTrue(all(not row['local'].endswith('.py') for row in support.pins()['files']))
 def test_no_extra_kernel_closure(self):
  d=json.loads((OUTPUT/'scalar-recurrence-result.json').read_text());self.assertEqual(d['setup_counts'],{'old':3188});self.assertEqual(d['removed_initial_reads'],{'old':25604,'old_units':25604});self.assertEqual(d['forward']['weighted_additions'],336253);self.assertEqual(d['forward']['literal_unit_additions'],338173)
if __name__=='__main__':unittest.main()
