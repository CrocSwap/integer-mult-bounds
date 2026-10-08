"""Focused exact controls; fresh full DAG/profile replay is a make target."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from copy import deepcopy
import importlib.util,json,sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/rad-fixed-reversed'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
w=load('test_rad_fixed_witness',HERE/'witness.py');p=load('test_rad_fixed_producer',HERE/'producer.py')
class RadFixedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=w.run()
    def test_frozen_certificate(self):self.assertEqual(w.js(self.result),json.loads((HERE/'certificate.json').read_text()))
    def test_exact_assembly(self):
        r=self.result;self.assertEqual(len(r['assembly']['constraints']),47);self.assertEqual(len(r['assembly']['margins']),7)
        self.assertTrue(all(x>0 for x in r['assembly']['constraints'].values()));self.assertEqual(r['finite_bridge']['rows']['degree'],2000)
        self.assertGreater(r['comparison']['ratio'],1)
    def test_complete_partition(self):
        b=self.result['bit']['counts'];self.assertEqual(len(b['child_multiplicities']),26);self.assertEqual(sum(b['parts'].values(),Counter()),Counter(b['child_multiplicities']))
        self.assertEqual(b['parts']['paid_correction'],{1:b['N']});self.assertEqual(sum(t*n for t,n in b['child_multiplicities'].items()),b['W']*b['m']-b['N']+b['L'])
        self.assertEqual(b['W'],178378409)
    def test_actual_axis_cardinalities(self):
        b=self.result['bit']['counts']
        for h,roles,links in [(23,36685,5749),(25,48479,7565)]:
            r=b['inputs'][h]['original'];self.assertEqual((r['R'],r['matched']),(roles,links));self.assertEqual(r['c']+r['q']-r['matched'],roles)
            self.assertEqual(b['copied_blocks'][h][h],b['original_profiles'][h]['blocks'][h]-h)
            self.assertEqual(b['copied_blocks'][h][1],b['original_profiles'][h]['blocks'][1]+h)
    def test_next_grid_excluded_by_lower(self):self.assertGreater(self.result['next_bit_grid']['lower'],1)
    def test_rank_preserving_unbatch_fails(self):
        b=deepcopy(self.result['bit']['counts']);rows=b['child_multiplicities'];n=rows.pop(17);rows[1]+=17*n
        self.assertEqual(sum(t*n for t,n in rows.items()),b['total_rank']);self.assertGreater(w.moment(b['m'],b['W'],rows,w.AB)['lower'],1)
    def test_source_corruption(self):
        read=w.read
        def corrupt(path):
            r=read(path)
            if path.name=='source-manifest.json':r['sha256']['research/rad-fixed-reversed/witness.py']='0'*64
            return r
        with patch.object(w,'read',side_effect=corrupt),self.assertRaises(AssertionError):w.verify_sources()
    def test_wrong_axis_roles_rejected(self):
        read=w.read
        def corrupt(path):
            r=read(path)
            if path.name=='input-23.json':r['original']['R']-=1
            return r
        with patch.object(w,'read',side_effect=corrupt),self.assertRaises(AssertionError):w.counts()
    def test_wrong_profile_rank_rejected(self):
        read=w.read
        def corrupt(path):
            r=read(path)
            if path.name=='profile-25.json':r['blocks'][1]-=25
            return r
        with patch.object(w,'read',side_effect=corrupt),self.assertRaises(AssertionError):w.counts()
    def test_float_and_old_E_rejected(self):
        f=self.result['finite_bridge']
        with self.assertRaises(AssertionError):w.base.balanced.assembly(f,float(w.AB),w.KAPPA,a_complex=w.AC)
        bad=deepcopy(f);bad['semantic']['E']=64*(f['complex']['W']+f['complex']['m']+1)**3
        with self.assertRaises(AssertionError):w.base.balanced.assembly(bad,w.AB,w.KAPPA,a_complex=w.AC)
    def test_builder_restores_global_state_on_failure(self):
        beforepath=list(sys.path);sentinel=object();missing=object();old=sys.modules.get('producer_search',missing);sys.modules['producer_search']=sentinel
        try:
            with self.assertRaises(RuntimeError):
                with p.builder_context():
                    import partial_swap.graph as graph
                    oldpoints=graph.aligned_points;graph.aligned_points=lambda *_:[]
                    raise RuntimeError('controlled builder failure')
            self.assertIs(graph.aligned_points,oldpoints);self.assertEqual(sys.path,beforepath);self.assertIs(sys.modules['producer_search'],sentinel)
        finally:
            if old is missing:sys.modules.pop('producer_search',None)
            else:sys.modules['producer_search']=old
    def test_all_negative_controls(self):self.assertEqual(set(self.result['negative_controls']),{'old_guard','old_exposures','original_prefix','next_kappa_grid'})
if __name__=='__main__':unittest.main()
