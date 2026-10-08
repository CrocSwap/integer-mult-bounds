import importlib.util,json,unittest,copy
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('test_certified_data_corners',ROOT/'research/two-stage-corners/witness.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class CertifiedDataCornerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=w.run()
    def test_rank_mass_and_paid_correction(self):
        r=self.result;n=r['counts'];self.assertEqual(sum(t*c for t,c in n['rows'].items()),n['s'])
        self.assertEqual(n['W']*n['m']-n['s'],n['N']-2*n['L']);self.assertGreaterEqual(n['rows'][1],n['N'])
        self.assertEqual(r['data_profile']['singletons'],11);self.assertEqual(r['data_profile']['blocks'],[51,45,2701])
    def test_exact_identities_and_contiguity(self):
        c=self.result['identity_controls'];self.assertEqual((c['zero_certificates'],c['integer_ranks'],c['rational_pivots']),(2265,4530,107))
        self.assertEqual(c['blocks'][0]['columns'],[2863,2913]);self.assertEqual(c['blocks'][1]['columns'],[2812,2856]);self.assertEqual(c['middle'],[107,2807])
    def test_moment_and_assembly(self):
        r=self.result;self.assertEqual(r['bit']['saving'],Q(15879079,10**12));self.assertGreater(r['bit']['strict_gap'],0);self.assertGreaterEqual(r['bit']['next_moment_upper'],1)
        self.assertEqual(r['assembly']['parameters']['kappa'],Q(15878574,10**12));self.assertEqual(len(r['assembly']['constraints']),47);self.assertEqual(len(r['assembly']['margins']),7)
        self.assertTrue(all(v>0 for v in r['assembly']['constraints'].values()));self.assertEqual(r['finite_bridge']['rows']['degree'],47000)
    def test_wrong_residue_and_missing_identity_rejected(self):
        c=json.loads((w.HERE/'a5-residual-two-stage.json').read_text());c['gamma_offset']=0
        with self.assertRaises(AssertionError):w.identities.run(c)
        c=json.loads((w.HERE/'a5-residual-two-stage.json').read_text());c['zero_minor_certificates'].pop()
        with self.assertRaises(KeyError):w.identities.run(c)
    def test_saved_certificate(self):
        self.assertEqual(json.loads((w.HERE/'certificate.json').read_text()),w.cutoff.js(self.result))
    def test_parameterized_assembly_matches_parent(self):
        old=w.parent.run();fresh=w.arithmetic.assembly(old['finite_bridge'],Q(15537,10**9),Q(15536,10**9))
        self.assertEqual(fresh,old['assembly'])

if __name__=='__main__':unittest.main()
