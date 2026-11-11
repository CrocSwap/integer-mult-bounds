"""Negative tests for the fixed154 and156 PR305 arithmetic bindings.

Mutations affect temporary files only. The pinned sources and candidate
witnesses are unchanged. No extra candidate search is performed.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,tempfile,unittest
import reproduce_pr305 as base
from bank_receipt_binding import bind_banks
from check_candidate_charts import run as check_charts
from price_witness import witness_delta
from source_data import validate
from finite_bill import invoice

ROOT=Path(__file__).resolve().parent

class CandidateBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.folder=Path(cls.temp.name)
        import witness,check_shared_banks,check_bridge
        from price_candidate import price
        cls.cand=witness.write_case('156');witness.write_case('154')
        cls.result=price({1:197,2:283,3:-283,4:70,5:-70},{24:-156,23:156},{23:156},label='test156')
        cls.result['candidate_sha256']=hashlib.sha256(cls.cand.read_bytes()).hexdigest()
        bank=check_shared_banks.run(cls.cand,cls.folder)
        cls.receipt=cls.folder/'receipt.json';cls.receipt.write_text(json.dumps(bank));cls.tablepath=cls.folder/'bank-address-table.json'
        cls.table=json.loads(cls.tablepath.read_text());check_bridge.configure('156');cls.bridge=check_bridge.run()
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def bad_table(self,table):
        p=self.folder/'table.json';p.write_text(json.dumps(table))
        with self.assertRaises(AssertionError):bind_banks(self.result,self.receipt,p,'PASS_PR305_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT')
    def test_exact_witness_costs(self):
        expected=[('candidate154.json',{1:194,2:278,3:-278,4:70,5:-70},154,194,2541),('candidate_reclosed.json',{1:197,2:283,3:-283,4:70,5:-70},156,197,2545)]
        for name,h,p,d,s in expected:
            actual,c=witness_delta(self.cand.parent/name);self.assertEqual(actual,h);self.assertEqual((c['pivots'],c['distinct_donors'],c['setup_pairs']),(p,d,s))
    def test_wrong_literal_stock_rejected(self):
        r=deepcopy(self.result);r['literal_stock']+=1
        with self.assertRaises(AssertionError):bind_banks(r,self.receipt,self.tablepath,'PASS_PR305_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT')
    def test_wrong_replica_multiplier_rejected(self):
        t=deepcopy(self.table);t['replicas']=59;self.bad_table(t)
    def test_wrong_stage_multiplier_rejected(self):
        t=deepcopy(self.table);t['stages']=4;self.bad_table(t)
    def test_duplicate_helper_role_rejected(self):
        t=deepcopy(self.table);t['families']['23'][1]=t['families']['23'][0];self.bad_table(t)
    def test_missing_bank_width_rejected(self):
        t=deepcopy(self.table);t['patterns'][0]['widths'].pop();self.bad_table(t)
    def test_moved_block_offset_rejected(self):
        t=deepcopy(self.table);t['segments']['23'][0]['blocks'][0][1]+=1;self.bad_table(t)
    def test_missing_path_rejected(self):
        b=deepcopy(self.bridge);b['selected_paths'].pop()
        with self.assertRaises(AssertionError):check_charts(self.cand,b,1229275)
    def test_wrong_first_frame_rejected(self):
        b=deepcopy(self.bridge);b['selected_paths'][0]['first_frame']=0
        with self.assertRaises(AssertionError):check_charts(self.cand,b,1229275)
    def test_wrong_stream_rejected(self):
        b=deepcopy(self.bridge);b['selected_paths'][0]['stream']+=1
        with self.assertRaises(AssertionError):check_charts(self.cand,b,1229275)
    def test_occupied_new_pivot_rejected(self):
        c=json.loads(self.cand.read_text());c['entries'][0]['pivot']=12667;p=self.folder/'bad-candidate.json';p.write_text(json.dumps(c))
        with self.assertRaises(AssertionError):witness_delta(p)
    def test_wrong_source_head_rejected(self):
        c=json.loads(self.cand.read_text());c['source_head']='0'*40;p=self.folder/'bad-candidate.json';p.write_text(json.dumps(c))
        with self.assertRaises(AssertionError):witness_delta(p)
    def test_corrupt_source_rejected(self):
        raw=(base.SOURCE/'kernel-selection.json').read_bytes()
        with self.assertRaises(AssertionError):validate('kernel-selection.json',raw[:-1]+b'x')
    def test_actual_pr305_invoice(self):
        b=invoice(1229665,482030,0);c=invoice(1229275,483015,5090)
        self.assertEqual(b['displayed_finite_coefficient'],90312891518490001)
        self.assertEqual(c['displayed_finite_coefficient'],90417469526202901)
        self.assertEqual(c['selector_calls_bound'],905817884400)
        self.assertEqual(c['route_families'],11788800)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    unittest.main()
