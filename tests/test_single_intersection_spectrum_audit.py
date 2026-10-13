"""Independent determinant and corruption controls for the spectral audit."""
import json
import sys
import unittest
from hashlib import sha256
from itertools import permutations
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from typing import Sequence
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "single-intersection-spectrum-audit"))

import spectrum_audit
from spectrum_audit import (
    AuditFailure,
    binary_rank,
    binary_square,
    certificate,
    characteristic_polynomial,
    check_spectrum,
    literal_rows,
    main,
    parity_polynomial,
)


def leibniz_polynomial(rows: Sequence[int]) -> int:
    order = len(rows)
    result = 0
    for permutation in permutations(range(order)):
        product = 1
        for row, column in enumerate(permutation):
            entry = (rows[row] >> column) & 1
            if row == column:
                product = (product << 1) ^ (product if entry else 0)
            elif not entry:
                product = 0
                break
        result ^= product
    return result


def kernel_rank(rows: Sequence[int]) -> int:
    kernel_size = sum(all((row & vector).bit_count() % 2 == 0 for row in rows)
                      for vector in range(1 << len(rows)))
    return len(rows) - (kernel_size.bit_length() - 1)


class SpectrumAuditTests(unittest.TestCase):

    def test_every_three_by_three_binary_matrix_against_leibniz_and_kernel(self) -> None:
        for packed in range(1 << 9):
            rows = [(packed >> (3 * row)) & 7 for row in range(3)]
            self.assertEqual(characteristic_polynomial(rows), leibniz_polynomial(rows))
            self.assertEqual(binary_rank(rows), kernel_rank(rows))

    def test_larger_nonsymmetric_matrices_against_leibniz_and_kernel(self) -> None:
        generator = Random(65)
        for order in (4, 5, 6):
            for _ in range(16):
                rows = [generator.randrange(1 << order) for _ in range(order)]
                self.assertEqual(characteristic_polynomial(rows), leibniz_polynomial(rows))
                self.assertEqual(binary_rank(rows), kernel_rank(rows))

    def test_literal_complement_pairs_are_nonsemisimple(self) -> None:
        for k in (2, 3, 4, 5):
            rows = literal_rows(2 * k, k, 0)
            self.assertEqual(characteristic_polynomial(rows), 1 << len(rows))
            self.assertEqual(binary_rank(rows), len(rows) // 2)
            self.assertEqual(binary_square(rows), [0] * len(rows))
            check_spectrum(rows, 0)

    def test_degree_preserving_corruption_escapes_both_trace_checks(self) -> None:
        rows = literal_rows(7, 3, 0)
        mutated = list(rows)
        for left, right in ((0, 32), (1, 28), (0, 1), (28, 32)):
            mutated[left] ^= 1 << right
            mutated[right] ^= 1 << left
        for matrix in (rows, mutated):
            self.assertEqual(sum((row >> index) & 1 for index, row in enumerate(matrix)), 35)
            self.assertEqual(sum(row.bit_count() for row in matrix), 175)
        self.assertEqual([row.bit_count() for row in rows],
                         [row.bit_count() for row in mutated])
        self.assertNotEqual(characteristic_polynomial(rows),
                            characteristic_polynomial(mutated))
        with self.assertRaisesRegex(AuditFailure, "characteristic polynomial"):
            check_spectrum(mutated, 15)

    def test_wrong_spectral_parity_is_rejected(self) -> None:
        rows = literal_rows(7, 3, 0)
        with self.assertRaisesRegex(AuditFailure, "characteristic polynomial"):
            check_spectrum(rows, 16)

    def test_permutation_similarity_and_transpose(self) -> None:
        rows = literal_rows(6, 3, 1)
        permutation = list(reversed(range(len(rows))))
        permuted = [sum(((rows[old_row] >> old_column) & 1) << column
                        for column, old_column in enumerate(permutation))
                    for old_row in permutation]
        transpose = [sum(((rows[row] >> column) & 1) << row
                         for row in range(len(rows))) for column in range(len(rows))]
        for matrix in (permuted, transpose):
            self.assertEqual(characteristic_polynomial(matrix), characteristic_polynomial(rows))
            self.assertEqual(binary_rank(matrix), binary_rank(rows))

    def test_committed_certificate_matches_complete_domain(self) -> None:
        expected = json.loads((ROOT / "research" / "single-intersection-spectrum-audit" /
                               "RESULT.json").read_text())
        self.assertEqual(certificate(), expected)
        self.assertEqual(expected["domain"]["completed_cases"], 41)

    def test_changed_source_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "dependency.py"
            source.write_text("original source\n")
            manifest = {"source_sha256": {"dependency.py": sha256(source.read_bytes()).hexdigest()}}
            (root / "SOURCE.json").write_text(json.dumps(manifest))
            with patch.object(spectrum_audit, "ROOT", root), patch.object(spectrum_audit, "PACKAGE", root):
                self.assertEqual(spectrum_audit.source_pins(), manifest["source_sha256"])
                source.write_text("changed source\n")
                with self.assertRaisesRegex(AuditFailure, "Changed pinned source"):
                    spectrum_audit.source_pins()

    def test_default_command_rejects_changed_result(self) -> None:
        package = ROOT / "research" / "single-intersection-spectrum-audit"
        expected = json.loads((package / "RESULT.json").read_text())
        expected["cases"][0]["characteristic_polynomial_hex"] = "0x41"
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            (temporary / "SOURCE.json").write_bytes((package / "SOURCE.json").read_bytes())
            (temporary / "RESULT.json").write_text(json.dumps(expected))
            with patch.object(spectrum_audit, "PACKAGE", temporary), patch.object(sys, "argv", ["audit"]):
                with self.assertRaisesRegex(AuditFailure, "Committed result"):
                    main()

    def test_matrix_shape_and_spectral_domain_are_checked(self) -> None:
        for rows in ([-1], [2], [True], [0, 4]):
            for check in (binary_rank, binary_square, characteristic_polynomial):
                with self.assertRaises(AuditFailure):
                    check(rows)
        for order, odd in ((-1, 0), (2, 3), (2, -1), (True, 1)):
            with self.assertRaises(AuditFailure):
                parity_polynomial(order, odd)
        for parameters in ((4, 3, 1), (4, 2, 2), (4, 2, -1)):
            with self.assertRaises(AuditFailure):
                literal_rows(*parameters)


if __name__ == "__main__":
    unittest.main()
