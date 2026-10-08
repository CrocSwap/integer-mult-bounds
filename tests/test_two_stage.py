import importlib.util,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]/'research/two-stage'
sys.path.insert(0,str(HERE))
def module(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class TwoStageTests(unittest.TestCase):
    def test_exact_certificate(self):
        r=module('two_stage_verify','verify.py').run()
        self.assertEqual(len(r['assembly']['constraints']),47)
        self.assertGreater(r['assembly']['gap_above_2_minus16'],0)
    def test_dirty_endpoints_and_copy(self):
        self.assertEqual(module('two_stage_controls','controls.py').run()['complete_input_basis_columns'],16)
    def test_basis_corners(self):
        m=module('two_stage_corners','check_unequal_corners.py')
        for b in [10,23,30,51,53]:
            for seed in [1,2,3]:self.assertEqual(m.control(b,seed)['data_nullity_rank'],2*b+1)
    def test_profile_rank_charge(self):
        import json
        m=module('two_stage_profile','two_stage_unequal.py')
        rows=[json.loads((HERE/f'producer-{h}.json').read_text())['matched'] for h in [55,53]]
        p=m.profile(*rows)
        self.assertEqual(sum(t*n for t,n in p['rows'].items()),p['W']*p['m']-p['N']+2*p['L'])
        self.assertGreater(p['rows'][1],p['N'])
if __name__=='__main__':unittest.main()
