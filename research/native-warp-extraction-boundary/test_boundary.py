# SPDX-License-Identifier: Apache-2.0
import copy
import random
import shutil
import tempfile
import unittest
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import algebra as a
import operators as op
import verify as v


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = v.load_words()
        cls.word = cls.words['base']
        cls.matrix = a.replay(cls.word)

    def test_aliasing_can_expand_the_space(self):
        # X1 == X2 changes x1=X1*x1=0, x2=0 into x1+x2=0.
        # An actual positive example prevents assuming the desired negative.
        free = [{0: Q(1)}, {1: Q(1)}]
        grouped = [{0: Q(1), 1: Q(1)}]
        self.assertEqual(len(a.nullspace(grouped, [0, 1])[1]), 1)
        with self.assertRaisesRegex(ValueError, 'larger'):
            a.same_kernel(free, grouped, [0, 1])

    def test_missing_constraint_and_changed_basis_reject(self):
        rows = [{0: Q(1), 1: Q(2)}, {1: Q(1), 2: Q(-3)}]
        free, basis = a.nullspace(rows, range(3))
        a.same_kernel(rows, rows, range(3))
        with self.assertRaises(ValueError):
            a.same_kernel(rows, rows[:1], range(3))
        bad = copy.deepcopy(basis)
        bad[0][0] += 1
        with self.assertRaisesRegex(ValueError, 'null vector'):
            a.check_basis(rows, range(3), free, bad)
        with self.assertRaises(ValueError):
            a.check_basis(rows, range(3), free * 2, basis * 2)

    def test_modular_rank_is_only_a_lower_bound(self):
        rows = [{0: Q(a.PRIME)}]
        self.assertEqual(a.modular_rank(rows, [0])[0], 0)
        self.assertEqual(len(a.nullspace(rows, [0])[1]), 0)
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            a.same_kernel(rows, rows, [0])

    def test_modular_rank_small_exhaustive(self):
        from itertools import product
        for entries in product((-1, 0, 1), repeat=4):
            rows = [{j: Q(entries[2*i+j]) for j in range(2)} for i in range(2)]
            determinant = entries[0]*entries[3] - entries[1]*entries[2]
            rank = 2 if determinant else int(any(entries))
            self.assertEqual(a.modular_rank(rows, range(2))[0], rank)
            self.assertEqual(2-len(a.nullspace(rows, range(2))[1]), rank)

    def test_operator_identity_phase_and_dependence(self):
        identity = [(x, 0) for x in range(512)]
        self.assertEqual(op.monomial(op.IDENTITY), identity)
        _, rows = op.operator_rows([identity, identity])
        self.assertEqual(a.modular_rank(rows, [0, 1])[0], 1)
        original = op.direct_columns
        def bad(columns):
            result = original(columns)
            y, phase = result[7]
            result[7] = (y, (phase+2) % 4)
            return result
        with patch.object(op, 'direct_columns', bad):
            with self.assertRaisesRegex(ValueError, 'phase/column'):
                op.certify(self.word)
        with self.assertRaises(ValueError):
            op.monomial([0] * 9)

    def test_target_feedback_and_non_affine_words_reject(self):
        bad = copy.deepcopy(self.word)
        bad['A'][84] = ['add', 224, 112, 1, 1, []]
        with self.assertRaisesRegex(ValueError, 'target cannot feed'):
            a.replay(bad)
        # A second warp on a lender leaves a genuine two-symbol product.
        # Construct a product explicitly at the same register and adjacent time.
        bad = copy.deepcopy(self.word)
        first = bad['warps'][0]
        bad['warps'].append(list(first))
        with self.assertRaisesRegex(ValueError, 'affine-linear'):
            a.replay(bad)

    def test_compensation_is_part_of_the_right_space(self):
        word = {'helper_final': {}, 'start_extra': {}, 'initial_corrections': [],
                'compensation': [['add', 112, 224, 1, 1, []]]}
        matrix = {224: {(224, 0): Q(1)}}
        right, _, helpers, _ = a.constraints(matrix, word)
        self.assertEqual(helpers, [224])
        self.assertEqual(a.nullspace(right, helpers)[1], [])
        word['compensation'] = []
        self.assertEqual(len(a.nullspace(a.constraints(matrix, word)[0], helpers)[1]), 1)

    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as root:
            package = Path(root) / 'package'
            package.mkdir()
            shutil.copytree(v.PACKAGE / 'inputs', package / 'inputs')
            shutil.copyfile(v.PACKAGE / 'INPUTS.json', package / 'INPUTS.json')
            path = package / 'inputs/base.json.gz'
            path.write_bytes(path.read_bytes() + b'x')
            with self.assertRaisesRegex(ValueError, 'source input digest'):
                v.load_words(package)

    def test_literal_replay_against_independent_vector_interpreter(self):
        # Separate array interpreter: no symbolic row propagation, and genuinely
        # noncommuting two-dimensional matrices substituted for the formal warps.
        p = 65537
        rng = random.Random(84)
        live = sorted(self.matrix)
        initial = {r: [rng.randrange(p), rng.randrange(p)] for r in live}
        rows = copy.deepcopy(initial)
        matrices = {}
        for i in range(1, len(self.word['warps']) + 1):
            while True:
                m = [rng.randrange(p) for _ in range(4)]
                if (m[0]*m[3]-m[1]*m[2]) % p:
                    break
            matrices[i] = m
        def mv(m, x):
            return [(m[0]*x[0]+m[1]*x[1]) % p, (m[2]*x[0]+m[3]*x[1]) % p]
        def scalar(gate):
            if gate[1] not in rows:
                return
            if gate[0] == 'add':
                c = gate[3]*pow(gate[4], -1, p) % p
                rows[gate[1]] = [(x+c*y) % p for x,y in zip(rows[gate[1]],rows[gate[2]])]
            else:
                c = gate[2]*pow(gate[3], -1, p) % p
                rows[gate[1]] = [x*c % p for x in rows[gate[1]]]
        for gate in self.word['A'][84:]:
            scalar(gate)
        warps = defaultdict(list)
        for i, record in enumerate(self.word['warps'], 1):
            warps[record[0]].append((record[1], i))
        for position in range(len(self.word['B'])+1):
            for register, i in warps[position]:
                rows[register] = mv(matrices[i], rows[register])
            if position < len(self.word['B']):
                scalar(self.word['B'][position])
        for gate in self.word['restore']:
            scalar(gate)
        evaluated = {}
        for r, row in self.matrix.items():
            value = [0, 0]
            for (c, operator), q in row.items():
                source = mv(matrices[operator], initial[c]) if operator else initial[c]
                coefficient = q.numerator*pow(q.denominator, -1, p) % p
                value = [(x+coefficient*y) % p for x,y in zip(value,source)]
            evaluated[r] = value
        self.assertEqual(evaluated, rows)
        evaluated[live[0]][0] ^= 1
        self.assertNotEqual(evaluated, rows)


if __name__ == '__main__':
    unittest.main()
