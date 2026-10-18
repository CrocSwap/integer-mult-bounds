#!/usr/bin/env python3
"""Independent oracles and corruption controls. Hanson Sun / OpenAI Codex, Apache-2.0."""
import copy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pr485_reconciliation', HERE/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def rational_basis(rows):
    """Test oracle: ordinary Fraction Gauss-Jordan, separate from integer echelon."""
    matrix = [list(map(Q, row)) for row in rows]
    pivot_row = 0
    for column in range(8):
        pivot = next((i for i in range(pivot_row, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        coefficient = matrix[pivot_row][column]
        matrix[pivot_row] = [x/coefficient for x in matrix[pivot_row]]
        for i in range(len(matrix)):
            if i != pivot_row:
                factor = matrix[i][column]
                matrix[i] = [x-factor*y for x, y in zip(matrix[i], matrix[pivot_row])]
        pivot_row += 1
    return matrix[:pivot_row]


class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = V.ROOT/V.ARCHIVE
        cls.word = V.read_json(cls.archive/'local/baseline112/WORD.json')
        cls.local = V.local_replay(cls.word)
        cls.selection = V.read_json(cls.archive/'pricing/baseline112/SELECTION.json')
        cls.price = V.read_json(cls.archive/'pricing/baseline112/RESULT.json')

    def test_committed_receipt(self):
        # JSON round trip gives integer-key dictionaries their external shape.
        actual = V.json.loads(V.json.dumps(V.reconcile()))
        self.assertEqual(actual, V.read_json(HERE/'EXPECTED.json'))

    def test_all_frame_spaces_with_fraction_oracle(self):
        unique = {}
        for tag in ('baseline112', 'promoted-0'):
            word = V.read_json(self.archive/'local'/tag/'WORD.json')
            lines = word['lines']
            dims, masks = V.frame_geometry(tuple(map(tuple, lines)), tuple(map(tuple, word['frames'])))
            for frame, dim, mask in zip(word['frames'], dims, masks):
                key = tuple(frame)
                if key not in unique:
                    basis = rational_basis([lines[i] for i in frame])
                    oracle_mask = 0
                    for i, line in enumerate(lines):
                        residual = list(map(Q, line))
                        for row in basis:
                            pivot = next(j for j, x in enumerate(row) if x)
                            factor = residual[pivot]
                            residual = [x-factor*y for x, y in zip(residual, row)]
                        if not any(residual):
                            oracle_mask |= 1 << i
                    unique[key] = (len(basis), oracle_mask)
                self.assertEqual((dim, mask), unique[key])
        self.assertEqual(len(unique), 964)

    def test_binomial_bounds_against_exact_square_roots(self):
        for base in (Q(1), Q(3, 2), Q(2), Q(78)):
            lo, hi = V.power_bounds(base, Q(1, 2))
            self.assertLessEqual(lo*lo, base)
            self.assertGreaterEqual(hi*hi, base)
            self.assertLess(hi-lo, Q(1, 10**30))

    def test_binomial_bounds_against_exact_cube_roots(self):
        for base in (Q(1), Q(13, 8), Q(2), Q(78)):
            lo, hi = V.power_bounds(base, Q(1, 3))
            self.assertLessEqual(lo**3, base)
            self.assertGreaterEqual(hi**3, base)

    def test_source_byte_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/'input.json'
            path.write_bytes(b'{}')
            manifest = {'files': {'input.json': sha256(b'{}').hexdigest()}}
            V.check_sources(root, manifest)
            path.write_bytes(b'{ }')
            with self.assertRaisesRegex(ValueError, 'source bytes changed'):
                V.check_sources(root, manifest)

    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'missing or escaped'):
                V.check_sources(Path(directory), {'files': {'missing': '0'*64}})

    def test_scalar_corruption(self):
        word = copy.deepcopy(self.word)
        word['C'][-1][2] = []
        with self.assertRaisesRegex(ValueError, 'scalar map'):
            V.local_replay(word)

    def test_non_nested_frame(self):
        word = copy.deepcopy(self.word)
        word['A'].insert(0, [0, 240, [0]])
        with self.assertRaisesRegex(ValueError, 'non-nested'):
            V.local_replay(word)

    def test_empty_visit_preserves_scalar_but_changes_price(self):
        word = copy.deepcopy(self.word)
        dims, masks = V.frame_geometry(tuple(map(tuple, word['lines'])), tuple(map(tuple, word['frames'])))
        current = list(word['start'])
        changed = False
        for phase in ('D', 'A', 'B', 'C'):
            for index, (frame, destination, sources) in enumerate(word[phase]):
                old = current[destination]
                delta = dims[frame]-dims[old]
                if destination >= 240 and delta >= 2:
                    root = next(i for i in word['frames'][frame] if not (masks[old] >> i & 1))
                    word['frames'].append(word['frames'][old]+[root])
                    word[phase].insert(index, [len(word['frames'])-1, destination, []])
                    changed = True
                    break
                for register in [destination]+sources:
                    current[register] = frame
            if changed:
                break
        self.assertTrue(changed)
        replay = V.local_replay(word)
        self.assertEqual(replay['columns'], 955)
        self.assertEqual(replay['additions'], self.local['additions'])
        self.assertEqual(sum(r*n for r, n in replay['profile'].items()),
                         sum(r*n for r, n in self.local['profile'].items()))
        self.assertEqual(sum(replay['profile'].values()), sum(self.local['profile'].values())+1)
        with self.assertRaisesRegex(ValueError, 'aggregate profile differs'):
            V.check_price(replay, self.selection, self.price)

    def test_stage_swap_preserves_totals_but_breaks_window(self):
        selection = copy.deepcopy(self.selection)
        rows = selection['bit']['stages']
        first = next(x for x in rows if x[:3] == [0, 7, 0])
        second = next(x for x in rows if x[:3] == [1, 7, 2])
        self.assertEqual(first[3], second[3])
        first[2], second[2] = second[2], first[2]
        with self.assertRaisesRegex(ValueError, 'outside idle window'):
            V.aggregate(self.local, selection, 21)

    def test_pattern_capacity(self):
        selection = copy.deepcopy(self.selection)
        selection['bit']['patterns'][0][1].append(8)
        with self.assertRaisesRegex(ValueError, 'exceeds capacity'):
            V.aggregate(self.local, selection, 21)

    def test_pattern_copy_conservation(self):
        selection = copy.deepcopy(self.selection)
        selection['bit']['patterns'][0][2] += 1
        with self.assertRaisesRegex(ValueError, 'copy conservation'):
            V.aggregate(self.local, selection, 21)

    def test_stage_conservation(self):
        selection = copy.deepcopy(self.selection)
        selection['bit']['stages'][0][3] -= 1
        with self.assertRaisesRegex(ValueError, 'pattern/width conservation'):
            V.aggregate(self.local, selection, 21)

    def test_duplicate_rows(self):
        for key in ('patterns', 'stages'):
            selection = copy.deepcopy(self.selection)
            selection['bit'][key].append(selection['bit'][key][0])
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                V.aggregate(self.local, selection, 21)

    def test_nonpositive_counts_and_boolean_replicas(self):
        for count in (0, -1, True):
            selection = copy.deepcopy(self.selection)
            selection['bit']['patterns'][0][2] = count
            with self.assertRaises(ValueError):
                V.aggregate(self.local, selection, 21)
        with self.assertRaisesRegex(ValueError, 'replica count'):
            V.aggregate(self.local, self.selection, True)

    def test_endpoint_adjacent_shift(self):
        price = copy.deepcopy(self.price)
        price['bit_lower'] = self.price['bit_upper']
        price['bit_upper'] = str(Q(self.price['bit_upper'])+Q(1, 10**24))
        with self.assertRaisesRegex(ValueError, 'endpoint signs'):
            V.check_price(self.local, self.selection, price)

    def test_fallback_charge_is_material(self):
        paid = V.aggregate(self.local, self.selection, 21)
        upper = Q(self.price['bit_upper'])
        charged = V.moment_bounds(paid, 21, upper)
        free = V.moment_bounds(paid, 21, upper, fallback=False)
        self.assertGreater(charged[0], 1)
        self.assertLess(free[1], 1)

    def test_reject_corrupt_reported_profile(self):
        price = copy.deepcopy(self.price)
        price['profile']['1'] += 1
        with self.assertRaisesRegex(ValueError, 'aggregate profile differs'):
            V.check_price(self.local, self.selection, price)

    def test_promotion_log_to_word_binding(self):
        original = V.read_json(self.archive/'PR485-KERNEL-SELECTION.json')
        selection = V.read_json(self.archive/'local/promoted-0/SELECTION.json')
        word = V.read_json(self.archive/'local/promoted-0/WORD.json')
        row = V.read_json(self.archive/'local/promoted-0/RESULT.json')
        result = V.selection_provenance(original, selection, word, row)
        self.assertEqual(result['entrance_rank'], 119)
        selection['moves'].pop()
        with self.assertRaisesRegex(ValueError, 'promotion log/selection mismatch'):
            V.selection_provenance(original, selection, word, row)

    def test_unrecorded_entrance_rejected(self):
        original = V.read_json(self.archive/'PR485-KERNEL-SELECTION.json')
        selection = V.read_json(self.archive/'local/baseline112/SELECTION.json')
        row = V.read_json(self.archive/'local/baseline112/RESULT.json')
        word = copy.deepcopy(self.word)
        pivot = original[0][1]
        word['start'][pivot] = 0
        with self.assertRaisesRegex(ValueError, 'selected entrance/word mismatch'):
            V.selection_provenance(original, selection, word, row)


if __name__ == '__main__':
    unittest.main(verbosity=2)
