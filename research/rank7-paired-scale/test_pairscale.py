# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for paired negation and source-bound accounting."""

import json
import tempfile
import unittest
from pathlib import Path

import bindings
import checks
import pairscale as p
import verify
from vendor import scalars as s


class PairedScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bits, cls.caller, _, cls.lower, _ = bindings.load()

    def test_modular_minimum_is_supported_but_signed_prefix_rejects(self):
        self.assertEqual(p.execute(4, p.negate(4), -8, -3), (8, 3))
        with self.assertRaisesRegex(ValueError, "negation prefix"):
            p.endpoint(4, -1, 2, -8)

    def test_signed_scale_and_inverse_include_both_components(self):
        gates = p.circuit(8, 1, -2, [("neg", 0), ("half", 0)])
        self.assertEqual(p.execute(8, gates, 30, -18), (241, 9))
        self.assertEqual(p.execute(8, list(reversed(gates)), -15, 9), (30, 238))

    def test_dirty_carry_rejected(self):
        with self.assertRaisesRegex(ValueError, "clean carry"):
            p.execute(4, p.negate(4), 1, 2, carry=1)

    def test_widest_legal_negative_half_scale_and_control(self):
        recipe = [("neg", 0)] + [("half", 0)] * 12
        self.assertEqual(len(p.circuit(256, -1, 4096, recipe)), 24500)
        for control in (False, True):
            gates = p.circuit(256, -1, 4096, recipe, control=control)
            self.assertEqual(p.execute(256, gates, 4096, -4096), ((1 << 256) - 1, 1))
            self.assertEqual(
                p.execute(256, list(reversed(gates)), -1, 1), (4096, (1 << 256) - 4096)
            )
        self.assertEqual(
            p.scale(256, -1, 4096, 4096, -4096, recipe), ((1 << 256) - 1, 1)
        )

    def test_omitted_fourth_shear_is_detected(self):
        gates = p.negate(4)
        del gates[-(6 * 3 - 4) :]
        with self.assertRaisesRegex(ValueError, "pair endpoint"):
            checks.batch(4, gates, [(2, 3)], [(-2, -3)])

    def test_wrong_double_coefficient_is_detected(self):
        add = s.adder(tuple(range(4, 8)), tuple(range(4)), 8)
        subtract = list(reversed(s.adder(tuple(range(4)), tuple(range(4, 8)), 8)))
        with self.assertRaisesRegex(ValueError, "pair endpoint"):
            checks.batch(4, add + subtract + add + subtract, [(2, 3)], [(-2, -3)])

    def test_borrowed_partner_control_has_same_complete_endpoint(self):
        for control in (False, True):
            self.assertEqual(
                p.execute(
                    8, p.circuit(8, -1, 1, [("neg", 0)], control=control), -51, 76
                ),
                (51, 180),
            )

    def test_alignment_and_signed_overflow_rejected(self):
        for args in ((4, 1, 2, 3), (4, 2, 1, 5), (4, -2, 1, -8)):
            with self.assertRaises(ValueError):
                p.endpoint(*args)
        for real, imag in ((2, 3), (-8, 2)):
            with self.assertRaises(ValueError):
                p.scale(4, -1, 2, real, imag, [("neg", 0), ("half", 0)])

    def test_guard_matches_existing_boundary_at_extremes(self):
        for a, b in ((-1, 1), (1, -2), (2, -1), (1, 2), (2, 1)):
            for value in range(-8, 8):
                try:
                    expected = self.caller.guards(4, "scale", a, b, value, 0)
                except ValueError:
                    with self.assertRaises(ValueError):
                        p.endpoint(4, a, b, value)
                else:
                    self.assertEqual(p.endpoint(4, a, b, value), expected)

    def test_invalid_coefficient_recipe_and_width_rejected(self):
        for a, b, recipe in (
            (0, 1, []),
            (3, 2, []),
            (1, 0, []),
            (-1, 1, []),
            (1, 2, [("half", 1)]),
            (1, 8192, [("half", 0)] * 13),
        ):
            with self.assertRaises(ValueError):
                p.circuit(4, a, b, recipe)
        for width in (0, 3, 257, 4.0):
            with self.assertRaises(ValueError):
                p.negate(width)
        for a, b in ((512, 1), (-512, 1), (1, 8192)):
            with self.assertRaisesRegex(ValueError, "bounded dyadic"):
                p.endpoint(23, a, b, 0)
            with self.assertRaises(ValueError):
                self.caller.guards(23, "scale", a, b, 0, 0)

    def test_alias_and_foreign_wires_rejected(self):
        with self.assertRaisesRegex(ValueError, "disjoint"):
            s.adder((0, 1), (1, 2), 3)
        with self.assertRaises(ValueError):
            s.apply(4, [(0, 9)], [0] * 9)

    def test_negative_denominators_are_charged(self):
        data = json.loads((bindings.PACKAGE / "vendor/RESULT.json").read_text())
        histogram = data["streams"]["base/forward"]["histogram"]
        result = verify.aggregate(84, histogram, self.bits, self.lower)
        self.assertEqual(result["negative_scales"], 462)
        self.assertEqual(result["paired"], {"cx": 7132540, "ccx": 3461616})
        self.assertEqual(result["saving"], {"cx": 545160, "ccx": 155232})

    def test_missing_macro_is_detected(self):
        data = json.loads((bindings.PACKAGE / "vendor/RESULT.json").read_text())
        histogram = data["streams"]["base/forward"]["histogram"]
        histogram["scale:1:-1"] -= 1
        with self.assertRaisesRegex(ValueError, "complete scalar histogram"):
            verify.aggregate(84, histogram, self.bits, self.lower)

    def test_source_hash_mutation_is_detected_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "package"
            package.mkdir()
            for name in ("SOURCES.json", "UPSTREAM.json"):
                (package / name).write_bytes((bindings.PACKAGE / name).read_bytes())
            records = json.loads((package / "SOURCES.json").read_text())
            records["files"] = [
                {"path": "mutant.py", "usage": "input", "sha256": "0" * 64}
            ]
            (package / "SOURCES.json").write_text(json.dumps(records))
            (root / "mutant.py").write_text("raise RuntimeError('must not import')\n")
            with self.assertRaisesRegex(ValueError, "source hash"):
                bindings.authenticate(package, root)


if __name__ == "__main__":
    unittest.main()
