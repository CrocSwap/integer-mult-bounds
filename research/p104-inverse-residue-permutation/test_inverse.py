"""Failure controls for the precise inverse transport and evidence boundary."""

import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import inverse
import verify

HERE = Path(__file__).resolve().parent


class InverseControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basis, cls.predecessor, cls.word = verify.load()

    def test_component_swap_is_not_complex_conjugation(self):
        # Conjugation changes floor(-x/2) at odd signed inputs; S only swaps.
        def conjugate(value):
            return [x if j % 2 == 0 else -x for j, x in enumerate(value)]
        witness = None
        for v in itertools.product(range(-1, 2), repeat=4):
            v = list(v)
            if conjugate(inverse.literal(conjugate(v), 1)) != inverse.literal(v, 1, True):
                witness = v
                break
        self.assertIsNotNone(witness)
        self.assertEqual(inverse.turn(inverse.literal(inverse.turn(witness, 1), 1), 1),
                         inverse.literal(witness, 1, True))

    def test_both_parts_of_turn_are_needed(self):
        def only_swap(v):
            return [v[j ^ 1] for j in range(len(v))]
        def only_reverse(v):
            return [v[j ^ 1] for j in inverse.permutation(2)]
        for mutant in (only_swap, only_reverse):
            found = any(mutant(inverse.literal(mutant(list(v)), 2))
                        != inverse.literal(list(v), 2, True)
                        for v in itertools.product(range(2), repeat=8))
            self.assertTrue(found, "mutation escaped the tiny complete domain")

    def test_forward_box_is_not_the_inverse_box(self):
        # PR3035 rank-two witness, replicated across the five remaining bits.
        z = [0, 0, 0, 0, 1, 1, 1, 3] * 32
        image = inverse.ideal_prefix(z, 7)
        self.assertNotEqual(self.predecessor.canonical(image, self.basis), [0]*256)
        self.assertEqual(inverse.inverse_canonical(image, self.basis,
                                                   self.predecessor.canonical), [0]*256)
        self.assertEqual(inverse.ideal_prefix(image, 7, True), z)

    def test_unchanged_index_does_not_certify_a_basis(self):
        mutant = [row[:] for row in self.basis]
        mutant[0][1] = 1  # Same triangular diagonal/determinant, wrong lattice.
        with self.assertRaisesRegex(ValueError, "prefix parity"):
            self.predecessor.validate_basis(mutant)

    def test_dirty_scratch_and_permutation_are_exact(self):
        for rank in range(8):
            p = inverse.permutation(rank)
            self.assertEqual(sorted(p), list(range(2 << rank)))
            self.assertTrue(all(i != j and p[j] == i for i, j in enumerate(p)))
            value = list(range(2 << rank))
            original = value[:]
            scratch, meter = inverse.turn_inplace(value, rank, -(1 << 4096))
            self.assertEqual(scratch, -(1 << 4096))
            self.assertEqual(value, inverse.turn(original, rank))
            scratch, _ = inverse.turn_inplace(value, rank, scratch)
            self.assertEqual(value, original)
            self.assertEqual(meter['scalar_reads'], 6 * (1 << rank))

    def test_input_domain_and_nonperiod(self):
        for rank in (-1, 8, True, 1.0):
            with self.assertRaises(ValueError):
                inverse.permutation(rank)
        for value in ([0], [0, True], [0, 1 << 8192]):
            with self.assertRaises(ValueError):
                inverse.turn(value, 0)
        with self.assertRaisesRegex(ValueError, "prefix parity"):
            inverse.ideal_prefix([1] + [0]*255, 7)

    def test_zero_and_signed_limit_inverse_split(self):
        for value in ([0]*256, [(1 << 4095)-1, -(1 << 4095)]*128):
            answer, scratch, _ = inverse.inverse_split(value, self.basis,
                                                       self.predecessor.split, 37)
            self.assertEqual(answer, inverse.literal(value, 7, True))
            self.assertEqual(inverse.literal(answer, 7), value)
            self.assertEqual(scratch, 37)

    def test_export_optimized_and_evidence_corruption(self):
        run_root = os.environ.get('IMB_RUN_ROOT')
        with tempfile.TemporaryDirectory(prefix='p104-inverse-', dir=run_root) as temporary:
            destination = Path(temporary) / 'package'
            shutil.copytree(HERE, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
            # No repo/history, cwd is unrelated, no .pyc reads from this export.
            def command():
                return subprocess.run([sys.executable, '-O', '-B',
                                       '-X', 'pycache_prefix=' + str(Path(temporary)/'cache'),
                                       str(destination/'verify.py')],
                                      cwd=temporary, env=environment, capture_output=True,
                                      text=True, encoding='utf-8', timeout=60)
            good = command()
            self.assertEqual(good.returncode, 0, good.stderr)
            receipt_path = destination / 'RESULT.json'
            original = receipt_path.read_bytes()
            receipt = json.loads(original)
            receipt['rank7_one_turn']['cycles'] = 128.0
            receipt_path.write_text(json.dumps(receipt), encoding='utf-8')
            bad = command()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('typed result receipt', bad.stderr)
            receipt_path.write_bytes(original)
            source = destination / 'vendor' / 'lifting.py'
            source.write_bytes(source.read_bytes() + b'\nraise RuntimeError("MUST_NOT_RUN")\n')
            bad = command()
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('source hash: lifting.py', bad.stderr)
            self.assertNotIn('RuntimeError: MUST_NOT_RUN', bad.stderr)


if __name__ == '__main__':
    unittest.main()
