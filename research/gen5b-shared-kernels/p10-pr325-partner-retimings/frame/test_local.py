from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
"""Companion bindings and negative controls for the fresh PR325 local frame word."""
from pathlib import Path
from collections import Counter
import json,gzip,hashlib,subprocess,sys,unittest
P=contract.FRAME;S=contract.SOURCE
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=read(P/'RESULT.json');cls.v=read(P/'VALIDATION.json');cls.e=read(P/'local-events.json.gz');cls.records=read(P/'local-records.json.gz');cls.end=read(P/'local-endpoints.json');cls.f=read(P/'local-frames.json.gz');cls.roles=read(P/'role-map.json');cls.w=read(S/'inputs/bitword__selected__bit__word_p10.json.gz')
 def test_immutable_source_packet(self):
  self.assertTrue(contract.verify_source())
  for z in read(S/'MANIFEST.json')['files']:self.assertEqual(sha(S/z['path']),z['sha256'])
 def test_all_code_and_output_bindings(self):
  self.assertEqual(sha(contract.HERE/'frame/build_local.py'),self.r['checker_sha256']);self.assertEqual(sha(P/'RESULT.json'),self.v['builder_receipt_sha256']);self.assertEqual(sha(contract.HERE/'frame/validate_local.py'),self.v['checker_sha256'])
  for n,h in self.r['artifacts'].items():self.assertEqual(sha(P/n),h)
 def test_source_projection_exact_rebinding(self):
  sm={v:int(k)for k,v in read(P/'source-frame-map.json').items()};old=read(S/'scalar-events.json.gz');self.assertEqual(len(old),len(self.e))
  for i,(a,b)in enumerate(zip(old,self.e)):
   self.assertEqual(b['original_index'],i);c=dict(b);del c['original_index'];c['frame']=sm[c['frame']];self.assertEqual(a,c)
 def test_physical_role_map_rederived(self):
  aliases={b:a for a,b in self.w['pairs']};regs=sorted(set(range(9060))-set(aliases));idx={r:1920+i for i,r in enumerate(regs)}
  self.assertEqual(self.roles['physical_by_virtual'],{str(r):idx[aliases.get(r,r)]for r in range(9060)});self.assertEqual(self.roles['representative_by_physical'],{str(idx[r]):r for r in regs});self.assertEqual(len(set(self.roles['physical_by_virtual'].values())),8100)
 def test_every_current_operation_bound(self):
  m=self.roles['physical_by_virtual'];seen=Counter()
  for e in self.e:
   if e['semantic'][0]in('forward','inverse'):
    k,i=e['semantic'];a,b,_=self.w['ops'][i];self.assertEqual((e['a'],e['b']),(m[str(a)],m[str(b)]));self.assertEqual(e['c'],1 if k=='forward'else-1);seen[k,i]+=1
  self.assertEqual(seen,Counter({(k,i):1 for k in('forward','inverse')for i in range(len(self.w['ops']))}))
 def test_endpoint_dimensions_and_paths(self):
  dim=lambda x:self.f[str(x)]['rank'];initial=self.end['initial'];final=self.end['final'];self.assertEqual(len(initial),10020);self.assertEqual(Counter(dim(initial[str(q)])for q in range(1920,10020)),{0:6900,16:1200});self.assertEqual({dim(final[str(q)])for q in range(1920,10020)},{20});self.assertEqual({dim(final[str(q)])for q in range(960,1920)},{19})
  for q,ch in read(P/'local-paths.json.gz').items():self.assertEqual(ch[0],initial[q]);self.assertEqual(ch[-1],final[q])
 def test_literal_histogram(self):
  h=Counter()
  for op,a,b,c,f,z in self.records:
   if op==0 and f:h[f]+=1
   if op==2:h[z]+=1
  self.assertEqual(h,{int(k):v for k,v in self.r['one_stage_paid_histogram'].items()});self.assertEqual((sum(h.values()),sum(k*v for k,v in h.items())),(46844,179640));self.assertEqual(self.r['histogram_parts']['source'],{'2':960,'17':960})
 def test_all_frame_and_COPY_validation(self):
  self.assertEqual(self.v['frames'],12885);self.assertEqual(self.v['records'],398660);self.assertEqual(self.v['exact_MOVE_containment_pairs'],40125);self.assertEqual(self.v['copies'],20);self.assertTrue(self.v['all_frame_G_nondegeneracy_certified']);self.assertTrue(self.v['source_and_target_and_helper_final_states_exact']);self.assertEqual(self.v['zeroed_basis_row_controls_rejected'],12884)
 def test_integer_operand_support_and_norms(self):
  self.assertEqual(self.r['integer_operand_source_support_checks'],563928);self.assertTrue(self.r['all_helper_integer_sources_restored']);self.assertEqual(self.r['copied_input_source_checks'],2880);self.assertEqual((self.v['forward_norm'],self.v['inverse_norm']),(22071,959838));self.assertEqual(self.r['payload_bound'],64*22071**3*959838**2);self.assertEqual(self.r['payload_bits'],90)
 def test_copy_orientation_mutation_rejected(self):
  copy=next(z for z in self.records if z[0]==2);op,a,b,c,f,z=copy;self.assertEqual(b,10020);self.assertLess(a,10020);self.assertNotEqual(a,b);bad=copy[:];bad[1],bad[2]=bad[2],bad[1];self.assertNotEqual(bad[2],10020)
 def test_nonmonotone_MOVE_mutation_rejected(self):
  row=next(z for z in self.records if z[0]==0 and z[4]>0);_,q,a,b,gap,_=row;self.assertEqual(self.f[str(b)]['rank']-self.f[str(a)]['rank'],gap);self.assertLess(self.f[str(a)]['rank']-self.f[str(b)]['rank'],0)
 def test_assertions_required(self):
  for name in('build_local.py','validate_local.py'):
   x=subprocess.run([sys.executable,'-O',str(contract.HERE/'frame'/name)],capture_output=True,text=True);self.assertNotEqual(x.returncode,0);self.assertIn('Assertions must be enabled',x.stderr)
if __name__=='__main__':unittest.main()
