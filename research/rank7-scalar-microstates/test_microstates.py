# SPDX-License-Identifier: Apache-2.0
"""Behavior and rejection controls for literal scalar arithmetic and capacity."""

import copy
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import integer
import microstates as m
import verify
from vendor import lower
from vendor.format_source import format as f


class MicrostateTests(unittest.TestCase):
    def fixture(self, q=Q(7, 8), policy="source_walk"):
        recipe = lower.certify("add", q.numerator, q.denominator, policy=policy)
        gate = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
        event = ["scalar", gate, 0]
        events = [["phase", "A"], event, ["phase", "centers"]]
        raw = f.canonical(m.literal_record(1, gate, 0, recipe)) + b"\n"
        return recipe, event, events, raw

    def test_positive_fraction_integer_every_prefix(self):
        for q in (Q(1), Q(7, 8), Q(3, 8), Q(3, 2), Q(-7, 4)):
            for policy in lower.POLICIES:
                recipe, _, events, raw = self.fixture(q, policy)
                digest, ledger = hashlib.sha256(), f.Ledger(True)
                m.macro(
                    {(0, ()): Q(1)},
                    {(1, ()): Q(1)},
                    {(0, ()): Q(1), (1, ()): q},
                    recipe,
                    0,
                    ledger,
                    1,
                    digest,
                )
                self.assertEqual(
                    integer.trace(events, io.BytesIO(raw)), digest.hexdigest()
                )

    def test_real_dirty_values(self):
        for q in (Q(7, 8), Q(3, 8), Q(3, 2), Q(-7, 4)):
            for policy in lower.POLICIES:
                recipe, _, _, _ = self.fixture(q, policy)
                for target in range(-8, 8):
                    for source in range(-8, 8):
                        rows = [
                            {0: target * integer.UNIT},
                            {0: source * integer.UNIT},
                            {},
                        ]
                        for item in recipe:
                            integer.instruction(rows, item)
                        self.assertEqual(
                            rows[0].get(0, 0), (target + q * source) * integer.UNIT
                        )
                        self.assertEqual(rows[1].get(0, 0), source * integer.UNIT)
                        self.assertEqual(rows[2], {})

    def reject_mutation(self, policy, mutate):
        _, _, events, raw = self.fixture(policy=policy)
        literal = json.loads(raw)
        mutate(literal)
        with self.assertRaises(ValueError):
            integer.trace(events, io.BytesIO(f.canonical(literal) + b"\n"))

    def test_wrong_half(self):
        def mutate(literal):
            literal["instructions"][0] = ["double", 1]

        self.reject_mutation("source_walk", mutate)

    def test_missing_source_restore(self):
        self.reject_mutation("source_walk", lambda x: x["instructions"].pop())

    def test_missing_scratch_return(self):
        self.reject_mutation("scratch", lambda x: x["instructions"].pop())

    def test_wrong_target_operand(self):
        def mutate(literal):
            for item in literal["instructions"]:
                if item[0] == "add":
                    item[1] = item[2]
                    break

        self.reject_mutation("source_walk", mutate)

    def test_wrong_frame_and_event(self):
        for key in ("frame", "event"):
            with self.subTest(key=key):
                self.reject_mutation(
                    "source_walk", lambda x, k=key: x.__setitem__(k, 7)
                )

    def test_truncated_or_extra_literals(self):
        _, _, events, raw = self.fixture()
        for data in (b"", raw + raw):
            with self.assertRaises(ValueError):
                integer.trace(events, io.BytesIO(data))

    def test_exact_integer_division(self):
        self.assertEqual(integer.scaled({0: 8}, 1, -2), {0: -4})
        with self.assertRaises(ValueError):
            integer.scaled({0: 1}, 1, 2)
        with self.assertRaises(ValueError):
            integer.scaled({0: 1}, 1, 0)

    def test_instruction_boundary(self):
        for item in (["half", 3], ["other", 0], ["add", 0, 1, 2], ["copy", 0, 0]):
            with self.assertRaises(ValueError):
                integer.instruction([{}, {}, {}], item)

    def test_capacity_controls(self):
        bound = {"fractional_bits": 7, "symmetric_amplitude_in_input_L": "4896"}
        self.assertTrue(f.capacity(bound, 64, 7, 84))
        for grid, width in ((6, 84), (7, 83)):
            with self.assertRaises(ValueError):
                f.capacity(bound, 64, grid, width)
        # The positive signed endpoint is excluded, even for an exact power of two.
        with self.assertRaises(ValueError):
            f.capacity(
                {"fractional_bits": 0, "symmetric_amplitude_in_input_L": "1"}, 64, 0, 64
            )

    def test_endpoint_correct_hidden_grid_and_range(self):
        for source, recipe, grid, width in (
            (
                {(1, ()): Q(1, 128)},
                [("half", 1), ("double", 1), ("add", 0, 1, 1)],
                7,
                84,
            ),
            ({(1, ()): Q(1)}, [("double", 1), ("half", 1), ("add", 0, 1, 1)], 0, 65),
        ):
            ledger = f.Ledger(True)
            m.macro({}, source, source, recipe, 0, ledger, 1, hashlib.sha256())
            with self.assertRaises(ValueError):
                f.capacity(ledger.result(64), 64, grid, width)

    def test_target_policy_preserves_source_at_every_prefix(self):
        for n in range(-7, 8):
            for denominator in (1, 2, 4, 8):
                recipe = lower.certify("add", n, denominator, policy="target_walk")
                self.assertTrue(all(item[1] != 1 for item in recipe))

    def test_frozen_source_and_corruption(self):
        self.assertEqual(verify.authenticate(), 25)
        with tempfile.TemporaryDirectory(
            prefix="microstate-source-control-"
        ) as directory:
            root = Path(directory)
            shutil.copytree(verify.PACKAGE / "vendor", root / "vendor")
            shutil.copyfile(verify.PACKAGE / "VENDOR.json", root / "VENDOR.json")
            with (root / "vendor/lower.py").open("ab") as output:
                self.assertEqual(output.write(b"\n"), 1)
            with patch.object(verify, "PACKAGE", root), self.assertRaises(ValueError):
                verify.authenticate()

    def test_independent_original_macro_propagation(self):
        recipe, first, _, raw = self.fixture(Q(1, 2))
        gate = ["add", ["L", 1], ["L", 0], 3, 8]
        second = lower.certify("add", 3, 8, policy="source_walk")
        raw += f.canonical(m.literal_record(2, gate, 0, second)) + b"\n"
        events = [["phase", "A"], first, ["scalar", gate, 0], ["phase", "centers"]]
        x, y = {(0, ()): Q(1)}, {(1, ()): Q(1)}
        middle = {(0, ()): Q(1), (1, ()): Q(1, 2)}
        final = {(0, ()): Q(3, 8), (1, ()): Q(19, 16)}
        digest, ledger = hashlib.sha256(), f.Ledger(True)
        m.macro(x, y, middle, recipe, 0, ledger, 1, digest)
        m.macro(y, middle, final, second, 0, ledger, 2, digest)
        with patch.object(
            f, "apply_event", side_effect=AssertionError("shared propagation forbidden")
        ):
            self.assertEqual(integer.trace(events, io.BytesIO(raw)), digest.hexdigest())

    def test_claim_comparison_and_corruptions(self):
        result = json.loads((verify.PACKAGE / "RESULT.json").read_text())
        claim = json.loads((verify.PACKAGE / "vendor/CLAIM-3090.json").read_text())
        self.assertEqual(verify.compare(result["providers"], claim)["cases"], 12)
        for field, bad in (
            ("recipe_sha256", "0" * 64),
            ("source_writes", -1),
            ("scratch_macros", -1),
        ):
            changed = copy.deepcopy(claim)
            changed["providers"]["base"]["streams"]["forward"]["policies"]["scratch"][
                field
            ] = bad
            with self.assertRaises(ValueError):
                verify.compare(result["providers"], changed)

    def test_literal_result_counts(self):
        result = json.loads((verify.PACKAGE / "RESULT.json").read_text())
        for provider in result["providers"].values():
            for policies in provider.values():
                for name, report in policies.items():
                    self.assertEqual(report["macros"], 9992)
                    self.assertEqual(
                        report["real_instruction_slots"],
                        64782 if name == "scratch" else 57710,
                    )
                    self.assertLessEqual(report["envelope"]["fractional_bits"], 7)
                    self.assertTrue(
                        f.capacity(report["combined_with_native"], 64, 7, 84)
                    )


if __name__ == "__main__":
    unittest.main()
