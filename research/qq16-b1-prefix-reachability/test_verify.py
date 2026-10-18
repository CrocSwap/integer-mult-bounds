#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Controls for the literal prefix proof and its restricted hybrid model."""

import copy
import importlib.util
import json
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("prefix_audit", HERE / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("local verifier unavailable")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class PrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.events = AUDIT.load()
        cls.units, cls.epochs = AUDIT.compile_prefix(cls.events)

    def test_actual_private_epochs_and_named_cut(self):
        self.assertEqual(len(self.epochs), 16)
        self.assertEqual(
            [(e["start"], e["stop"]) for e in self.epochs[:2]], [(12, 20), (29, 37)]
        )
        self.assertEqual(self.epochs[-1]["stop"], 10566)
        self.assertTrue(
            all(set(e["controls"]).isdisjoint(e["targets"]) for e in self.epochs)
        )
        self.assertEqual(self.events[11795], ["climb", "A", 470, 0, 5, 1])

    def test_control_target_alias_is_rejected(self):
        changed = copy.deepcopy(self.events)
        changed[13][1][2] = ["L", 0]
        with self.assertRaisesRegex(ValueError, "shear disjointness"):
            AUDIT.compile_prefix(changed)

    def test_erased_or_noninvertible_ordinary_state_is_rejected(self):
        for replacement in [["clear", ["L", 133]], ["scale", ["L", 133], 0, 1]]:
            changed = copy.deepcopy(self.events)
            changed[1291][1] = replacement
            with self.assertRaises(ValueError):
                AUDIT.compile_prefix(changed)
        changed = copy.deepcopy(self.events)
        index = next(
            i
            for i, e in enumerate(changed[:11795])
            if e[0] == "scalar" and e[1][0] == "add" and e[1][1][0] == e[1][2][0] == "L"
        )
        changed[index][1][2] = changed[index][1][1]
        with self.assertRaises(ValueError):
            AUDIT.compile_prefix(changed)

    def test_private_clear_and_opaque_type_controls(self):
        changed = copy.deepcopy(self.events)
        changed[20] = ["phase", "omitted clear"]
        with self.assertRaises(ValueError):
            AUDIT.compile_prefix(changed)
        changed = copy.deepcopy(self.events)
        changed[0][0] = "singular_unpriced_projection"
        with self.assertRaises(ValueError):
            AUDIT.compile_prefix(changed)

    def test_opaque_substitutions_are_nontrivial_and_invertible(self):
        value = (Q(1), Q(2), Q(-3), Q(5))
        images = []
        for event in self.events[:12]:
            result = AUDIT.opaque(value, event)
            self.assertEqual(AUDIT.opaque(result, event, inverse=True), value)
            self.assertNotEqual(result, value)
            images.append(result)
        self.assertGreater(len(set(images)), 1)
        a, b = self.events[0], self.events[1]
        self.assertNotEqual(
            AUDIT.opaque(AUDIT.opaque(value, a), b),
            AUDIT.opaque(AUDIT.opaque(value, b), a),
        )

    def test_complete_reachable_state_not_just_two_local_fields(self):
        cut = [AUDIT.ZERO] * 704
        cut[470] = (Q(64), Q(0), Q(4), Q(0))
        cut[17] = (Q(3), Q(-2), Q(1), Q(7))
        cut[703] = (Q(9), Q(5), Q(-3), Q(2))
        cut[465] = (Q(1), Q(2), Q(3), Q(4))
        entry = AUDIT.run(cut, self.units, inverse=True)
        self.assertEqual(AUDIT.run(entry, self.units), cut)
        wrong = self.units[:-1]
        self.assertNotEqual(AUDIT.run(entry, wrong), cut)

    def test_uniform_local_rounding_and_actual_binary64(self):
        for precision in range(2, 10):
            large = 4 << (precision + 1)
            self.assertEqual(
                {AUDIT.nearest(large + c, precision) for c in (-4, 0, 4)}, {large}
            )
            self.assertEqual(
                len({AUDIT.rounded_pair(precision, c) for c in (-4, 0, 4)}), 1
            )
        large = 4 << 54
        self.assertEqual(float(large - 4), float(large + 4))
        self.assertNotEqual(AUDIT.nearest(large - 4, 55), AUDIT.nearest(large + 4, 55))

    def test_receipt_and_scope_limits(self):
        result = AUDIT.compute()
        expected = json.loads((HERE / "RESULT.json").read_text())
        self.assertEqual(json.loads(json.dumps(result)), expected)
        self.assertIn("fully rounded prefix", result["not_checked"])
        self.assertIn("F0-to-B1 entry reachability", result["not_checked"])


if __name__ == "__main__":
    unittest.main()
