#!/usr/bin/env python3
"""Behavioral rejection and ownership controls for the joint backing bound."""

import copy
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "joint_backing", Path(__file__).with_name("verify.py")
)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class JointBackingTests(unittest.TestCase):
    def test_complete_native_cut(self):
        with VERIFY.source_modules() as m:
            result = VERIFY.run_case(m)
        self.assertEqual((result["peak"], result["live_peak"]), (134, 114))
        self.assertEqual(
            result["witness"],
            {"count": 32, "numerical": 102, "live_cells": 66, "phase": "native"},
        )

    def test_one_cell_short_and_observer_restoration(self):
        with VERIFY.source_modules() as m:
            original = m.words.Arena.zero
            with self.assertRaisesRegex(ValueError, "joint backing quota"):
                VERIFY.run_case(m, quota=133)
            self.assertIs(m.words.Arena.zero, original)
            self.assertEqual(VERIFY.run_case(m, quota=134)["peak"], 134)

    def test_warm_history_and_borrowed_residents(self):
        with VERIFY.source_modules() as m:
            result = VERIFY.run_case(m, warm_slots=32)
            resident = VERIFY.run_case(m, residents=7)
        self.assertEqual((result["peak"], result["slots"]), (536, [32, 16]))
        self.assertEqual(resident["peak"], resident["bound"])
        self.assertGreater(resident["peak"], 134)

    def test_released_and_captured_count_tapes(self):
        with VERIFY.source_modules() as m:
            released = VERIFY.run_case(m, count_scratch=2)
            captured = VERIFY.run_case(m, count_scratch=2, retain=True)
        self.assertEqual(released["peak"], 216)
        self.assertEqual((captured["peak"], captured["bound"]), (304, 216))

    def test_sources_reject_changed_runtime(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path, content in VERIFY.authenticate().items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            target = root / (VERIFY.PREFIX + "stream.py")
            target.write_bytes(target.read_bytes() + b"\n# altered source\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                VERIFY.authenticate(root)

    def test_module_scope_restores_preexisting_binding(self):
        old = sys.modules.get("words")
        sentinel = types.ModuleType("words")
        sys.modules["words"] = sentinel
        try:
            with VERIFY.source_modules() as m:
                self.assertEqual(VERIFY.run_case(m, alias=True)["peak"], 126)
            self.assertIs(sys.modules["words"], sentinel)
        finally:
            if old is None:
                sys.modules.pop("words", None)
            else:
                sys.modules["words"] = old

    def test_receipt_rejects_understatement_and_wrong_type(self):
        expected = json.loads((VERIFY.PACKAGE / "RESULT.json").read_text())
        for value in (133, True):
            changed = copy.deepcopy(expected)
            changed["cases"][0]["peak"] = value
            with self.assertRaisesRegex(ValueError, "typed result receipt"):
                VERIFY.check_receipt(expected, changed)


if __name__ == "__main__":
    unittest.main()
