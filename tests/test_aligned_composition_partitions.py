"""Exercise the portable firstK grouping and newly explicit configuration guards."""
from copy import deepcopy
from pathlib import Path
from random import Random
import sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/experiments'))
import aligned_composition_graph as provider
class PartitionControls(unittest.TestCase):
 def test_first_k_respects_original_indices_and_strict_contraction(self):
  rng=Random(20261009)
  for n in range(3,81):
   for k in (0,1,2,6,9,n//2,n,n+7):
    points=list(range(n));rng.shuffle(points);groups=[];i=0
    while i<n:
     size=1 if i==n-1 or rng.random()<.3 else 2;groups.append(points[i:i+size]);i+=size
    if len(groups)==n:groups[:2]=[groups[0]+groups[1]]
    class Parent:
     def grouping(self,unused):return deepcopy(groups)
    obj=provider.split_class(Parent,[f'first{k}'])();obj._level=0
    chosen=[i for i in range(min(k,len(groups))) if len(groups[i])==2][:max(0,n-len(groups)-1)] if n>3 else []
    expected=[piece for i,g in enumerate(groups) for piece in ([[x] for x in g] if i in chosen else [g])]
    actual=obj.grouping(points);self.assertEqual(actual,expected);self.assertLess(len(actual),n);self.assertEqual([x for g in actual for x in g],points)
 def test_absent_depth_uses_original_partition(self):
  class Parent:
   def grouping(self,unused):return [[0,1],[2,3],[4]]
  obj=provider.split_class(Parent,['first6'])();obj._level=10
  self.assertEqual(obj.grouping(list(range(5))),[[0,1],[2,3],[4]])
 def test_new_depth_and_anchor_settings_are_certified(self):
  for h in (23,25):
   for key,value in (('anchor_pairs',True),('anchor_pairs',0),('coarse_word','hhh'+'c'),('coarse_word','ccc')):
    changed=deepcopy(provider.EXPECTED_CONFIGS[h]);changed[key]=value
    with self.subTest(h=h,key=key,value=value),patch.object(provider.json,'loads',return_value=changed),self.assertRaises(ValueError):provider.configuration(h)
if __name__=='__main__':unittest.main()
