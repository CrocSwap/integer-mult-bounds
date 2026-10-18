"""Behavior checks and deliberate corruptions for the independent anti-Fano audit."""
# Copyright 2026 Nick Petalas
import copy
import hashlib
import itertools
import json
import unittest

import verify


class SubspaceAuditTests(unittest.TestCase):
    """Exercise exact results, independent oracles and meaningful failure paths."""

    @classmethod
    def setUpClass(cls) -> None:
        """Compute the complete fixed audit once for these read-only tests."""
        cls.config = verify.load_configuration((verify.PACKAGE / "CONFIGURATION.json").read_bytes())
        cls.report = verify.audit(cls.config)

    def test_exact_full_receipt(self) -> None:
        """Match the full receipt and every vendored source digest."""
        expected = json.loads((verify.PACKAGE / "EXPECTED.json").read_bytes())
        verify.compare_report(self.report, expected)
        self.assertEqual(self.report["upper_ranks"], [4, 4, 4])
        self.assertEqual([b["completions"] for b in self.report["blocks"]], [1, 1, 1])
        sources = json.loads((verify.PACKAGE / "SOURCES.json").read_bytes())
        for source in sources["vendored_files"]:
            payload = (verify.PACKAGE / source["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), source["sha256"])

    def test_rank_against_dense_exhaustive_oracle(self) -> None:
        """Match dense elimination on every three-by-four binary matrix."""
        # Every 3x4 binary matrix, using a separate dense Gauss-Jordan oracle.
        for encoded in range(4096):
            rows = [(encoded >> (4 * i)) & 15 for i in range(3)]
            matrix = [[(row >> j) & 1 for j in range(4)] for row in rows]
            rank = 0
            for column in range(4):
                pivot = next((i for i in range(rank, 3) if matrix[i][column]), None)
                if pivot is None:
                    continue
                matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
                for i in range(3):
                    if i != rank and matrix[i][column]:
                        matrix[i] = [x ^ y for x, y in zip(matrix[i], matrix[rank], strict=True)]
                rank += 1
            self.assertEqual(verify.binary_rank(rows), rank)

    def test_census_counts_multiple_and_zero_completions(self) -> None:
        """Compare completion counts with brute force on small affine alphabets."""
        # First three columns have a variable upper-triangular 3x3 minor.
        options = ((15, 1, (1,)), (14, 2, (2, 3)), (12, 4, (4, 5, 6, 7)),
                   (8, 0, tuple(range(8))))
        trials, count, _ = verify.column_census(options, (0, 1, 2))
        brute = sum(verify.binary_rank(list(columns)) == 3
                    for columns in itertools.product(*(o[2] for o in options)))
        self.assertEqual((trials, count, brute), (8, 64, 64))
        impossible = (*options[:3], (15, 8, (8,)))
        self.assertEqual(verify.column_census(impossible, (0, 1, 2)), (8, 0, None))

    def test_invalid_upper_witnesses_reject(self) -> None:
        """Reject wrong diagonals, forbidden entries and a cost-twenty-four witness."""
        good = self.report["upper_rows"]
        missing = good.copy()
        missing[0] ^= 1
        forbidden = good.copy()
        forbidden[0] |= 1 << 1
        for bad in (missing, forbidden, [1 << t for t in range(12)]):
            with self.subTest(rows=bad), self.assertRaises(ValueError):
                verify.validate_upper(self.config, bad)

    def test_receipt_corruptions_reject(self) -> None:
        """Reject truncated counts, false uniqueness and false mathematical claims."""
        mutations = []
        for key, value in (("column_trials", 262143), ("completions", 0)):
            bad = copy.deepcopy(self.report)
            bad["blocks"][0][key] = value
            mutations.append(bad)
        bad = copy.deepcopy(self.report)
        bad["blocks"][1]["unique_columns"][0] ^= 1
        mutations.append(bad)
        bad = copy.deepcopy(self.report)
        bad["lower_bound"] = 13
        mutations.append(bad)
        for bad in mutations:
            with self.subTest(receipt=bad), self.assertRaisesRegex(ValueError, "receipt mismatch"):
                verify.compare_report(self.report, bad)

    def test_full_pattern_is_not_a_cost_twelve_claim(self) -> None:
        """Confirm that some admissible matrices cost twenty-four, not twelve."""
        allowed = verify.incidence(self.config)
        rows = [(1 << t) | sum(1 << s for s in range(12) if allowed[t][s])
                for t in range(12)]
        self.assertEqual(verify.block_ranks(self.config, rows), [8, 8, 8])

    def test_capacity_failures(self) -> None:
        """Reject rank, configuration and census requests outside fixed capacities."""
        for vectors in ([4096], [0] * 13):
            with self.subTest(vectors=vectors), self.assertRaisesRegex(ValueError, "rank capacity"):
                verify.binary_rank(vectors)
        with self.assertRaisesRegex(ValueError, "configuration capacity"):
            verify.load_configuration(b" " * 4097)
        with self.assertRaisesRegex(ValueError, "census shape"):
            verify.column_census((), (0, 1, 2))
        options = ((15, 1, (1,)), (15, 2, (2,)), (15, 4, (4,)))
        with self.assertRaisesRegex(ValueError, "census shape"):
            verify.column_census(options, (0, 1, 2, 2))
        with self.assertRaisesRegex(ValueError, "row census shape"):
            verify.row_census(self.config, tuple(range(8)), (0, 1, 2, 2))

    def test_configuration_pin_rejects_semantic_mutation(self) -> None:
        """Reject a changed source vector before the audit runs."""
        bad = copy.deepcopy(self.config)
        bad[0][1][0] = 1
        with self.assertRaisesRegex(ValueError, "configuration pin"):
            verify.load_configuration(json.dumps(bad).encode())

    def test_exchange_rejects_wrong_class_space(self) -> None:
        """Reject a proposed completion that violates the projection premises."""
        block = self.report["blocks"][0]
        values = block["unique_columns"].copy()
        values[0] ^= 1 << block["zero_rows"][0]
        with self.assertRaises(ValueError):
            verify.exchange_properties(self.config, 0, block["columns"], values)

    def test_dependent_census_basis_rejects(self) -> None:
        """Reject dependent basis choices instead of counting a smaller space twice."""
        options = ((15, 1, (1,)), (15, 1, (1,)), (15, 4, (4,)))
        with self.assertRaisesRegex(ValueError, "basis is not independent"):
            verify.column_census(options, (0, 1, 2))


if __name__ == "__main__":
    unittest.main()
