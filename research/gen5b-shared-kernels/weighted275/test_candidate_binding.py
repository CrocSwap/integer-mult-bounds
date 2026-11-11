"""Independent binding mutations for the bounded166 candidate.

Mutations affect temporary copies only; the pinned source, witness and completed
70 checkpoint are untouched. Prepared with substantial OpenAI assistance.
Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json,tempfile,unittest
import reproduce_pr275 as base
from bank_receipt_binding import bind_banks
from check_candidate_charts import run as check_charts

from source_data import ROOT
CAND=ROOT/'candidate-combined166-reclosed.json'

class CandidateBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import hashlib,check_bridge,check_shared_banks
        from price_candidate import price
        cls.temp=tempfile.TemporaryDirectory();cls.folder=Path(cls.temp.name)
        bank=check_shared_banks.run(CAND,cls.folder)
        (cls.folder/'receipt.json').write_text(json.dumps(bank))
        r=price({1:210,2:306,3:-306,4:70,5:-70},{24:-166,23:166},{23:166},label='test166')
        r['candidate_sha256']=hashlib.sha256(CAND.read_bytes()).hexdigest()
        cls.result=r;cls.table=json.loads((cls.folder/'bank-address-table.json').read_text())
        check_bridge.configure('166');cls.bridge=check_bridge.run()
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def run_bad_table(self,table):
        with tempfile.TemporaryDirectory()as directory:
            path=Path(directory)/'table.json';path.write_text(json.dumps(table))
            with self.assertRaises(AssertionError):
                bind_banks(self.result,self.folder/'receipt.json',path,'PASS_PR275_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT')

    def test_wrong_literal_stock_rejected(self):
        result=deepcopy(self.result);result['literal_stock']+=1
        with self.assertRaises(AssertionError):
            bind_banks(result,self.folder/'receipt.json',self.folder/'bank-address-table.json','PASS_PR275_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT')

    def test_wrong_replica_multiplier_rejected(self):
        table=deepcopy(self.table);table['replicas']=59;self.run_bad_table(table)

    def test_duplicate_helper_role_rejected(self):
        table=deepcopy(self.table);roles=table['families']['23'];roles[1]=roles[0];self.run_bad_table(table)

    def test_missing_bank_width_rejected(self):
        table=deepcopy(self.table);table['patterns'][0]['widths'].pop();self.run_bad_table(table)

    def test_missing_path_rejected(self):
        bridge=deepcopy(self.bridge);bridge['selected_paths'].pop()
        with self.assertRaises(AssertionError):check_charts(CAND,bridge,1229320)

    def test_wrong_first_frame_rejected(self):
        bridge=deepcopy(self.bridge);bridge['selected_paths'][0]['first_frame']=0
        with self.assertRaises(AssertionError):check_charts(CAND,bridge,1229320)

    def test_wrong_physical_stream_rejected(self):
        bridge=deepcopy(self.bridge);bridge['selected_paths'][0]['stream']+=1
        with self.assertRaises(AssertionError):check_charts(CAND,bridge,1229320)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    unittest.main()
