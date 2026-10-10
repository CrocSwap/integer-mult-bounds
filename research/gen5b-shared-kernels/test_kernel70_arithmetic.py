"""Focused kernel70 exact-pricing, chart, composition and finite-bound checks."""
import copy
from fractions import Fraction as F
import unittest

import check_kernel70
import check_kernel70_norm
import check_pr300_kernel70_composition
import check_kernel70_bank_assignment
import check_complete_suffix
import kernel70_pricing as price
import kernel70_charts as charts
import kernel70_finite_bill as bill


class SmallChartTests(unittest.TestCase):
    def test_both_line_orders(self):
        for line in ((6,7),(16,17),(2,3)):
            for rank in (1,23):
                z=charts.line_chart(*line,rank)
                self.assertEqual(abs(z['determinant']),2)
                self.assertLessEqual(z['max_numerator'],2)
                self.assertLessEqual(z['max_denominator'],2)
    def test_bad_line_rejected(self):
        with self.assertRaises(AssertionError):charts.line_chart(2,2,1)
    def test_nonorthogonal_partition_rejected(self):
        cols=[[int(i==j)for i in range(24)]for j in range(24)]
        with self.assertRaises(AssertionError):charts.checked_chart(cols,1)
    def test_bad_histogram_types_rejected(self):
        for d in ({1:True},{True:1},{'x':1},{1:1,'1':2}):
            with self.assertRaises(ValueError):price.integer_map(d)
    def test_odd_pivot_packing_rejected(self):
        with self.assertRaises(ValueError):price.patterns(69,{})


class IntegratedBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge=check_kernel70.run()
        cls.composition=check_pr300_kernel70_composition.run()
        cls.price=price.run(cls.bridge,composition=cls.composition)
        cls.charts=charts.run(cls.bridge)
        cls.norm=check_kernel70_norm.run()
        cls.banks=check_kernel70_bank_assignment.run()
        cls.suffix=check_complete_suffix.run()
    def run_bill(self,**changes):
        args=dict(chart=self.charts,norm=self.norm,math=self.price,bridge=self.bridge,
                  banks=self.banks,suffix=self.suffix,composition=self.composition)
        args.update(changes)
        return bill.run(**args)
    def test_full_pricing_and_bill(self):
        r=self.run_bill()
        self.assertEqual(self.price['kappa'],F(749940157923873,10**18))
        self.assertEqual(self.price['literal_stock'],1229560)
        self.assertEqual(self.price['calls'],483425)
        self.assertEqual(r['payload_bits'],104)
        self.assertEqual(r['payload_strict_gap'],7354671393307281152206899447616)
        self.assertLess(r['conservative_payload_upper'],2**104)
        self.assertEqual(r['displayed_finite_coefficient'],90466979917115701)
        self.assertEqual(r['pivot_residual_demands'],70)
        self.assertFalse(r['all_size_theorem_verified'])
    def test_measured_histogram_mismatch_rejected(self):
        z=copy.deepcopy(self.bridge);z['local_paid_histogram_delta'][1]+=1
        with self.assertRaises(AssertionError):price.measured_kernel_delta(z)
    def test_missing_path_rejected(self):
        z=copy.deepcopy(self.bridge);z['paths'].pop()
        with self.assertRaises(AssertionError):price.measured_kernel_delta(z)
    def test_corrupt_paid_entrance_rejected(self):
        z=copy.deepcopy(self.bridge);z['paths'][0]['new_paid_entrance_dimensions']=[1,3]
        with self.assertRaises(AssertionError):price.measured_kernel_delta(z)
    def test_wrong_shear_count_rejected(self):
        z=copy.deepcopy(self.bridge);z['setup_adds']=473
        with self.assertRaises(AssertionError):price.measured_kernel_delta(z)
    def test_missing_chart_use_rejected(self):
        z=copy.deepcopy(self.charts);z['role_chart_uses'].pop()
        with self.assertRaises(AssertionError):self.run_bill(chart=z)
    def test_wrong_chart_rank_rejected(self):
        z=copy.deepcopy(self.charts);p=z['role_chart_uses'][0]['program_id']
        z['factor_programs'][p]['residual_rank']+=1
        with self.assertRaises(AssertionError):self.run_bill(chart=z)
    def test_missing_sink_redirects_rejected(self):
        z=copy.deepcopy(self.norm);z['actual_sink_redirects']=0
        with self.assertRaises(AssertionError):self.run_bill(norm=z)
    def test_missing_sink_graph_edges_rejected(self):
        z=copy.deepcopy(self.norm);z['target_majorant_edges']-=1
        with self.assertRaises(AssertionError):self.run_bill(norm=z)
    def test_payload_equality_at_cap_rejected(self):
        z=copy.deepcopy(self.norm);z['payload_bound']=2**104
        with self.assertRaises(AssertionError):self.run_bill(norm=z)
    def test_wrong_bank_count_rejected(self):
        z=copy.deepcopy(self.banks);z['banks_per_stage']-=1
        with self.assertRaises(AssertionError):self.run_bill(banks=z)
    def test_final12_multiset_required(self):
        z=copy.deepcopy(self.suffix);z['unchanged_scalar_multiset']=False
        with self.assertRaises(AssertionError):self.run_bill(suffix=z)
    def test_pr300_scalar_invariance_required(self):
        z=copy.deepcopy(self.composition);z['scalar_majorants_unchanged_by_descent2']=False
        with self.assertRaises(AssertionError):self.run_bill(composition=z)
    def test_pr300_disjointness_required(self):
        z=copy.deepcopy(self.composition);z['descent2_overlap_kernel70']=[1]
        with self.assertRaises(AssertionError):self.run_bill(composition=z)
    def test_pr300_histogram_binding_required(self):
        z=copy.deepcopy(self.composition);z['combined_local_histogram_delta_over299'][1]+=1
        with self.assertRaises(AssertionError):self.run_bill(composition=z)
    def test_pr300_wrong_source_pin_rejected(self):
        z=copy.deepcopy(self.composition);z['input_sha256']['pr300/descent2-selection.json']='0'*64
        with self.assertRaises(AssertionError):self.run_bill(composition=z)


if __name__=='__main__':unittest.main(verbosity=2)
