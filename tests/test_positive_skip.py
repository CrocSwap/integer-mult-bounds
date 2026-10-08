"""Controls for the positive-frame cloned skip-prefix witness."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util, struct, unittest
ROOT = Path(__file__).resolve().parents[1]; HERE = ROOT/'research/positive-skip'
_s = importlib.util.spec_from_file_location('positive_skip_witness', HERE/'witness.py')
w = importlib.util.module_from_spec(_s); _s.loader.exec_module(w)

class PositiveSkipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r = w.run()
    def test_frozen_certificate(self): self.assertEqual(w.js(self.r), w.read(HERE/'certificate.json'))
    def test_assembly(self):
        a = self.r['assembly']; self.assertEqual(len(a['constraints']), 47); self.assertEqual(len(a['margins']), 7)
        self.assertTrue(all(x > 0 for x in a['constraints'].values()))
    def test_beats_pr53_and_pr54(self):
        self.assertGreater(w.KAPPA, w.PR54_KAPPA); self.assertGreater(w.KAPPA, w.PR53_KAPPA)
        for n in ('comparison-pr53.json', 'comparison-pr54.json'): self.assertGreater(self.r['exclusion_lower_moments'][n], 1)
    def test_roles(self):
        for h, R, k in ((23, 32693, 13225), (25, 43009, 17791)):
            p = w.read(HERE/f'profiles-{h}.json'); self.assertEqual((p['R'], p['matched']), (R, k))
            raw = (HERE/f'links-{h}.uses').read_bytes(); n, c = struct.unpack_from('<2I', raw); self.assertEqual(c, k)
            e = [struct.unpack_from('<2I', raw, 8+8*i) for i in range(c)]
            self.assertEqual(len({d for d, _ in e}), c); self.assertEqual(len({u for _, u in e}), c)

if __name__ == '__main__': unittest.main()
