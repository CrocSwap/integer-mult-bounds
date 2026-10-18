# SPDX-License-Identifier: Apache-2.0
"""Semantic differential and mutation controls; standard-library unittest."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import types
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


K = load('kernel')
A = load('adapter')
V = load('verify')


def dot_product(left, right, dimension):
    """Independent parity-of-dot-products oracle (no row-selection XOR loop)."""
    columns = [sum(((right[i] >> j) & 1) << i for i in range(dimension))
               for j in range(dimension)]
    return tuple(sum(((row & col).bit_count() % 2) << j for j, col in enumerate(columns))
                 for row in left)


class KernelTests(unittest.TestCase):
    def test_exhaustive_small_actions(self):
        for d in range(1, 5):
            # Every row and every single-bit matrix, plus dense/zero matrices.
            matrices = [tuple(0 for _ in range(d)), tuple((1 << d)-1 for _ in range(d))]
            matrices += [tuple((1 << j) if i == k else 0 for i in range(d))
                         for j in range(d) for k in range(d)]
            for matrix in matrices:
                for row in range(1 << d):
                    self.assertEqual(K.row_action(row, matrix), dot_product((row,), matrix, d)[0])

    def test_seeded_full_width_and_packing(self):
        rng = random.Random(91)
        for _ in range(30):
            matrices = [tuple(rng.randrange(1 << 17) for _ in range(17)) for _ in range(4)]
            pairs, actions, _ = K.prepare(matrices)
            for (a, b), indices in pairs.items():
                ab = dot_product(matrices[a], matrices[b], 17)
                for c in range(4):
                    expected = dot_product(ab, matrices[c], 17)
                    key = sum(row << (17*i) for i, row in enumerate(expected))
                    self.assertEqual(K.product_key(indices, actions[c]), key)

    def test_census_with_collisions_and_degenerate_domains(self):
        ref = A.reference()
        rng = random.Random(91)
        identity = tuple(1 << i for i in range(17))
        examples = [[], [identity], [identity]*4, [(0,)*17]*4,
                    [tuple(rng.randrange(1 << 17) for _ in range(17)) for _ in range(7)]]
        for matrices in examples:
            self.assertEqual(K.relation_census(matrices), ref.relation_census(matrices))
        dense = examples[-1]
        self.assertNotEqual(ref.mul(dense[0], dense[1]), ref.mul(dense[1], dense[0]))
        self.assertEqual(K.relation_census(list(reversed(dense))), ref.relation_census(list(reversed(dense))))

    def test_input_rejection(self):
        for d in (0, 33):
            with self.assertRaises(ValueError): K.prepare([], d)
        for matrix in ((0,)*16, (-1,)+(0,)*16, (1 << 17,)+(0,)*16, (True,)+(0,)*16):
            with self.assertRaises(ValueError): K.prepare([matrix])

    def test_semantic_mutants(self):
        ref = A.reference()
        rng = random.Random(91)
        matrices = [tuple(rng.randrange(1 << 17) for _ in range(17)) for _ in range(4)]
        # Exercise the very differential checker used by verify.py.
        for name, key in [('omit_high_bit', lambda ids, action: K.product_key(ids, action) & ((1 << 288)-1)),
                          ('wrong_row_order', lambda ids, action: K.product_key(tuple(reversed(ids)), action)),
                          ('wrong_stride', lambda ids, action: K.product_key(ids, action, 16))]:
            mutant = types.SimpleNamespace(prepare=K.prepare, product_key=key)
            with self.subTest(name=name), self.assertRaises(ValueError):
                V.compare_products(ref, mutant, matrices)
        def corrupted(m):
            pairs, actions, domain = K.prepare(m)
            actions[2][pairs[0, 1][0]] ^= 1
            return pairs, actions, domain
        with self.assertRaises(ValueError):
            V.compare_products(ref, types.SimpleNamespace(prepare=corrupted, product_key=K.product_key), matrices)

    def test_source_corruption(self):
        # Same-size and same-timestamp drift after successful admission still
        # fails: each call hashes current bytes, with no acceptance cache.
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            original = A.ROOT, A.HERE
            A.ROOT = A.HERE = root = Path(directory)
            source = root / 'input.py'
            source.write_bytes(b'x = 1\n')
            pins = {'files': [{'path': 'input.py', 'usage': 'input',
                               'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]}
            (root / 'SOURCES.json').write_text(json.dumps(pins))
            try:
                A.check_pins()
                before = source.stat()
                source.write_bytes(b'x = 2\n')
                os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
                with self.assertRaisesRegex(ValueError, 'source pin: input.py'):
                    A.check_pins()
                source.write_bytes(b'x = 1\n')
                A.check_pins()
                source.unlink()
                with self.assertRaises(FileNotFoundError): A.check_pins()
            finally:
                A.ROOT, A.HERE = original

    def test_existing_output_refused(self):
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'receipt.json'
            output.write_bytes(b'do not overwrite\n')
            child = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'adapter.py'),
                                    '--output', str(output)], capture_output=True)
            self.assertNotEqual(child.returncode, 0)
            self.assertIn(b'output exists', child.stderr)
            self.assertEqual(output.read_bytes(), b'do not overwrite\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
