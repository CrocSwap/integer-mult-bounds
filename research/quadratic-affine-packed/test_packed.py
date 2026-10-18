"""Independent integer-component controls for the optional packed replay.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. The original family and
rank witness are Douglas Colkitt's research, with its retained Codex disclosure.
"""
from itertools import product
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiments import quadratic_affine as original
from packed import PackedRows, rank_witness


PHASES = ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1))


def encode(coordinates):
    support = lo = hi = 0
    for k, coordinate in enumerate(coordinates):
        if coordinate == (0, 0):
            continue
        phase = PHASES.index(coordinate) - 1
        support |= 1 << k
        lo |= (phase % 2) << k
        hi |= (phase // 2) << k
    return support, lo, hi


def components(v, dimension):
    support, lo, hi = v
    return [PHASES[1 + ((lo >> k) & 1) + 2*((hi >> k) & 1)]
            if (support >> k) & 1 else PHASES[0] for k in range(dimension)]


def scalar_product(v, w, dimension):
    """Literal Hermitian product, with no packed arithmetic or original.inner."""
    real = imag = 0
    for (a, b), (c, d) in zip(components(v, dimension), components(w, dimension)):
        real += a*c + b*d
        imag += a*d - b*c
    return real, imag


def scalar_row(vectors, dimension, index, diagonal=True):
    return sum(1 << j for j, w in enumerate(vectors)
               if (diagonal and j == index) or
               scalar_product(vectors[index], w, dimension) == (0, 0))


class PackedArithmetic(unittest.TestCase):
    def check_vectors(self, vectors, dimension):
        rows = PackedRows(vectors, dimension)
        for index, v in enumerate(vectors):
            real, imag = rows.products(v)
            real_digits = real.to_bytes(len(vectors), 'little')
            imag_digits = imag.to_bytes(len(vectors), 'little')
            expected_row = 0
            for j, w in enumerate(vectors):
                expected = scalar_product(v, w, dimension)
                self.assertEqual((real_digits[j] - dimension, imag_digits[j] - dimension), expected)
                if expected == (0, 0):
                    expected_row |= 1 << j
            self.assertEqual(rows.orthogonality_row(v), expected_row)
            self.assertEqual(rows.central_row(index), expected_row | (1 << index))

    def test_every_three_coordinate_phase_vector(self):
        # All 5^3 vectors, including zero and all support patterns: 15,625
        # independent exact products, a larger class than affine labels.
        vectors = [encode(p) for p in product(PHASES, repeat=3)]
        self.check_vectors(vectors, 3)

    def test_every_small_gaussian_label(self):
        f = original.family(2, True)
        self.check_vectors([original.vector(f, i) for i in range(f['n'])], f['D'])

    def test_signed_extremes_at_maximum_dimension(self):
        vectors = [encode([phase] * 32) for phase in PHASES]
        vectors += [encode([PHASES[1 + (k + shift) % 4] for k in range(32)])
                    for shift in range(4)]
        self.check_vectors(vectors, 32)

    def test_seed_92_all_dimensions(self):
        rng = random.Random(92)
        counts = (1, 7, 8, 9, 31, 32, 33, 63, 64, 65)
        for dimension in range(1, 33):
            count = counts[(dimension + 92) % len(counts)]
            vectors = [encode([rng.choice(PHASES) for _ in range(dimension)])
                       for _ in range(count)]
            with self.subTest(dimension=dimension, count=count):
                self.check_vectors(vectors, dimension)

    def test_compaction_boundary_counts_and_positions(self):
        # Unit query versus either same/disjoint unit support realizes any
        # chosen orthogonality pattern independently of byte compaction.
        query = encode(((1, 0), (0, 0)))
        orthogonal = encode(((0, 0), (1, 0)))
        counts = (1, 2, 3, 7, 8, 9, 15, 16, 17, 31, 32, 33,
                  63, 64, 65, 127, 128, 129, 255, 256, 257)
        for count in counts:
            for selected in ({0}, {count - 1}, set(range(count)),
                             set(range(0, count, 2)), set(range(1, count, 2)), set()):
                columns = [orthogonal if j in selected else query for j in range(count)]
                expected = sum(1 << j for j in selected)
                with self.subTest(count=count, selected=len(selected)):
                    self.assertEqual(PackedRows(columns, 2).orthogonality_row(query), expected)

    def test_all_offset_digit_pairs(self):
        # Independent direct inputs to zero_lanes cover every permitted pair
        # of output digits at the largest D; consecutive lanes cross zero.
        dimension = 32
        digit_pairs = list(product(range(2*dimension + 1), repeat=2))
        rows = PackedRows([(0, 0, 0)] * len(digit_pairs), dimension)
        real = int.from_bytes(bytes(a for a, b in digit_pairs), 'little')
        imag = int.from_bytes(bytes(b for a, b in digit_pairs), 'little')
        expected = sum(1 << j for j, pair in enumerate(digit_pairs)
                       if pair == (dimension, dimension))
        self.assertEqual(rows.zero_lanes(real, imag), expected)

    def test_negative_controls_conjugation_imaginary_diagonal(self):
        v = encode(((1, 0), (0, 1)))
        w = encode(((1, 0), (0, -1)))
        rows = PackedRows([v, w], 2)
        self.assertEqual(scalar_product(v, w, 2), (0, 0))
        self.assertEqual(rows.orthogonality_row(v), 2)
        # Conjugating the query before the Hermitian kernel intentionally
        # computes a bilinear product and must fail the same oracle.
        conjugate_v = (v[0], v[1], v[2] ^ v[1])
        self.assertNotEqual(rows.orthogonality_row(conjugate_v), 2)
        real_unit, imaginary_unit = encode(((1, 0),)), encode(((0, 1),))
        imaginary_rows = PackedRows([imaginary_unit], 1)
        self.assertEqual(imaginary_rows.orthogonality_row(real_unit), 0)
        real, imag = imaginary_rows.products(real_unit)
        self.assertEqual(imaginary_rows.zero_lanes(real, imaginary_rows.offset), 1)
        # Omitting I changes the actual matrix, since norms are nonzero.
        self.assertEqual(rows.central_row(0), 3)
        self.assertNotEqual(rows.central_row(0), rows.orthogonality_row(v))

    def test_negative_control_cross_lane_borrow(self):
        rows = PackedRows([(0, 0, 0)] * 2, 1)
        # Offset-real bytes (1,0), imaginary (1,1) give comparison bytes
        # (0,1). Subtract-one zero-byte detection falsely marks BOTH lanes.
        real, imag = 1, 257
        self.assertEqual(rows.zero_lanes(real, imag), 1)
        different = (real ^ rows.offset) | (imag ^ rows.offset)
        bad_flags = (different - 257) & ~different & (128*257)
        bad_row = sum(((bad_flags >> (8*j + 7)) & 1) << j for j in range(2))
        self.assertEqual(bad_row, 3)
        self.assertNotEqual(bad_row, rows.zero_lanes(real, imag))

    def test_validation_and_input_snapshot(self):
        for dimension in (0, 33, True, 1.0):
            with self.assertRaises(ValueError):
                PackedRows([(1, 0, 0)], dimension)
        for vectors in ([], [(1, 0)], [(-1, 0, 0)], [(True, 0, 0)],
                        [(2, 0, 0)], [(1, 2, 0)], [(0, 0, 1)]):
            with self.assertRaises(ValueError):
                PackedRows(vectors, 1)
        vectors = [[1, 0, 0], [2, 0, 0]]
        rows = PackedRows(vectors, 2)
        vectors[0][0] = 2
        self.assertEqual(rows.central_row(0), 3)
        for index in (-1, 2, True, 0.0):
            with self.assertRaises(ValueError):
                rows.central_row(index)


class RankReplay(unittest.TestCase):
    def test_receipts_and_nonmonotone_orders_match_original(self):
        for phases in (False, True):
            f = original.family(2, phases)
            sample = list(range(f['n']))
            random.Random(92).shuffle(sample)
            vectors = [original.vector(f, i) for i in sample]
            basis, independent = {}, []
            order = list(range(len(sample)))
            random.Random(93).shuffle(order)
            for i in order:
                x = scalar_row(vectors, f['D'], i)
                while x:
                    pivot = x.bit_length() - 1
                    if pivot not in basis:
                        basis[pivot] = x
                        independent.append(i)
                        break
                    x ^= basis[pivot]
            args = dict(t=2, complex_phases=phases, parity=None,
                        sample=sample, independent_rows=independent)
            expected = original.rank_witness(**args)
            self.assertEqual(rank_witness(original, **args), expected)
            args['independent_rows'] = independent[::-1]
            reordered = original.rank_witness(**args)
            self.assertNotEqual(reordered['independent_row_sha256'], expected['independent_row_sha256'])
            self.assertEqual(rank_witness(original, **args), reordered)

    def test_same_rejections_as_original(self):
        valid = dict(t=1, complex_phases=False, parity=None,
                     sample=[0, 1, 2, 3], independent_rows=[0, 2])
        mutations = [dict(sample=x) for x in ([], [0, 0], [-1], [4], [True], [1.0])]
        mutations += [dict(independent_rows=x) for x in
                      ([], [0, 0], [-1], [4], [True], [0.0], [0, 1])]
        mutations += [dict(t=0), dict(t=6), dict(complex_phases=True, parity=0)]
        for mutation in mutations:
            args = dict(valid, **mutation)
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError) as old_error:
                    original.rank_witness(**args)
                with self.assertRaises(ValueError) as new_error:
                    rank_witness(original, **args)
                self.assertEqual(str(old_error.exception), str(new_error.exception))

    def test_receipt_detects_diagonal_mutation(self):
        args = dict(t=1, complex_phases=False, parity=None,
                    sample=[0, 1, 2, 3], independent_rows=[0, 2])
        expected = original.rank_witness(**args)
        with patch.object(PackedRows, 'central_row',
                          lambda self, i: self.orthogonality_row(self.vectors[i])):
            mutated = rank_witness(original, **args)
            with self.assertRaisesRegex(ValueError, 'Packed row differs from original exact row'):
                rank_witness(original, **args, compare_rows=True)
        self.assertEqual(mutated['binary_rank_lower'], expected['binary_rank_lower'])
        self.assertNotEqual(mutated['independent_row_sha256'], expected['independent_row_sha256'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
