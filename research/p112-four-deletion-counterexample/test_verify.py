#!/usr/bin/env python3
"""Behavioral controls and separate arithmetic checks for the literal witness."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

import verify

PACKAGE = Path(__file__).resolve().parent


def matrix_label(root: tuple[int, ...]) -> int:
    """Independent rational solve, rather than verify.py's triangular formulas."""
    simple = [
        [1, -1, -1, -1, -1, -1, -1, 1],
        [2, 2, 0, 0, 0, 0, 0, 0],
        [-2, 2, 0, 0, 0, 0, 0, 0],
        [0, -2, 2, 0, 0, 0, 0, 0],
        [0, 0, -2, 2, 0, 0, 0, 0],
        [0, 0, 0, -2, 2, 0, 0, 0],
        [0, 0, 0, 0, -2, 2, 0, 0],
        [0, 0, 0, 0, 0, -2, 2, 0],
    ]
    matrix = [
        [Fraction(simple[j][i]) for j in range(8)] + [Fraction(root[i])]
        for i in range(8)
    ]
    for col in range(8):
        pivot = next(i for i in range(col, 8) if matrix[i][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        divisor = matrix[col][col]
        matrix[col] = [value / divisor for value in matrix[col]]
        for i in range(8):
            if i != col:
                factor = matrix[i][col]
                matrix[i] = [matrix[i][j] - factor * matrix[col][j] for j in range(9)]
    coordinates = [matrix[i][-1] for i in range(8)]
    if any(value.denominator != 1 for value in coordinates):
        raise ValueError("root is not in the simple-root lattice")
    return 256 + sum((int(value) % 2) << i for i, value in enumerate(coordinates))


def low_bit_rank(values: list[int]) -> int:
    """Separate row elimination, with low bits first and no production helpers."""
    rows = list(values)
    rank = 0
    for bit in range(9):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] & (1 << bit)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i] & (1 << bit):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


class WitnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.witness = json.loads(
            (PACKAGE / "WITNESS.json").read_text(encoding="utf-8")
        )

    def test_literal_result(self) -> None:
        report = verify.check(self.witness)
        self.assertEqual(report["Lambda_sizes"], [20, 16])
        self.assertEqual(report["covered_union_size"], 32)
        self.assertEqual(report["independent_direction_count"], 5)
        self.assertEqual(report["minor_determinant"], "-2")
        self.assertEqual(report["minimum_common_deletions"], 12)
        self.assertEqual(
            [len(row["removed_labels"]) for row in report["directions"]],
            [2, 4, 2, 4, 4],
        )
        self.assertEqual(
            [row["next_character_support_size"] for row in report["directions"]],
            [13, 14, 13, 14, 14],
        )

    def test_all_labels_by_rational_coordinate_solve(self) -> None:
        roots = verify.root_lines()
        self.assertEqual(len(roots), 120)
        labels = [matrix_label(root) for root in roots]
        self.assertEqual(len(set(labels)), 120)
        for root in roots:
            self.assertEqual(verify.root_label(root), matrix_label(root))

    def test_binary_rank_on_complete_three_bit_domain(self) -> None:
        for mask in range(256):
            values = [value for value in range(8) if mask & (1 << value)]
            span = {0}
            for value in values:
                span |= {point ^ value for point in span}
            expected = len(span).bit_length() - 1
            self.assertEqual(verify.binary_rank(values), expected)
        self.assertEqual(verify.binary_span((3, 5)), {0, 3, 5, 6})

    def test_minor_by_leibniz_formula(self) -> None:
        rows = [row["vector"] for row in self.witness["directions"]]
        columns = (0, 2, 3, 4, 6)
        total = 0
        for perm in permutations(range(5)):
            inversions = sum(perm[i] > perm[j] for i, j in combinations(range(5), 2))
            term = (-1) ** inversions
            for i in range(5):
                term *= rows[i][columns[perm[i]]]
            total += term
        self.assertEqual(total, -2)
        self.assertEqual(
            verify.determinant([[row[j] for j in columns] for row in rows]), -2
        )

    def test_four_line_cut_by_exhaustive_deletion(self) -> None:
        lines = verify.geometry(self.witness)
        covered, _ = verify.spaces(self.witness, lines)
        row = self.witness["directions"][1]
        residual = sorted(
            label
            for label, root in lines.items()
            if sum(x * y for x, y in zip(root, row["vector"], strict=True))
            and label not in covered
        )
        self.assertEqual(len(residual), 36)
        solutions = []
        for size in range(5):
            for cut in combinations(residual, size):
                remaining = [label for label in residual if label not in cut]
                if low_bit_rank(remaining) <= 7:
                    solutions.append(cut)
        self.assertEqual(solutions, [(317, 319, 381, 383)])

    def test_character_supports_by_xor_code_generation(self) -> None:
        frame = {tuple(root) for root in self.witness["omitted_frame"]}
        lines = {matrix_label(root): root for root in verify.root_lines() - frame}
        covered = set()
        for key in ("V1_basis", "V2_basis"):
            basis = self.witness[key]
            span = set()
            for mask in range(64):
                value = 0
                for j in range(6):
                    if mask & (1 << j):
                        value ^= basis[j]
                span.add(value)
            covered |= set(lines) & span
        actual = verify.check(self.witness)["directions"]
        for index, row in enumerate(self.witness["directions"]):
            residual = sorted(
                label
                for label, root in lines.items()
                if label not in covered
                and sum(root[j] * row["vector"][j] for j in range(8))
            )
            self.assertIn(len(residual), (34, 36))
            code = {0}
            for bit in range(9):
                column = sum(
                    ((label >> bit) & 1) << i for i, label in enumerate(residual)
                )
                code |= {word ^ column for word in code}
            self.assertEqual(len(code), 256)
            nonzero = sorted(code - {0}, key=int.bit_count)
            self.assertEqual(nonzero[1].bit_count(), (13, 14, 13, 14, 14)[index])
            cut = [label for i, label in enumerate(residual) if nonzero[0] & (1 << i)]
            self.assertEqual(cut, actual[index]["removed_labels"])

    def test_p2_control_rejects_four_line_direction(self) -> None:
        self.witness["directions"][1]["remove_labels"] = [317, 319]
        with self.assertRaisesRegex(ValueError, "does not leave rank seven"):
            verify.check(self.witness)

    def test_missing_line_in_two_line_cut(self) -> None:
        self.witness["directions"][0]["remove_labels"].pop()
        with self.assertRaisesRegex(ValueError, "does not leave rank seven"):
            verify.check(self.witness)

    def test_dependent_directions(self) -> None:
        self.witness["directions"][4] = copy.deepcopy(self.witness["directions"][0])
        with self.assertRaisesRegex(ValueError, "directions are dependent"):
            verify.check(self.witness)

    def test_nonorthogonal_frame(self) -> None:
        self.witness["omitted_frame"][0] = [0, 0, 0, 0, 0, 2, 2, 0]
        with self.assertRaisesRegex(ValueError, "nonorthogonal frame"):
            verify.check(self.witness)

    def test_nonroot_frame(self) -> None:
        self.witness["omitted_frame"][0][0] = 1
        with self.assertRaisesRegex(ValueError, "invalid root frame"):
            verify.check(self.witness)

    def test_dimension_five_space(self) -> None:
        self.witness["V1_basis"][5] = self.witness["V1_basis"][0]
        with self.assertRaisesRegex(ValueError, "dimension six"):
            verify.check(self.witness)

    def test_duplicate_deleted_line(self) -> None:
        self.witness["directions"][0]["remove_labels"] = [341, 341]
        with self.assertRaisesRegex(ValueError, "duplicate removed label"):
            verify.check(self.witness)

    def test_boolean_is_not_integer_input(self) -> None:
        self.witness["V1_basis"][0] = True
        with self.assertRaisesRegex(ValueError, "invalid integer"):
            verify.check(self.witness)

    def test_over_budget_cut(self) -> None:
        self.witness["directions"][0]["remove_labels"] = [341, 279, 275, 337, 317]
        with self.assertRaisesRegex(ValueError, "budget is four"):
            verify.check(self.witness)

    def test_cli_normal_and_optimized(self) -> None:
        outputs = []
        for flags in ([], ["-O"]):
            result = subprocess.run(
                [sys.executable, *flags, "-B", str(PACKAGE / "verify.py")],
                capture_output=True,
                text=True,
                check=False,
                timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append(json.loads(result.stdout))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(outputs[0]["minimum_common_deletions"], 12)

    def test_bounded_read_rejects_oversized_input(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p112-limit-") as directory:
            path = Path(directory) / "large.json"
            path.write_bytes(b" " * 32769)
            with self.assertRaisesRegex(ValueError, "exceeds byte limit"):
                verify.read_json(path)

    def test_source_hash_rejects_other_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p112-source-") as directory:
            path = Path(directory) / "wrong-data.txt"
            path.write_text("not the frozen source", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                verify.check_source(path, self.witness)

    def test_cli_rejects_wrong_schema(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p112-control-") as directory:
            path = Path(directory) / "wrong.json"
            path.write_text("{}", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PACKAGE / "verify.py"),
                    "--witness",
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=20,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("wrong schema", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
