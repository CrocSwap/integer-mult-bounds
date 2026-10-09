"""Mathematical controls bypass byte guards and exercise exact paid formulas."""
import copy,json,unittest
import arithmetic as A
class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs=A.load_inputs();cls.logical,cls.physical,cls.scaled,cls.native,cls.bank,cls.oldbit,cls.zeros=cls.inputs
        cls.cp=A.paid_complex(cls.physical);cls.bp=A.paid_bank(cls.scaled,cls.bank,cls.oldbit)
        cls.bridge=A.A.reconstruct_bridge(cls.logical,cls.physical)
    def test_regenerated_certificate(self):self.assertEqual(A.regenerate(),json.loads((A.HERE/'certificate.json').read_bytes()))
    def test_supplier_successors_full_fallback(self):
        for p,s,kwargs in [(self.cp,A.COMPLEX,{}),(self.bp,A.COARSE,dict(bad_fraction=A.M.BAD,fallback_children_per_edge=32*72**2))]:
            b=A.M.supplier_bounds(p['width'],p['stock'],p['children'],s+A.STEP,**kwargs)
            self.assertGreaterEqual(b['total_lower'],1)
            with self.assertRaisesRegex(ValueError,'does not contract'):A.M.require_contraction(b)
    def test_previous_atom_grid(self):
        with self.assertRaisesRegex(ValueError,'adapter and row tolls'):A.strict_bit(self.bp,A.COARSE,A.ATOM-A.STEP)
    def test_next_headline_grid(self):
        effective=(1-A.ATOM)*A.COARSE+A.ATOM*A.M.OLD
        with self.assertRaisesRegex(ValueError,'compact_phase_layer_above_kappa'):A.A.balanced_assembly(self.bridge,effective,A.COMPLEX,A.KAPPA+A.STEP,eta=A.ETA,beta=A.BETA,phase_gap=A.PHASE_GAP)
    def test_unpaid_bank_stock(self):
        row=copy.deepcopy(self.scaled);row['stock']-=1100
        with self.assertRaisesRegex(ValueError,'unpaid bank stock'):A.paid_bank(row,self.bank,self.oldbit)
    def test_children_not_scaled(self):
        row=copy.deepcopy(self.scaled);row['children']={k:n//3 for k,n in row['children'].items()}
        with self.assertRaisesRegex(ValueError,'unscaled children'):A.paid_bank(row,self.bank,self.oldbit)
    def test_omitted_fallback(self):
        with self.assertRaisesRegex(ValueError,'omitted full bad-class fallback'):A.strict_bit(self.bp,A.COARSE,A.ATOM,bad_fraction=A.Q(0),fallback_children_per_edge=0)
        ideal=A.M.supplier_bounds(72,self.bp['stock'],self.bp['children'],A.COARSE+A.STEP)
        full=A.M.supplier_bounds(72,self.bp['stock'],self.bp['children'],A.COARSE+A.STEP,bad_fraction=A.M.BAD,fallback_children_per_edge=32*72**2)
        self.assertLess(ideal['total_upper'],1);self.assertGreaterEqual(full['total_lower'],1)
    def test_deleted_paid_child(self):
        row=copy.deepcopy(self.physical);row['local_histogram']['1']-=1
        with self.assertRaisesRegex(ValueError,'complete complex paid children'):A.paid_complex(row)
    def test_scalar_bill_guard(self):
        bridge=dict(self.bridge,literal_charge=self.bridge['E']+1);effective=(1-A.ATOM)*A.COARSE+A.ATOM*A.M.OLD
        with self.assertRaisesRegex(ValueError,'literal_scalar_guard'):A.A.balanced_assembly(bridge,effective,A.COMPLEX,A.KAPPA,eta=A.ETA,beta=A.BETA,phase_gap=A.PHASE_GAP)
    def test_zero_events_create_no_paid_child(self):
        row=copy.deepcopy(self.physical);row['target_data_histogram']['0']+=1
        self.assertEqual(A.paid_complex(row),self.cp)
        self.assertEqual(self.zeros,{'native':6270,'independent_literal_events':6325})
    def test_bank_common_chart_controls(self):
        import check_banks as B
        for width in (4,24):
            n=72//width
            self.assertEqual(B.validate(width,list(range(n)),0,[True]*n),144)
            with self.assertRaisesRegex(ValueError,'endpoint column'):B.validate(width,list(range(n)),0,[False]*(n-1)+[True])
if __name__=='__main__':unittest.main()
