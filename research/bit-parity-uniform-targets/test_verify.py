# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Behavioral controls, including actual CLI and implementation mutants."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import verify

PACKAGE = Path(__file__).resolve().parent


class LatticeTests(unittest.TestCase):
    def test_unsaturated_lattice_is_not_its_rational_span(self):
        basis = verify.lattice_basis([(2, 0) + (0,) * 7, (0, 4) + (0,) * 7])
        self.assertEqual(verify.lattice_coordinates(basis, (1, 0) + (0,) * 7), None)
        self.assertEqual(verify.lattice_coordinates(basis, (2, 8) + (0,) * 7), (1, 2))
        self.assertEqual(verify.lattice_coordinates(basis, (0, 0, 1) + (0,) * 6), None)

    def test_actual_generated_classes(self):
        frames, targets = verify.example()
        result = verify.target_classes(frames, targets)
        self.assertEqual(result["lattice_rank"], 5)
        self.assertEqual(result["target_coordinates"], [[1, 0, 0, 1, 1],
                                                       [1, 0, 2, 1, 1], [1, 2, 0, 1, 1]])
        self.assertEqual(result["target_classes"], [[1, 0, 0, 1, 1]] * 3)
        even_frames = tuple(verify.scale_frame(a, Fraction(1, 2)) for a in frames for _ in range(2))
        self.assertEqual(verify.target_classes(even_frames, targets)["target_classes"], [[0] * 5] * 3)

    def test_projection_can_kill_the_common_class(self):
        frames, targets = verify.example()
        projected = tuple(tuple(a[1] if i == 0 else Fraction(0) for i in range(9)) for a in frames)
        projected_targets = tuple(tuple(a[1] if i == 0 else Fraction(0) for i in range(9))
                                  for a in targets)
        result = verify.target_classes(projected, projected_targets)
        self.assertEqual(result["lattice_rank"], 1)
        self.assertEqual(result["target_classes"], [[0], [0], [0]])
        self.assertTrue(result["uniform"])

    def test_capacity_and_outside_target_fail(self):
        frames, targets = verify.example()
        with self.assertRaisesRegex(ValueError, "target outside generated lattice"):
            verify.target_classes(frames, (verify.unit(2, 1), targets[1], targets[2]))
        with self.assertRaisesRegex(ValueError, "frame capacity"):
            verify.target_classes(frames * 3, targets)
        with self.assertRaisesRegex(ValueError, "exact rational"):
            verify.target_classes(((0,) * 9,), targets)
        with self.assertRaisesRegex(ValueError, "integer capacity"):
            verify.lattice_basis([((1 << 4096),) + (0,) * 8])

    def test_noncommuting_targets_and_literal_endpoint(self):
        frames, targets = verify.example()
        expected_targets = ((1, 0, 0, 0, 1, 0, 0, 0, 1),
                            (1, 0, 0, 4, 1, 0, 0, 0, 1),
                            (1, 4, 0, 0, 1, 0, 0, 0, 1))
        self.assertEqual(targets, expected_targets)
        word = tuple((a, tuple((1 << (i // 3)) if row == i // 3 else 0 for row in range(4)))
                     for i, a in enumerate(frames))
        expected = {verify.ZERO: (0, 0, 0, 8), targets[0]: (1, 0, 0, 0),
                    targets[1]: (0, 2, 0, 0), targets[2]: (0, 0, 4, 0)}
        self.assertEqual(verify.expand(word, 4), expected)
        self.assertNotEqual(verify.expand(word[:-1], 4), expected)
        commutator = tuple(sum(targets[1][3 * i + k] * targets[2][3 * k + j]
                               - targets[2][3 * i + k] * targets[1][3 * k + j] for k in range(3))
                           for i in range(3) for j in range(3))
        self.assertEqual(commutator, (-16, 0, 0, 0, 16, 0, 0, 0, 0))


class CommandTests(unittest.TestCase):
    def run_copy(self, root, optimized=False):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        return subprocess.run([*command, str(root / "verify.py")], cwd=root.parent,
                              capture_output=True, text=True, timeout=60, check=False)

    def test_relocated_normal_and_optimized_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "package"
            root.mkdir()
            for name in ("verify.py", "RESULT.json"):
                shutil.copyfile(PACKAGE / name, root / name)
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            for optimized in (False, True):
                result = self.run_copy(root, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_PARITY_UNIFORM_TARGETS", result.stdout)
                self.assertIn('"integer_oracle_cases": 3969', result.stdout)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)

    def test_actual_implementation_and_receipt_mutants(self):
        source = (PACKAGE / "verify.py").read_text()
        mutants = (
            ("return tuple(tuple(row) for row in work[:pivot])",
             "return tuple(tuple(x // math.gcd(*row) for x in row) for row in work[:pivot])",
             "common nonzero class"),
            ("if not all(invariant(p, subspace) for p in spectra):", "if False:",
             "spectral subspace reconstruction"),
            ("scale_frame(e21, 2)), frame_add(e22", "scale_frame(e21, 3)), frame_add(e22",
             "common nonzero class"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copyfile(PACKAGE / "RESULT.json", root / "RESULT.json")
            for old, new, failure in mutants:
                self.assertEqual(source.count(old), 1)
                (root / "verify.py").write_text(source.replace(old, new))
                result = self.run_copy(root, optimized=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(failure, result.stderr)
                self.assertNotIn("PASS_PARITY_UNIFORM_TARGETS", result.stdout)
            (root / "verify.py").write_text(source)
            payload = json.loads((root / "RESULT.json").read_text())
            payload["integer_oracle_cases"] = 3970
            (root / "RESULT.json").write_text(json.dumps(payload))
            result = self.run_copy(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESULT.json mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
