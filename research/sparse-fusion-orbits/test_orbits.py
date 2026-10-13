#!/usr/bin/env python3
"""Independent finite controls for the source-pinned spectator-orbit screen.

The rank oracle below eliminates rows by increasing column, independently of
the original checker's highest-bit column-basis algorithm. All checks remain
active under python -O; this is finite coverage, not a full theorem proof.
"""
from collections import Counter
from itertools import combinations
import json
from math import comb
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import accelerator


def row_rank(rows, width):
    """Gaussian elimination of packed F2 rows, scanning left to right."""
    rows = list(rows)
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows))
                      if (rows[i] >> column) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if (rows[i] >> column) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def symmetric_rows(bits, h):
    """Build the six-entry symmetric block independently, as matrix rows."""
    rows = [0, 0, 0] + [1 << i for i in range(3, h)]
    entries = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
    for bit, (i, j) in enumerate(entries):
        if (bits >> bit) & 1:
            rows[i] |= 1 << j
            rows[j] |= 1 << i
    return rows


def rank_one_rows(rows, t):
    return [row ^ (t if (t >> i) & 1 else 0)
            for i, row in enumerate(rows)]


def triple_masks(h):
    return [sum(1 << i for i in indices)
            for indices in combinations(range(h), 3)]


def spectator_permutation(t, h):
    """Map selected spectators to 3,...,3+w-1; fix coordinates 0,1,2."""
    selected = [i for i in range(3, h) if (t >> i) & 1]
    remaining = [i for i in range(3, h) if not (t >> i) & 1]
    permutation = list(range(h))
    for old, new in zip(selected, range(3, 3 + len(selected))):
        permutation[old] = new
    for old, new in zip(remaining, range(3 + len(selected), h)):
        permutation[old] = new
    return permutation


def permute_mask(mask, permutation):
    value = 0
    while mask:
        bit = mask & -mask
        value |= 1 << permutation[bit.bit_length() - 1]
        mask ^= bit
    return value


def conjugate_rows(rows, permutation):
    result = [0] * len(rows)
    for old, row in enumerate(rows):
        result[permutation[old]] = permute_mask(row, permutation)
    return result


def independent_unary_totals(orbits, h=25):
    return [sum(weight * row_rank(rank_one_rows(symmetric_rows(bits, h), t), h)
                for t, weight in orbits) for bits in range(64)]


