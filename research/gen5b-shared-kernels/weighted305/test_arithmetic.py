"""Our exact arithmetic and input-contract regression tests for pinned PR305."""
from fractions import Fraction as F
from collections import Counter
import unittest
import reproduce_pr305 as replay

class PR305ArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h,cls.profile=replay.final_profile();cls.inv=replay.inventory()
    def test_source_contract(self):self.assertEqual(replay.verify_sources()['pinned_head'],'a17c42903bbe8d9d26c4bc712d7216a7176237e9')
    def test_base_role_inventory(self):
        b=self.profile['base'];self.assertEqual((b['reused_pairs'],b['physical_helpers_before_sinks']),(1728,15432))
        self.assertEqual((self.inv['physical_R'],self.inv['sink_count']),(15424,8))
    def test_complete_signed_delta_census(self):
        d=self.profile['stages']['descent2'];self.assertEqual((d['delta_calls'],d['delta_rank_mass']),(63,0))
        self.assertEqual((self.profile['final_local_calls'],self.profile['final_local_rank_mass']),(93590,404394))
    def test_shared_donor_accounting(self):
        k=self.profile['kernel'];self.assertEqual((k['entries'],k['distinct_donors'],k['shared_donors']),(1734,1427,927))
        self.assertEqual(k['histogram_delta'][1],3286);self.assertEqual(replay.mass(k['histogram_delta']),-2196)
    def test_profile_normalization(self):
        self.assertEqual((sum(self.h.values()),replay.mass(self.h)),(482030,2454930));self.assertEqual(self.inv['literal_stock'],1229665)
        self.assertEqual(120*F(self.inv['literal_stock'],60)-replay.mass(self.h),4400)
        self.assertEqual(self.inv['banks_per_stage'],161453)
    def test_adjacent_bit_root(self):
        W=F(self.inv['literal_stock'],60);low=F(751705165759922,10**18);high=low+F(1,10**18)
        self.assertLess(replay.moment(self.h,120,W,low)[1],1);self.assertGreater(replay.moment(self.h,120,W,high)[0],1)
    def test_all47_adjacent_kappa(self):
        a=replay.assembly(F(751705165759922,10**18));self.assertEqual(a['kappa'],F(751140529238897,10**18))
        self.assertEqual(len(a['strict_constraints']),47);self.assertGreater(min(a['strict_constraints'].values()),0)
        self.assertEqual(a['adjacent_grid_rejected'],['g3_above_kappa'])
    def test_bad_numeric_inputs_rejected(self):
        for bad in (True,.001,'0.001'):
            with self.assertRaises(ValueError):replay.ae.rational(bad)
        with self.assertRaises(ValueError):replay.ex.moment_interval(120,1,{120:1},F(1,1000))
    def test_missing_completion_detected(self):
        missing=self.h.copy();missing[4]-=1
        self.assertNotEqual(120*F(self.inv['literal_stock'],60)-replay.mass(missing),4400)
    def test_exact_line_charts(self):
        import chart_construction as charts
        for line in ((2,3),(6,7),(16,17)):
            for rank in (1,23):
                c=charts.line_chart(*line,rank);self.assertEqual(c['residual_rank'],rank);self.assertNotEqual(c['determinant'],0);self.assertLessEqual(c['count'],576)
    def test_degenerate_chart_rejected(self):
        import chart_construction as charts
        columns=[[int(i==j)for i in range(24)]for j in range(24)];columns[-1]=columns[0][:]
        with self.assertRaises(AssertionError):charts.checked_chart(columns,1)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    unittest.main()
