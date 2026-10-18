# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the exact native-cost replacement and its boundary."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import verify
from contract import FRAME, NEW, OLD, START, expected_cleanup, operator
from tariff import (
    INVERSE,
    OPTIMAL,
    TARGET,
    bounded_exclusions,
    lower_bound,
    matrix,
    price,
    produce,
)


class TariffTests(unittest.TestCase):
    def test_block_maps_and_prices(self):
        self.assertEqual([matrix(g) for g in (OLD, NEW, OPTIMAL)], [TARGET] * 3)
        self.assertEqual(
            [sum(map(price, g)) for g in (OLD, NEW, OPTIMAL)], [16, 13, 10]
        )
        self.assertEqual(lower_bound(TARGET), 10)
        self.assertEqual(lower_bound(INVERSE), 10)
        self.assertEqual(bounded_exclusions(), 368)

    def test_dirty_inputs_and_exact_inverse(self):
        inverse = [
            ["scale", 230, 1, -1, FRAME],
            ["scale", 22, 1, -1, FRAME],
            ["add", 22, 230, -1, 1, FRAME],
            ["add", 230, 22, 1, 1, FRAME],
        ]
        self.assertEqual(matrix(inverse), INVERSE)
        self.assertEqual(sum(map(price, inverse)), 10)
        rows = operator(OPTIMAL, (22, 230))
        for x in range(-5, 6):
            for y in range(-5, 6):
                inputs = {22: Fraction(x, 8), 230: Fraction(y, 4)}
                outputs = tuple(
                    sum(q * inputs[c] for c, q in rows[r].items()) for r in (22, 230)
                )
                self.assertEqual(outputs, (-inputs[230], inputs[22] - inputs[230]))
        self.assertEqual(
            operator(OPTIMAL + inverse, (22, 230)),
            {22: {22: Fraction(1)}, 230: {230: Fraction(1)}},
        )

    def test_lower_bound_hypotheses_are_necessary(self):
        cheap = OLD[:2]
        self.assertEqual(sum(map(price, cheap)), 8)
        with self.assertRaisesRegex(ValueError, "two unscaled ADDs"):
            lower_bound(matrix(cheap))
        det_minus_one = [*cheap, ["scale", 230, -1, 1, FRAME]]
        self.assertEqual(sum(map(price, det_minus_one)), 9)
        with self.assertRaisesRegex(ValueError, "unit determinant"):
            lower_bound(matrix(det_minus_one))
        with self.assertRaisesRegex(ValueError, "both ADD directions"):
            lower_bound(((-1, 0), (0, -1)))

    def test_tariff_accepts_reduced_dyadics_and_rejects_other_alphabets(self):
        for a, b, expected in (
            (1, 1, 4),
            (-1, 1, 4),
            (2, 1, 5),
            (1, 2, 5),
            (2, 2, 4),
            (3, 4, 8),
        ):
            self.assertEqual(price(["add", 22, 230, a, b, FRAME]), expected)
        for a, b, expected in ((1, 1, 0), (-1, 1, 1), (2, 1, 1), (1, 2, 1)):
            self.assertEqual(price(["scale", 22, a, b, FRAME]), expected)
        for gate in (
            ["add", 22, 230, 1, 3, FRAME],
            ["add", 22, 230, 0, 1, FRAME],
            ["scale", 22, 3, 1, FRAME],
            ["scale", 22, 0, 1, FRAME],
        ):
            with self.assertRaises(ValueError):
                price(gate)


