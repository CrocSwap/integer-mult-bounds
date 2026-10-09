"""Controls for the hill-climbed PR #48 producer witness."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'research/climbed-48'
spec = importlib.util.spec_from_file_location('climbed_48_witness', HERE/'witness.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class OptimalMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = w.run()

    def test_frozen_certificate(self):
        actual = w.js(self.result)
        actual['local_sha256'] = {k.replace('\\', '/'): v for k, v in actual['local_sha256'].items()}
        self.assertEqual(actual, w.read(HERE/'certificate.json'))

    def test_strict_assembly_and_bracket(self):
        a = self.result['assembly']
        self.assertEqual(len(a['constraints']), 47)
        self.assertEqual(len(a['margins']), 7)
        self.assertTrue(all(x > 0 for x in a['constraints'].values()))
        self.assertGreater(w.KAPPA, w.PR48_KAPPA)
        self.assertGreater(w.KAPPA, Q(1, 2**15))
        self.assertLess(w.KAPPA, Q(1, 2**14))

    def test_fewer_roles_than_pr48(self):
        for h, R in ((23, 36287), (25, 48165)):
            ours = w.read(HERE/f'original-{h}.json')
            theirs = w.read(ROOT/f'research/copied-fixed/original-{h}.json')
            self.assertEqual(ours['R'], R)
            self.assertLess(ours['R'], theirs['R'])
            self.assertEqual(ours['loss'], theirs['loss'])

    def test_matching_differs_from_pr43_and_is_injective(self):
        for h, expected in ((23, 6220), (25, 7937)):
            raw = (HERE/f'links-{h}.uses').read_bytes()
            n, k = struct.unpack_from('<2I', raw)
            edges = [struct.unpack_from('<2I', raw, 8+8*i) for i in range(k)]
            self.assertEqual(k, expected)
            self.assertEqual(len({d for d, _ in edges}), k)
            self.assertEqual(len({u for _, u in edges}), k)
            profile = w.read(HERE/f'profiles-{h}.json')['blocks']
            pr43 = w.read(ROOT/f'research/copied-fixed/profiles-{h}.json')['blocks']
            self.assertNotEqual(profile, pr43)  # PR46 profiles

    def test_pr48_network_excluded(self):
        self.assertGreater(self.result['exclusion_lower_moments']['comparison-pr48.json'], 1)


if __name__ == '__main__':
    unittest.main()
