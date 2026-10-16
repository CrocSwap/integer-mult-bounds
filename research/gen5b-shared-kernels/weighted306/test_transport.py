"""Fast independent algebraic and receipt-binding regression controls."""
from collections import Counter
from pathlib import Path
import copy,hashlib,json,unittest
import check_transport as t

def add(M,a,b,c):
 M=[r[:]for r in M];M[a]=[x+c*y for x,y in zip(M[a],M[b])];return M
def cp(M,d,s):
 M=[r[:]for r in M];M[d]=M[s][:];return M
def eye(n):return [[int(i==j)for j in range(n)]for i in range(n)]
def path_contract(r,base):
 changed=[]
 for z in r['selected_paths']:
  old=base[z['stream']];assert z['first_frame']==old['first_frame'] and z['first_dimension']==old['first_dimension']
  if z['frames']!=old['frames']:
   assert z['dimensions']==old['dimensions'][:-1]+[22,24]
   assert z['frames'][:-2]==old['frames'][:-1] and z['frames'][-1]==old['frames'][-1]
   changed.append(z['stream'])
 assert set(changed)=={x['stream']for x in r['reorder_overlaps']} and len(changed)==18

class TransportTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from test_fixture306 import load_fixture
  r=load_fixture();cls.r=r['bridge'];cls.base={z['stream']:z for z in r['prior_bridge']['selected_paths']}
 def test_source_and_candidate_binding(self):
  t.verify();self.assertEqual(self.r['checker_sha256'],t.sha(t.HERE/'check_transport.py'));self.assertEqual(self.r['candidate_sha256'],t.sha(t.CAND))
 def test_signed_and_unsigned_add_commutation(self):
  I=eye(4);count=0
  for a in range(4):
   for b in range(4):
    if a==b:continue
    for x in range(4):
     for y in range(4):
      if x==y or y==a or x==b:continue
      for c in (-2,-1,1,2):
       for d in (-2,-1,1,2):
        self.assertEqual(add(add(I,a,b,c),x,y,d),add(add(I,x,y,d),a,b,c))
        self.assertEqual(add(add(I,a,b,abs(c)),x,y,abs(d)),add(add(I,x,y,abs(d)),a,b,abs(c)));count+=1
  self.assertGreater(count,100)
 def test_read_destination_crossing_rejected(self):
  I=eye(3);self.assertNotEqual(add(add(I,0,1,1),2,0,1),add(add(I,2,0,1),0,1,1))
 def test_write_source_crossing_rejected(self):
  I=eye(3);self.assertNotEqual(add(add(I,0,1,1),1,2,1),add(add(I,1,2,1),0,1,1))
 def test_copy_commutation_and_forbidden_control(self):
  I=eye(5)
  for a in range(4):
   for b in range(4):
    if a==b:continue
    for x in range(4):
     if x!=a:self.assertEqual(cp(add(I,a,b,2),4,x),add(cp(I,4,x),a,b,2))
     else:self.assertNotEqual(cp(add(I,a,b,2),4,x),add(cp(I,4,x),a,b,2))
 def test_entire_interval_separation(self):
  self.assertEqual(self.r['raw_prefix_upper'],656881)
  for z in self.r['interval_separation']:
   self.assertLess(z['raw_prefix_upper'],z['minimum_interval_start']);self.assertTrue(z['appended_inverse_after_entire_old_word'])
  self.assertFalse(691125<self.r['interval_separation'][0]['minimum_interval_start'])
 def test_all_changed_paths_and_missing_visit_control(self):
  path_contract(self.r,self.base);bad=copy.deepcopy(self.r);z=next(z for z in bad['selected_paths']if'reorder_extra_frame'in z);old=self.base[z['stream']];z['frames']=old['frames'];z['dimensions']=old['dimensions']
  with self.assertRaises(AssertionError):path_contract(bad,self.base)
 def test_norm_and_inherited_boundary(self):
  r=self.r['unsigned_norm_transport'];self.assertEqual((r['forward'],r['inverse']),(438151,14104135));self.assertLess(r['payload'],2**112);self.assertGreaterEqual(r['payload'],2**104)
  self.assertFalse(self.r['inherited_reorder_contract']['all239_raw_crossings_independently_replayed']);self.assertTrue(self.r['inherited_reorder_contract']['raw_crossing_admission_inherited'])
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 unittest.main()
