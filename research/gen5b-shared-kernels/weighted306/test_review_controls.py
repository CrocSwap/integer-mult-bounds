"""Focused positive and corruption controls for the fixed PR306 review.
Parameterized data paths; only original review modules are executed.
Prepared with OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from pathlib import Path
import argparse,hashlib,json,unittest
import review_finite as finite
import check_chart_transport as charts
import test_norm_commutation as norms

class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_fixture306 import load_fixture
        cls.configure(load_fixture()['config'])
    @classmethod
    def configure(cls,config):
        old=Path(config['old_source']);new=Path(config['new_source']);prices=Path(config['pricing_dir'])
        cls.oldtext=(old/'finite_check.py.txt').read_bytes();cls.newtext=(new/'finite_check.py.txt').read_bytes()
        cls.pins=finite.load(new/'expected/kernel-pins.json');cls.priorpins=finite.load(old/'expected/kernel-pins.json')
        cls.baseline=finite.load(prices/'baseline-receipt.json');cls.candidate=finite.load(prices/'combined156-provisional-receipt.json')
        cls.chart=finite.load(Path(config['prior_charts']));cls.witness=finite.load(Path(config['witness']))
        cls.word=charts.data(old/'gen5bit/selected/bit/word_p12.json.gz');cls.frames=charts.data(old/'gen5bit/selected/bit/frames_p12.json.gz')['frames']
        cls.sinks=finite.load(old/'sink-selection.json')['sinks']
        cls.selections={tag:finite.load(new/(tag+'-selection.json')) for tag in ['reorder','reorder2']}
    def check_chart(self,chart=None,selections=None):
        return charts.check_inputs(self.word,self.frames,self.sinks,self.witness,chart or self.chart,selections or self.selections)
    def test_01_finite_ast_matches(self):self.assertTrue(finite.compare_finite_ast(self.oldtext,self.newtext))
    def test_02_finite_formula_mutation_rejected(self):
        changed=self.newtext.replace(b'E*(128*N**3)',b'E*(129*N**3)');self.assertNotEqual(changed,self.newtext)
        with self.assertRaises(AssertionError):finite.compare_finite_ast(self.oldtext,changed)
    def test_03_scalar_pin_mutation_rejected(self):
        p=deepcopy(self.pins);p['scalar_events']+=1
        with self.assertRaises(AssertionError):finite.invoice(1229275,483015,5090,p,self.priorpins)
    def test_04_normalizer_pin_mutation_rejected(self):
        p=deepcopy(self.pins);p['normalizer_factor_bound']+=1
        with self.assertRaises(AssertionError):finite.invoice(1229275,483015,5090,p,self.priorpins)
    def test_05_baseline_invoice(self):
        result=finite.bind(self.baseline,0,self.pins,self.priorpins,'test')
        self.assertEqual(result['displayed_finite_coefficient'],90312891518490001)
    def test_06_candidate_invoice_and_gaps(self):
        result=finite.bind(self.candidate,5090,self.pins,self.priorpins,'test')
        self.assertEqual(result['displayed_finite_coefficient'],90417469526202901)
        self.assertEqual([x['displayed_coefficient_cutoff_log2'] for x in result['bootstrap_gap_checks']],
            [125004767561877,221024550975833775858,390799911770465175736198773])
    def test_07_bootstrap_mutation_rejected(self):
        value=deepcopy(self.candidate);value['assembly']['bootstrap_chain'][1]='0'
        with self.assertRaises(AssertionError):finite.bind(value,5090,self.pins,self.priorpins,'test')
    def test_08_chart_inputs_match(self):self.assertEqual(len(self.check_chart()),18)
    def test_09_chart_first_frame_mutation_rejected(self):
        value=deepcopy(self.chart);value['role_chart_uses'][0]['frame']+=1
        with self.assertRaises(AssertionError):self.check_chart(chart=value)
    def test_10_chart_line_mutation_rejected(self):
        value=deepcopy(self.chart);value['factor_programs'][0]['line']=[0,1]
        self.assertNotEqual(value['factor_programs'][0]['line'],self.chart['factor_programs'][0]['line'])
        with self.assertRaises(AssertionError):self.check_chart(chart=value)
    def test_11_chart_factor_mutation_rejected(self):
        value=deepcopy(self.chart['factor_programs'][0]);i=next(i for i,f in enumerate(value['factors']) if f[0]=='add')
        value['factors'][i][3]=str(finite.Q(value['factors'][i][3])+1)
        with self.assertRaises(AssertionError):charts.replay_program(value)
    def test_12_all_chart_programs_replay(self):charts.replay_charts(self.chart)
    def test_13_commutation_both_directions(self):
        result=norms.run();self.assertEqual(result['signed_commuting_pairs'],1344);self.assertEqual(result['directions_per_pair'],2)
    def test_14_crossed_read_rejected(self):
        with self.assertRaises(AssertionError):norms.check_pair((0,1,1),(2,0,1),[1,2,5,11])
    def test_15_crossed_write_rejected(self):
        with self.assertRaises(AssertionError):norms.check_pair((0,1,1),(1,2,1),[1,2,5,11])
    def test_16_early_active_forward_move_rejected(self):
        value=deepcopy(self.selections);value['reorder']['moves'][16]['category']='forward_gate'
        with self.assertRaises(AssertionError):self.check_chart(selections=value)

def run(config):
    Controls.configure(config)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    assert result.wasSuccessful()
    paths=[Path(config['pricing_dir'])/name for name in ['baseline-receipt.json','combined156-provisional-receipt.json']]
    output=dict(status='PASS_FOCUSED_PR306_FINITE_CHART_NORM_CONTROLS',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        positive_tests=6,corruption_rejection_tests=10,unsigned_signed_pair_cases=1344,unsigned_directions_per_pair=2,
        chart_inverse_programs=281,price_receipt_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    out=Path(config['output_dir']);out.mkdir(parents=True,exist_ok=True)
    (out/'regression-controls.json').write_text(json.dumps(output,indent=2)+'\n')
    return output
if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True)
    print(json.dumps(run(finite.load(parser.parse_args().config)),indent=2))
