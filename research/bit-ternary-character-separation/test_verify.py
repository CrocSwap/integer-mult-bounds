# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Behavioral and independent arithmetic checks for the fixed separation."""

from collections import Counter
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("separation", HERE / "verify.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def oracle_histogram(paid, targets, modulus):
    # Build the image code by repeated vector addition, without dot products.
    columns = tuple(zip(*(paid + targets), strict=True))
    words = {(0,) * 11}
    for column in columns:
        words = {tuple((a + multiplier * b) % modulus
                       for a, b in zip(word, column, strict=True))
                 for word in words for multiplier in range(modulus)}
    if len(words) != modulus**6:
        raise ValueError("independent character image lost rank")
    return Counter(sum(x != 0 for x in word[:8]) - sum(x != 0 for x in word[8:])
                   for word in words)


def determinant_leibniz(rows):
    total = 0
    for permutation in itertools.permutations(range(6)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(6) for j in range(i + 1, 6))
        term = (-1) ** inversions
        for i, j in enumerate(permutation):
            term *= rows[i][j]
        total += term
    return total


def run_cli(package, *options):
    return subprocess.run([sys.executable, "-I", "-B", *options,
                           str(package / "verify.py")],
                          cwd=package.parent, capture_output=True, text=True,
                          timeout=30, check=False)


class SeparationTests(unittest.TestCase):
    def setUp(self):
        self.example = CHECK.read_json(HERE / "EXAMPLE.json")
        self.lattice = CHECK.read_json(HERE / "LATTICE.json")

    def test_literal_result_and_independent_character_oracle(self):
        result = CHECK.verify(self.example, self.lattice)
        self.assertEqual(result["target_determinants"], [5184, 576, 25524])
        expected = ({0: 21, 2: 25, 4: 15, 6: 3},
                    {-2: 2, 0: 59, 1: 88, 2: 198, 3: 170, 4: 124, 5: 72, 6: 14, 7: 2})
        paid = self.lattice["paid_coordinates"]
        targets = self.lattice["target_coordinates"]
        for modulus, key, histogram in zip(
                (2, 3), ("binary", "ternary"), expected, strict=True):
            self.assertEqual(oracle_histogram(paid, targets, modulus), histogram)
            self.assertEqual(result[key]["margin_histogram"],
                             {str(k): v for k, v in histogram.items()})
        self.assertEqual(result["ternary"]["witness"]["target_residues"], [1, 1, 2])
        expected_four = {0: 175, 1: 430, 2: 861, 3: 1120, 4: 921,
                         5: 454, 6: 123, 7: 12}
        self.assertEqual(oracle_histogram(paid, targets, 4), expected_four)
        self.assertEqual(result["order_four"]["margin_histogram"],
                         {str(k): v for k, v in expected_four.items()})

    def test_independent_minors_and_outer_products(self):
        paid = self.example["paid_frames"]
        vectors = ((-3, 3, 3), (5, 5, 1), (3, -1, 2), (-3, -4, 4),
                   (3, -2, 3), (-1, -5, -3), (5, 5, 5))
        for frame, vector in zip(paid[1:], vectors, strict=True):
            self.assertEqual(frame, [[3 * x * y for y in vector] for x in vector])
        indices = (0, 1, 2, 4, 5, 8)
        rows = [tuple(sum(frame, [])[i] for i in indices) for frame in paid]
        minors = [abs(determinant_leibniz(subset))
                  for subset in itertools.combinations(rows, 6)]
        self.assertEqual(len(minors), 28)
        self.assertEqual(min(minors), 3639168)

    def test_field_table_and_rank_boundary(self):
        for a, b in itertools.product(range(4), repeat=2):
            low = (a & 1) * (b & 1) ^ (a >> 1) * (b >> 1)
            high = ((a & 1) * (b >> 1) ^ (a >> 1) * (b & 1)
                    ^ (a >> 1) * (b >> 1))
            self.assertEqual(CHECK.F4[a][b], low | (high << 1))
        self.assertEqual(CHECK.field_controls(), {
            "four_role_projectors": 120, "single_increment_binary_rank": 2,
            "target_difference_binary_rank": 6, "positive_word_orders": 2})

    def test_semantic_certificate_failures(self):
        lattice = copy.deepcopy(self.lattice)
        lattice["basis"][1] = [x // 3 for x in lattice["basis"][1]]
        self.assertTrue(all(x % 3 == 0 for x in self.lattice["basis"][1]))
        for key in ("paid_coordinates", "target_coordinates"):
            for row in lattice[key]:
                row[1] *= 3
        with self.assertRaisesRegex(ValueError, "basis must belong"):
            CHECK.verify(self.example, lattice)
        lattice = copy.deepcopy(self.lattice)
        lattice["target_coordinates"][2][0] += 1
        with self.assertRaisesRegex(ValueError, "coordinate reconstruction"):
            CHECK.verify(self.example, lattice)
        example = copy.deepcopy(self.example)
        example["paid_frames"][0][1][1] = 1
        with self.assertRaisesRegex(ValueError, "paid rational rank one"):
            CHECK.verify(example, self.lattice)
        example = copy.deepcopy(self.example)
        example["target_frames"][0] = [[0] * 3 for _ in range(3)]
        with self.assertRaisesRegex(ValueError, "invertible target"):
            CHECK.verify(example, self.lattice)
        lattice = copy.deepcopy(self.lattice)
        lattice["three_e11_from_other_paid"][0][0] += 1
        with self.assertRaisesRegex(ValueError, "three E11 belongs"):
            CHECK.verify(self.example, lattice)

    def test_boundary_validation(self):
        for value in (True, 1.0, "1", 1 << 65):
            example = copy.deepcopy(self.example)
            example["paid_frames"][0][0][0] = value
            with self.assertRaisesRegex(ValueError, "integer entry capacity"):
                CHECK.verify(example, self.lattice)
        example = copy.deepcopy(self.example)
        example["paid_frames"].pop()
        with self.assertRaisesRegex(ValueError, "fixed paid count"):
            CHECK.verify(example, self.lattice)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                CHECK.read_json(path)
            path.write_bytes(b" " * (CHECK.MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "JSON byte capacity"):
                CHECK.read_json(path)

    def test_relocated_cli_optimized_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            files = sorted(p for p in package.iterdir() if p.is_file())
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            for options in ((), ("-O",)):
                result = run_cli(package, *options)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("cut=1<3", result.stdout)
            self.assertEqual(before, {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
            receipt = package / "RESULT.json"
            for value in (True, 28.0):
                payload = CHECK.read_json(HERE / "RESULT.json")
                payload["independent_six_frame_subsets"] = value
                receipt.write_text(json.dumps(payload, indent=2) + "\n",
                                   encoding="utf-8")
                result = run_cli(package)
                self.assertEqual(result.returncode, 2)
                self.assertIn("receipt differs", result.stderr)
            receipt.unlink()
            self.assertEqual(run_cli(package).returncode, 2)

    def test_actual_implementation_mutants(self):
        changes = (
            ("% modulus", "% 2", "ternary separation"),
            ("sum(x != 0 for x in t)", "sum(x == 1 for x in t)", "ternary separation"),
            ("tuple(range(9))", "tuple(range(8))", "exact formal diagonal endpoint"),
            ("(0, 0, 0, 1, 1, 2, 2, 2)", "(0, 0, 0, 1, 2, 2, 2, 2)",
             "full projected diagonal word"))
        original = (HERE / "verify.py").read_text(encoding="utf-8")
        for old, new, expected in changes:
            with tempfile.TemporaryDirectory() as directory:
                package = Path(directory) / "package"
                shutil.copytree(HERE, package,
                                ignore=shutil.ignore_patterns("__pycache__"))
                self.assertIn(old, original)
                (package / "verify.py").write_text(original.replace(old, new),
                                                 encoding="utf-8")
                result = run_cli(package, "-O")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
