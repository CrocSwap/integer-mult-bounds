"""Independent exact controls for the optional determinant-prefix engine.

Run with ``python3 research/gram-prefix-performance/test_kernel.py``.
Small cases use the Leibniz formula, with no elimination or prefix reuse.
Larger controls use the original prime-witness determinant implementation.
"""

import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import types
import unittest

from kernel import PrefixDeterminant


HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "e8-bit-carrier-skeleton/code/pricing/prime_witnesses.py"
SPEC = importlib.util.spec_from_file_location("original_prime_witnesses", REFERENCE)
REFERENCE_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFERENCE_MODULE)
reference_det = REFERENCE_MODULE.det


def permutation_det(matrix):
    """Leibniz determinant with the sign obtained from inversion parity."""
    n = len(matrix)
    total = 0
    for permutation in itertools.permutations(range(n)):
        term = 1
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(n)
            for j in range(i + 1, n)
        )
        total += -term if inversions % 2 else term
    return total


def leading(matrix, dimension):
    return [row[:dimension] for row in matrix[:dimension]]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def positive_gram(matrix):
    dimension = len(matrix[0])
    return [
        [
            sum(row[i] * row[j] for row in matrix) + (i == j)
            for j in range(dimension)
        ]
        for i in range(dimension)
    ]


