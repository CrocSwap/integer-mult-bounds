import copy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import tempfile
import unittest
import verify as V


class CoordinateControls(unittest.TestCase):
    def setUp(self):
        self.word = json.loads(gzip.decompress((V.HERE/'word-23.json.gz').read_bytes()))

    def rejected(self,word):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'word.json'
            path.write_text(json.dumps(word))
            with self.assertRaises(AssertionError):
                V.replay(path)

    def test_duplicate_coordinate_rejected(self):
        permutation = V.permutation(23)
        permutation[0] = permutation[1]
        with self.assertRaises(AssertionError):
            V.relabel(self.word,permutation)

    def test_swap_is_involution_and_restores_parent(self):
        restored = V.relabel(copy.deepcopy(self.word),V.permutation(23))
        parent = json.loads(gzip.decompress((V.ROOT/'certificates/aligned-composition-word-23.json.gz').read_bytes()))
        self.assertEqual(restored,parent)

    def test_unrelabelled_sources_rejected(self):
        original = copy.deepcopy(self.word['sources'])
        changed = V.relabel(self.word,V.permutation(23))
        changed['sources'] = original
        self.rejected(changed)

    def test_unrelabelled_outputs_rejected(self):
        original = copy.deepcopy(self.word['outputs'])
        changed = V.relabel(self.word,V.permutation(23))
        changed['outputs'] = original
        self.rejected(changed)

    def test_aliased_terminal_rejected(self):
        self.word['outputs'][1][0] = self.word['outputs'][0][0]
        self.rejected(self.word)

    def test_missing_terminal_operations_rejected(self):
        terminal = self.word['outputs'][0][0]
        self.word['ops'] = [op for op in self.word['ops'] if op[0] != terminal]
        self.rejected(self.word)


class ArithmeticControls(unittest.TestCase):
    def test_parent_exact_arithmetic_unchanged(self):
        profiles = [json.loads((V.ROOT/f'certificates/aligned-composition-profiles-{h}.json').read_text()) for h in (23,25)]
        result = V.score(profiles)
        self.assertEqual(result['kappa'],V.TARGET)
        self.assertEqual(result['improvement'],0)

    def test_candidate_value_and_next_grid(self):
        record = json.loads((V.HERE/'certificate.json').read_text())
        self.assertEqual(Q(record['kappa']),V.EXPECTED)
        self.assertGreater(Q(record['kappa']),V.LATEST_TARGET)
        self.assertGreater(Q(record['coarse_grid_control']['assembly']['kappa']),V.LATEST_TARGET)
        with self.assertRaises(V.refine.balanced.InvalidAssembly):
            V.refine.balanced.assembly(record['finite_bridge'],Q(record['bit_saving']),
                                       V.EXPECTED+Q(1,10**18),h=Q(1,10**12))

    def test_pr93_profile_reproduces_latest_record(self):
        profiles = [json.loads((V.HERE/f'pr93-profiles-{h}.json').read_text()) for h in (23,25)]
        self.assertEqual(V.score(profiles)['kappa'],V.LATEST_TARGET)

    def test_rank_mass_corruption_rejected(self):
        profiles = [json.loads((V.HERE/f'profiles-{h}.json').read_text()) for h in (23,25)]
        profiles[0]['blocks'][1] += 1
        with self.assertRaises(AssertionError):
            V.paid_profile(profiles)

    def test_source_closure(self):
        self.assertEqual(V.sources(),json.loads((V.HERE/'certificate.json').read_text())['source_manifest_sha256'])


if __name__ == '__main__':
    unittest.main()
