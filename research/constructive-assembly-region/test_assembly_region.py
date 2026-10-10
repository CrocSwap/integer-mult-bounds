"""Regression and mutation tests for the original scoped arithmetic diagnostic."""
from fractions import Fraction as F
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

import assembly_region as ar


class RegionTests(unittest.TestCase):
    def setUp(self):
        self.params=ar.construct_for_kappa(F(23,100))

    def test_source_pin_and_all_47_labels(self):
        source=ar.source_contract()
        self.assertEqual(set(source['labels']),set(ar.direct_slacks(**self.params)['slacks']))

    def test_source_mutation_rejected(self):
        source=(ar.REPO_ROOT/ar.SOURCE_PATH).read_text()
        source=source.replace('h/8','h/7',1)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'mutant.py'; path.write_text(source)
            with self.assertRaisesRegex(ValueError,'source bytes'):
                ar.source_contract(path)

    def test_published_45_constraints_and_seven_margins(self):
        path=ar.CERTIFICATE_PATH
        self.assertTrue(path.exists(), 'Pinned repository certificate required')
        self.assertEqual(ar.published_regression(path)['matched_non_bridge_constraints'],45)

    def test_certificate_mutation_rejected(self):
        source=ar.CERTIFICATE_PATH.read_bytes()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'mutant.json'; path.write_bytes(source+b' ')
            with self.assertRaisesRegex(ValueError,'certificate bytes'):
                ar.published_regression(path)

    def test_nonpositive_kappa_precondition_rejected(self):
        for kappa in (0,-1):
            result=ar.verdict(ar.direct_slacks(**dict(self.params,kappa=kappa)),
                              include_production_cap=False)
            self.assertIn('positive_kappa',result['failed'])

    def test_cli_report_from_other_directory(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'report.json'
            run=subprocess.run([sys.executable,'-B',str(ar.HERE/'assembly_region.py'),
                                '--output',str(output)],cwd=d,text=True,
                               capture_output=True,check=True)
            summary=json.loads(run.stdout)
            report=json.loads(output.read_text())
            self.assertEqual(summary['diagnostic_rows'],7)
            self.assertTrue(summary['retained_cap_control_pass'])
            self.assertEqual(report['published_regression']['matched_non_bridge_constraints'],45)
            self.assertEqual(report['published_regression']['matched_margins'],7)
            self.assertTrue(all(row['diagnostic']['accepted'] for row in report['diagnostic_rows']))
            self.assertEqual(report['retained_entry_requirements'],['0 < h < 1/2','kappa > 0'])

    def test_whole_region_constructed_grid(self):
        count=0
        for denominator in range(4,61):
            for numerator in range(1,(denominator-1)//3+1):
                a=F(numerator,denominator)
                if a>=F(1,3): continue
                b=(a+F(1,3))/2
                for fraction in (F(1,3),F(9,10),F(999,1000)):
                    params=ar.construct(a,b,fraction*a/(1+a))
                    self.assertTrue(all(ar.proof_bounds(params).values()))
                    result=ar.direct_slacks(**params)
                    self.assertTrue(ar.verdict(result,include_production_cap=False)['accepted'])
                    count+=1
        self.assertEqual(count,1710)

    def test_strict_arithmetic_supremum_sequences(self):
        for power in (2,4,12,50,100):
            for production,bound in ((False,F(1,4)),(True,F(1,33))):
                params=ar.construct_for_kappa(bound-F(1,10**power),production=production)
                result=ar.direct_slacks(**params)
                self.assertTrue(ar.verdict(result,include_production_cap=production)['accepted'])
                self.assertTrue(all(ar.proof_bounds(params).values()))

    def test_supremum_endpoint_construction_rejected(self):
        for kappa,production in ((F(1,4),False),(F(1,33),True),(0,False),(-1,False)):
            with self.assertRaises(ValueError):
                ar.construct_for_kappa(kappa,production=production)

    def test_diagnostic_cap_stays_active_by_default(self):
        result=ar.direct_slacks(**self.params)
        self.assertEqual(ar.verdict(result)['failed'],[ar.CAP_NAME])
        self.assertTrue(ar.verdict(result,include_production_cap=False)['accepted'])

    def test_strict_cap_boundary_rejected(self):
        result=ar.direct_slacks(F(1,100),F(1,32),F(1,100),F(1,1000),F(1,1000))
        self.assertEqual(ar.verdict(result)['failed'],[ar.CAP_NAME])
        self.assertTrue(ar.verdict(result,include_production_cap=False)['accepted'])

    def test_target_at_margin_rejected(self):
        params=dict(self.params)
        params['kappa']=ar.direct_slacks(**params)['parameters']['G']
        result=ar.verdict(ar.direct_slacks(**params),include_production_cap=False)
        self.assertIn('g3_above_kappa',result['failed'])

    def test_gaussian_overclaim_rejected(self):
        params=dict(self.params,kappa=F(1,4))
        result=ar.verdict(ar.direct_slacks(**params),include_production_cap=False)
        self.assertFalse(result['accepted'])
        self.assertIn('g5_above_kappa',result['failed'])

    def test_zero_backoff_rejected(self):
        result=ar.verdict(ar.direct_slacks(**dict(self.params,h=0)),include_production_cap=False)
        self.assertIn('positive_backoff',result['failed'])
        self.assertIn('gamma_sublinear',result['failed'])

    def test_half_backoff_rejected(self):
        result=ar.verdict(ar.direct_slacks(**dict(self.params,h=F(1,2))),include_production_cap=False)
        self.assertIn('backoff_below_half',result['failed'])
        self.assertIn('q_positive',result['failed'])

    def test_zero_supplier_rejected(self):
        result=ar.verdict(ar.direct_slacks(**dict(self.params,a=0)),include_production_cap=False)
        self.assertIn('a_positive',result['failed'])

    def test_equal_suppliers_rejected(self):
        result=ar.verdict(ar.direct_slacks(**dict(self.params,b=self.params['a'])),include_production_cap=False)
        self.assertIn('a_below_b',result['failed'])

    def test_leaf_equality_rejected(self):
        params=dict(self.params,beta=1-self.params['a']/self.params['b'])
        result=ar.verdict(ar.direct_slacks(**params),include_production_cap=False)
        self.assertIn('phase_leaf_above_bit',result['failed'])

    def test_beta_endpoints_rejected(self):
        for value,label in ((0,'beta_positive'),(1,'beta_below_one')):
            result=ar.verdict(ar.direct_slacks(**dict(self.params,beta=value)),include_production_cap=False)
            self.assertIn(label,result['failed'])

    def test_nonpositive_bridge_gaps_rejected(self):
        for key,label in (('scalar_gap','literal_scalar_guard'),('row_gap','row_product_gap')):
            for value in (0,-1):
                result=ar.verdict(ar.direct_slacks(**dict(self.params,**{key:value})),include_production_cap=False)
                self.assertIn(label,result['failed'])

    def test_floats_and_bools_rejected(self):
        for value in (0.1,True,False,'1.0','NaN','1/0'):
            with self.assertRaises(ValueError):
                ar.rational(value)

    def test_input_region_not_claimed_necessary(self):
        # a=1/3 is excluded by our sufficient construction, but can meet the
        # relaxed displayed slacks at a positive h. Do not overclaim maximality.
        result=ar.direct_slacks(F(1,3),F(2,5),F(1,20),F(1,100),F(6,25))
        self.assertTrue(ar.verdict(result,include_production_cap=False)['accepted'])
        with self.assertRaises(ValueError):
            ar.construct(F(1,3),F(2,5),F(6,25))


if __name__=='__main__':
    unittest.main()