class PrefixDeterminantTests(unittest.TestCase):
    def setUp(self):
        self.engine = PrefixDeterminant(reference_det)

    def assert_exact(self, matrix, oracle=permutation_det):
        before = [list(row) for row in matrix]
        actual = self.engine(matrix)
        self.assertIs(type(actual), int)
        self.assertEqual(actual, oracle(before), before)
        self.assertEqual([list(row) for row in matrix], before, "input changed")

    def assert_all_prefixes(self, matrix, oracle=permutation_det):
        # The production checker requests the full determinant before its minors.
        self.assert_exact(matrix, oracle)
        dimensions = list(range(1, len(matrix) + 1)) + [0]
        for dimension in dimensions + list(reversed(dimensions)):
            self.assert_exact(leading(matrix, dimension), oracle)

    def test_empty_scalar_and_tuple_inputs(self):
        for matrix in ([], (), [[0]], [[1]], [[-7]], ((3, 2), (4, 5))):
            with self.subTest(matrix=matrix):
                self.assert_exact(matrix)

    def test_rejects_invalid_shapes_and_noninteger_entries(self):
        for matrix in ([[1, 2]], [[1], [2]], [[1, 2], [3]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                self.engine(matrix)
        for entry in (True, 1.0, "1", None):
            with self.subTest(entry=entry), self.assertRaises(TypeError):
                self.engine([[entry]])

    def test_previous_matrix_cache_stays_bounded(self):
        for dimension in (12, 3, 9, 1, 8, 2):
            matrix = [
                [100 + dimension + row if row == column else 0
                 for column in range(dimension)]
                for row in range(dimension)
            ]
            self.assert_exact(matrix, reference_det)
            self.assertLessEqual(self.engine.cache_size, dimension)
            for size in range(1, dimension + 1):
                self.assert_exact(leading(matrix, size), reference_det)
                self.assertLessEqual(self.engine.cache_size, dimension)

    def test_zero_pivot_delegates_to_original(self):
        delegated = []

        def recording_reference(matrix):
            delegated.append([list(row) for row in matrix])
            return reference_det(matrix)

        self.engine = PrefixDeterminant(recording_reference)
        matrix = [[1, 1, 0], [1, 1, 1], [0, 1, 1]]
        self.assert_exact(matrix)
        self.assertIn(matrix, delegated)

    def test_hand_computable_determinants(self):
        controls = (
            ([], 1),
            ([[0, 1], [1, 0]], -1),
            ([[2, 3], [5, 7]], -1),
            ([[2, 1], [1, 3]], 5),
            ([[-2, 1], [1, -3]], 5),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 0),
            ([[0, 1, 0], [0, 0, 1], [1, 0, 0]], 1),
        )
        for matrix, expected in controls:
            with self.subTest(matrix=matrix):
                self.assertEqual(permutation_det(matrix), expected)
                self.assertEqual(self.engine(matrix), expected)

    def test_all_small_binary_matrices(self):
        # Exhaustive inputs include singular, nonsymmetric, and pivot-swap cases.
        for dimension in range(1, 4):
            for entries in itertools.product((0, 1), repeat=dimension**2):
                matrix = [
                    list(entries[row * dimension : (row + 1) * dimension])
                    for row in range(dimension)
                ]
                with self.subTest(dimension=dimension, entries=entries):
                    self.assert_all_prefixes(matrix)

    def test_seed88_small_signed_matrices(self):
        rng = random.Random(88)
        for dimension in range(1, 6):
            for case in range(48):
                matrix = [
                    [rng.randint(-7, 7) for _ in range(dimension)]
                    for _ in range(dimension)
                ]
                with self.subTest(dimension=dimension, case=case):
                    self.assert_all_prefixes(matrix)

    def test_positive_definite_gram_prefixes(self):
        rng = random.Random(88)
        for dimension in range(1, 10):
            for case in range(12):
                basis = [
                    [rng.randint(-4, 4) for _ in range(dimension)]
                    for _ in range(dimension + 2)
                ]
                matrix = positive_gram(basis)
                oracle = permutation_det if dimension <= 5 else reference_det
                with self.subTest(dimension=dimension, case=case):
                    self.assert_all_prefixes(matrix, oracle)
                    for size in range(1, dimension + 1):
                        self.assertGreater(self.engine(leading(matrix, size)), 0)

    def test_negative_pivots_and_indefinite_forms(self):
        matrices = (
            [[-3, 0, 0], [0, -5, 0], [0, 0, -7]],
            [[-3, 2, 1], [2, 5, 4], [1, 4, -2]],
            [[1, 0, 0, 0], [0, -2, 0, 0], [0, 0, 3, 0], [0, 0, 0, -4]],
            [[-2, 4, 1], [3, -7, 5], [2, 0, -9]],
        )
        for matrix in matrices:
            with self.subTest(matrix=matrix):
                self.assert_all_prefixes(matrix)

    def test_zero_leading_minors_with_nonsingular_full_matrix(self):
        matrices = (
            [[0, 2], [3, 4]],
            [[1, 1, 0], [1, 1, 1], [0, 1, 1]],
            [[0, 1, 0], [0, 0, 1], [1, 0, 0]],
            [[1, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0]],
        )
        for matrix in matrices:
            with self.subTest(matrix=matrix):
                self.assertNotEqual(permutation_det(matrix), 0)
                self.assertTrue(
                    any(permutation_det(leading(matrix, k)) == 0
                        for k in range(1, len(matrix)))
                )
                self.assert_all_prefixes(matrix)

    def test_singular_and_repeated_rows(self):
        rng = random.Random(88)
        for dimension in range(2, 10):
            matrix = [
                [rng.randint(-11, 11) for _ in range(dimension)]
                for _ in range(dimension)
            ]
            matrix[-1] = matrix[0][:]
            oracle = permutation_det if dimension <= 5 else reference_det
            with self.subTest(dimension=dimension):
                self.assertEqual(oracle(matrix), 0)
                self.assert_all_prefixes(matrix, oracle)
        shared_row = [2, 3, 5]
        self.assert_all_prefixes([shared_row, shared_row, shared_row])

    def test_integers_beyond_machine_precision(self):
        huge = 2**137 + 2**61 + 17
        matrices = (
            [[huge, huge - 1], [huge + 1, huge]],
            [[huge, 1, 0], [1, -huge, 3], [0, 3, huge + 7]],
            [[0, huge, 1], [huge + 1, 2, 4], [5, 6, -huge]],
        )
        self.assertEqual(permutation_det(matrices[0]), 1)
        for matrix in matrices:
            with self.subTest(matrix=matrix):
                self.assert_all_prefixes(matrix)

    def test_cached_input_is_value_sensitive_and_copied(self):
        matrix = [[4, 1, 2, 0], [1, 5, 3, 1], [2, 3, 7, 2], [0, 1, 2, 6]]
        self.assert_all_prefixes(matrix)
        # Mutate the same nested lists, including both cached and uncached corners.
        for row, column, change in ((0, 0, 2), (0, 1, -5), (3, 3, 7), (2, 0, 3)):
            matrix[row][column] += change
            self.assert_all_prefixes(matrix)
        # A new object with the same value must remain correct after caller edits.
        other = [row[:] for row in matrix]
        self.assert_exact(other)
        matrix[0][0] += 99
        self.assert_all_prefixes(other)
        self.assert_all_prefixes(matrix)

    def test_interleaved_matrices_and_out_of_order_prefixes(self):
        matrices = (
            [[4, 1, 2], [1, 5, 3], [2, 3, 7]],
            [[4, 1, 9], [1, 6, 3], [8, 3, -2]],
            [[0, 1, 2], [1, 0, 3], [2, 3, 0]],
        )
        for size in (3, 1, 2, 0, 3, 2, 1):
            for matrix in matrices:
                self.assert_exact(leading(matrix, size))

    def test_seed88_larger_matrices_against_original(self):
        rng = random.Random(88)
        for dimension in (6, 7, 8, 9, 12, 16):
            for case in range(24):
                matrix = [
                    [rng.randint(-20, 20) for _ in range(dimension)]
                    for _ in range(dimension)
                ]
                with self.subTest(dimension=dimension, case=case):
                    self.assert_all_prefixes(matrix, reference_det)

    def test_determinant_identities_on_larger_matrices(self):
        # These metamorphic controls do not obtain expected values from reference_det.
        rng = random.Random(88)
        for dimension in (6, 9, 12):
            matrix = [
                [rng.randint(-9, 9) for _ in range(dimension)]
                for _ in range(dimension)
            ]
            original = self.engine(matrix)
            self.assertEqual(self.engine(transpose(matrix)), original)
            swapped = [row[:] for row in matrix]
            swapped[0], swapped[-1] = swapped[-1], swapped[0]
            self.assertEqual(self.engine(swapped), -original)
            added = [row[:] for row in matrix]
            added[2] = [a + 7 * b for a, b in zip(added[2], added[0])]
            self.assertEqual(self.engine(added), original)
            scaled = [row[:] for row in matrix]
            scaled[1] = [-3 * entry for entry in scaled[1]]
            self.assertEqual(self.engine(scaled), -3 * original)


def run_mutation_controls():
    """Run the real suite against isolated source mutants; never edit kernel.py."""
    global PrefixDeterminant
    original_engine = PrefixDeterminant
    source = (HERE / "kernel.py").read_text()
    mutations = {
        "wrong_full_determinant_sign": (
            "result = work[-1][-1]",
            "result = -work[-1][-1]",
        ),
        "wrong_cached_leading_minor": (
            "minors.append(pivot)",
            "minors.append(pivot + 1)",
        ),
        "cache_hit_by_shape_only": (
            "cached = self._cache.get(key)",
            "cached = next((value for prior, value in self._cache.items()"
            " if len(prior) == n), None)",
        ),
        "zero_pivot_returns_zero": (
            "result = self.reference_det([list(row) for row in key])",
            "result = 0",
        ),
    }
    outcomes = []
    try:
        for name, replacement in [("baseline", None)] + list(mutations.items()):
            if replacement is None:
                PrefixDeterminant = original_engine
            else:
                before, after = replacement
                if source.count(before) != 1:
                    raise RuntimeError("Mutation anchor changed: " + name)
                mutant = types.ModuleType("kernel_mutant_" + name)
                exec(compile(source.replace(before, after, 1), name, "exec"), mutant.__dict__)
                PrefixDeterminant = mutant.PrefixDeterminant
            result = unittest.TestResult()
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(PrefixDeterminantTests)
            suite.run(result)
            outcome = dict(
                name=name,
                methods_run=result.testsRun,
                assertion_failures=len(result.failures),
                errors=len(result.errors),
                expected_outcome_met=(result.wasSuccessful() if name == "baseline"
                                      else bool(result.failures) and not result.errors),
            )
            outcomes.append(outcome)
            print(json.dumps(outcome, sort_keys=True))
    finally:
        PrefixDeterminant = original_engine
    return all(outcome["expected_outcome_met"] for outcome in outcomes)


if __name__ == "__main__":
    if sys.argv[1:] == ["--mutations"]:
        sys.exit(0 if run_mutation_controls() else 1)
    unittest.main(verbosity=2)
