#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Focused semantic controls for the scoped proof and source boundary."""
from fractions import Fraction as F
import importlib.util
from itertools import product
from pathlib import Path
import json
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def local_module(name):
    spec = importlib.util.spec_from_file_location('test_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


primary = local_module('verify')
independent = local_module('independent')


class SemanticControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = independent.build()

    def test_binary_elimination_against_determinants(self):
        for a, b, c, d in product((0, 1), repeat=4):
            expected = 2 if (a*d - b*c) % 2 else int(bool(a or b or c or d))
            self.assertEqual(independent.binary_rank([a | (b << 1), c | (d << 1)]), expected)

    def test_coefficient_and_one_coordinate_shift_corruptions(self):
        vectors, gram, pairing, frame, indices, live, normals, base = self.model
        valid = {i: [base[i][k] + (4 if i == 45 and k < 3 else 0) for k in range(9)] for i in indices}
        self.assertTrue(independent.identity(gram, vectors, indices, normals, valid))
        invalid = {i: list(row) for i, row in base.items()}
        invalid[45][0] += 4  # Updating just one dependent coordinate is not a kernel shift.
        self.assertFalse(independent.identity(gram, vectors, indices, normals, invalid))

    def test_arbitrary_complex_parameters_and_generic_support(self):
        vectors, gram, pairing, frame, indices, live, normals, base = self.model
        # Represent complex numbers by their exact rational real and imaginary parts.
        real = {i: [base[i][k] - F(i + 1, 7) if k < 3 else base[i][k] for k in range(9)] for i in indices}
        imag = {i: [-F(i + 1, 11) if k < 3 else F(0) for k in range(9)] for i in indices}
        self.assertTrue(independent.identity(gram, vectors, indices, normals, real))
        for i in indices:
            for coordinate in range(8):
                self.assertEqual(sum(imag[i][k] * normals[k][coordinate] for k in range(9)), 0)
        # The imaginary part makes every variable coefficient nonzero.
        support_rows = {i: [int(bool(real[i][k] or imag[i][k])) for k in range(9)] for i in indices}
        self.assertEqual(independent.charges(pairing, indices, support_rows, normals, vectors)[0],
                         [9, 9, 9, 8, 8, 9, 9, 9, 9])

    def test_fixed_column_span_is_not_always_nine(self):
        vectors, gram, pairing, frame, indices, live, normals, base = self.model
        costs, supports, columns = independent.charges(pairing, indices, base, normals, vectors)
        wrong = [independent.binary_rank([pairing[i] for i in indices if supports[k] >> i & 1]) for k in range(9)]
        self.assertNotEqual(wrong, costs)
        self.assertEqual(costs[4], 8)
        self.assertEqual(wrong[4], 9)  # Full-column shortcut would overcharge this fixed term.

    def test_source_change_rejected_before_execution(self):
        with tempfile.TemporaryDirectory(prefix='a2-e6-source-') as directory:
            root = Path(directory)
            for item in json.loads((HERE / 'SOURCES.json').read_text())['files']:
                if item['usage'] == 'input':
                    target = root / item['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(primary.ROOT / item['path'], target)
            primary.source_check(root)
            target = root / 'research/nine-term-decoder-normal-form-seed42/e8lab.py'
            with target.open('ab') as stream:
                stream.write(b'\nraise RuntimeError("must never execute")\n')
            with self.assertRaisesRegex(ValueError, 'source mismatch'):
                primary.source_check(root)

    def test_missing_conflict_is_rejected(self):
        model, frame, puncture, indices, live, base = primary.setup()
        _, chars = primary.character_table(model.E)
        constraints = {p: sum(1 << i for i in indices if base[i][p[0]] != base[i][p[1]]) for p in primary.PAIRS}
        relations = primary.compatibility(chars, constraints)
        primary.census(relations)
        # A false compatibility can admit unsupported simultaneous coefficient zeros.
        relations[(0, 2)][1] |= 1 << 1
        with self.assertRaises(ValueError):
            primary.census(relations)


if __name__ == '__main__':
    unittest.main()
