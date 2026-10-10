from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Independent binding and individual new-kernel mutation regressions."""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import hashlib,json,gzip,subprocess,sys,unittest
P=packet.ADMISSION;BASE=packet.BASE_FRAME
def read(n):
 p=Path(n);p=p if p.is_absolute()else P/p;b=p.read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
@lru_cache(None)
def events():return read('local-events.json.gz')
def wrong_with_omission(kind,pivot):
 n=10141;col=[1<<q for q in range(n+1)];tmp=None
 for e in events():
  op,a,b=e['op'],e['a'],e['b']
  if op==1:
   if e['semantic'][:2]==[kind,pivot]:continue
   col[a]^=col[b]
  elif op==2:
   if tmp is not None:raise AssertionError('overlapping COPY')
   tmp=a;col[b]=col[a]
  else:
   if tmp!=a or col[a]!=col[b]:raise AssertionError('changed COPY capture')
   tmp=None
 return [q for q in range(n)if col[q]!=((1<<q)^((1<<(q-960))if 960<=q<1920 else 0))]
class AdmissionTests(unittest.TestCase):
 def test_immutable_upstream_witnesses(self):
  d=read(packet.SOURCE_PROVENANCE);self.assertEqual([x['author']for x in d['metadata']],['eumemic','eumemic']);self.assertEqual([x['head']for x in d['metadata']],['8ce22e5e487e9d1017c26702adc09d5646565d0c','e51f5ffee8ab574e5b8249a4612411b2ca5f100d'])
  for r in d['files']:
   b=(packet.INPUTS/r['label']).read_bytes();self.assertEqual(len(b),r['bytes']);self.assertEqual(hashlib.sha256(b).hexdigest(),r['sha256']);self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),r['sha'])
 def test_checker_and_artifact_bindings(self):
  d=read('RESULT.json');self.assertEqual(sha(packet.HERE/'admission/build_local.py'),d['checker_sha256'])
  for n,h in d['artifacts'].items():self.assertEqual(sha(P/n),h)
  v=read('VALIDATION.json');self.assertEqual(v['builder_receipt_sha256'],sha(P/'RESULT.json'));self.assertEqual(v['checker_sha256'],sha(packet.HERE/'admission/validate_local.py'))
 def test_physical_rebinding(self):
  r=read('physical-rebinding.json');self.assertEqual(len(r),20);self.assertEqual(len({x['new_compact']for x in r}),20);self.assertTrue(all(1920<=x['new_compact']<10141 for x in r));self.assertTrue(read('RESULT.json')['all20_selected_physical_ports_rebound'])
 def test_each_own_kernel_cut(self):
  r=read('new-kernel-receipts.json');self.assertEqual([x['pivot']for x in r],[7000,7234,7349]);self.assertEqual([x['removed_reads']for x in r],[4,12,16]);self.assertEqual([x['nonzero_target_responses']for x in r],[4,12,16]);self.assertTrue(all(x['rank']==2 and len(x['basis'])==2 and len(x['donors'])==3 for x in r))
 def test_individual_setup_omissions(self):
  for pivot in[7000,7234,7349]:self.assertTrue(wrong_with_omission('new_kernel2_setup',pivot),pivot)
 def test_individual_restore_omissions(self):
  for pivot in[7000,7234,7349]:self.assertTrue(wrong_with_omission('new_kernel2_restore',pivot),pivot)
 def test_all133_live_anchor_positions(self):
  es=events();pos={x['original_index']:i for i,x in enumerate(es)};rs=read('reorder-receipts.json');self.assertEqual(len(rs),133)
  for r in rs:
   i,j=pos[r['moved_uid']],pos[r['anchor_uid']];self.assertEqual(es[i]['frame'],r['frame']);self.assertTrue(es[i].get('moved'));self.assertEqual(es[i]['semantic'],r['moved_semantic']);self.assertEqual(es[j]['semantic'],r['anchor_semantic']);self.assertTrue(i<j if r['side']=='before'else j<i);self.assertTrue(r['literal_crossed_interval_verified'])
 def test_retiming_shapes(self):
  r=read('retiming-receipts.json');f=read('local-frames.json.gz');self.assertEqual(len(r),4);self.assertEqual([f[str(e['old_frame'])]['rank']for e in r],[8,8,8,13]);self.assertEqual([f[str(e['new_frame'])]['rank']for e in r],[9,9,9,14])
 def test_literal_profile_delta(self):
  d=read('RESULT.json');old=read(BASE/'RESULT.json');x=Counter({int(k):v for k,v in d['one_stage_paid_histogram'].items()});x.subtract({int(k):v for k,v in old['one_stage_paid_histogram'].items()});self.assertEqual({k:v for k,v in x.items()if v},{1:24,2:1,3:-12,8:-3,9:3,13:-1,14:1});self.assertEqual(d['one_stage_calls'],48486);self.assertEqual(d['one_stage_rank_mass'],179458)
 def test_fresh_norms_and_payload(self):
  d=read('RESULT.json');self.assertEqual(d['forward']['max_row_l1'],132195);self.assertEqual(d['inverse']['max_row_l1'],1307808);self.assertEqual(d['payload_bound'],64*132195**3*1307808**2);self.assertLess(d['payload_bound'],2**104)
 def test_all_frame_validation_and_controls(self):
  d=read('VALIDATION.json');self.assertEqual(d['frames'],15041);self.assertEqual(d['exact_MOVE_containment_pairs'],44773);self.assertEqual(d['zeroed_basis_row_controls_rejected'],15040)
  for k in['all_frame_ranks_and_annihilators_exact','all_frame_G_nondegeneracy_certified','source_and_target_and_helper_final_states_exact','moved_ADD_omission_rejected']:self.assertTrue(d[k])
 def test_prior_frozen_packet_unchanged(self):
  self.assertTrue(packet.verify_base())
 def test_assertion_disabled_rejected(self):
  for name in['build_local.py','validate_local.py','check_frozen_experiment.py']:
   r=subprocess.run([sys.executable,'-O',str(packet.HERE/'admission'/name)],capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertIn('Assertions must be enabled',r.stderr)
if __name__=='__main__':unittest.main()
