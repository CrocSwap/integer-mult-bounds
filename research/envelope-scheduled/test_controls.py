"""Negative and positive controls for coordinate binding, the physical word and
the region-order hook."""
import copy,gzip,json,tempfile,unittest
from fractions import Fraction as Q
from pathlib import Path
import verify,scheduler
class WordControls(unittest.TestCase):
    def setUp(self):
        self.word=json.loads(gzip.decompress((verify.HERE/'word-23.json.gz').read_bytes()))
        self.roles=json.loads((verify.HERE/'profiles-23.json').read_text())['R']
        self.config=json.loads((verify.PINNED/'order-23.json').read_text())
    def shifted_order(self):
        order=list(self.config['order'])
        return order[7:]+order[:7]
    def rejected(self,word):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'word.json';p.write_text(json.dumps(word))
            with self.assertRaises(AssertionError):verify.replay(p)
    def test_duplicate_coordinate(self):
        config=copy.deepcopy(self.config);config['order'][0]=config['order'][1]
        with self.assertRaises(AssertionError):verify.relabel(self.word,config)
    def test_inconsistent_mapping(self):
        config=copy.deepcopy(self.config);config['mapping']['0']=0
        with self.assertRaises(AssertionError):verify.relabel(self.word,config)
    def test_shipped_word_replays(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'word.json';p.write_text(json.dumps(self.word))
            self.assertEqual(verify.replay(p)['roles'],self.roles)
    def test_further_relabelling_is_still_valid(self):
        word=verify.relabel(copy.deepcopy(self.word),self.shifted_order())
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'word.json';p.write_text(json.dumps(word))
            self.assertEqual(verify.replay(p)['roles'],self.roles)
    def test_unrelabelled_source_values(self):
        word=verify.relabel(copy.deepcopy(self.word),self.shifted_order())
        word['sources']=copy.deepcopy(self.word['sources']);self.rejected(word)
    def test_unrelabelled_outputs(self):
        word=verify.relabel(copy.deepcopy(self.word),self.shifted_order())
        word['outputs']=copy.deepcopy(self.word['outputs']);self.rejected(word)
    def test_missing_terminal_synthesis(self):
        word=verify.relabel(copy.deepcopy(self.word),self.shifted_order())
        terminal=word['outputs'][0][0];word['ops']=[op for op in word['ops'] if op[0]!=terminal];self.rejected(word)
    def test_aliased_terminal(self):
        word=verify.relabel(copy.deepcopy(self.word),self.shifted_order())
        word['outputs'][1][0]=word['outputs'][0][0];self.rejected(word)
class ScheduleControls(unittest.TestCase):
    def fake(self,dimension):
        blocks=[dict(rank=0,inputs=[],nodes=[0],frame=(),candidates=[]),
                dict(rank=0,inputs=[0],nodes=[1],frame=(),candidates=[])]
        return (None,blocks,[],None,{0:0},None,None,None)
    def test_recorded_modes(self):
        self.assertEqual(scheduler.MODES,{23:'node-asc',25:'width-node'})
        recorded=json.loads((verify.HERE/'certificate.json').read_text())['axes']
        self.assertEqual({axis['h']:axis['mode'] for axis in recorded},scheduler.MODES)
    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):scheduler.order_keys('not-a-mode',{},__import__('hashlib'))
    def test_forward_order_accepted(self):
        original=scheduler.order_keys
        try:
            scheduler.order_keys=lambda mode,blocks,hashlib:lambda g:(blocks[g]['rank'],g)
            built=scheduler.ordered_build(self.fake,23,'cover-core')(23)
        finally:
            scheduler.order_keys=original
        self.assertEqual(list(built[6]),[0,1])
    def test_backward_region_order_rejected(self):
        original=scheduler.order_keys
        try:
            scheduler.order_keys=lambda mode,blocks,hashlib:lambda g:(blocks[g]['rank'],-g)
            with self.assertRaises(AssertionError):scheduler.ordered_build(self.fake,23,'cover-core')(23)
        finally:
            scheduler.order_keys=original
    def test_candidate_improves_pinned_kappa(self):
        recorded=json.loads((verify.HERE/'certificate.json').read_text())
        self.assertGreater(Q(recorded['comparison']['kappa']),Q(recorded['comparison']['pinned_kappa']))
        self.assertEqual(recorded['comparison']['kappa'],recorded['assembly']['kappa'])
    def test_next_kappa_grid_rejected(self):
        recorded=json.loads((verify.HERE/'certificate.json').read_text())
        inherited=json.loads((verify.ROOT/'references/frame-compiler/pr48/research/copied-fixed/certificate.json').read_text())['finite_bridge']
        bridge=verify.bridge_for_width(inherited,recorded['bit']['W'])
        saving=Q(recorded['bit_saving']);kappa=Q(recorded['comparison']['kappa'])
        backoff=Q(1,10**12)
        self.assertEqual(verify.refine.assemble(bridge,saving,backoff,10**18)['kappa'],kappa)
        with self.assertRaises(verify.refine.balanced.InvalidAssembly):
            verify.refine.balanced.assembly(bridge,saving,kappa+Q(1,10**18),h=backoff)
class WidthControls(unittest.TestCase):
    def test_stale_bridge_fields(self):
        inherited=json.loads((verify.ROOT/'references/frame-compiler/pr48/research/copied-fixed/certificate.json').read_text())['finite_bridge']
        bridge=verify.bridge_for_width(inherited,json.loads((verify.HERE/'certificate.json').read_text())['bit']['W'])
        for section,field in (('bit','wire_bits'),('rows','coefficient'),('rows','degree_gap')):
            with self.subTest(field=field):
                stale=copy.deepcopy(bridge);stale[section][field]=inherited[section][field]
                with self.assertRaises(verify.refine.balanced.InvalidAssembly):verify.refine.balanced.validate_bridge(stale)
if __name__=='__main__':unittest.main()
