#!/usr/bin/env python3
"""Independent arithmetic and escape controls for the local collision."""

import hashlib
import itertools
import json
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

import verify

HERE = Path(__file__).resolve().parent


def hardware(source, recipe, ref):
    """Actual binary64 additions; independently written Gaussian arithmetic."""
    right = ref.table(recipe["right"])
    left = ref.table(recipe["left"])
    work = [0j] * 512
    for j, (dest, phase) in enumerate(right):
        a, b = source[j]
        work[dest] = complex(a, b) * (1j ** phase)
    mixed = [0j] * 512
    for j in range(256):
        a, b = work[2 * j:2 * j + 2]
        sr, si = a.real + b.real, a.imag + b.imag
        dr, di = a.real - b.real, a.imag - b.imag
        mixed[2 * j] = complex((sr - di) / 2, (si + dr) / 2)
        mixed[2 * j + 1] = complex((sr + di) / 2, (si - dr) / 2)
    out = [0j] * 512
    for j, (dest, phase) in enumerate(left):
        out[dest] = mixed[j] * (1j ** phase)
    return [(int(z.real), int(z.imag)) for z in out]


class CollisionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = verify.authenticated_reference()
        _, recipes = cls.ref.load()
        cls.recipe = recipes[0]

    def test_fraction_midpoints_for_all_fixture_precisions(self):
        for p in (2, 3, 5, 11, 53, 104, 256):
            a = 1 << (p + 1)
            # Adjacent p-bit numbers below and above a are a-2 and a+4.
            self.assertEqual(Fraction(a - 2 + a, 2), a - 1)
            self.assertLess(Fraction(a + 1), Fraction(a + a + 4, 2))
            self.assertEqual((a // 2) % 2, 0)  # a is the even lower-binade endpoint.
            for c in (-1, 0, 1):
                self.assertEqual(self.ref.nearest(a + c, p), a)
                self.assertEqual(self.ref.nearest(a - c, p), a)

    def test_actual_binary64_all_returned_components(self):
        for choice in (-1, 0, 1):
            original, source, destination, _ = verify.execute(
                [choice] * 256, 53, self.recipe, self.ref)
            actual = hardware(original, self.recipe, self.ref)
            self.assertEqual(actual, source)
            self.assertEqual([(-a // 2, -b // 2) for a, b in actual], destination)

    def test_two_extra_significand_bits_escape(self):
        endpoints = []
        for choice in (-1, 0, 1):
            original = verify.entry([choice] * 256, 5, self.recipe, self.ref)
            exact, exact_dest = self.ref.exact(original, [(0, 0)] * 512, self.recipe)
            source, dest, counts = self.ref.run(list(original), [(0, 0)] * 512,
                                               self.recipe, 7, 7)
            self.assertEqual(source, exact)
            self.assertEqual(dest, exact_dest)
            self.assertEqual(counts["nonzero_rounds"], 0)
            endpoints.append(verify.digest([source, dest]))
        self.assertEqual(len(set(endpoints)), 3)

    def test_perturbation_above_collision_radius_survives(self):
        # Magnitude two exceeds the common one-unit half-ulp radius below A.
        a, p = 64, 5
        self.assertNotEqual(self.ref.nearest(a - 2, p), a)
        self.assertEqual(self.ref.nearest(a + 2, p), a)

    def test_monomials_and_ideal_map_preserve_distinctions(self):
        mapping = self.ref.table(self.recipe["right"])
        for axis in (0, 1, 127, 255):
            choices = [0] * 256
            choices[axis] = 1
            source = verify.entry(choices, 5, self.recipe, self.ref)
            work = [(0, 0)] * 512
            self.ref.monomial(source, work, mapping, Counter())
            self.assertEqual(work[2 * axis + 1], (4, 0))
            exact, _ = self.ref.exact(source, [(0, 0)] * 512, self.recipe)
            base = verify.entry([0] * 256, 5, self.recipe, self.ref)
            exact_base, _ = self.ref.exact(base, [(0, 0)] * 512, self.recipe)
            self.assertEqual(self.ref.error2(exact, exact_base), 16)

    def test_fixed_summary_family_and_cardinality(self):
        hashes, summaries = set(), set()
        for signs in itertools.product((-1, 1), repeat=4):
            choices = list(signs) + [1] * 252
            _, source, dest, counts = verify.execute(choices, 5, self.recipe, self.ref)
            hashes.add(verify.digest([source, dest]))
            summaries.add(json.dumps(counts, sort_keys=True))
        self.assertEqual((len(hashes), len(summaries)), (1, 1))
        self.assertTrue(2 ** 405 < 3 ** 256 <= 2 ** 406)
        self.assertEqual((3 ** 256 - 1).bit_length(), 406)

    def test_entry_capacity_and_mutated_source_pin_rejected(self):
        with self.assertRaisesRegex(ValueError, "precision capacity"):
            verify.entry([0] * 256, 2047, self.recipe, self.ref)
        with self.assertRaisesRegex(ValueError, "ternary word"):
            verify.entry([2] * 256, 5, self.recipe, self.ref)
        rows = json.loads((HERE / "SOURCES.json").read_text())["retained_predecessor"]["files"]
        pin = next(r for r in rows if r["path"].endswith("child-halfadd/verify.py"))
        raw = (HERE / "reference.py").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), pin["sha256"])
        with self.assertRaisesRegex(ValueError, "reference source hash"):
            verify.authenticate(raw + b"\n", pin["sha256"])


if __name__ == "__main__":
    unittest.main()
