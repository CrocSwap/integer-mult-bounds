"""Exhaustive small-model check of target-prefix plus sink domination."""
from itertools import permutations,product
import unittest

def close(v):
    # Dp: row0<-row1. Ds: row2<-row0. Dp Ds=0, Ds Dp !=0.
    z=v[:];z[0]+=2*v[1];z[2]+=2*z[0];return z

def replay(word,seed):
    v=seed[:]
    for op in word:
        if op in ('p0','p1'):v[0]+=v[1]
        elif op in ('s0','s1'):v[2]+=v[0]
        else:v[int(op)]+=1
    return v

class TargetMajorant(unittest.TestCase):
 def test_all_interleavings_nonnegative_sources(self):
    count=0
    # Two copies of each target shear and one increment in every coordinate.
    for word in permutations(('p0','p1','s0','s1','0','1','2')):
        for seed in product(range(2),repeat=3):
            bound=close([x+1 for x in seed]);actual=replay(word,list(seed))
            self.assertTrue(all(a<=b for a,b in zip(actual,bound)));count+=1
    self.assertEqual(count,40320)
 def test_missing_sink_batch_can_underestimate(self):
    seed=[0,1,0];actual=replay(('p0','p1','s0','s1'),seed)
    prefix_only=[2,1,0]
    self.assertGreater(actual[2],prefix_only[2])
 def test_reversing_closure_can_underestimate(self):
    # (I+2Dp)(I+2Ds) misses the directed Ds Dp cross-term.
    actual=replay(('p0','p1','s0','s1'),[0,1,0])
    self.assertEqual(actual,[2,1,4]);self.assertGreater(actual[2],0)

if __name__=='__main__':unittest.main()
