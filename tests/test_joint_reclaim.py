"""Physical and exact-arithmetic controls for the ranked-reclamation witness."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import gzip
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT/'scripts/experiments'
sys.path.insert(0, str(EXPERIMENTS))
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
from binary_frame_math import moment


class JointReclamationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = {h: json.loads(gzip.decompress((ROOT/f'certificates/joint-dual-word-{h}.json.gz').read_bytes()))
                     for h in (23,25)}

    def reject_mutation(self, mutate, checker='both'):
        for h, original in self.words.items():
            with self.subTest(h=h), tempfile.TemporaryDirectory() as directory:
                changed = deepcopy(original)
                mutate(changed)
                path = Path(directory)/'word.json'
                path.write_text(json.dumps(changed, separators=(',', ':'))+'\n')
                with self.assertRaises((AssertionError, ValueError, IndexError, KeyError)):
                    if checker != 'transitions':
                        replay(path)
                    if checker != 'replay':
                        prepare(path, Path(directory)/'transitions.bin')

    def test_selected_words_pass_independent_replay(self):
        recorded = json.loads((ROOT/'certificates/joint-dual-compiler.json').read_text())
        for h in (23,25):
            with self.subTest(h=h):
                actual = replay(ROOT/f'certificates/joint-dual-word-{h}.json.gz')
                self.assertEqual(json.loads(json.dumps(actual)), recorded['axes'][str(h)]['replay'])

    def test_omitted_literal_xor_is_rejected(self):
        self.reject_mutation(lambda word: word['ops'].pop(0))

    def test_self_xor_is_rejected(self):
        def mutate(word):
            word['ops'][0][1] = word['ops'][0][0]
        self.reject_mutation(mutate, 'replay')

    def test_non_nested_operation_frame_is_rejected(self):
        def mutate(word):
            narrow = next(i for i,(core,cover) in enumerate(word['frames']) if core == cover)
            operation = next(op for op in word['ops'] if word['frames'][op[2]][0] != word['frames'][op[2]][1])
            operation[2] = narrow
        self.reject_mutation(mutate)

    def test_aliased_terminal_role_is_rejected(self):
        def mutate(word):
            word['outputs'][1][0] = word['outputs'][0][0]
        self.reject_mutation(mutate, 'replay')

    def test_missing_copied_center_is_rejected(self):
        def mutate(word):
            index = next(i for i,(_,_,_,target) in enumerate(word['outputs']) if len(target) == 1)
            word['outputs'].pop(index)
        self.reject_mutation(mutate)

    def test_omitted_transition_cannot_reduce_paid_profile(self):
        self.reject_mutation(lambda word: word['events'].pop(0), 'transitions')

    def test_understated_physical_width_is_rejected(self):
        def mutate(word):
            word['R'] -= 1
        self.reject_mutation(mutate)

    def test_complete_pr58_profile_fails_new_bit_saving(self):
        previous = json.loads((ROOT/'references/frame-compiler/pr58/certificates/joint-dual-kappa.json').read_text())
        current = json.loads((ROOT/'certificates/joint-dual-kappa.json').read_text())
        old = previous['bit']
        result = moment(old['m'], old['W'], {int(t): n for t,n in old['child_multiplicities'].items()}, Fraction(current['bit_saving']))
        self.assertGreater(result['lower'], 1)
        self.assertGreater(Fraction(current['kappa']), Fraction(previous['kappa']))

    def test_optimized_python_is_rejected_by_every_new_entry(self):
        for name in ('joint_dual_reclaim_compiler.py', 'joint_dual_compiler.py', 'joint_dual_compose.py', 'verify_joint_dual.py'):
            with self.subTest(entry=name):
                result = subprocess.run([sys.executable, '-O', str(EXPERIMENTS/name), '--help'], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Assertions must remain enabled', result.stderr)


if __name__ == '__main__':
    unittest.main()
