from pathlib import Path
from itertools import combinations
from copy import deepcopy
import importlib.util,json,unittest
from nodeops import order_key,reorder,verify_dense,relabel
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original',ROOT/'original/nodeops.py');original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
KEYS=json.loads((ROOT/'keys.json').read_text())
class Fake:
 def __init__(self):
  self.h=5;self.inputs=list(combinations(range(5),3));self.args=[None]*11;self.core=[0]+[sum(1<<i for i in t) for t in self.inputs];self.union=self.core.copy();self.provenance=[None]*11
  # Same-envelope ordered dependency at nodes11,12; other same-rank envelope13.
  for a,b in [(1,6),(11,2),(2,3)]:
   self.args.append((a,b));self.core.append(self.core[a]&self.core[b]);self.union.append(self.union[a]|self.union[b]);self.provenance.append(None)
  self.active=set(range(1,len(self.args)));self.outputs={};self.support_in=type('Cache',(),{'cache_clear':lambda self:None})()
 def verify(self):
  for x in self.active:
   for y in self.args[x] or ():assert y<x
  return {'PASS':True}
class OrderTests(unittest.TestCase):
 def test_all_keys_rank_first(self):
  items=[((core,cover),[i]) for i,(core,cover) in enumerate(( (7,7),(3,7),(1,7),(1,15),(2,14),(0,31)),20)]
  for key in KEYS:
   ranks=[order_key(x,key)[0] for x in sorted(items,key=lambda x:order_key(x,key))]
   self.assertEqual(ranks,sorted(ranks))
 def test_original_pr74_exact_arrays(self):
  a=original.reorder(Fake());b=reorder(Fake(),'pr74')
  for n in ('args','core','union','provenance','active','outputs'):self.assertEqual(getattr(a,n),getattr(b,n))
 def test_all_keys_preserve_topological_dependencies(self):
  for key in KEYS:reorder(Fake(),key).verify()
 def test_same_envelope_order_is_unchanged(self):
  for key in KEYS:
   c=Fake();c.provenance=list(range(len(c.args)));c=reorder(c,key)
   before=[11,12];positions=[c.provenance.index(i) for i in before];self.assertEqual(positions,sorted(positions))
 def test_relabel_equal_original(self):
  word={'h':4,'v':4,'frames':[[7,15],[3,7]],'sources':{'0':0,'1':1},'scatter':[[4,8],[6,9]],'outputs':[[0,0,0,[0,1,2]]]}
  self.assertEqual(relabel(deepcopy(word),[1,0,3,2]),original.relabel(deepcopy(word),[1,0,3,2]))
 def test_dense_accepts_correct_disjoint_graph(self):
  self.assertIn('PASS',verify_dense(Fake())['status'])
 def test_dense_rejects_wrong_envelope(self):
  c=Fake();c.core[11]=0
  with self.assertRaises(AssertionError):verify_dense(c)
if __name__=='__main__':unittest.main(verbosity=2)
