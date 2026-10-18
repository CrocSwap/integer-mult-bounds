#!/usr/bin/env python3
"""Exact oracle comparisons and deliberately bad modular-rank controls."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from kernel import PRIME, screened_rank
import replay

replay.check_sources()
sys.path.insert(0, str(replay.ROOT / "scripts"))
from audit_fused_block import rational_rank


def minor_oracle(matrix):
    """Independent Leibniz determinants of every minor; small inputs only."""
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    for size in range(min(n, m), 0, -1):
        for rows in combinations(range(n), size):
            for cols in combinations(range(m), size):
                determinant = Q(0)
                for perm in permutations(range(size)):
                    inversions = sum(perm[i] > perm[j] for i in range(size)
                                     for j in range(i + 1, size))
                    term = Q((-1) ** inversions)
                    for i, j in enumerate(perm):
                        term *= matrix[rows[i]][cols[j]]
                    determinant += term
                if determinant:
                    return size
    return 0


class KernelTests(unittest.TestCase):
    def test_all_530_binary_square_matrices_through_dimension_three(self):
        count = 0
        for size in (1, 2, 3):
            for entries in product((0, 1), repeat=size * size):
                matrix = [entries[i * size:(i + 1) * size] for i in range(size)]
                expected = minor_oracle(matrix)
                self.assertEqual(screened_rank(matrix, rational_rank), expected)
                self.assertEqual(rational_rank(matrix), expected)
                count += 1
        self.assertEqual(count, 530)

    def test_seed85_rectangular_rational_matrices(self):
        rng = random.Random(85)
        for case in range(240):
            n, m = rng.randrange(1, 13), rng.randrange(1, 13)
            matrix = [[Q(rng.randrange(-303, 304), rng.choice((1, 2, 3, 7, 101, 202)))
                       for _ in range(m)] for _ in range(n)]
            if case % 3 == 0 and n > 1:
                matrix[-1] = list(matrix[0])
            if case % 5 == 0:
                for row in matrix:
                    row[-1] = Q(0)
            before = deepcopy(matrix)
            self.assertEqual(screened_rank(matrix, rational_rank), rational_rank(matrix))
            self.assertEqual(matrix, before)
            if n <= 4 and m <= 4:
                self.assertEqual(screened_rank(matrix, rational_rank), minor_oracle(matrix))

    def test_rank_drop_modulo_prime_must_fall_back(self):
        stats = Counter()
        matrix = [[PRIME, 0], [0, 1]]
        seen = []

        def fallback(arg):
            seen.append(arg)
            return rational_rank(arg)

        self.assertEqual(screened_rank(matrix, fallback, stats), 2)
        self.assertEqual(stats, {"rank_fallback": 1})
        self.assertEqual(len(seen), 1)
        self.assertIs(seen[0], matrix)

    def test_noninvertible_denominator_must_fall_back(self):
        # Replacing denominator 0 mod p by 1 would incorrectly certify rank 2.
        matrix = [[Q(1, PRIME), 1], [1, PRIME]]
        stats = Counter()
        self.assertEqual(screened_rank(matrix, rational_rank, stats), 1)
        self.assertEqual(stats, {"denominator_fallback": 1})

    def test_row_swaps_and_rectangular_full_rank_avoid_fallback(self):
        def forbidden(_):
            self.fail("Full rank should be certified by its nonzero modular minor")

        for matrix, expected in (([[0, 1], [1, 0]], 2),
                                 ([[0, 0, 2], [0, 3, 0]], 2),
                                 ([[0], [0], [Q(1, 3)]], 1)):
            self.assertEqual(screened_rank(matrix, forbidden), expected)

    def test_zero_empty_and_zero_width(self):
        for matrix in ([], (), [[], []], [[0, 0], [0, 0]]):
            self.assertEqual(screened_rank(matrix, rational_rank), 0)

    def test_large_exact_entries_and_fraction_cancellation(self):
        big = 2 ** 1024 + 1
        cases = [[[big, 1], [big + 1, 1]],
                 [[Q(1, big), Q(1, 3)], [3, big]],
                 [[Q(PRIME, PRIME), 0], [0, Q(-2, -2)]],
                 [[Q(1, 2), Q(1, 3)], [3, 2]]]
        for matrix in cases:
            self.assertEqual(screened_rank(matrix, rational_rank), minor_oracle(matrix))

    def test_rejects_nonexact_and_malformed_inputs(self):
        for matrix in ([[1.0]], [["1/2"]], [[True]], [[complex(1, 0)]],
                       [[1], [1, 2]], [1], iter([[1]])):
            with self.assertRaises((TypeError, ValueError)):
                screened_rank(matrix, rational_rank)

    def test_four_wrong_kernels_are_detected(self):
        text = (PACKAGE / "kernel.py").read_text()
        controls = [
            ('record("rank_fallback")\n    return fallback(matrix)',
             'record("rank_fallback")\n    return rank', [[PRIME, 0], [0, 1]]),
            ('denominator = x.denominator % PRIME',
             'denominator = x.denominator % PRIME or 1', [[Q(1, PRIME), 1], [1, PRIME]]),
            ('x.numerator % PRIME * inverses[denominator] % PRIME',
             'x.numerator % PRIME', [[Q(1, 2), Q(1, 3)], [3, 2]]),
            ('coefficient = rows[i][col]', 'coefficient = 0', [[1, 1], [1, 1]]),
        ]
        for old, new, matrix in controls:
            self.assertEqual(text.count(old), 1)
            namespace = {}
            exec(compile(text.replace(old, new), "<negative control>", "exec"), namespace)
            self.assertNotEqual(namespace["screened_rank"](matrix, rational_rank),
                                minor_oracle(matrix))

    def test_fixed_modulus_is_prime(self):
        self.assertEqual(PRIME, 101)
        self.assertTrue(all(PRIME % d for d in range(2, 11)))


class AdmissionTests(unittest.TestCase):
    def test_changed_or_missing_predecessor_is_rejected(self):
        manifest = replay.check_sources()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in manifest["files"]:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(replay.ROOT / name, dest)
            replay.check_sources(root)
            source = root / "scripts/audit_fused_block.py"
            data = source.read_bytes()
            source.write_bytes(data + b"\n# source drift control\n")
            with self.assertRaisesRegex(ValueError, "Source pin mismatch"):
                replay.check_sources(root)
            source.unlink()
            with self.assertRaisesRegex(ValueError, "Source pin mismatch"):
                replay.check_sources(root)

    def test_changed_expected_certificate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            shutil.copyfile(PACKAGE / "SOURCE.json", package / "SOURCE.json")
            (package / "EXPECTED.json").write_text("{}\n")
            with patch.object(replay, "PACKAGE", package):
                with self.assertRaisesRegex(ValueError, "Expected certificate pin mismatch"):
                    replay.check_sources()


if __name__ == "__main__":
    unittest.main(verbosity=2)
