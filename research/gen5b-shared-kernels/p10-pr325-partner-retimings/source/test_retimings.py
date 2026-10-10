from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
"""Focused independently encoded tests for the emitted PR325 source witnesses."""
from pathlib import Path
from collections import Counter
import json,gzip,hashlib,unittest,subprocess,sys
P=contract.SOURCE
def read(n):
 b=(P/n).read_bytes();return json.loads(gzip.decompress(b)if n.endswith('.gz')else b)
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=read('RESULT.json');cls.s=read('retiming-selection.json')['entries'];cls.e=read('scalar-events.json.gz');cls.p=read('source-events.json.gz');cls.g=read('inputs/bitword__selected__bit__graph_p10.json')
 def test_code_and_artifact_bindings(self):
  self.assertEqual(contract.sha(contract.HERE/'source/check_retimings.py'),self.r['checker_sha256'])
  for n,h in self.r['artifacts'].items():self.assertEqual(sha(n),h)
 def test_fresh_source_pins(self):
  m=read('SOURCES.json');self.assertEqual(m['head'],'0eca9340a3df6141b8e71a41638c3937b3522888')
  for z in m['files']:
   b=(P/'inputs'/z['local']).read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),z['sha256']);self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),z['git_blob'])
 def test_actual_source_projection(self):
  p=[dict(event=i,**e)for i,e in enumerate(self.e)if e['op']==1 and min(e['a'],e['b'])<960];self.assertEqual(p,self.p);self.assertEqual(len(p),3840)
 def test_disjoint_pairs_and_own_source_uses(self):
  self.assertEqual(Counter(q for z in self.s for q in(z['carrier'],z['passive'])),Counter(range(960)))
  for z in self.s:
   for key,typ in [('carrier_uses',['inject','partner_setup','partner_delivery','partner_delivery','partner_cleanup','uninject']),('passive_uses',['inject','partner_setup','partner_cleanup','uninject'])]:self.assertEqual([self.e[i]['semantic'][0]for i in z[key]],typ)
   self.assertEqual(z['setup_event']+1,z['delivery_events'][0]);self.assertEqual(z['delivery_events'][0]+1,z['delivery_events'][1]);self.assertLess(z['delivery_events'][-1],z['cleanup_event'])
 def test_integer_containment_and_gram(self):
  dot=lambda a,b:sum(x*y for x,y in zip(a,b))
  for z in self.s:
   A=z['new_annihilator'];B=z['new_basis'];self.assertEqual((len(A),len(B)),(2,18))
   self.assertTrue(all(dot(a,b)==0 for a in A for b in B))
   for q in(z['carrier'],z['passive']):self.assertTrue(all(sum(a[j]for j in self.g['labels'][q])==0 for a in A))
   H=[[11*dot(a,b)-sum(a)*sum(b)for b in A]for a in A];self.assertEqual(H,z['gram_inverse_integer']);self.assertEqual(H[0][0]*H[1][1]-H[0][1]*H[1][0],4356)
 def test_individual_setup_and_cleanup_omissions(self):
  for z in self.s:
   a,b=z['carrier'],z['passive'];base=[self.e[i]for i in z['carrier_uses']if self.e[i]['a']==a]
   for omitted in(z['setup_event'],z['cleanup_event']):
    x={a:1,b:2}
    for i in z['carrier_uses']:
     e=self.e[i]
     if e['a']==a and i!=omitted:x[a]^=x[b]
    self.assertNotEqual(x[a],1)
 def test_histogram_and_endpoints(self):
  self.assertEqual(self.r['admitted'],480);self.assertEqual(self.r['rejected'],0);self.assertEqual(self.r['local_histogram_delta'],{'1':-960,'2':480,'16':-480,'17':960,'18':-480});self.assertEqual(self.r['source_rank_mass'],18240);self.assertEqual(self.r['source_histogram_after'],{'2':960,'17':960});self.assertTrue(self.r['source_endpoints_exactly_restored'])
 def test_scalar_projection_and_COPY_lifetimes(self):
  work=None;counts=Counter()
  for e in self.e:
   op,a,b=e['op'],e['a'],e['b'];counts[op]+=1
   if op==2:self.assertIsNone(work);work=(a,b,e['frame'])
   elif op==3:self.assertEqual(work,(a,b,e['frame']));work=None
   elif b==10020:self.assertIsNotNone(work);self.assertEqual(e['frame'],-1)
  self.assertEqual(counts,{1:350640,2:20,3:20});self.assertIsNone(work);self.assertEqual(sum(abs(e['c'])for e in self.e if e['op']==1),352560)
 def test_fresh_norms_and_controls(self):
  self.assertEqual((self.r['forward_norm'],self.r['inverse_norm']),(22071,959838));self.assertTrue(self.r['full_F2_forward_and_inverse_all_columns_pass']);self.assertEqual(set(self.r['controls'].values()),{480});self.assertTrue(self.r['COPY_and_ERASE_records_byte_equivalent'])
 def test_assertions_required(self):
  x=subprocess.run([sys.executable,'-O',str(contract.HERE/'source/check_retimings.py')],capture_output=True,text=True);self.assertNotEqual(x.returncode,0);self.assertIn('Assertions must be enabled',x.stderr)
if __name__=='__main__':unittest.main()
