# SPDX-License-Identifier: Apache-2.0
"""Behavioral identities, mutation controls, and exact native-ledger checks."""

import json
import tempfile
import unittest
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

from contract import expected_cleanup, operator
from contractions import apply_edit, check_gate, commutes, produce
from frames import trace
from tariff import produce as tariff_parent
from verify import (
    PACKAGE,
    check_ledger,
    check_pins,
    compare,
    compile_word,
    digest,
    read,
)


def add(target, source, coefficient, frame=None):
    value = Fraction(coefficient)
    return ["add", target, source, value.numerator, value.denominator, frame or []]


def edit_for(gates):
    first, last = gates[0], gates[-1]
    coefficient = Fraction(first[3], first[4]) + Fraction(last[3], last[4])
    replacement = add(first[1], first[2], coefficient) if coefficient else None
    from tariff import price

    saving = price(first) + price(last) - (price(replacement) if replacement else 0)
    return [0, len(gates) - 1, first, last, replacement, saving]


class Algebra(unittest.TestCase):
    def test_independent_dirty_matrix_and_cancellation(self):
        for a, b, expected in (
            (Fraction(1, 2), -1, Fraction(-1, 2)),
            (-1, -1, -2),
            (-1, 1, 0),
            (Fraction(1, 4), -1, Fraction(-3, 4)),
        ):
            gates = [add(0, 1, a), add(2, 1, 3), add(0, 1, b)]
            changed, _ = apply_edit(gates, edit_for(gates), 0)
            literal = {0: {0: 1}, 1: {1: 1}, 2: {2: 1, 1: 3}}
            if expected:
                literal[0][1] = expected
            self.assertEqual(operator(gates, range(3)), literal)
            self.assertEqual(operator(changed, range(3)), literal)

    def test_target_read_and_source_write_are_barriers(self):
        for middle in (add(2, 0, 1), add(1, 2, 1)):
            gates = [add(0, 1, -1), middle, add(0, 1, -1)]
            with self.assertRaisesRegex(ValueError, "intervening"):
                apply_edit(gates, edit_for(gates), 0)
        # A wrong commuting test really changes an independent dirty output.
        old = [add(0, 1, -1), add(2, 0, 1), add(0, 1, -1)]
        wrong = [add(2, 0, 1), add(0, 1, -2)]
        self.assertEqual(operator(old, range(3))[2], {2: 1, 0: 1, 1: -1})
        self.assertEqual(operator(wrong, range(3))[2], {2: 1, 0: 1})

    def test_frames_scales_and_warps_are_checked(self):
        first = add(0, 1, -1)
        self.assertFalse(commutes(first, add(2, 1, 1, [1])))
        self.assertFalse(commutes(first, ["scale", 1, -1, 1, []]))
        self.assertFalse(commutes(first, ["warp", 1, 1, [], []]))
        self.assertTrue(commutes(first, ["warp", 2, 1, [], []]))
        self.assertTrue(commutes(first, ["scale", 2, -1, 1, []]))

    def test_coefficient_cost_address_and_prelude_controls(self):
        gates = [add(0, 1, -1), add(0, 1, -1)]
        original = edit_for(gates)
        for column, value in ((0, -1), (1, 5), (4, add(0, 1, -3)), (5, 4)):
            mutant = deepcopy(original)
            mutant[column] = value
            with self.assertRaises(ValueError):
                apply_edit(gates, mutant, 0)
        with self.assertRaisesRegex(ValueError, "addresses"):
            apply_edit(gates, original, 1)

    def test_invalid_gate_boundaries(self):
        for gate in (
            add(0, 0, 1),
            add(704, 1, 1),
            add(0, 1, Fraction(1, 3)),
            ["scale", 0, 3, 1, []],
            ["unknown", 0],
        ):
            with self.assertRaises(ValueError):
                check_gate(gate)


