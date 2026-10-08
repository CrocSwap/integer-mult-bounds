"""Controls for the searched-order producer witness."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'research/ordered-descent'
spec = importlib.util.spec_from_file_location('ordered_descent_witness', HERE/'witness.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

PR49_KAPPA = Q(4123863984, 10**14)
PR49_W = 177284805


class SearchedOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = w.run()

    def test_frozen_certificate(self):
        self.assertEqual(w.js(self.result), w.read(HERE/'certificate.json'))

    def test_strict_assembly_and_bracket(self):
        a = self.result['assembly']
        self.assertEqual(len(a['constraints']), 47)
        self.assertEqual(len(a['margins']), 7)
        self.assertTrue(all(x > 0 for x in a['constraints'].values()))
        self.assertGreater(self.result['kappa'], PR49_KAPPA)
        self.assertGreater(self.result['kappa'], Q(1, 2**15))
        self.assertLess(self.result['kappa'], Q(1, 2**14))

    def test_fewer_roles_than_pr49(self):
        for h, expected in ((23, 36341), (25, 48247)):
            ours = w.read(HERE/f'original-{h}.json')
            theirs = w.read(ROOT/f'research/climbed-48/original-{h}.json')
            self.assertEqual(ours['R'], expected)
            self.assertLess(ours['R'], theirs['R'])
            self.assertEqual(ours['loss'], theirs['loss'])
            self.assertEqual(ours['R'], ours['c'] + ours['q'] - ours['matched'])

    def test_role_volume_undercuts_pr49(self):
        W = self.result['bit']['counts']['W']
        self.assertEqual(W, 177176337)
        self.assertLess(W, PR49_W)

    def test_pinned_matchings_are_injective(self):
        for h, expected in ((23, 6153), (25, 7825)):
            raw = (HERE/f'links-{h}.uses').read_bytes()
            n, k = struct.unpack_from('<2I', raw)
            edges = [struct.unpack_from('<2I', raw, 8+8*i) for i in range(k)]
            self.assertTrue(all(0 < d < n for d, _ in edges))
            self.assertEqual(k, expected)
            self.assertEqual(len({d for d, _ in edges}), k)
            self.assertEqual(len({u for _, u in edges}), k)

    def test_every_earlier_network_is_excluded(self):
        controls = self.result['exclusion_lower_moments']
        self.assertIn('comparison-climbed48.json', controls)
        self.assertIn('comparison-pr48.json', controls)
        for name, value in controls.items():
            self.assertGreater(Q(value), 1, name)


if __name__ == '__main__':
    unittest.main()