class WordTests(unittest.TestCase):
    def setUp(self):
        self.parent = verify.read(verify.PACKAGE / "vendor/WORD-base.json.gz")

    def test_both_literal_provider_outputs(self):
        for variant in ("base", "extra"):
            parent = verify.read(verify.PACKAGE / f"vendor/WORD-{variant}.json.gz")
            candidate = produce(parent)
            result = verify.check_words(parent, candidate)
            self.assertEqual(result["local_profile"], verify.LOCAL)
            self.assertEqual(result["helper_count"], 408)
            self.assertEqual(result["private_buffers"], 91)
            self.assertEqual(candidate["restore"][START : START + 4], OPTIMAL)
            self.assertEqual(len(candidate["restore"]), 212)
            self.assertEqual(len(candidate["cleanup"]), 5216)
            self.assertEqual(candidate["cleanup"], expected_cleanup(candidate))
            self.assertEqual(parent["restore"][START : START + 4], OLD)

    def test_semantic_negation_and_cleanup_defects(self):
        candidate = produce(self.parent)
        candidate["restore"][START + 2][2] = 1
        candidate["cleanup"] = expected_cleanup(candidate)
        with self.assertRaisesRegex(ValueError, "one literal tariff replacement"):
            verify.check_words(self.parent, candidate)
        self.assertNotEqual(
            operator(self.parent["restore"], range(704)),
            operator(candidate["restore"], range(704)),
        )
        candidate = produce(self.parent)
        candidate["cleanup"] = self.parent["cleanup"]
        with self.assertRaisesRegex(ValueError, "candidate cleanup"):
            verify.check_words(self.parent, candidate)

    def test_literal_preimage_is_required(self):
        wrong = copy.deepcopy(self.parent)
        wrong["restore"][START][3] = 1
        with self.assertRaisesRegex(ValueError, "literal PR3042 block"):
            produce(wrong)

    def test_unrelated_state_changes_are_rejected(self):
        candidate = produce(self.parent)
        candidate["report"]["local_profile"]["1"] += 1
        with self.assertRaisesRegex(ValueError, "other word section"):
            verify.check_words(self.parent, candidate)
        candidate = produce(self.parent)
        candidate["helper_final"]["230"] = [256, 128, 64, 32, 16, 8, 4]
        with self.assertRaises(ValueError):
            verify.check_words(self.parent, candidate)

    def test_native_endpoint_alone_does_not_certify_restore_or_derived_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, defect in enumerate(("sign", "cleanup")):
                candidate = produce(self.parent)
                if defect == "sign":
                    candidate["restore"][START + 2][2] = 1
                    candidate["cleanup"] = expected_cleanup(candidate)
                else:
                    candidate["cleanup"] = self.parent["cleanup"]
                compiled = verify.compile_word(candidate, Path(directory) / str(index))
                self.assertEqual(compiled["checks"]["forward"]["all_columns"], 632)
                self.assertEqual(
                    compiled["checks"]["forward"]["zero_buffers_returned_to_zero"], 91
                )
                with self.assertRaises(ValueError):
                    verify.check_words(self.parent, candidate)

    def test_native_transport_rejects_nonmonotone_frame(self):
        candidate = produce(self.parent)
        candidate["restore"][START + 2][-1] = [256]
        candidate["cleanup"] = expected_cleanup(candidate)
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaises(subprocess.CalledProcessError),
        ):
            verify.compile_word(candidate, Path(directory) / "wrong-frame")

    def test_source_inventory_and_bytes(self):
        self.assertEqual(verify.check_pins(), 11)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertRaisesRegex(
                ValueError, "bounded input file", verify.read, root / "missing"
            )
            path = root / "invalid.json"
            path.write_text("not json", encoding="utf-8")
            self.assertRaises(json.JSONDecodeError, verify.read, path)
        oversized = copy.deepcopy(self.parent)
        oversized["restore"] = [OLD[0]] * 1001
        with self.assertRaisesRegex(ValueError, "bounded word section"):
            verify.validate_word(oversized)

    def test_copied_source_byte_and_inventory_mutants(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            records = verify.read(verify.PACKAGE / "VENDOR.json")
            for record in records["files"]:
                target = root / record["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.PACKAGE / record["path"], target)
            shutil.copyfile(verify.PACKAGE / "SOURCES.json", root / "SOURCES.json")
            (root / "VENDOR.json").write_text(json.dumps(records), encoding="utf-8")
            with patch.object(verify, "PACKAGE", root):
                self.assertEqual(verify.check_pins(), 11)
                short = copy.deepcopy(records)
                short["files"].pop()
                (root / "VENDOR.json").write_text(json.dumps(short), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "complete frozen input"):
                    verify.check_pins()
                (root / "VENDOR.json").write_text(json.dumps(records), encoding="utf-8")
                target = root / "vendor/native/bw_emit.py"
                target.write_bytes(target.read_bytes() + b"\n")
                with self.assertRaisesRegex(ValueError, "frozen input hash"):
                    verify.check_pins()

    def test_ledger_controls_against_real_emitted_program(self):
        with tempfile.TemporaryDirectory() as directory:
            compiled = verify.compile_word(
                produce(self.parent), Path(directory) / "valid"
            )
            events = compiled["programs"]["forward"]
            checks = compiled["checks"]["forward"]
            self.assertEqual(checks["real_component_primitive_bound"], 158124)
            verify.check_ledger(checks, events)
            for field, value in (
                ("real_component_primitive_bound", 158125),
                ("all_columns", 631),
                ("zero_buffers_returned_to_zero", 90),
                ("scalar_macros", 17448),
                ("sha256", "0" * 64),
            ):
                bad = copy.deepcopy(checks)
                bad[field] = value
                with self.assertRaises(ValueError):
                    verify.check_ledger(bad, events)
            changed = copy.deepcopy(events)
            next(e for e in changed if e[0] == "climb")[5] = 99
            with self.assertRaisesRegex(ValueError, "child recount"):
                verify.check_ledger(checks, changed)

    def test_fresh_workspace_and_optimized_cli_refusal(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ValueError, "fresh compiler workspace"),
        ):
            verify.compile_word(self.parent, Path(directory))
        result = subprocess.run(
            [sys.executable, "-O", "-B", str(verify.PACKAGE / "verify.py")],
            capture_output=True,
            text=True,
            timeout=10,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("require assertions", result.stderr)


if __name__ == "__main__":
    unittest.main()
