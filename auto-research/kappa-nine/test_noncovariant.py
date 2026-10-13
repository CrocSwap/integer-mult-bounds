from copy import deepcopy
from fractions import Fraction as Q
import unittest
from noncovariant_search import CLIQUE,TRIPLES,EDGES,control_factors,verify_factors,gauged_control
from shared_scalar_screen import audit


class NoncovariantControls(unittest.TestCase):
    def test_exact_positive_control_and_corruption(self):
        factors=control_factors()
        self.assertEqual(verify_factors(factors,16)['unordered_edges'],1890)
        bad=deepcopy(factors);bad[TRIPLES[0]][0][0][0]+=1
        with self.assertRaises(AssertionError):verify_factors(bad,16)
        bad={t:factors[TRIPLES[0]] for t in TRIPLES}
        with self.assertRaises(AssertionError):verify_factors(bad,16)

    def test_exact_gauge_and_support_replay(self):
        self.assertEqual(verify_factors(gauged_control(),16)['vertices'],84)

    def test_shared_scalar_screen(self):
        result=audit()
        self.assertEqual(result['normalized_cross_line_pairing'],'-1/15')
        self.assertEqual(Q(result['shared_scalar_cross_determinant']),Q(1,225))

    def test_gauge_support_is_exact(self):
        self.assertTrue(all(len(set(s)&set(t))==1 for s,t in __import__('itertools').combinations(CLIQUE,2)))
        # Only adjacency to anchored projectors removes rows/columns.
        free=0
        for t in TRIPLES:
            if t in CLIQUE:continue
            allowed=15-2*sum(len(set(t)&set(c))==1 for c in CLIQUE)
            free+=4*allowed
        self.assertEqual(free,2436)


if __name__=='__main__':unittest.main()
