"""Exact arithmetic and mutation controls; no upstream program execution."""
from collections import Counter
from fractions import Fraction as F
import copy,unittest
from unittest.mock import patch
import price_reorder as p
class ArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_fixture306 import load_fixture
        r=load_fixture();cls.baseline,cls.result,cls.summary=r['baseline'],r['candidate'],r['summary']
    def test_pins_and_unchanged_sources(self):
        r=self.baseline['integrity'];self.assertEqual(r['newly_verified_files'],13);self.assertEqual(len(r['unchanged_inherited_files']),34)
    def test_baseline_exact(self):
        self.assertEqual(self.baseline['assembly']['kappa'],F(751458925311258,10**18))
        self.assertEqual(self.baseline['bit_root_bracket']['lower'],F(752024040794268,10**18))
    def test_conditional_candidate_exact(self):
        r=self.result;self.assertEqual(r['assembly']['kappa'],F(751478472895775,10**18));self.assertFalse(r['composition_verified'])
        self.assertEqual((r['literal_stock'],r['calls'],r['rank_mass']),(1229275,483015,2454150))
    def test_all_constraints_and_adjacent_rejection(self):
        for r in [self.baseline,self.result]:
            self.assertEqual(len(r['assembly']['strict_constraints']),47)
            self.assertGreater(min(r['assembly']['strict_constraints'].values()),0)
            self.assertEqual(r['assembly']['adjacent_grid_rejected'],['g3_above_kappa'])
            root=r['bit_root_bracket'];self.assertLess(root['lower_moment'][1],1);self.assertGreater(root['upper_moment'][0],1)
            self.assertEqual(root['upper']-root['lower'],F(1,10**18))
    def test_two_deltas_preserve_rank_calls(self):
        d,stages=p.reorder_delta();self.assertEqual(sum(d.values()),0);self.assertEqual(p.old.mass(d),0)
        self.assertEqual([r['moves']for r in stages],[237,2])
    def test_bad_move_count_rejected(self):
        read=p.read_new
        def bad(name):
            r=copy.deepcopy(read(name))
            if name=='reorder-selection.json':r['selected']-=1
            return r
        with patch.object(p,'read_new',bad),self.assertRaises(AssertionError):p.reorder_delta()
    def test_bad_histogram_rejected(self):
        read=p.read_new
        def bad(name):
            r=copy.deepcopy(read(name))
            if name=='reorder2-selection.json':r['expected_local_delta']['2']+=1
            return r
        with patch.object(p,'read_new',bad),self.assertRaises(AssertionError):p.reorder_delta()
    def test_wrong_inherited_manifest_rejected(self):
        read=p.read_new
        def bad(name):
            r=copy.deepcopy(read(name))
            if name=='MANIFEST.json':r['files']['sink-selection.json']='0'*64
            return r
        with patch.object(p,'read_new',bad),self.assertRaises(AssertionError):p.source_contract()
if __name__=='__main__':unittest.main()
