#!/usr/bin/env python3
"""Source/transport/acceptance-tool unit tests. No Lean compiler is invoked.
Synthetic strings below test only parser behavior and are NOT compiler receipts.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import copy
import hashlib
import json
import unittest
from generate import (ROOT, JSON_SHA, BRIDGE_SHA, validate_values, load_source,
                      reject_duplicate_keys, check_generated)
from check_numeric import read_emitted_values, numeric_result
from audit_sources import audit
from check_axioms import parse_records
from replay import (ReplayFailure, check_positive, check_negative,
                    validate_version, VERSION, COMMIT)


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.obj = load_source(ROOT)
        cls.data_text = (ROOT / "P112Data.lean").read_text(encoding="utf-8")

    def test_01_pins_and_full_regeneration(self) -> None:
        self.assertEqual(hashlib.sha256((ROOT/"P112.json").read_bytes()).hexdigest(), JSON_SHA)
        self.assertEqual(hashlib.sha256((ROOT/"PR1497Bridge.lean").read_bytes()).hexdigest(), BRIDGE_SHA)
        self.assertEqual(check_generated(ROOT)["generated_files"], 39)

    def test_02_inverse_parser_recovers_every_field(self) -> None:
        self.assertEqual(read_emitted_values(self.data_text), self.obj)

    def test_03_all_matrix_identities_and_real_corruption(self) -> None:
        result = numeric_result(self.obj)
        self.assertEqual(result["identity_scalar_obligations"], 21409)
        self.assertEqual(len(result["damaged_residual_mismatches_row_column_lhs_rhs"]), 4)
        self.assertFalse(result["new_lean_executed"])

    def test_04_unknown_input_field_rejected(self) -> None:
        obj = copy.deepcopy(self.obj)
        obj["unused"] = 1
        with self.assertRaises(ValueError): validate_values(obj)

    def test_05_duplicate_json_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            json.loads('{"rank":71,"rank":71}', object_pairs_hook=reject_duplicate_keys)

    def test_06_duplicate_sparse_column_rejected(self) -> None:
        obj = copy.deepcopy(self.obj)
        obj["M"][0][1][0] = obj["M"][0][0][0]
        with self.assertRaises(ValueError): validate_values(obj)

    def test_07_out_of_range_column_rejected(self) -> None:
        obj = copy.deepcopy(self.obj)
        obj["W"][5][0][0] = 288
        with self.assertRaises(ValueError): validate_values(obj)

    def test_08_empty_row_and_metadata_changes_are_visible(self) -> None:
        changed = self.data_text.replace("[] -- /W/0", "[(⟨0, by decide⟩, (1 : Int))] -- /W/0", 1)
        self.assertNotEqual(read_emitted_values(changed), self.obj)
        changed = self.data_text.replace("def rankMetadata : Nat := 71", "def rankMetadata : Nat := 72", 1)
        self.assertNotEqual(read_emitted_values(changed), self.obj)

    def test_09_complete_census(self) -> None:
        report = audit(ROOT)
        self.assertEqual(report["inherited_named_queries"], 159)
        self.assertEqual(report["new_named_queries"], 477)
        self.assertEqual(report["new_theorems"], 457)


class AcceptanceTests(unittest.TestCase):
    SOURCE = "#print axioms Toy.only\n"
    LOG = "'Toy.only' does not depend on any axioms\n"
    FALSE = "fixtures/RejectDamagedW.lean:18:2: error: Tactic `decide` proved that the proposition\n  1 = -1\nis false\n"

    def test_10_synthetic_positive_parser(self) -> None:
        self.assertEqual(check_positive(self.SOURCE, self.LOG, "", 0, True), {"Toy.only": []})

    def test_11_errors_warnings_missing_olean_never_pass(self) -> None:
        for text, stderr, rc, present in [(self.LOG, "", 1, True), (self.LOG, "", 0, False),
                                         (self.LOG+"file:1:1: error: bad\n", "", 0, True),
                                         (self.LOG+"file:1:1: warning: bad\n", "", 0, True),
                                         (self.LOG, "unexpected stderr", 0, True)]:
            with self.assertRaises((ReplayFailure, ValueError)):
                check_positive(self.SOURCE, text, stderr, rc, present)

    def test_12_axioms_and_missing_duplicate_census_rejected(self) -> None:
        for text in ["'Toy.only' depends on axioms: [sorryAx]\n", "", self.LOG+self.LOG,
                     "'Toy.other' does not depend on any axioms\n"]:
            with self.assertRaises((ReplayFailure, ValueError)):
                check_positive(self.SOURCE, text, "", 0, True)
        self.assertEqual(parse_records("'Toy.x' depends on axioms: [propext, Quot.sound]\n"),
                         {"Toy.x": ["Quot.sound", "propext"]})

    def test_13_negative_requires_exact_mathematical_failure(self) -> None:
        check_negative(self.FALSE, "", 1, False)
        for text, rc, present in [("file:1:1: error: unknown module\n", 1, False),
                                 (self.FALSE, 0, False), (self.FALSE, 1, True),
                                 (self.FALSE, -9, False), (self.FALSE+self.FALSE, 1, False),
                                 (self.FALSE.replace("1 = -1", "True = False"), 1, False)]:
            with self.assertRaises(ReplayFailure): check_negative(text, "", rc, present)

    def test_14_exact_toolchain_identity_required(self) -> None:
        validate_version(VERSION+"\n", COMMIT+"\n")
        for v, c in [("4.29.0", COMMIT), (VERSION, "0"*40), (VERSION+"-rc1", COMMIT)]:
            with self.assertRaises(ReplayFailure): validate_version(v, c)


if __name__ == "__main__":
    unittest.main(verbosity=2)
