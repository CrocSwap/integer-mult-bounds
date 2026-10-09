from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import unittest
from local_support_elimination import classes,branch_orbits,TRIPLES,CLIQUE,EDGES,INDEX
from verify_local_support import verify_rejection


class LocalSupportTests(unittest.TestCase):
    def test_remainder_edges_partition_exactly(self):
        supports={t:{i for i,c in enumerate(CLIQUE) if len(set(t)&set(c))!=1}
                  for t in TRIPLES if t not in CLIQUE}
        expected={tuple(sorted((INDEX[s],INDEX[t]))) for s,t in EDGES
                  if s in supports and t in supports and not supports[s]&supports[t]}
        actual={tuple(sorted((i,j))) for x,y in classes() for i in x for j in y}
        self.assertEqual(actual,expected);self.assertEqual(len(actual),210)

    def test_four_modes_are_exact_and_specific_to_one_remainder(self):
        # True means the whole aggregate A or B block vanishes.
        for ax,bx,ay,by in product((False,True),repeat=4):
            equations=(bx or ay) and (by or ax)
            modes=(ax and ay) or (bx and by) or (ax and bx) or (ay and by)
            self.assertEqual(equations,modes)
        # In a two-dimensional remainder, a product can vanish with neither
        # factor zero. Thus this case split must not be reused for d=16.
        self.assertEqual(sum(x*y for x,y in zip([1,0],[0,1])),0)

    def test_orbits_cover_all_mode_patterns(self):
        orbits=branch_orbits()
        self.assertEqual(len(orbits),146)
        self.assertEqual(sum(size for _,size in orbits),16384)

    def test_all_negative_certificates_and_mutation(self):
        result=json.loads(Path(__file__).with_name('local-support-elimination.json').read_text())
        rejected=[row for row in result['branches'] if row['diagonal_test']['status'].startswith('EXCLUDED')]
        self.assertEqual(len(rejected),43)
        for row in rejected:self.assertTrue(verify_rejection(row['branch'],row['diagonal_test']))
        row=rejected[0];bad=deepcopy(row['diagonal_test'])
        bad['certificate'][0]['coefficient']=str(Q(bad['certificate'][0]['coefficient'])+1)
        with self.assertRaises(AssertionError):verify_rejection(row['branch'],bad)


if __name__=='__main__':unittest.main()
