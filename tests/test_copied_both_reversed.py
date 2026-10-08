"""Exact failure controls for the both-fixed composition."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research/copied-both-reversed'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
w=load('test_both_reversed_witness',HERE/'witness.py')
class BothReversedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=w.run()
    def test_frozen_exact_certificate(self):
        self.assertEqual(w.js(self.result),json.loads((HERE/'certificate.json').read_text()))
    def test_all_assembly_conditions(self):
        a=self.result['assembly'];self.assertEqual(len(a['constraints']),47);self.assertEqual(len(a['margins']),7)
        self.assertTrue(all(v>0 for v in a['constraints'].values()));self.assertTrue(all(v>w.KAPPA for v in a['margins'].values()))
        self.assertEqual(self.result['finite_bridge']['rows']['degree'],2000)
    def test_other_physical_classes_unchanged(self):
        c=self.result['bit']['counts'];old=w.prior.counts()
        for key,value in c['parts'].items():
            if key!='internal_23':self.assertEqual(value,old['parts'][key])
        self.assertEqual(dict(sum(c['parts'].values(),Counter())),c['child_multiplicities'])
        self.assertEqual(c['parts']['paid_correction'],{1:c['N']})
    def test_only23_full_cleanup_calls_replaced(self):
        c=self.result['bit']['counts']['fixed_first'];before=c['profile']['blocks'];after=c['copied_blocks']
        self.assertEqual({i:b-a for i,(a,b) in enumerate(zip(before,after)) if a!=b},{1:23,23:-23})
        self.assertEqual(sum(i*n for i,n in enumerate(after)),892354)
    def test_conservative_data_profile_loses_candidate(self):
        c=deepcopy(self.result['bit']['counts']);rows=c['child_multiplicities'];n=2*c['N'];rows[17]-=n;rows[1]+=17*n
        self.assertEqual(sum(t*n for t,n in rows.items()),c['total_rank'])
        self.assertGreater(w.moment(c['m'],c['W'],rows,w.AB)['lower'],1)
    def test_corrupted_profile_rejected(self):
        original=w.read
        def corrupt(path):
            d=original(path)
            if path.name=='profile-23.json':d['blocks'][23]-=1
            return d
        with patch.object(w,'read',side_effect=corrupt),self.assertRaises(AssertionError):w.counts()
    def test_corrupted_source_rejected(self):
        original=w.read
        def corrupt(path):
            d=original(path)
            if path.name=='producer-source.json':d['sha256']['research/copied-both-reversed/witness.py']='0'*64
            return d
        with patch.object(w,'read',side_effect=corrupt),self.assertRaises(AssertionError):w.verify_sources()
    def test_next_bit_grid_excluded(self):
        self.assertLess(self.result['bit']['upper'],1);self.assertGreater(self.result['next_bit_grid']['lower'],1)
    def test_unlucky_prime_is_not_rational_zero(self):
        a=load('test_both_reversed_unlucky',HERE/'review/unlucky_prime_check.py');r=a.run();x=Q(r['nonzero_rational_row26'])
        self.assertNotEqual(x,0);self.assertEqual(x.numerator%r['failed_modular_prime'],0)
        self.assertNotEqual(x.denominator%r['failed_modular_prime'],0);self.assertEqual(len(r['pivot_values']),47)
    def test_independent_local_transfer(self):
        a=load('test_both_reversed_local',HERE/'review/local_transfer.py');r=a.run()
        self.assertEqual(sum(d['triple_count'] for d in r['dimensions']),4071)
        self.assertEqual(sum(len(d['centers']) for d in r['dimensions']),48)
    def test_independent_crt_controls(self):
        a=load('test_both_reversed_crt',HERE/'review/fixed23_copied_crt_audit.py');r=a.run()
        self.assertGreater(r['prime_product'],r['all_minor_integer_bound']);self.assertEqual(len(r['negative_controls']),3)
if __name__=='__main__':unittest.main()
