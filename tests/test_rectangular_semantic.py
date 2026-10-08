import importlib.util,json,unittest
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('test_rectangular_witness',ROOT/'research/rectangular-semantic/witness.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class RectangularSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=w.run()
    def test_complete_rank_mass(self):
        n=self.result['counts']
        self.assertEqual(sum(t*c for t,c in n['rows'].items()),n['s'])
        self.assertEqual(n['W']*n['m']-n['s'],2*n['N']-2*n['L'])
        self.assertEqual((n['m'],n['W'],max(n['rows'])),(43092,13904995529880,43038))
    def test_moment_and_grid_boundary(self):
        bit=self.result['bit'];self.assertEqual(bit['saving'],Q(12261239,10**12))
        self.assertGreater(bit['gap'],0);self.assertGreaterEqual(bit['next_moment'],1)
        self.assertLess(self.result['without_A5_saving'],bit['saving'])
    def test_joint_row_stock_and_assembly(self):
        r=self.result;f=r['finite_bridge'];a=r['assembly']
        self.assertEqual(f['rows']['coefficient'],44*553+41*544)
        self.assertEqual(f['rows']['degree'],96000)
        self.assertEqual(f['rows']['degree_gap'],Q(21564,25))
        self.assertEqual(len(a['constraints']),47);self.assertEqual(len(a['margins']),7)
        self.assertTrue(all(x>0 for x in a['constraints'].values()))
        self.assertEqual(a['parameters']['kappa'],Q(12260937,10**12))
        self.assertGreater(a['absorption_gap'],Q(9,10**13))
    def test_actual_corner_controls(self):
        c=self.result['fresh_exact_controls']
        self.assertEqual(c['A1']['runs'],[28,1,28,28])
        self.assertEqual(c['A1']['rank'],85)
        for case in c['A5']:
            self.assertEqual((case['rank'],case['block']),(54,25))
            self.assertEqual(case['negative_controls'],['wrong_boundary','omit_first_pivot'])
    def test_profiles_and_bad_basis(self):
        self.assertEqual(self.result['profiles']['A5']['singletons'],29)
        self.assertEqual(self.result['profiles']['A5']['blocks'],[25,648])
        self.assertIsNone(w.record.basis(28,28,57))
    def test_saved_certificate_and_source_pins(self):
        saved=json.loads((w.HERE/'certificate.json').read_text())
        self.assertEqual(saved,w.arithmetic.js(self.result))
        self.assertGreater(len(self.result['pin_validation']['live_pinned_sha256']),10)
    def test_negative_semantic_controls(self):
        self.assertTrue({'old_quadratic_guard','old_separate_exposure','next_kappa_grid'}<=set(self.result['negative_controls']))

if __name__=='__main__':unittest.main()
