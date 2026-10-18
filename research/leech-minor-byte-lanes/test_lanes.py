#!/usr/bin/env python3
"""Exact arithmetic, rejection, source-binding and CLI controls."""
import itertools
import importlib.util
import io
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lanes import lane_rows
import replay


def literal_rows(sample, indices, shift):
    return [sum(1 << j for j, v in enumerate(sample)
                if i == j or sum(a * b for a, b in zip(sample[i], v)) == shift)
            for i in indices]


class LaneArithmetic(unittest.TestCase):
    def test_all_small_signed_vectors(self):
        sample = list(itertools.product(range(-4, 5), repeat=2))
        indices = list(range(len(sample)))
        for shift in range(-32, 33):
            self.assertEqual(lane_rows(sample, indices, shift),
                             literal_rows(sample, indices, shift))

    def test_seeded_signed_leech_vectors(self):
        _, namespace, _ = replay.load('lanes')
        lines = namespace['leech_lines']()
        rng = random.Random(86)
        # All three generator families plus their negatives, then shuffled.
        sample = [lines[i] for start, end in ((0, 552), (552, 49128), (49128, 98280))
                  for i in rng.sample(range(start, end), 32)]
        sample += [tuple(-x for x in v) for v in sample]
        rng.shuffle(sample)
        for shift in (-32, -16, -8, 0, 8, 16, 32):
            self.assertEqual(lane_rows(sample, list(range(192)), shift),
                             literal_rows(sample, list(range(192)), shift))

    def test_byte_boundaries_and_diagonal(self):
        sample = [[4] * 7 + [3], [-4] * 8, [4] * 8, [0] * 8]
        for shift in (-124, -1, 0, 1, 124, 255, -256):
            self.assertEqual(lane_rows(sample, [0, 3], shift),
                             literal_rows(sample, [0, 3], shift))
        self.assertEqual(lane_rows([[4], [-4]], [0, 1], 0), [1, 2])

    def test_mutated_arithmetic_is_detectable(self):
        sample = [[4, 0], [-4, 0], [0, 4], [1, -3]]
        indices = list(range(4))
        expected = literal_rows(sample, indices, -16)
        mutants = {
            'wrong_sign': literal_rows([[abs(x) for x in v] for v in sample], indices, -16),
            'wrong_shift': lane_rows(sample, indices, 0),
            'omitted_diagonal': [row & ~(1 << i) for i, row in enumerate(expected)],
            'reversed_columns': [int(f'{row:04b}'[::-1], 2) for row in expected],
        }
        for name, rows in mutants.items():
            with self.subTest(name=name):
                self.assertNotEqual(expected, rows)
        # Equal rank alone misses this permutation: the ordered stream matters.
        _, namespace, _ = replay.load('lanes')
        rank = namespace['rank_of_rows']
        self.assertEqual(rank(expected), rank(mutants['reversed_columns']))

    def test_lane_admission(self):
        bad = [([], [0], 0), ([[]], [0], 0), ([[5]], [0], 0),
               ([[True]], [0], 0), ([[1], [1, 2]], [0], 0),
               ([[1]], [0, 0], 0), ([[1]], [-1], 0),
               ([[1]], [1], 0), ([[1]], [True], 0),
               ([[1]], [], 0), ([[1]], [0], 0.0),
               ([[4] * 8], [0], 0)]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError):
                lane_rows(*args)


class ReplayControls(unittest.TestCase):
    def test_unchanged_original_tests_in_both_modes(self):
        for mode in ('baseline', 'lanes'):
            _, namespace, _ = replay.load(mode)
            path = replay.ROOT / 'tests/test_affine_vector_screens.py'
            spec = importlib.util.spec_from_file_location('original_tests', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.leech_minor = namespace['leech_minor']
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            log = io.StringIO()
            result = unittest.TextTestRunner(stream=log).run(suite)
            self.assertEqual(result.testsRun, 3)
            self.assertTrue(result.wasSuccessful(), log.getvalue())

    def test_changed_or_incomplete_receipt(self):
        from verify import check_receipt
        result = json.loads((HERE / 'EXPECTED.json').read_text())
        check_receipt(result)
        changed = dict(result, matrix_entries_compared=0)
        with self.assertRaisesRegex(ValueError, 'receipt differs'):
            check_receipt(changed)
        changed = dict(result, cases=result['cases'][:-1])
        with self.assertRaisesRegex(ValueError, 'receipt differs'):
            check_receipt(changed)

    def test_original_admission_and_dependent_rows(self):
        bad = [([0, 0], [0], 0, False), ([0], [0, 0], 0, False),
               ([-1], [0], 0, False), ([196560], [0], 0, True),
               ([0], [0], 3, True), ([0], [0], 8, False),
               ([0, 1], [0, 1], 0, False)]
        for mode in ('baseline', 'lanes'):
            _, namespace, _ = replay.load(mode)
            for args in bad:
                with self.subTest(mode=mode, args=args), self.assertRaises(ValueError):
                    namespace['leech_minor'](*args)

    def test_faulty_kernel_fails_inherited_rank_check(self):
        with patch.object(replay, 'lane_rows', lambda sample, indices, shift: [0] * len(indices)):
            _, namespace, _ = replay.load('lanes')
            with self.assertRaisesRegex(ValueError, 'dependent'):
                namespace['leech_minor']([0, 2], [0, 1])

    def test_source_fixture_and_certificate_corruption(self):
        pins = replay.check_pins()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in pins['files']:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(replay.ROOT / name, target)
            replay.check_pins(root)
            for name in (replay.SOURCE, 'scripts/experiments/affine_vector_witnesses.json',
                         'certificates/affine-vector-screens.json', 'scripts/experiments/single_intersection.py'):
                target = root / name
                original = target.read_bytes()
                target.write_bytes(original + b'\n')
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Pinned file changed'):
                    replay.check_pins(root)
                target.write_bytes(original)
            target.unlink()
            with self.assertRaisesRegex(ValueError, 'Missing'):
                replay.check_pins(root)

    def test_cli_optimization_and_output_preservation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'receipt.json'
            command = [sys.executable, '-I', '-O', '-B', str(HERE / 'replay.py'),
                       '--output', str(output)]
            p = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('Assertions must remain enabled', p.stderr)
            self.assertFalse(output.exists())
            output.write_text('preserve me')
            p = subprocess.run([x for x in command if x != '-O'], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('Output already exists', p.stderr)
            self.assertEqual(output.read_text(), 'preserve me')


if __name__ == '__main__':
    unittest.main()