class SpectatorOrbits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = accelerator.load_original(ROOT)
        cls.screens = {}

    def original_screen(self, h):
        if h not in self.screens:
            self.screens[h] = self.original.central_gate_screen(h)
        return self.screens[h]

    def test_independent_row_rank_controls(self):
        self.assertEqual(row_rank([], 3), 0)
        self.assertEqual(row_rank([0, 0, 0], 3), 0)
        self.assertEqual(row_rank([1, 2, 4], 3), 3)
        self.assertEqual(row_rank([3, 5, 6], 3), 2)
        self.assertEqual(row_rank([7, 7, 0], 3), 1)
        self.assertEqual(row_rank([2, 0, 1], 3), 2)

    def test_orbit_partition_and_explicit_conjugation(self):
        for h in (22, 25, 28):
            with self.subTest(h=h):
                representatives = accelerator.orbit_representatives(h)
                actual = dict(representatives)
                self.assertEqual(len(representatives), 8)
                self.assertEqual(len(actual), 8)
                counts = Counter()
                for t in triple_masks(h):
                    low = t & 7
                    w = 3 - low.bit_count()
                    canonical = low | (((1 << w) - 1) << 3)
                    counts[canonical] += 1
                    permutation = spectator_permutation(t, h)
                    self.assertEqual(sorted(permutation), list(range(h)))
                    self.assertEqual(permutation[:3], [0, 1, 2])
                    self.assertEqual(permute_mask(t, permutation), canonical)
                    # These seven matrices span every screened Q over F2.
                    # Checking conjugation for their generators establishes
                    # the mapping for all 64 blocks without a rank oracle.
                    for bits in (0, 1, 2, 4, 8, 16, 32):
                        rows = symmetric_rows(bits, h)
                        self.assertEqual(conjugate_rows(rows, permutation), rows)
                    self.assertEqual(
                        conjugate_rows(rank_one_rows([0] * h, t), permutation),
                        rank_one_rows([0] * h, canonical))
                self.assertEqual(actual, dict(counts))
                self.assertEqual(sum(actual.values()), comb(h, 3))
                self.assertEqual(actual, {
                    low | (((1 << (3 - low.bit_count())) - 1) << 3):
                    comb(h - 3, 3 - low.bit_count())
                    for low in range(8)})

    def test_all_blocks_and_triples_against_independent_rank(self):
        coverage = 0
        for h in (22, 25, 28):
            triples = triple_masks(h)
            representatives = accelerator.orbit_representatives(h)
            canonical_by_low = {t & 7: t for t, _ in representatives}
            for bits in range(64):
                with self.subTest(h=h, bits=bits):
                    rows = symmetric_rows(bits, h)
                    ranks = {t: row_rank(rank_one_rows(rows, t), h)
                             for t, _ in representatives}
                    exhaustive_sum = 0
                    for t in triples:
                        perturbed_rows = rank_one_rows(rows, t)
                        rank = row_rank(perturbed_rows, h)
                        # The matrices are symmetric, so these rows also give
                        # the original column oracle's input representation.
                        self.assertEqual(self.original.binary_rank(perturbed_rows), rank)
                        self.assertEqual(rank, ranks[canonical_by_low[t & 7]],
                                         f'h={h}, block={bits}, triple={t}')
                        exhaustive_sum += rank
                        coverage += 1
                    orbit_sum = sum(weight * ranks[t]
                                    for t, weight in representatives)
                    self.assertEqual(orbit_sum, exhaustive_sum)
        self.assertEqual(coverage, 64 * sum(comb(h, 3) for h in (22, 25, 28)))
        self.assertEqual(coverage, 455424)

    def test_complete_original_and_accelerated_screens(self):
        for h in (22, 25, 28):
            with self.subTest(h=h):
                self.assertEqual(accelerator.accelerated_screen(self.original, h),
                                 self.original_screen(h))

    def screen_trace(self, screen, h):
        trace = []
        original_require = self.original.require

        def recording_require(condition, message):
            trace.append((bool(condition), message))
            original_require(condition, message)

        with patch.object(self.original, 'require', recording_require):
            result = screen(h)
        return result, trace

    def test_original_check_predicates_and_messages_are_retained(self):
        accelerated = lambda h: accelerator.accelerated_screen(self.original, h)
        for h in (22, 25, 28):
            with self.subTest(h=h):
                expected, original_trace = self.screen_trace(
                    self.original.central_gate_screen, h)
                result, accelerated_trace = self.screen_trace(accelerated, h)
                self.assertEqual(result, expected)
                self.assertEqual(accelerated_trace, original_trace)
                self.assertEqual(len(original_trace), 8256)
                self.assertTrue(all(condition for condition, _ in original_trace))
        for screen in (self.original.central_gate_screen, accelerated):
            with self.assertRaisesRegex(ValueError, 'Use the admissible complex family'):
                screen(21)

    def failure_trace(self, screen, rank_kernel):
        trace = []
        original_require = self.original.require

        def recording_require(condition, message):
            trace.append((bool(condition), message))
            original_require(condition, message)

        with patch.object(self.original, 'require', recording_require), \
                patch.object(self.original, 'binary_rank', rank_kernel):
            with self.assertRaises(ValueError) as raised:
                screen(25)
        self.assertFalse(trace[-1][0])
        return str(raised.exception), trace

    def test_faulty_rank_kernels_fail_original_and_accelerated_checks(self):
        rank = self.original.binary_rank
        accelerated = lambda h: accelerator.accelerated_screen(self.original, h)
        for name, kernel, message in (
                ('zero', lambda columns: 0, 'Joint central-frame bound failed'),
                ('deficient', lambda columns: max(0, rank(columns) - 1),
                 'Central-frame lower bound failed')):
            with self.subTest(kernel=name):
                expected = self.failure_trace(self.original.central_gate_screen, kernel)
                result = self.failure_trace(accelerated, kernel)
                self.assertEqual(result, expected)
                self.assertEqual(result[0], message)

    def test_unmodified_complete_certificate(self):
        original_certificate = self.original.certificate()
        committed = json.loads((ROOT / 'certificates/sparse-fusion-audit.json').read_text())
        self.assertEqual(self.original.serializable(original_certificate), committed)
        with patch.object(self.original, 'central_gate_screen',
                          side_effect=lambda h=25:
                          accelerator.accelerated_screen(self.original, h)):
            accelerated_certificate = self.original.certificate()
        self.assertEqual(accelerated_certificate, original_certificate)

    def assert_faulty_reduction_detected(self, representatives):
        canonical = accelerator.orbit_representatives(25)
        self.assertNotEqual(independent_unary_totals(representatives),
                            independent_unary_totals(canonical),
                            'The negative control did not change any unary rank total')
        expected = self.original_screen(25)
        with patch.object(accelerator, 'orbit_representatives',
                          return_value=representatives):
            try:
                result = accelerator.accelerated_screen(self.original, 25)
            except ValueError:
                # A mathematical/coverage check may reject the corruption
                # before producing a receipt; other exceptions are failures.
                return
        self.assertNotEqual(result, expected,
                            'A faulty orbit reduction preserved the full receipt')

    def test_wrong_weight_control(self):
        representatives = list(accelerator.orbit_representatives(25))
        t, weight = representatives[0]
        representatives[0] = (t, weight + 1)
        self.assert_faulty_reduction_detected(representatives)

    def test_omitted_orbit_control(self):
        representatives = list(accelerator.orbit_representatives(25))
        self.assert_faulty_reduction_detected(representatives[1:])

    def test_wrong_representative_control(self):
        representatives = list(accelerator.orbit_representatives(25))
        t, weight = representatives[0]
        # Change an all-spectator triple to a different low-coordinate orbit
        # while retaining its multiplicity and a genuine weight-three mask.
        representatives[0] = (7, weight)
        self.assertNotEqual(t & 7, representatives[0][0] & 7)
        self.assert_faulty_reduction_detected(representatives)

    def test_retained_minima_do_not_replace_independent_unary_checks(self):
        canonical = accelerator.orbit_representatives(25)
        representatives = list(canonical)
        _, weight = representatives[0]
        representatives[0] = (1 | (1 << 3) | (1 << 4), weight)
        self.assertNotEqual(independent_unary_totals(representatives),
                            independent_unary_totals(canonical))
        with patch.object(accelerator, 'orbit_representatives',
                          return_value=representatives):
            result = accelerator.accelerated_screen(self.original, 25)
        # This real corruption changes individual frames but not the final
        # sampled minima. Receipt equality alone would miss the error.
        self.assertEqual(result, self.original_screen(25))

    def test_source_and_certificate_pins_reject_corruption(self):
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
        for changed in ('scripts/audit_sparse_fusion.py',
                        'certificates/sparse-fusion-audit.json'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for relative in manifest['files']:
                    destination = root / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / relative, destination)
                target = root / changed
                target.write_bytes(target.read_bytes() + b'\n# pin corruption control\n')
                with self.assertRaisesRegex(ValueError, 'Source pin mismatch: '):
                    accelerator.load_original(root)


if __name__ == '__main__':
    unittest.main()
