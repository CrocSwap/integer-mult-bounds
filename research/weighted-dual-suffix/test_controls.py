"""Adversarial matching, exact-frame and full-cost controls."""
import tempfile,unittest,importlib.util,copy
from pathlib import Path
import verify as v
import audit
class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(dir=v.ROOT/'build/weighted-dual-suffix')
        spec=importlib.util.spec_from_file_location('producer_controls',v.ROOT/'research/dual-suffix-centers/producer.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        prefix=Path(cls.tmp.name)/'producer';module.build(24,prefix,24)
        cls.graph=audit.load(prefix);cls.links=audit.read_links(v.HERE/'links.txt')
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_selected_complete_profile(self):
        got=audit.replay(self.graph,self.links);expected=v.read(v.HERE/'producer.json')
        for key,value in got.items():self.assertEqual(value,expected[key],key)
    def test_duplicate_link(self):
        with self.assertRaisesRegex(ValueError,'Matching uniqueness'):audit.replay(self.graph,self.links+[self.links[0]])
    def test_nonaddition_donor(self):
        with self.assertRaisesRegex(ValueError,'Addition donor'):audit.replay(self.graph,[(1,self.links[0][1])])
    def test_out_of_range_use(self):
        with self.assertRaisesRegex(ValueError,'Link range'):audit.replay(self.graph,[(self.links[0][0],10**9)])
    def test_incorrect_frame_rank(self):
        g=dict(self.graph);r=list(g['ranks']);r[1]+=1;g['ranks']=r
        with self.assertRaisesRegex(ValueError,'Singleton frame'):audit.replay(g,self.links)
    def test_omitted_retained_loss(self):
        row=v.read(v.HERE/'producer.json');row['loss']=0
        with self.assertRaises((ValueError,AssertionError)):v.exact(row)
    def test_unpaid_cleanup(self):
        row=v.read(v.HERE/'producer.json');row['histogram'][24]-=1
        with self.assertRaises((ValueError,AssertionError)):v.exact(row)
    def test_old108_network_cannot_claim_new_bound(self):
        with self.assertRaises((ValueError,AssertionError)):v.exact(v.read(v.ROOT/'research/dual-suffix-centers/producer.json'))
    def test_histogram_mass_preserving_mutation(self):
        row=v.read(v.HERE/'producer.json');row['histogram'][1]+=2;row['histogram'][2]-=1
        with self.assertRaises((ValueError,AssertionError)):v.exact(row)
    def test_strict_certificate_and_next_grids(self):v.exact(v.read(v.HERE/'producer.json'))
if __name__=='__main__':unittest.main()
