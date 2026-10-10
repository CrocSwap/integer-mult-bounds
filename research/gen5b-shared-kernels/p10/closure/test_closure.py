"""Bounded closure regressions; all data is inert and all executed code authored."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collections import Counter
from itertools import combinations
from fractions import Fraction
import copy,gzip,json,math,unittest
import search_closure as s
from support import OUTPUT
R=OUTPUT/'closure'

def check_witness(witness,cache):
 rows=cache['roles'];pivots={e['virtual_pivot']for e in witness['entries']};donors={d for e in witness['entries']for d in e['virtual_donors']};H=Counter()
 assert len(pivots)==len(witness['entries'])==witness['pivots']and not pivots&donors
 frames={int(k):v for k,v in s.read('bitword/selected/bit/frames_p10.json.gz')['frames'].items()}
 for e in witness['entries']:
  p=e['virtual_pivot'];ds=e['virtual_donors'];assert e['pivot']==rows[str(p)]['stream'] and e['donors']==[rows[str(d)]['stream']for d in ds]
  value=int(rows[str(p)]['response_hex'],16)
  for d in ds:value^=int(rows[str(d)]['response_hex'],16)
  assert value==0 and ds
  assert e['cut_read']==cache['last_plain_read']['scalar']
  line=e['basis'];assert len(line)==1 and len(line[0])==20 and sorted(x for x in line[0]if x)==[-1,1]
  for role in [p]+ds:
   frame=frames[rows[str(role)]['first_base_use']['frame']];A=s.annihilator(frame)
   assert all(sum(a*b for a,b in zip(z,line[0]))==0 for z in A)
 for r in pivots|donors:
  d=frames[rows[str(r)]['first_base_use']['frame']]['dim'];H[d]-=1
  if d>1:H[d-1]+=1
 H[1]+=len(donors);assert {k:v for k,v in H.items()if v}=={int(k):v for k,v in witness['local_histogram_delta'].items()}
 assert sum(k*v for k,v in H.items())==-len(pivots)
 assert witness['distinct_donors']==len(donors)and witness['scalar_setup_pairs']==sum(len(e['donors'])for e in witness['entries'])
 return True
class ClosureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cache=json.loads(gzip.decompress((R/'response-cache.json.gz').read_bytes()));cls.w=json.loads((R/'candidate15.json').read_text())
 def test_01_all_source_pins(self):self.assertEqual(len(s.verify_inputs()),40)
 def test_02_fixed_scope(self):
  z=json.loads((R/'screen-summary.json').read_text());self.assertEqual((z['lines'],z['donor_orders'],z['basis_screens']),(190,2,380));self.assertEqual(z['eligible_after_reorder_guard'],4291)
 def test_03_witness_and_activation_count(self):self.assertTrue(check_witness(self.w,self.cache))
 def test_04_wrong_mapping_rejected(self):
  z=copy.deepcopy(self.w);z['entries'][0]['pivot']+=1
  with self.assertRaises(AssertionError):check_witness(z,self.cache)
 def test_05_omitted_donor_rejected(self):
  z=copy.deepcopy(self.w);z['entries'][0]['virtual_donors'].pop();z['entries'][0]['donors'].pop()
  with self.assertRaises(AssertionError):check_witness(z,self.cache)
 def test_06_missed_activation_rejected(self):
  z=copy.deepcopy(self.w);z['local_histogram_delta']['1']-=1
  with self.assertRaises(AssertionError):check_witness(z,self.cache)
 def test_07_residues_retained(self):
  z=json.loads((R/'best-residue-unions.json').read_text());self.assertEqual(set(z),set(map(str,range(5))))
  for k,w in z.items():self.assertEqual(w['pivots']%5,int(k))
  self.assertEqual(z['4']['pivots'],19)
 def test_08_maxflow_matches_complete_subset_enumeration(self):
  dimensions={0:3,1:3,2:5,3:3,4:5,5:3,6:5};phi=lambda r:r*math.log(100/r)if r else 0
  relations=[dict(pivot=0,donors=[3,4]),dict(pivot=1,donors=[3,5]),dict(pivot=2,donors=[4,5,6])]
  for n in range(1,4):
   rel=relations[:n];chosen,profit=s.closure(rel,dimensions,phi)
   def invoice(xs):
    used={d for e in xs for d in e['donors']}
    return sum(round((phi(dimensions[e['pivot']])-phi(dimensions[e['pivot']]-1))*10**9)for e in xs)-sum(round((phi(1)+phi(dimensions[d]-1)-phi(dimensions[d]))*10**9)for d in used)
   best=max(invoice([e for i,e in enumerate(rel)if mask>>i&1])for mask in range(1<<n))
   self.assertEqual(invoice(chosen),best);self.assertEqual(profit,best)
if __name__=='__main__':unittest.main()
