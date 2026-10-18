#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the physical tariff and strict fitting boundaries."""

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent
import verify


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.planes = verify.load_geometry()

    def test_complete_receipt(self):
        expected = json.loads((verify.HERE / "RESULT.json").read_bytes())
        self.assertEqual(verify.build(), expected)
        self.assertEqual(expected["lower_bound"], 20)

    def test_tariff_not_abstract_graph(self):
        strengthened = ((2, 3, 2),) + verify.COVER[1:]
        with self.assertRaisesRegex(ValueError, "rank-cover inequality"):
            verify.tariff_certificate(self.planes, strengthened)

    def test_source_corruption_rejected(self):
        names = ("DATA-PHASES.json.gz", "MATCHING.json")
        for corrupted in names:
            with tempfile.TemporaryDirectory(prefix="c5-source-control-") as directory:
                root = Path(directory)
                for name in names:
                    relative = verify.PREFIX + name
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    raw = (verify.ROOT / relative).read_bytes()
                    path.write_bytes(raw + b" " if name == corrupted else raw)
                with self.assertRaisesRegex(ValueError, "source SHA256"):
                    verify.load_geometry(root)

    def test_changed_geometry_rejected(self):
        changed = list(self.planes)
        changed[0], changed[1] = changed[1], changed[0]
        with self.assertRaisesRegex(ValueError, "physical C5"):
            verify.check_geometry(changed)

    def test_all_small_rectangular_ranks(self):
        # Every binary matrix through 2x3, including empty sides.
        for height in range(3):
            for width in range(4):
                for word in range(1 << (height * width)):
                    rows = [
                        [(word >> (i * width + j)) & 1 for j in range(width)]
                        for i in range(height)
                    ]
                    left = [sum(bit << j for j, bit in enumerate(row)) for row in rows]
                    right = [1 << j for j in range(width)]
                    self.assertEqual(
                        verify.pairing_rank(left, right), independent.dense_rank(rows)
                    )

    def test_signed_asymmetric_fit(self):
        matrix, price = verify.attaining_fit(self.planes, Fraction(-3, 2))
        self.assertEqual(price, 20)
        self.assertNotEqual(matrix[1][2], matrix[2][1])
        self.assertEqual(matrix[1][2], Fraction(-2, 3))
        self.assertEqual(matrix[2][1], Fraction(-3, 2))

    def test_strict_and_free_entries_distinguished(self):
        matrix, _ = verify.attaining_fit(self.planes)
        matrix[1][2] = Fraction(17)  # Neighboring planes, a genuinely free entry.
        verify.check_fit(matrix, self.planes)
        matrix[0][4] = Fraction(1)  # Nonorthogonal planes, a forbidden entry.
        with self.assertRaisesRegex(ValueError, "strict scalar constraint"):
            verify.check_fit(matrix, self.planes)

    def test_same_plane_offdiagonal_rejected(self):
        matrix, _ = verify.attaining_fit(self.planes)
        matrix[0][1] = Fraction(1)
        with self.assertRaisesRegex(ValueError, "strict scalar constraint"):
            verify.check_fit(matrix, self.planes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
