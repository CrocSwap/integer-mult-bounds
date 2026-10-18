#!/usr/bin/env python3
"""Independent completeness, source fixtures, faults, and isolated replay.

Copyright 2026 yssite. Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
import importlib.util
from itertools import product
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gauss_census", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def definition_quadratic(table, n):
    """Definition-only test: the polarization is even and additive in x.

    Symmetry in x,y follows from this table definition. No matrix generator,
    diagonal-lift formula, Walsh routine, or production arithmetic is used.
    """
    for y in range(1 << n):
        on_basis = [(table[(1 << i) ^ y] - table[1 << i] - table[y]) % 4
                    for i in range(n)]
        if any(value % 2 for value in on_basis):
            return False
        for x in range(1 << n):
            if (table[x ^ y] - table[x] - table[y]) % 4 != sum(
                    on_basis[i] for i in range(n) if x >> i & 1) % 4:
                return False
    return True


def elimination_rank(rows):
    """A second rank representation: integer row masks with XOR elimination."""
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


class GaussCensusTests(unittest.TestCase):
    def test_definition_enumeration_through_dimension_three(self):
        for n in range(4):
            actual = {(0,) + values for values in product(range(4), repeat=(1 << n) - 1)
                      if definition_quadratic((0,) + values, n)}
            generated = {audit.quadratic_table(matrix, lift)
                         for matrix in audit.symmetric_matrices(n)
                         for lift in product((0, 1), repeat=n)}
            self.assertEqual(actual, generated)
            self.assertEqual(len(actual), 1 << (n*(n+3)//2))

    def test_full_matrix_enumeration_and_independent_rank(self):
        expected = json.loads((HERE / "EXPECTED.json").read_text())["exhaustive"]
        for n in range(5):
            ranks = Counter()
            # Enumerate ALL n-by-n binary matrices, then filter by symmetry;
            # do not share the upper-triangle enumeration from the checker.
            for values in product(range(1 << n), repeat=n):
                if all((values[i] >> j & 1) == (values[j] >> i & 1)
                       for i in range(n) for j in range(n)):
                    ranks[str(elimination_rank(values))] += 1 << n
            self.assertEqual(dict(ranks), expected[n]["rank_counts"])

    def test_all_signed_hamming_source_fixtures(self):
        # The four V matrices in the pinned tests/test_endpoint_gauge.py.
        cases = 0
        for columns in ((1,), (3, 6), (1, 6, 12), (1, 3, 7)):
            r, ambient = len(columns), max(columns).bit_length()
            gram = tuple(tuple((a & b).bit_count() % 2 for b in columns) for a in columns)
            images = audit.linear_images(gram)
            inverse = {image: x for x, image in enumerate(images)}
            self.assertEqual(len(inverse), 1 << r)
            # Read columns of G^-1 from the exhaustive inverse map. The
            # generator uses big-endian vector indices, hence r-1-j.
            inverse_matrix = tuple(tuple(inverse[1 << (r-1-j)] >> (r-1-i) & 1
                                         for j in range(r)) for i in range(r))
            for signs in product((-1, 1), repeat=ambient):
                values = []
                for z in range(1 << r):
                    coordinate = inverse[z]
                    embedded = 0
                    for j, col in enumerate(columns):
                        if coordinate >> (r-1-j) & 1:
                            embedded ^= col
                    values.append(sum(signs[j] for j in range(ambient) if embedded >> j & 1) % 4)
                lift = tuple((values[1 << (r-1-i)] - inverse_matrix[i][i]) // 2
                             for i in range(r))
                self.assertEqual(audit.quadratic_table(inverse_matrix, lift), tuple(values))
                audit.check_case(inverse_matrix, lift)
                cases += 1
        self.assertEqual(cases, 34)

    def test_mathematical_negative_controls(self):
        self.assertEqual(len(audit.negative_controls()), 11)
        for matrix, lift in ((((1, 0),), (0,)), (((True,),), (0,)), (((1,),), (False,))):
            with self.assertRaises(audit.VerificationError):
                audit.quadratic_table(matrix, lift)

    def test_root_phase_and_singular_support_boundaries(self):
        self.assertEqual(audit.root_phase((1, 0), 0), 0)
        self.assertEqual(audit.root_phase((1, 1), 1), 0)
        self.assertEqual(audit.root_phase((1, -1), 1), 3)
        # A singular form can have S_q=0, or S_q of the wrong magnitude.
        self.assertEqual(audit.walsh((0, 2)), ((0, 0), (2, 0)))
        self.assertEqual(audit.walsh((0, 0)), ((2, 0), (0, 0)))
        for value in ((0, 0), (2, 0)):
            with self.assertRaisesRegex(audit.VerificationError, "fourth-root"):
                audit.root_phase(value, 1)
        self.assertNotEqual(audit.canonical({"count": 1}), audit.canonical({"count": True}))

    def test_optimized_minimal_relocation_and_failed_output_preservation(self):
        with tempfile.TemporaryDirectory(prefix="gauss replay with spaces ") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            package.parent.mkdir()
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for path in audit.SOURCE_PATHS:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parents[1] / path, target)
            output = root / "receipt.json"
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                       "--source-root", str(root), "--output", str(output)]
            # No account credentials, config directories, or network are needed.
            environment = {"PATH": os.defpath}
            result = subprocess.run(command, cwd=root, env=environment, capture_output=True,
                                    text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_SIGNED_GAUSS_CENSUS", result.stdout)
            self.assertEqual(json.loads(output.read_text()), json.loads((HERE / "EXPECTED.json").read_text()))
            before = output.read_bytes()
            # Corrupt an actual proof source: fail before arithmetic or output.
            with (root / audit.SOURCE_PATHS[0]).open("a") as stream:
                stream.write("\nchanged source\n")
            result = subprocess.run(command, cwd=root, env=environment, capture_output=True,
                                    text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source digest mismatch", result.stderr)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
