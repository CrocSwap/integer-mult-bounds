"""Arithmetic and actual CLI failure tests for the whole-word grid contract."""
from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify
from arithmetic import ZERO, half, stage

HERE = Path(__file__).resolve().parent


class GridTests(unittest.TestCase):
    def test_literal_gaussian_pair_and_signed_ties(self):
        vector = ((2, 3), (-1, 4)) + ZERO[2:]
        self.assertEqual(stage(vector, 0)[:2], ((1, 5), (0, 2)))
        self.assertEqual([half(n, False) for n in (-5, -3, -1, 1, 3, 5)],
                         [-2, -2, 0, 0, 2, 2])
        with self.assertRaisesRegex(ValueError, 'inexact internal halving'):
            stage(((1, 0),) + ZERO[1:], 0)

    def test_fraction_prefix(self):
        scale = 256
        vector = ((scale, 0),) + ZERO[1:]
        coefficient = (Q(1), Q(0))
        for k in range(1, 9):
            a, b = coefficient
            coefficient = ((a-b)/2, (a+b)/2)
            vector = stage(vector, k-1)
            actual = (Q(vector[0][0], scale), Q(vector[0][1], scale))
            self.assertEqual(actual, coefficient)
            self.assertEqual(sum(Q(a*a+b*b, scale*scale) for a, b in vector), Q(1))

    def test_receipt_integer_boolean_and_duplicate_keys(self):
        self.assertNotEqual(verify.canonical({'bits': 1}),
                            verify.canonical({'bits': True}))
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            json.loads('{"a":1,"a":2}', object_pairs_hook=verify.unique)

    def command(self, root, *arguments):
        argv = [sys.executable, '-I', '-O', '-B', str(root/'verify.py'), *arguments]
        return subprocess.run(argv,
                              capture_output=True, text=True, timeout=120)

    def test_git_free_cli_and_real_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)/'package'
            shutil.copytree(HERE, root, ignore=shutil.ignore_patterns('__pycache__'))
            receipt = Path(temp)/'receipt.json'
            result = self.command(root, '--out', str(receipt))
            self.assertEqual((result.returncode, result.stdout.strip()),
                             (0, 'PASS_P104_WHOLE_WORD_INTERNAL_GRID'), result.stderr)
            self.assertEqual(json.loads(receipt.read_text())['physical_fixtures'][1]
                             ['matched_public_fields'], 358)
            result = self.command(root, '--out', str(receipt))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileExistsError', result.stderr)
            expected = verify.read(root/'RESULT.json')
            damaged = deepcopy(expected)
            damaged['one_layer_extra_bits'] = True
            (root/'RESULT.json').write_text(json.dumps(damaged))
            result = self.command(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('typed receipt mismatch', result.stderr)
            (root/'RESULT.json').write_text(json.dumps(expected))
            with (root/'inputs/WORD.json').open('ab') as handle:
                handle.write(b' ')
            result = self.command(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source SHA256', result.stderr)


if __name__ == '__main__':
    unittest.main()
