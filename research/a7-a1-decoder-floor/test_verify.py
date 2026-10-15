#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Focused exact and clean-export controls for the A7+A1 certificate."""
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
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("a7_checker", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def dense_rank(rows, width):
    """Separate low-pivot Boolean-matrix elimination oracle."""
    matrix = [[(row >> j) & 1 for j in range(width)] for row in rows]
    pivot = 0
    for column in range(width):
        found = next((i for i in range(pivot, len(matrix)) if matrix[i][column]), None)
        if found is None:
            continue
        matrix[pivot], matrix[found] = matrix[found], matrix[pivot]
        for i in range(len(matrix)):
            if i != pivot and matrix[i][column]:
                matrix[i] = [a ^ b for a, b in zip(matrix[i], matrix[pivot])]
        pivot += 1
    return pivot


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = V.model()

    def test_binary_rank_independent_oracle(self):
        for entries in itertools.product(range(8), repeat=3):
            self.assertEqual(V.rank(entries), dense_rank(entries, 3))
        _, pairing, labels, _, _, supports = self.model
        for support in supports:
            selected = list(V.bits(support))
            self.assertEqual(V.rank(labels[i] for i in selected),
                             dense_rank([pairing[i] for i in selected], 120))

    def test_every_complex_shift_is_formally_free(self):
        rr, _, _, _, t16, _ = self.model
        # Exact Gaussian-integer shifts (real,imaginary), no floating arithmetic.
        # Both coordinates of every product entry are checked separately.
        for row_number, shift in ((0, (2, 3)), (13, (-7, 1)), (119, (0, -11))):
            row = rr[row_number]
            real = [4 * (x + shift[0]) for x in row] + [sum(row)]
            imag = [4 * shift[1]] * 8 + [0]
            for j, target in enumerate(rr):
                self.assertEqual(V.dot(real, t16[j]), 32 * V.dot(row, target))
                self.assertEqual(V.dot(imag, t16[j]), 0)
        # Giving A1 the same shift is the plausible incorrect dependency.
        malformed = [4] * 9
        self.assertTrue(any(V.dot(malformed, column) != 0 for column in t16))

    def test_character_corruption_rejects(self):
        rr, _, labels, words, _, _ = self.model
        wrong = words[:]
        wrong[1] = 0
        with self.assertRaisesRegex(ValueError, "dimension|forced"):
            V.compatibility_census(rr, labels, wrong)

    def test_power_profile_extreme_points(self):
        # All sorted integer rank profiles; the written concavity exchange is
        # universal in q, not inferred from sampled floating exponents.
        covered = 0
        for profile in itertools.combinations_with_replacement(range(10), 9):
            if sum(profile) < 72:
                continue
            remaining = list(profile)
            minimum = 1 if min(profile) > 0 else 0
            excess = sum(remaining) - 72
            for i in range(9):
                removed = min(excess, remaining[i] - minimum)
                remaining[i] -= removed
                excess -= removed
            self.assertEqual(excess, 0)
            self.assertEqual(sum(remaining), 72)
            remaining.sort()
            while True:
                interior = [i for i, value in enumerate(remaining) if minimum < value < 9]
                if len(interior) < 2:
                    break
                i, j = interior[0], interior[-1]
                amount = min(remaining[i] - minimum, 9 - remaining[j])
                remaining[i] -= amount
                remaining[j] += amount
                remaining.sort()
            expected = [1, 8] + [9] * 7 if minimum else [0] + [9] * 8
            self.assertEqual(remaining, expected)
            covered += 1
        self.assertEqual(covered, 97)

    def test_readonly_export_and_source_receipt_mutations(self):
        with tempfile.TemporaryDirectory(prefix="a7-a1-export-") as directory:
            root = Path(directory)
            destination = root / "research" / HERE.name
            destination.mkdir(parents=True)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(HERE / name, destination / name)
            manifest = json.loads((HERE / "SOURCES.json").read_text())
            for item in manifest["files"]:
                if item["usage"] == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / item["path"], target)
            command = [sys.executable, "-I", "-O", "-B", str(destination / "verify.py")]
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            good = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(good.returncode, 0, good.stderr)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertIn("PASS_A7_A1_DECODER_FLOOR", good.stdout)
            receipt = destination / "RESULT.json"
            bad = json.loads(receipt.read_text())
            bad["minimum_copy"] = 71
            receipt.write_text(json.dumps(bad))
            rejected = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("stored certificate mismatch", rejected.stderr)
            shutil.copyfile(HERE / "RESULT.json", receipt)
            executable = root / V.SOURCE / "e8lab.py"
            executable.write_text(executable.read_text() + '\nraise RuntimeError("UNTRUSTED_EXECUTED")\n')
            rejected = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("executable source drift", rejected.stderr)
            self.assertNotIn("UNTRUSTED_EXECUTED", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
