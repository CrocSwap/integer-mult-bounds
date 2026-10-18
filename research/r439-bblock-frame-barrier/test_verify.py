#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Arham Tahir, with substantial OpenAI Codex assistance.
"""Semantic failure controls and a constructive hypothesis-removal example."""
import copy
import importlib.util
import itertools
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('barrier', Path(__file__).with_name('verify.py'))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def determinant(matrix):
    """Small integer determinant, independent of the verifier's elimination."""
    n = len(matrix)
    total = 0
    for perm in itertools.permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        product = -1 if inversions % 2 else 1
        for i, j in enumerate(perm):
            product *= matrix[i][j]
        total += product
    return total


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = v.load_sources()
        cls.original = cls.words['pr589']

    def test_positive_four_words(self):
        report = v.run(self.words)
        self.assertEqual(report['blocked_wire_incidents'], 92)
        self.assertEqual(report['forced_exit_incidents'], 112)

    def test_witnesses_independent_by_integer_gram_determinants(self):
        w = self.original
        for args in v.BLOCKS:
            block = v.prove_block(w, *args)
            for row in block['dependencies']:
                roots = [w['lines'][i] for i in row['required_root_basis']]
                gram = [[sum(x * y for x, y in zip(a, b)) for b in roots] for a in roots]
                self.assertGreater(determinant(gram), 0)

    def test_deleted_cleanup_fails_dirty_restoration(self):
        w = copy.deepcopy(self.words['candidate'])
        w['C'].pop()
        with self.assertRaisesRegex(ValueError, 'literal dirty endpoint'):
            v.literal_endpoint(w)

    def test_changed_block_gate_fails_map(self):
        b = v.prove_block(self.original, *v.BLOCKS[0])
        ops = copy.deepcopy(self.original['B'][102:128])
        ops.pop()
        self.assertNotEqual(v.block_matrix(ops, b['registers'], 506), b['matrix_rows'])

    def test_frame_descent_is_rejected(self):
        w = copy.deepcopy(self.original)
        w['B'][102][0] = 0
        with self.assertRaisesRegex(ValueError, 'non-nested gate frame'):
            v.paths_and_profile(w)

    def test_extra_wire_is_outside_alphabet(self):
        b = v.prove_block(self.original, *v.BLOCKS[0])
        with self.assertRaisesRegex(ValueError, 'block wire alphabet'):
            v.block_matrix([[506, b['registers'][0], [660]]], b['registers'], 506)

    def test_identity_wire_can_be_dropped(self):
        b = v.prove_block(self.original, *v.BLOCKS[0])
        entry = list(self.original['start'])
        for row in b['dependencies']:
            entry[row['register']] = row['entry_frame']
        with self.assertRaisesRegex(ValueError, 'identity wire can be omitted'):
            v.dependency_obligation(self.original, 506, b['registers'], entry,
                                    [1 << i for i in range(len(b['registers']))])

    def test_output_dependencies_are_material(self):
        b = v.prove_block(self.original, *v.BLOCKS[0])
        entry = list(self.original['start'])
        for row in b['dependencies']:
            entry[row['register']] = row['entry_frame']
        i = next(i for i, row in enumerate(b['dependencies']) if row['entry_rank'] < 4
                 and any(b['matrix_rows'][j] >> i & 1 for j in range(len(b['registers'])) if j != i))
        rows = list(b['matrix_rows'])
        rows[i] = 1 << i
        out = v.dependency_obligation(self.original, 506, b['registers'], entry, rows)
        self.assertLess(out[i]['forced_exit_rank'], 4)

    def test_entry_outside_frame_is_rejected(self):
        b = v.prove_block(self.original, *v.BLOCKS[0])
        entry = list(self.original['start'])
        for row in b['dependencies']:
            entry[row['register']] = row['entry_frame']
        entry[b['registers'][0]] = 1  # full rank-eight frame
        with self.assertRaisesRegex(ValueError, 'entry outside block frame'):
            v.dependency_obligation(self.original, 506, b['registers'], entry, b['matrix_rows'])

    def test_unique_source_prefix_checked_by_literal_star(self):
        for frame, a, b in v.BLOCKS:
            if frame not in (508, 509):
                continue
            block = v.prove_block(self.original, frame, a, b)
            proof = block['source_prefix_obstruction']
            regs = block['registers']
            source = proof['source']
            star = [[frame, d, [source]] for d in proof['unique_prefix_donors']]
            p = v.block_matrix(star, regs, frame)
            i = regs.index(source)
            # H=M P, composed explicitly from P's symbolic rows.
            h = []
            for row in block['matrix_rows']:
                value = 0
                for j in range(len(regs)):
                    if row >> j & 1:
                        value ^= p[j]
                h.append(value)
            self.assertEqual(h[i], 1 << i)
            self.assertEqual([row >> i & 1 for row in h], [int(j == i) for j in range(len(regs))])
            # Omitting any required donor leaves a nontrivial residual source.
            for missing in proof['unique_prefix_donors']:
                bad = v.block_matrix([g for g in star if g[1] != missing], regs, frame)
                column = [sum((row >> j & 1) * (bad[j] >> i & 1)
                              for j in range(len(regs))) % 2 for row in block['matrix_rows']]
                self.assertNotEqual(column, [int(j == i) for j in range(len(regs))])

    def test_source_corruption_fails_pin(self):
        with tempfile.TemporaryDirectory(prefix='.pin-control-', dir=v.HERE) as tmp:
            root = Path(tmp)
            for path in v.INPUTS.values():
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(v.ROOT / path, dest)
            path = root / v.INPUTS['pr589']
            path.write_bytes(path.read_bytes() + b'corrupt')
            old = v.ROOT
            try:
                v.ROOT = root
                with self.assertRaisesRegex(ValueError, 'source pin'):
                    v.load_sources()
            finally:
                v.ROOT = old

    def test_same_frame_canceling_pair_preserves_paths(self):
        w = copy.deepcopy(self.original)
        gate = copy.deepcopy(w['B'][102])
        w['B'][102:102] = [copy.deepcopy(gate), copy.deepcopy(gate)]
        self.assertEqual(v.paths_and_profile(w), v.paths_and_profile(self.original))
        b = v.prove_block(self.original, *v.BLOCKS[0])
        self.assertEqual(v.block_matrix(w['B'][102:130], b['registers'], 506), b['matrix_rows'])
        v.literal_endpoint(w)

    def test_hypothesis_removal_constructively_allows_a_gain(self):
        # Two dirty wires enter on S=<e0>. F has rank 4; H has rank 5.
        # The same XOR can occur on S instead of F, retaining the exact map.
        lines = [[int(i == j) for j in range(5)] for i in range(5)]
        w = {'lines': lines, 'frames': [[0], [0, 1, 2, 3], [0, 1, 2, 3, 4]],
             'start': [0, 0], 'final': [2, 2], 'ret': [],
             'D': [], 'A': [], 'B': [[1, 1, [0]]], 'C': []}
        rows = v.block_matrix(w['B'], [0, 1], 1)
        out = v.dependency_obligation(w, 1, [0, 1], [0, 0], rows)
        self.assertEqual([r['forced_exit_rank'] for r in out], [1, 1])
        old_profile = v.paths_and_profile(w)[1]
        self.assertEqual(old_profile, {1: 2, 3: 2})
        lower = copy.deepcopy(w)
        lower['B'][0][0] = 0
        self.assertEqual(v.block_matrix(lower['B'], [0, 1], 0), rows)
        new_profile = v.paths_and_profile(lower)[1]
        self.assertEqual(new_profile, {4: 2})
        # At a=1/2 the common m,W scaling cancels. Square the positive
        # quantities to certify new < old without floating-point roots.
        difference = 2 * new_profile[4] - old_profile[1]
        self.assertGreaterEqual(difference, 0)
        self.assertLess(difference**2, 3 * old_profile[3]**2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
