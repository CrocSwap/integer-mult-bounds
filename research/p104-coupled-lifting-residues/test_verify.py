"""Behavioral controls for the public mathematical certificate and replay."""

import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import independent
import lattice
import verify


def definition_member(value, rank):
    """Single-vector rational-prefix definition; no lattice/basis imports."""
    numerator, denominator = list(value), 1
    for bit in range(rank):
        following = [0] * len(value)
        for a in range(1 << rank):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            ar, ai = numerator[2 * a : 2 * a + 2]
            br, bi = numerator[2 * b : 2 * b + 2]
            if (ar - br) % (2 * denominator) or (ai - bi) % (2 * denominator):
                return False
            following[2 * a : 2 * a + 2] = ar - ai + br + bi, ar + ai - br + bi
            following[2 * b : 2 * b + 2] = ar + ai + br - bi, -ar + ai + br + bi
        numerator, denominator = following, denominator * 2
    return True


def run_cli(directory, optimized=False):
    options = ["-O"] if optimized else []
    return subprocess.run(
        [sys.executable, *options, "-B", "-Werror", str(directory / "verify.py")],
        cwd=directory,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basis = verify.load_basis()

    def test_unpruned_small_quotients(self):
        for rank, modulus, expected in ((1, 2, 4), (2, 4, 1024)):
            count = sum(
                definition_member(value, rank)
                for value in itertools.product(range(modulus), repeat=2 << rank)
            )
            self.assertEqual(count, expected)
            matrix, m = independent.congruences(rank)
            factors = independent.quotient_factors(matrix, m)
            image = 1
            for order, multiplicity in factors.items():
                image *= order**multiplicity
            self.assertEqual(modulus ** (2 << rank) // count, image)

    def test_strictly_larger_than_scalar_lattice(self):
        # Column two is a certified period outside the scalar 16-sublattice.
        period = [row[2] for row in self.basis]
        self.assertTrue(any(x % 16 for x in period))
        self.assertTrue(definition_member(period, 7))
        x = [-17, -16, -1, 0, 1, 15, 16, 17] * 32
        self.assertEqual(
            lattice.canonical(x, self.basis),
            lattice.canonical(
                [a + b for a, b in zip(x, period, strict=True)], self.basis
            ),
        )
        self.assertEqual(lattice.split(x, self.basis), lattice.lift(x, 7))

    def test_hnf_box_representatives(self):
        for offset in range(4):
            residue = [(i + offset) % self.basis[i][i] for i in range(256)]
            self.assertEqual(lattice.canonical(residue, self.basis), residue)
            self.assertEqual(
                lattice.split(residue, self.basis), lattice.lift(residue, 7)
            )

    def test_same_index_bad_basis_rejected(self):
        corrupted = [row[:] for row in self.basis]
        # Keep the determinant and Hermite bounds; destroy a prefix congruence.
        corrupted[0][1] = (corrupted[0][1] + 1) % corrupted[0][0]
        with self.assertRaisesRegex(ValueError, "prefix parity|full prefix lattice"):
            lattice.validate_basis(corrupted)

    def test_inverse_uses_image_lattice(self):
        z = [0, 0, 0, 0, 1, 1, 1, 3]
        self.assertTrue(definition_member(z, 2))
        image = lattice.ideal(z, 2)
        self.assertEqual(image, [2, 0, 1, 1, 0, 2, -1, 1])
        self.assertFalse(definition_member(image, 2))
        x = [-3, 7, 1, -2, 11, -4, 0, 5]
        actual = lattice.lift(
            [a + b for a, b in zip(x, image, strict=True)], 2, inverse=True
        )
        self.assertEqual(
            actual, [a + b for a, b in zip(lattice.lift(x, 2, True), z, strict=True)]
        )

    def test_boundary_contracts(self):
        for rank in (0, 8, True):
            with self.assertRaises(ValueError):
                lattice.index_counts(rank)
        for value in ([0] * 255, [False] * 256, [1 << 4096] * 256):
            with self.assertRaises(ValueError):
                lattice.split(value, self.basis)
        for sign in (-1, 1):
            value = [sign * ((1 << 4096) - 1)] + [0] * 255
            expected = verify.reference(value, 7, verify.predecessor())
            self.assertEqual(lattice.split(value, self.basis), expected)

    def test_public_cli_receipt_and_source_controls(self):
        with tempfile.TemporaryDirectory() as temporary:
            export = Path(temporary) / "export"
            shutil.copytree(
                verify.HERE, export, ignore=shutil.ignore_patterns("__pycache__")
            )
            receipt = json.loads((export / "RESULT.json").read_text())
            receipt["rank7_index_log2"] = True
            (export / "RESULT.json").write_text(json.dumps(receipt))
            result = run_cli(export, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("typed result receipt mismatch", result.stderr)
            shutil.copyfile(verify.HERE / "RESULT.json", export / "RESULT.json")
            with (export / "vendor/lifting.py").open("a") as output:
                output.write("\n# deliberate changed-source control\n")
            result = run_cli(export)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("predecessor hash", result.stderr)

    def test_read_only_git_free_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            export = Path(temporary) / "export"
            shutil.copytree(
                verify.HERE, export, ignore=shutil.ignore_patterns("__pycache__")
            )
            paths = [
                export,
                export / "vendor",
                *export.glob("*"),
                *export.glob("vendor/*"),
            ]
            try:
                for path in paths:
                    path.chmod(0o555 if path.is_dir() else 0o444)
                for optimized in (False, True):
                    result = run_cli(export, optimized)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("PASS_P104_COUPLED_LIFTING_RESIDUES", result.stdout)
                self.assertFalse(any(export.rglob("__pycache__")))
            finally:
                for path in paths:
                    path.chmod(0o755 if path.is_dir() else 0o644)


if __name__ == "__main__":
    unittest.main()
