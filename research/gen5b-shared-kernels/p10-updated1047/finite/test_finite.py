"""Positive and adversarial checks for the new finite certificate binding."""
import unittest,copy,gzip,json,struct,hashlib
import context as c
import bind_finite as b

class FiniteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c.verify();cls.ps,cls.raw,cls.hashes,cls.data=b.load_bundle();cls.inv=c.inventory()
    def rejects(self,fn):
        with self.assertRaises((AssertionError,KeyError,ValueError)):fn()
    def test_valid_dependency_bundle(self):b.bindings(self.hashes,self.data)
    def test_word_change_rejected(self):
        h=self.hashes.copy();h['word']='0'*64;self.rejects(lambda:b.bindings(h,self.data))
    def test_stale_admission_checker_rejected(self):
        h=self.hashes.copy();h['admission/check_transport.py']='0'*64;self.rejects(lambda:b.bindings(h,self.data))
    def test_stale_target_receipt_rejected(self):
        h=self.hashes.copy();h['targets']='0'*64;self.rejects(lambda:b.bindings(h,self.data))
    def test_stale_context_rejected(self):
        h=self.hashes.copy();h['finite/context.py']='0'*64;self.rejects(lambda:b.bindings(h,self.data))
    def test_stale_price_rejected(self):
        h=self.hashes.copy();h['price']='0'*64;self.rejects(lambda:b.bindings(h,self.data))
    def test_source_pin_change_rejected(self):
        d=copy.deepcopy(self.data);d['admission_manifest']['files'][0]['sha256']='0'*64;self.rejects(lambda:b.bindings(self.hashes,d))
    def test_stale_matching_auditor_rejected(self):
        h=self.hashes.copy();h['matching/audit_matching.py']='0'*64;self.rejects(lambda:b.bindings(h,self.data))
    def test_wrong_audited_word_rejected(self):
        d=copy.deepcopy(self.data);d['matching_audit']['witnesses']['unrestricted']['candidate_sha256']='0'*64;self.rejects(lambda:b.bindings(self.hashes,d))
    def test_second_engine_price_change_rejected(self):
        d=copy.deepcopy(self.data);d['second_moment']['cases'][1]['sha256']='0'*64;self.rejects(lambda:b.bindings(self.hashes,d))
    def test_valid_chart(self):b.replay_chart(self.data['seam_charts']['factor_programs'][0])
    def test_chart_factor_change_rejected(self):
        p=copy.deepcopy(self.data['seam_charts']['factor_programs'][0]);p['factors'][0][3]='777';self.rejects(lambda:b.replay_chart(p))
    def test_chart_inverse_change_rejected(self):
        p=copy.deepcopy(self.data['seam_charts']['factor_programs'][0]);p['inverse'][0][0]='777';self.rejects(lambda:b.replay_chart(p))
    def test_chart_determinant_change_rejected(self):
        p=copy.deepcopy(self.data['seam_charts']['factor_programs'][0]);p['determinant']='777';self.rejects(lambda:b.replay_chart(p))
    def test_wrong_source_dimension_rejected(self):
        p=self.data['seam_charts']['factor_programs'][0];frames=self.inv[1];D=copy.deepcopy(frames[p['donor_end_frame']]);D['dim']+=1
        self.rejects(lambda:b.geometry(p,D,frames[p['recipient_gauge_frame']]))
    def test_wrong_projector_membership_rejected(self):
        p=copy.deepcopy(self.data['seam_charts']['factor_programs'][0]);frames=self.inv[1];p['basis_columns'][0][0]=777
        self.rejects(lambda:b.geometry(p,frames[p['donor_end_frame']],frames[p['recipient_gauge_frame']]))
    def test_valid_bank(self):b.verify_bank(self.raw['bank_table'],self.inv[6],self.data['banks'])
    def test_duplicate_role_replica_rejected(self):
        raw=bytearray(gzip.decompress(self.raw['bank_table']));raw[20:28]=raw[:8]
        r=copy.deepcopy(self.data['banks']);r['one_stage_table_uncompressed_sha256']=hashlib.sha256(raw).hexdigest()
        self.rejects(lambda:b.verify_bank(gzip.compress(raw),self.inv[6],r))
    def test_wrong_bank_offset_rejected(self):
        raw=bytearray(gzip.decompress(self.raw['bank_table']));struct.pack_into('>I',raw,12,1)
        r=copy.deepcopy(self.data['banks']);r['one_stage_table_uncompressed_sha256']=hashlib.sha256(raw).hexdigest()
        self.rejects(lambda:b.verify_bank(gzip.compress(raw),self.inv[6],r))
    def test_finite_formula(self):
        old=b.bill(658290,250195,336253,338173);new=b.bill(658290,250045,336253,338173)
        self.assertEqual(old['coefficient'],25485577221183401);self.assertEqual(new['coefficient'],25476360501102401)
        self.assertEqual(new['coefficient']-old['coefficient'],-9216720081000)
        self.assertEqual(new['coefficient_terms']['unit_expanded_additions'],101797500)
        self.assertEqual(new['coefficient_terms']['bank_selectors'],295929593400)
    def test_endpoint_bound_is_separate(self):
        old=b.bill(658290,250045,336253,338173);smaller=b.bill(658290,250045,336253,338173,chart_max=136)
        self.assertEqual(old['coefficient_terms']['generic_wrappers'],smaller['coefficient_terms']['generic_wrappers'])
        self.assertEqual(old['coefficient_terms']['matrix_preparation'],smaller['coefficient_terms']['matrix_preparation'])
        self.assertGreater(old['coefficient_terms']['bank_selectors'],smaller['coefficient_terms']['bank_selectors'])
if __name__=='__main__':unittest.main(verbosity=2)
