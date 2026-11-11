"""Original regression tests for the PR275 arithmetic replay."""
from fractions import Fraction as F
import unittest
import reproduce_pr275 as replay

class PR275ArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h,cls.profile=replay.final_profile()
        cls.inventory=replay.inventory()

    def test_base_role_inventory(self):
        b=self.profile['base']
        self.assertEqual((b['reused_pairs'],b['physical_helpers_before_sinks']), (1728,15432))
        self.assertEqual((self.inventory['physical_R'],self.inventory['sink_count']), (15425,7))

    def test_complete_signed_delta_census(self):
        d=self.profile['stages']['descent2']
        self.assertEqual(d['delta_calls'],65)
        self.assertEqual(d['delta_rank_mass'],0)
        self.assertTrue(any(n<0 for n in d['delta'].values()))
        self.assertEqual(self.profile['final_local_calls'],93604)
        self.assertEqual(self.profile['final_local_rank_mass'],404422)

    def test_shared_donors_not_counted_per_entry(self):
        k=self.profile['kernel']
        self.assertEqual((k['entries'],k['distinct_donors'],k['shared_donors']),(1720,1438,918))
        self.assertEqual(k['histogram_delta'][1],3294)
        self.assertEqual(sum(r*n for r,n in k['histogram_delta'].items()),-2192)

    def test_profile_and_normalization(self):
        self.assertEqual((sum(self.h.values()),replay.mass(self.h)),(482100,2455070))
        stock=self.inventory['literal_stock']
        self.assertEqual(stock,1229735)
        self.assertEqual(120*F(stock,60)-replay.mass(self.h),4400)
        self.assertEqual(self.inventory['banks_per_stage'],161467)

    def test_known_adjacent_bit_root_endpoints(self):
        W=F(self.inventory['literal_stock'],60)
        low=F(751640232848887,10**18);high=low+F(1,10**18)
        self.assertLess(replay.moment(self.h,120,W,low)[1],1)
        self.assertGreater(replay.moment(self.h,120,W,high)[0],1)

    def test_all47_and_kappa_grid_control(self):
        a=replay.assembly(F(751640232848887,10**18))
        self.assertEqual(a['kappa'],F('46942230864663/62500000000000000'))
        self.assertEqual(len(a['strict_constraints']),47)
        self.assertGreater(min(a['strict_constraints'].values()),0)
        self.assertEqual(a['adjacent_grid_rejected'],['g3_above_kappa'])

    def test_bad_numeric_inputs_rejected(self):
        for bad in (True,0.001,'0.001'):
            with self.assertRaises(ValueError):replay.ae.rational(bad)
        with self.assertRaises(ValueError):replay.ex.moment_interval(120,1,{120:1},F(1,1000))

    def test_exact_changed_line_chart(self):
        import chart_construction as charts
        for rank in (1,23):
            c=charts.line_chart(2,3,rank)
            self.assertEqual(c['residual_rank'],rank)
            self.assertNotEqual(c['determinant'],0)
            self.assertLessEqual(c['count'],576)

    def test_degenerate_changed_chart_rejected(self):
        import chart_construction as charts
        columns=[[int(i==j) for i in range(24)]for j in range(24)]
        columns[-1]=columns[0][:]
        with self.assertRaises(AssertionError):charts.checked_chart(columns,1)

    def test_bound_finite_formula_reproduces_baseline(self):
        import integrate_bounded_candidate as binding
        p=replay.read('expected/kernel-pins.json')
        r=binding.invoice(p['literal_stock'],p['priced_five_stage_calls'],0)
        self.assertEqual(r['displayed_finite_coefficient'],90322316339049601)
        self.assertEqual(r['selector_calls_bound'],905876840400)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    unittest.main()
