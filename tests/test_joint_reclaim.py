"""Physical and exact-arithmetic controls for the ranked-reclamation witness."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import gzip
import json
import os
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
                checks = {'replay': lambda: replay(path),
                          'transitions': lambda: prepare(path, Path(directory)/'transitions.bin')}
                for name, check in checks.items():
                    if checker in ('both', name):
                        with self.subTest(checker=name):
                            with self.assertRaises((AssertionError, ValueError, IndexError, KeyError)):
                                check()

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

    def test_self_cancelling_uncharged_scatter_is_rejected(self):
        # PR #64 (rfu08) supplies this checker counterexample. Algebraic
        # cancellation cannot authorize extra incidences absent from outputs.
        def mutate(word):
            outputs = {record[0] for record in word['outputs']}
            slot = next(s for s in range(word['R']) if s not in outputs)
            rogue = [word['v'], 2*word['v']+slot]
            word['scatter'].extend([rogue, rogue])
        self.reject_mutation(mutate)

    def test_negative_operation_frame_index_is_rejected(self):
        # Python aliases this to the original frame; the physical format uses
        # nonnegative indices, as does the unsigned native profiler.
        def mutate(word):
            word['ops'][0][2] -= len(word['frames'])
        self.reject_mutation(mutate, 'replay')

    def test_cancelled_repetitions_of_paid_scatter_are_rejected(self):
        def mutate(word):
            word['scatter'].extend([word['scatter'][0], word['scatter'][0]])
        self.reject_mutation(mutate)

    def test_missing_scatter_is_rejected_by_each_helper(self):
        self.reject_mutation(lambda word: word['scatter'].pop(0))

    def test_scatter_order_preserves_the_complete_basis_receipt(self):
        recorded = json.loads((ROOT/'certificates/joint-dual-compiler.json').read_text())
        for h, original in self.words.items():
            with self.subTest(h=h), tempfile.TemporaryDirectory() as directory:
                changed = deepcopy(original)
                changed['scatter'].reverse()
                path = Path(directory)/'word.json'
                path.write_text(json.dumps(changed)+'\n')
                self.assertEqual(json.loads(json.dumps(replay(path))), recorded['axes'][str(h)]['replay'])

    def test_optimized_helpers_reject_unchecked_word(self):
        # This word omits every output. Optimized entry points must reject the
        # interpreter before unchecked replay or profiler artifacts are emitted.
        word = dict(h=3, v=1, R=1, frames=[[7,7]], sources={'0':0},
                    ops=[], outputs=[], scatter=[], events=[[0,-1,0]])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'word.json'
            path.write_text(json.dumps(word)+'\n')
            for name in ('binary_frame_replay.py', 'binary_frame_profile_prepare.py'):
                for flags, optimization in ((['-O'], ''), (['-OO'], ''), ([], '1')):
                    with self.subTest(entry=name, flags=flags, env=optimization):
                        destination = Path(directory)/'transitions.bin'
                        args = [str(path)]
                        if name == 'binary_frame_profile_prepare.py':
                            args.append(str(destination))
                        env = dict(os.environ, PYTHONOPTIMIZE=optimization)
                        result = subprocess.run([sys.executable, *flags, str(EXPERIMENTS/name), *args],
                                                capture_output=True, text=True, env=env)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn('Assertions must remain enabled', result.stderr)
                        self.assertNotIn('PASS', result.stdout)
                        self.assertFalse(destination.exists())

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
