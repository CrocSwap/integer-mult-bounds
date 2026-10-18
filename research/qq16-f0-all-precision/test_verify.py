"""Behavioral checks for the symbolic ray, its source boundary and actual F0."""

import json
import tempfile
import types
import unittest
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

_SOURCE = Path(__file__).resolve().with_name("verify.py")
V = types.ModuleType("symbolic_f0_under_test")
V.__file__ = str(_SOURCE)
exec(compile(_SOURCE.read_bytes(), str(_SOURCE), "exec"), V.__dict__)


def oracle(value, precision):
    """Nearest among explicit neighboring normalized binary numbers."""
    if not value:
        return Q(0)
    sign = -1 if value < 0 else 1
    value = abs(value)
    guess = value.numerator.bit_length() - value.denominator.bit_length()
    candidates = set()
    for exponent in range(guess - 1, guess + 2):
        shift = exponent - precision + 1
        step = Q(2**shift) if shift >= 0 else Q(1, 2 ** (-shift))
        quotient = value // step
        for integer in range(
            max(2 ** (precision - 1), quotient - 1), min(2**precision, quotient + 2)
        ):
            candidates.add((integer * step, integer % 2))
    if not candidates:
        raise ValueError("oracle candidate domain")
    result, _ = min(candidates, key=lambda row: (abs(row[0] - value), row[1]))
    return sign * result


class SymbolicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.events, cls.context = V.load()

    def test_affine_classifier_against_neighbor_oracle(self):
        checked = 0
        for numerator in range(-5, 6):
            for denominator_power in range(3):
                a = Q(numerator, 2**denominator_power)
                for constant in range(-9, 10):
                    b = Q(constant, 8)
                    x, y = V.rounded_affine(a, b)
                    for precision in (8, 9, 16, 127, 256, 4096):
                        scale = 2 ** (precision + V.OFFSET)
                        self.assertEqual(
                            scale * x + y, oracle(scale * a + b, precision)
                        )
                        checked += 1
        self.assertEqual(checked, 3762)

    def test_rejects_unproved_ray_boundaries(self):
        for a, b in (
            (Q(0), Q(257)),
            (Q(1), -Q(2**20)),
            (Q(1), Q(2**21)),
            (Q(257), Q(0)),
            (Q(0), Q(1, 3)),
        ):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                V.rounded_affine(a, b)
        for precision in (True, 1, 257):
            with self.assertRaises(ValueError):
                V.rounded_affine(Q(1), Q(0), precision)

    def test_rounding_ties_and_signs(self):
        # A=2^(p+12) is even on both adjacent binade grids.
        for b in (Q(-256), Q(-128), Q(128), Q(256), Q(384), Q(512), Q(768)):
            for sign in (-1, 1):
                a, constant = V.rounded_affine(Q(sign), sign * b)
                for precision in (8, 9, 127):
                    scale = 2 ** (precision + 12)
                    self.assertEqual(
                        scale * a + constant, oracle(sign * (scale + b), precision)
                    )

    def test_actual_direct_native_endpoints(self):
        native = self.module.N
        leading, constant, _, _ = V.symbolic(self.module, self.events, self.context)
        packet, _, recipes, residuals = self.module.load()
        for precision in (8, 127, 256):
            entry = self.module.initial(precision)
            actual, faults = self.module.execute(
                self.events, packet, recipes, residuals, entry, precision
            )
            symbolic = [
                native.plus(native.scaled(a, Q(2 ** (precision + 12))), b)
                for a, b in zip(leading, constant, strict=True)
            ]
            self.assertEqual(actual, symbolic)
            self.assertEqual([row["event"] for row in faults], [3887, 4060])

    def test_missing_rounding_and_wrong_gate_are_discriminating(self):
        native = self.module.N
        _, exact, exact_faults, _ = V.symbolic(
            self.module, self.events, self.context, round_adds=False
        )
        _, rounded, faults, _ = V.symbolic(self.module, self.events, self.context)
        self.assertNotEqual(exact, rounded)
        self.assertFalse(exact_faults)
        changed = deepcopy(self.events)
        changed[4060][1][3] = 0
        _, mutant, mutant_faults, _ = V.symbolic(self.module, changed, self.context)
        self.assertNotEqual(mutant, rounded)
        self.assertNotEqual(mutant_faults, faults)
        self.assertEqual(rounded[112], native.ZERO)

    def test_source_corruption_fails_before_execution(self):
        sources = json.loads((V.HERE / "SOURCES.json").read_bytes())
        first = next(row for row in sources["files"] if row["usage"] == "input")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / first["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes(b"corrupted")
            with self.assertRaisesRegex(ValueError, "source pin"):
                V.load(root)

    def test_live_source_cannot_be_reclassified(self):
        sources = json.loads((V.HERE / "SOURCES.json").read_bytes())
        for row in sources["files"]:
            if row["path"] == V.PREDECESSOR:
                row["usage"] = "provenance"
        with tempfile.TemporaryDirectory() as directory:
            here = Path(directory)
            (here / "SOURCES.json").write_text(json.dumps(sources))
            with (
                patch.object(V, "HERE", here),
                self.assertRaisesRegex(ValueError, "exact live input inventory"),
            ):
                V.load()

    def test_complete_receipt(self):
        result = V.audit()
        expected = json.loads((V.HERE / "RESULT.json").read_bytes())
        self.assertEqual(V.canonical(result), V.canonical(expected))
        expected["new_kappa"] = 0
        self.assertNotEqual(V.canonical(result), V.canonical(expected))


if __name__ == "__main__":
    unittest.main()
