"""A5 geometry, conserved bridge inputs, and semantic-assembly failure modes."""
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('test_a5_semantic_witness',ROOT/'research/a5-semantic/witness.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class A5Semantic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=w.run()

    def test_actual_ordered_corner_and_negative_controls(self):
        controls=self.result['controls']
        self.assertEqual(len(controls['cases']),4)
        for case in controls['cases']:
            self.assertEqual(case['corner_rank'],47)
            self.assertEqual(case['block_rows'],[1,21])
            self.assertEqual(case['block_physical_inner_columns'],[553,573])
            self.assertEqual(len(case['negative_controls']),2)
        self.assertEqual(controls['conservative_profile'],dict(singletons=26,blocks=[21,481],rank_sum=528))

    def test_rank_mass_and_semantic_bridge_are_preserved(self):
        n,rows=w.bit_counts();old,original=w.prior.bit_counts()
        self.assertEqual(rows[1],original[1]-42*n['N'])
        self.assertEqual(rows[21],original[21]+2*n['N'])
        self.assertEqual(sum(r*c for r,c in rows.items()),old['s'])
        f=self.result['finite_bridge']
        self.assertEqual((n['W'],n['m'],max(rows)),(f['bit']['W'],f['bit']['m'],f['bit']['maxchild']))
        self.assertEqual(f['semantic']['C1'],1)
        self.assertEqual(f['rows']['degree'],89000)
        self.assertGreater(f['semantic']['strict_literal_gap'],0)

    def test_new_bit_moment_needs_the_contiguous_block(self):
        self.assertGreater(self.result['bit']['strict_gap'],Q(3,10**14))
        with self.assertRaisesRegex(ValueError,'Characteristic moment'):
            w.bit_certificate(use_block=False)
        with self.assertRaisesRegex(ValueError,'Characteristic moment'):
            w.bit_certificate(w.BIT_SAVING+Q(1,10**12))

    def test_47_constraints_and_independent_margin_formulas(self):
        a=self.result['assembly'];p=a['parameters'];e=p['epsilon'];c=p['c'];r=p['alpha_squared_power'];d=p['delta']
        expected=dict(g1=1-e*(1+c),g2=w.BIT_SAVING,g3=e*p['q'],g4=w.BIT_SAVING,
                      g5=min(1-e-d,r-d),g6=1-e-d,g7=e)
        self.assertEqual(a['margins'],expected)
        self.assertEqual(len(a['constraints']),47)
        self.assertTrue(all(x>0 for x in a['constraints'].values()))
        self.assertEqual(a['minimum_margin'],min(expected.values()))
        self.assertGreater(a['absorption_gap'],Q(5,10**13))
        for kwargs in ({'old_guard':True},{'old_exposures':True},{'kappa':w.KAPPA+Q(1,10**12)}):
            with self.assertRaises(AssertionError):w.assembly(self.result['finite_bridge'],**kwargs)

if __name__=='__main__':unittest.main()