class SourceWords(unittest.TestCase):
    def test_both_providers_and_disjoint_composition(self):
        edits = read(PACKAGE / "EDITS.json")
        for provider in ("base", "extra"):
            parent = read(PACKAGE / f"vendor/WORD-{provider}.json.gz")
            candidate = produce(parent, edits)
            self.assertEqual(len(candidate["A"]), 4052)
            self.assertEqual(len(candidate["cleanup"]), 5189)
            self.assertEqual(
                trace(candidate)["profile"],
                {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8},
            )
            self.assertEqual(
                tariff_parent(candidate), produce(tariff_parent(parent), edits)
            )

    def test_preimage_and_stale_cleanup_fail(self):
        parent = read(PACKAGE / "vendor/WORD-base.json.gz")
        edits = read(PACKAGE / "EDITS.json")
        wrong = deepcopy(parent)
        wrong["A"][84][3] *= -1
        wrong["cleanup"] = expected_cleanup(wrong)
        with self.assertRaisesRegex(ValueError, "preimage"):
            produce(wrong, edits)
        wrong = deepcopy(parent)
        wrong["cleanup"].pop()
        with self.assertRaisesRegex(ValueError, "parent cleanup"):
            produce(wrong, edits)
        candidate = produce(parent, edits)
        self.assertNotEqual(parent["cleanup"], expected_cleanup(candidate))

    def test_frozen_bytes_and_inventory_fail_closed(self):
        self.assertEqual(check_pins(), 12)
        with tempfile.TemporaryDirectory(prefix="contraction-pins-") as directory:
            target = Path(directory) / "package"
            target.mkdir()
            manifest = read(PACKAGE / "VENDOR.json")
            (target / "VENDOR.json").write_text(json.dumps(manifest))
            for record in manifest["files"]:
                source = PACKAGE / record["path"]
                destination = target / record["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read_bytes())
            path = target / "vendor/WORD-base.json.gz"
            path.write_bytes(path.read_bytes() + b"mutant")
            with self.assertRaisesRegex(ValueError, "frozen source bytes"):
                check_pins(target)
            manifest = read(target / "VENDOR.json")
            manifest["files"].pop()
            (target / "VENDOR.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "inventory"):
                check_pins(target)


class NativeLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="contraction-native-tests-")
        cls.addClassCleanup(cls.temporary.cleanup)
        work = Path(cls.temporary.name)
        original = read(PACKAGE / "vendor/WORD-base.json.gz")
        parent = tariff_parent(original)
        candidate = produce(parent, read(PACKAGE / "EDITS.json"))
        cls.before, cls.old = compile_word(parent, work / "parent")
        cls.after, cls.new = compile_word(candidate, work / "candidate")

    def test_literal_complete_native_saving(self):
        compare(self.before, self.after, self.old, self.new, 158124, 340)
        self.assertEqual(self.new["forward"]["real_component_primitive_bound"], 157784)
        self.assertEqual(self.new["backward"]["real_component_primitive_bound"], 157832)

    def test_wrong_native_cost_profile_erasure_and_hash_reject(self):
        for key, value in (
            ("real_component_primitive_bound", 157783),
            ("paid_profile", {"1": 1}),
            ("zero_buffers_returned_to_zero", 90),
            ("private_centers_cleared", False),
            ("sha256", "0" * 64),
        ):
            mutant = deepcopy(self.new["forward"])
            mutant[key] = value
            with self.assertRaises(ValueError):
                check_ledger(self.after["forward"], mutant)

    def test_equal_cost_wrong_non_scalar_stream_rejects(self):
        mutant = deepcopy(self.after)
        index = next(
            i for i, event in enumerate(mutant["forward"]) if event[0] == "warp"
        )
        mutant["forward"][index][2] *= -1
        checks = deepcopy(self.new)
        checks["forward"]["sha256"] = digest(mutant["forward"])
        with self.assertRaisesRegex(ValueError, "non-scalar"):
            compare(self.before, mutant, self.old, checks, 158124, 340)


if __name__ == "__main__":
    unittest.main()
