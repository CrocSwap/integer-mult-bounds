"""Failure controls for the rank-first pair-assembly witness."""
from copy import deepcopy
from fractions import Fraction
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'research/rank-pair'
sys.path.insert(0, str(HERE))
import screen


class RankPairControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = json.loads(gzip.decompress((HERE/'frame-word-23.json.gz').read_bytes()))

    def reject(self, mutate, checker):
        word = deepcopy(self.word)
        mutate(word)
        with tempfile.TemporaryDirectory(prefix='rank-pair-control-') as directory:
            path = Path(directory)/'word.json'
            path.write_text(json.dumps(word, separators=(',', ':'))+'\n')
            with self.assertRaises((AssertionError, ValueError, IndexError, KeyError)):
                if checker == 'replay':
                    screen.replay(path)
                else:
                    screen.prepare(path, Path(directory)/'transitions.bin')

    def test_omitted_literal_xor_is_rejected(self):
        self.reject(lambda word: word['ops'].pop(0), 'replay')

    def test_understated_width_is_rejected(self):
        def mutate(word):
            word['R'] -= 1
        self.reject(mutate, 'replay')

    def test_omitted_paid_transition_is_rejected(self):
        self.reject(lambda word: word['events'].pop(0), 'transitions')

    def test_nonnested_frame_is_rejected(self):
        def mutate(word):
            narrow = next(i for i,(core,cover) in enumerate(word['frames']) if core == cover)
            operation = next(op for op in word['ops'] if word['frames'][op[2]][0] != word['frames'][op[2]][1])
            operation[2] = narrow
        self.reject(mutate, 'replay')

    def test_exact_old_network_fails_new_saving(self):
        current = json.loads((HERE/'screen-certificate.json').read_text())
        previous = json.loads((ROOT/'research/pair-assembly/frame/frame-certificate.json').read_text())
        p = previous['bit']
        moment = screen.arithmetic.moment(p['m'], p['W'],
            {int(t):n for t,n in p['child_multiplicities'].items()}, Fraction(current['bit_saving']))
        self.assertGreater(moment['lower'], 1)
        self.assertGreater(Fraction(current['kappa']), Fraction(25508460085039,500000000000000000))

    def test_optimized_python_cannot_disable_checks(self):
        for path in (HERE/'frame_compile.py', HERE/'screen.py', ROOT/'scripts/experiments/rank_pair_compiler.py'):
            with self.subTest(entry=path.name):
                result = subprocess.run([sys.executable, '-O', str(path)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Assertions must remain enabled', result.stderr)


if __name__ == '__main__':
    unittest.main()
