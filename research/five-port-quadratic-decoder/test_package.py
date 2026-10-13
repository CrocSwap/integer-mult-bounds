#!/usr/bin/env python3
"""Adversarial checks of the proof-relevant finite validation paths.

Apache-2.0. Copyright 2026 Ross Richardson.
Prepared with substantial OpenAI Codex assistance.
"""
from itertools import permutations, product
from pathlib import Path
from unittest.mock import patch
import copy
import importlib.util
import json
import random
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location('five_port_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


primary = load('verify')
second = load('independent')


def permutation_determinant(matrix):
    n = len(matrix)
    value = 0
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        term = (-1)**inversions
        for i, j in enumerate(order):
            term *= matrix[i][j]
        value += term
    return value


class ProofRelevantControls(unittest.TestCase):
    def test_two_eliminations_against_definition(self):
        matrices = [[[a, b], [c, d]] for a, b, c, d in product(range(-1, 2), repeat=4)]
        rng = random.Random(40)
        matrices += [[[rng.randrange(-4, 5) for _ in range(4)] for _ in range(4)] for _ in range(40)]
        matrices += [[[0, 1, 0], [0, 0, 1], [1, 0, 0]], [[0, 0], [1, 1]]]
        for matrix in matrices:
            exact = permutation_determinant(matrix)
            self.assertEqual(primary.determinant_mod(matrix), exact % primary.PRIME)
            self.assertEqual(second.bareiss(matrix), exact)
            self.assertEqual(second.bareiss(matrix, second.MODULUS), exact % second.MODULUS)

    def test_all_named_controls(self):
        witness = json.loads((HERE / 'WITNESSES.json').read_text())['witnesses']
        self.assertEqual(len(primary.negative_controls(witness)), 9)

    def test_distinct_valid_labels_can_make_a_singular_minor(self):
        # Different ports can have identical pairings on a restricted column
        # set. Exercise elimination, not just duplicate-label rejection.
        ports = [sum(1 << (2*i+b) for i, b in enumerate(bits)) for bits in product((0, 1), repeat=5)]
        found = False
        for a, b in zip(ports, ports[1:]):
            matrix = [[primary.gram(x, y) for y in ports[:2]] for x in (a, b)]
            if permutation_determinant(matrix) == 0:
                self.assertEqual(primary.determinant_mod(matrix), 0)
                found = True
                break
        self.assertTrue(found)

    def test_missing_obligation_rejected(self):
        with tempfile.TemporaryDirectory(prefix='five port omission ') as tmp:
            shutil.copytree(HERE, Path(tmp) / 'package')
            root = Path(tmp) / 'package'
            data = json.loads((root / 'WITNESSES.json').read_text())
            data['witnesses'] = data['witnesses'][:-1]
            (root / 'WITNESSES.json').write_text(json.dumps(data))
            with patch.object(primary, 'HERE', root):
                with self.assertRaisesRegex(ValueError, '17 obligations'):
                    primary.verify()

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory(prefix='five port source ') as tmp:
            shutil.copytree(HERE, Path(tmp) / 'package')
            root = Path(tmp) / 'package'
            source = root / 'sources/pr446-PROOF.md'
            source.write_bytes(source.read_bytes() + b'\nchanged source\n')
            with patch.object(primary, 'HERE', root):
                with self.assertRaisesRegex(ValueError, 'immutable source hash'):
                    primary.check_sources()

    def test_valid_scalar_geometry_failure_is_visible(self):
        # An overlap-three correction is present in the true XOR identity,
        # but the predecessor's affine overlap kernel j-1 cannot route it.
        left = frozenset((0, 2, 4, 6, 8))
        right = frozenset((0, 2, 4, 7, 9))
        common = len(left & right)
        self.assertEqual((common + int(common in (1, 3))) % 2, 0)
        self.assertEqual(second.feature_entry(left, right), 0)
        self.assertNotEqual(common - 1, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
