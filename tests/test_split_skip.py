"""Finite identity and adversarial controls for split-pair/paid-clone witnesses."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/split-skip'
sys.path.insert(0,str(HERE))
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
w=load('split_skip_witness',HERE/'witness.py')
c=load('split_skip_cloned',HERE/'cloned_graph.py')
s=load('split_skip_uncloned',HERE/'split_graph.py')
ia=load('split_skip_independent',HERE/'independent_arithmetic.py')

class SplitSkipTests(unittest.TestCase):
    def test_general_singleton_pair_scalar_identity(self):
        for h in (7,8,10,11):
            for groups in ([0,0,0],[1,2,3],[3,1,2],[2,3,1]):
                g=s.graph(h,{'groups':groups})
                self.assertTrue(g.verify()['all_partial_outputs_exact'])
                g.support_in.cache_clear()

    def test_invalid_permutations_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Invalid total permutation'):
            s.graph(23,{'totals':{'0':[0,0]}})
        with self.assertRaisesRegex(AssertionError,'Invalid strip permutation'):
            s.graph(23,{'strips':{'0':[0,0]}})
        with self.assertRaisesRegex(AssertionError,'Invalid point permutation'):
            s.graph(23,{'points':{'0':[0,0]}})

    def test_partial_clone_chain_rejected(self):
        doc=w.read(HERE/'clone-jobs-23.json');job=next(x for x in doc['rounds'][0]['jobs'] if len(x['chain'])>1)
        job['chain'].pop()
        with self.assertRaisesRegex(ValueError,'whole continuation chain'):c.graph(23,doc)

    def test_duplicate_clone_provider_rejected(self):
        doc=w.read(HERE/'clone-jobs-23.json');job=doc['rounds'][0]['jobs'][0]
        job['providers'][1]=job['providers'][0]
        with self.assertRaisesRegex(ValueError,'Providers must be distinct'):c.graph(23,doc)

    def test_overlapping_clone_partition_rejected(self):
        doc=w.read(HERE/'clone-jobs-23.json');job=doc['rounds'][0]['jobs'][0]
        job['source_children'][1]=job['source_children'][0]
        with self.assertRaises(ValueError):c.graph(23,doc)

    def test_stale_graph_pin_rejected(self):
        doc=w.read(HERE/'clone-jobs-23.json');doc['rounds'][0]['source_graph_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'source graph differs'):c.graph(23,doc)

    def test_rank_mass_and_paid_endpoint(self):
        p=w.profile();self.assertEqual(p['W'],156805076)
        self.assertEqual(p['total_rank'],90161071800)
        self.assertEqual(p['deficit'],1846900)
        self.assertEqual(p['parts']['paid_endpoint_copy'],{1:4073300})
        rows=p['child_multiplicities'].copy();rows[1]-=4073300
        self.assertNotEqual(sum(t*n for t,n in rows.items()),p['total_rank'])

    def test_corrupted_profile_rejected(self):
        old=w.read
        def bad(path):
            x=old(path)
            if path.name=='profiles-23.json':x['blocks'][1]+=1
            return x
        with patch.object(w,'read',side_effect=bad):
            with self.assertRaisesRegex(ValueError,'Fixed mass'):w.profile()

    def test_strict_grid_and_final_margins(self):
        p=w.profile();a,k=w.parameters();m=w.moment(p['m'],p['W'],p['child_multiplicities'],a)
        self.assertLess(m['upper'],1)
        self.assertGreater(w.moment(p['m'],p['W'],p['child_multiplicities'],a+Q(1,10**14))['lower'],1)
        f,_=w.bridge(p);z=w.base.assembly(f,a,k,a_complex=w.base.AC)
        self.assertEqual(len(z['constraints']),47);self.assertEqual(len(z['margins']),7)
        self.assertTrue(all(x>0 for x in z['constraints'].values()))
        with self.assertRaises(AssertionError):w.base.assembly(f,a,z['minimum_margin'],a_complex=w.base.AC)

    def test_independent_exact_arithmetic(self):
        x=ia.run();self.assertEqual(x['W'],156805076)
        self.assertEqual(Q(x['kappa']),Q(4598878089,10**14))
        with self.assertRaises(ValueError):ia.exponential(Q(11))

if __name__=='__main__':unittest.main()
