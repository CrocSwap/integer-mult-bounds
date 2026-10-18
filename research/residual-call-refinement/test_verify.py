"""Behavior and rejection tests for the independently checked boundary."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify

verify.activate()
import specification as spec
import trace_checks


class RefinementTests(unittest.TestCase):
    def test_odd_reset_keeps_central_atom(self):
        plan = next(p for p in trace_checks.plans() if p.dimension == 2 and not p.good)
        actual, _ = trace_checks.check_case(plan, 3)
        self.assertEqual(
            actual[0], ("enter", 3, 5, 1, 10, "unit", 0, False, 23, True, None)
        )
        self.assertEqual(
            [row[0] for row in actual[:10]],
            [
                "enter",
                "atom_swap",
                "add",
                "atom_swap",
                "add",
                "atom_swap",
                "add",
                "atom_swap",
                "sign",
                "return",
            ],
        )
        self.assertEqual(actual[1][1:3], (3, 5))
        tail_main = next(
            row
            for row in actual
            if row[0] == "enter" and row[5] == "pair" and row[6] == 2
        )
        self.assertEqual(
            tail_main, ("enter", 6, 9, 3, 10, "pair", 2, True, 23, False, None)
        )

    def test_exact_half_cutoff_and_odd_width(self):
        plan = next(p for p in trace_checks.plans() if p.dimension == 2 and not p.good)
        signatures = []
        for width in (127, 128, 129):
            actual, _ = trace_checks.check_case(plan, width)
            signatures.append((actual[0][3], actual[1][0]))
        self.assertEqual(
            signatures, [(63, "atom_swap"), (64, "invoke"), (64, "invoke")]
        )

    def test_volume_requires_external_gap_once(self):
        factors, region = spec.spectator_extents(5, 2, 7, 3, 0, 8, 2)
        self.assertEqual((factors, region), ([(2, 0), (7, 6), (3, 0)], 1))
        actual = [coefficient * 3**exponent for coefficient, exponent in factors]
        self.assertEqual(actual[0] * actual[1] * actual[2] * 3**4, 2 * 7 * 3 * 3**10)
        with self.assertRaisesRegex(ValueError, "unsplit gap"):
            spec.spectator_extents(5, 2, 7, 3, 4, 8, 2)

    def test_literal_source_mutants_reject(self):
        self.assertEqual(
            trace_checks.controls(),
            ["double_sign", "duplicate_enter", "lose_half_flag", "omit_first_reset"],
        )

    def test_source_change_rejects_before_import(self):
        # No source copy is needed: use a private manifest selecting one small
        # real source and expose different bytes through a controlled Path read.
        source = (
            verify.ROOT / "research/selected-bit-physical-caller/residual_blocks.py"
        )
        original = Path.read_bytes
        reached = []

        def corrupt(path):
            raw = original(path)
            if path == source:
                reached.append(path)
                return raw + b"\n# deliberate source corruption\n"
            return raw

        with (
            patch.object(Path, "read_bytes", corrupt),
            self.assertRaisesRegex(ValueError, "source changed:.*residual_blocks.py"),
        ):
            verify.authenticate()
        self.assertEqual(reached, [source])

    def test_typed_receipt_rejects_boolean_alias(self):
        # The final comparison deliberately uses typed JSON, not Python's
        # equality, which treats True and 1 as equal.
        original = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        changed = dict(original, selected_kappa_unchanged=1)
        verify.check_receipt(original, original)
        with self.assertRaisesRegex(ValueError, "typed result receipt differs"):
            verify.check_receipt(changed, original)


if __name__ == "__main__":
    unittest.main()
