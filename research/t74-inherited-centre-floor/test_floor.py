# SPDX-License-Identifier: Apache-2.0
"""Behavior tests for the independent source-projection checker."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import verify


class FloorTests(unittest.TestCase):
    def test_rank_four_and_singular_control(self):
        matrix = [[Fraction(n, 4) for n in row] for row in verify.NUMERATORS]
        self.assertEqual(verify.determinant(matrix), Fraction(-1, 16))
        matrix[0] = list(matrix[1])
        self.assertEqual(verify.determinant(matrix), Fraction(0))

    def test_chart_inverse_preserves_an_independent_input(self):
        rows = [{} for _ in range(704)]
        rows[33] = {(33, ()): Fraction(1)}
        verify.apply(rows, ['warp', 33, 47])
        verify.apply(rows, ['warp', 33, -47])
        self.assertEqual(rows[33], {(33, ()): Fraction(1)})

    def test_one_omitted_correction_has_a_nonzero_literal_residual(self):
        word = verify.load_words()['base']
        index = next(i for i, gate in enumerate(word['A'])
                     if gate[:3] == ['add', 135, 33])
        word['A'][index][3] = 0
        self.assertEqual(verify.projection(word), {
            23: {(33, (47,)): Fraction(-1, 4)},
            108: {(33, (47,)): Fraction(1, 4)},
        })

    def test_target_feedback_is_not_an_invertible_target_block_certificate(self):
        word = verify.load_words()['base']
        word['B'].append(['add', 0, 112, 1, 1, []])
        with self.assertRaisesRegex(ValueError, 'target feedback into non-target'):
            verify.continuation(word)

    def test_cli_is_identical_with_optimization(self):
        outputs = []
        for flags in ([], ['-O']):
            result = subprocess.run(
                [sys.executable, *flags, '-B', str(verify.HERE / 'verify.py')],
                capture_output=True, text=True, check=True, timeout=30,
            )
            self.assertEqual(result.stderr, '')
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])
        report = json.loads(outputs[0])
        self.assertEqual(report, json.loads((verify.HERE / 'RESULT.json').read_text()))
        self.assertEqual(report['status'], 'PASS_T74_INHERITED_CENTRE_FLOOR')
        for tag in ('base', 'extra'):
            self.assertEqual(report['providers'][tag]['invoice'],
                             {'1': 4, '7': 4, '8': 4})
            self.assertEqual(len(report['providers'][tag]['controls']), 7)

    def test_cli_rejects_a_corrupt_word_before_parsing(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            for name in ('verify.py', 'INPUTS.json'):
                shutil.copyfile(verify.HERE / name, destination / name)
            shutil.copytree(verify.HERE / 'inputs', destination / 'inputs')
            path = destination / 'inputs/eight-alias-base.json.gz'
            path.write_bytes(b'not gzip')
            result = subprocess.run(
                [sys.executable, '-B', str(destination / 'verify.py')],
                capture_output=True, text=True, check=False, timeout=30,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, '')
            self.assertIn('ValueError: source hash', result.stderr)


if __name__ == '__main__':
    unittest.main()
