"""Failure modes and independent operator controls for the scoped theorem."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class Controls(unittest.TestCase):
    def test_full_symbolic_maps_and_late_negative_reads(self):
        for h in (6, 8, 10):
            noisy = v.stress(h)
            clean = v.normalize(h, noisy)
            self.assertEqual(v.symbolic(h, clean)['rank_mass'], h*(3*h-8))
            self.assertLess(v.symbolic(h, clean)['rank_mass'], v.symbolic(h, noisy)['rank_mass'])
            self.assertEqual(clean, v.direct(h))

    def test_independent_dense_engine_rejects_changed_readout(self):
        word = v.direct(6)
        pos = next(i for i, op in enumerate(word) if op[0] == 'add' and op[3] == 1)
        word[pos] = (*word[pos][:3], -1)
        with self.assertRaisesRegex(v.Rejected, 'dense dirty operator'):
            v.fourier(6, word)

    def test_rejects_scope_changes_and_corruption(self):
        original = v.direct(6)
        positive = next(i for i, op in enumerate(original) if op[0] == 'add' and op[3] == 1)
        first_phase = next(i for i, op in enumerate(original) if op[0] == 'phase')
        mutations = []
        w = copy.deepcopy(original); w.pop(positive); mutations.append(w)
        w = copy.deepcopy(original); w.append(w[0]); mutations.append(w)
        w = copy.deepcopy(original); op=w[positive]; w[positive]=(op[0],op[1],(op[2]+1)%6,op[3]); mutations.append(w)
        w = copy.deepcopy(original); op=w[first_phase]; w[first_phase]=(op[0],op[1],op[2],-op[3]); mutations.append(w)
        w = copy.deepcopy(original); w.pop(); mutations.append(w)
        w = copy.deepcopy(original); w[first_phase]=('phase',0,63,1); mutations.append(w)
        w = copy.deepcopy(original); w[0]=('add',0,1,1); mutations.append(w)
        w = copy.deepcopy(original); w[0]=('add',6,7,1); mutations.append(w)
        w = copy.deepcopy(original); w[0]=('add',True,0,-1); mutations.append(w)
        w = copy.deepcopy(original); w[0]=('add',6,0,-1.0); mutations.append(w)
        w = copy.deepcopy(original); w[first_phase]=('translate',0,1,-1); mutations.append(w)
        w = copy.deepcopy(original); w[first_phase]=('unknown',0,1,1); mutations.append(w)
        for index, word in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(v.Rejected):
                v.symbolic(6, word)

    def test_dense_engine_rejects_unrestored_dirty_columns(self):
        for word in (v.stress(6)[:-1], v.direct(6)[:-1]):
            with self.assertRaisesRegex(v.Rejected, 'dense dirty operator'):
                v.fourier(6, word)

    def test_cli_preserves_existing_output(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'receipt.json'
            path.write_text('sentinel')
            result = subprocess.run([sys.executable, '-I', '-O', '-B',
                                     str(Path(v.__file__)), str(path)],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('existing output refused', result.stderr)
            self.assertEqual(path.read_text(), 'sentinel')

    def test_translation_identity_on_every_character(self):
        for h in (6, 8):
            full=(1<<h)-1
            normals=[full^(1<<i) for i in range(h)]
            for character in range(1<<h):
                values=[(n&character).bit_count()%2 for n in normals]
                for i in range(h):
                    for j in range(h):
                        if i != j:
                            lhs=((h-1)*(-values[i]+values[j]))%4
                            rhs=(2*values[i]+(h-1)*(values[i]+values[j]))%4
                            self.assertEqual(lhs,rhs)

    def test_oriented_and_quotient_group_are_faithful(self):
        h=6
        full=(1<<h)-1
        images={sum((((full^(1<<i))&ch).bit_count()%2)<<i for i in range(h))
                for ch in range(1<<h)}
        self.assertEqual(len(images),1<<h)

    def test_normalizer_refuses_translation_alphabet(self):
        with self.assertRaisesRegex(v.Rejected, 'oriented normalizer'):
            v.normalize(6,v.direct(6,True))


if __name__ == '__main__':
    unittest.main()
