#!/usr/bin/env python3
"""Quick model/boundary fixtures only; verify.py performs the full census."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from algebra import Algebra, natural_image
from controls import ALIAS_TARGETS, ALIAS_WORD, regular_column


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algebra = Algebra()
        cls.targets = tuple(cls.algebra.index[g] for g in ALIAS_TARGETS)

    def test_natural_alias_fails_every_faithful_column(self):
        a = self.algebra
        target = a.target(*self.targets)
        alias = a.word(ALIAS_WORD)
        self.assertEqual(natural_image(a, alias), natural_image(a, target))
        self.assertNotEqual(alias, target)
        direct = a.direct_word(*self.targets)
        for role in range(2):
            for x in a.group:
                self.assertNotEqual(regular_column(a, ALIAS_WORD, role, x),
                                    regular_column(a, direct, role, x))

    def test_formal_row_orbits_are_equivariant(self):
        a = self.algebra
        state = a.word(ALIAS_WORD)
        for row in (state[:2], state[2:]):
            key, coordinate = a.canonical_row(*row)
            for g in range(168):
                translated = tuple(a.translate(p, g) for p in row)
                other, actual_coordinate = a.canonical_row(*translated)
                self.assertEqual(other, key)
                self.assertEqual(actual_coordinate, a.product[g][coordinate])

    def test_missing_call_and_dirty_cross_input(self):
        a = self.algebra
        target = a.target(*self.targets)
        word = a.direct_word(*self.targets)
        self.assertEqual(a.word(word), target)
        self.assertNotEqual(a.word(word[:-1]), target)
        dirty = (target[0], 1 << a.identity, 0, target[3])
        self.assertEqual((dirty[0], dirty[2]), (target[0], target[2]))
        self.assertNotEqual(dirty, target)

    def test_optimized_cli_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sentinel = root / "keep.txt"
            sentinel.write_text("existing user output\n")
            for option in (["--work", str(root)], ["--emit-certificate", str(sentinel)]):
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), *option],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("PASS_GL3_MIXED_TARGETS", result.stdout)
                self.assertEqual(sentinel.read_text(), "existing user output\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
