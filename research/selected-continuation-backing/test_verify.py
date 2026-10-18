#!/usr/bin/env python3
"""Behavioral checks of literal tape lengths and actual quota failures."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "backing_check", Path(__file__).with_name("verify.py")
)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class BackingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.predecessor = CHECK.authenticate()
        cls.modules = cls.predecessor.load_source()

    def run_case(self, modes="BB", bits=4, **options):
        return CHECK.execute(self.predecessor, self.modules, modes, bits, **options)

    def test_binary_tape_lengths(self):
        result = self.run_case()
        self.assertEqual(result["lengths"], (111, 32, 22, 7))
        self.assertEqual(result["backing"], 172)

    def test_depth_zero_scalar_dominant_exactness(self):
        result = self.run_case("", 32)
        self.assertEqual(result["lengths"], (21, 20, 36, 35))
        self.assertEqual(result["backing"], 112)

    def test_scalar_dominant_bound_is_conservative(self):
        result = self.run_case("BB", 32)
        self.assertEqual(result["lengths"], (167, 35, 106, 35))
        self.assertEqual((result["backing"], result["bound"]), (343, 352))

    def test_one_cell_short_rejects_and_methods_restore(self):
        write, pop = self.modules[1].Tape.write, self.modules[1].Stack.pop
        weight = self.modules[2].Callback.weight
        with self.assertRaisesRegex(ValueError, "directional tape capacity"):
            self.run_case(short=1)
        self.assertIs(self.modules[1].Tape.write, write)
        self.assertIs(self.modules[1].Stack.pop, pop)
        self.assertIs(self.modules[2].Callback.weight, weight)
        self.assertEqual(self.run_case()["backing"], 172)

    def test_erased_backing_outlives_live_content(self):
        with self.assertRaisesRegex(ValueError, "joint tape capacity"):
            self.run_case(total_quota=114)
        self.assertEqual(self.run_case()["live_peak"], 110)
        self.assertEqual(self.run_case()["backing"], 172)

    def test_warm_history_and_repeated_evaluation(self):
        self.assertEqual(self.run_case(repeats=2)["backing"], 172)
        result = self.run_case(warm=(500, 70, 90, 40), repeats=2)
        self.assertEqual(result["lengths"], (500, 70, 90, 40))
        self.assertEqual(result["backing"], 700)
        with self.assertRaisesRegex(ValueError, "joint tape capacity"):
            self.run_case(warm=(500, 70, 90, 40), total_quota=172)
        self.assertEqual(self.run_case()["backing"], 172)

    def test_bad_manifest_fails_before_source_execution(self):
        manifest = json.loads((CHECK.PACKAGE / "SOURCES.json").read_text())
        item = next(item for item in manifest["files"] if item["usage"] == "input")
        item["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            (temporary / "SOURCES.json").write_text(json.dumps(manifest))
            with patch.object(CHECK, "PACKAGE", temporary):
                with self.assertRaisesRegex(ValueError, "predecessor SHA256"):
                    CHECK.authenticate()

    def test_invalid_fixture_boundary(self):
        for modes, bits, options in (
            ("BBBBBBB", 4, {}),
            ("X", 4, {}),
            ("BB", True, {}),
            ("BB", 4, {"repeats": 3}),
        ):
            with self.assertRaisesRegex(ValueError, "bounded fixture"):
                self.run_case(modes, bits, **options)
        self.assertEqual(self.run_case()["backing"], 172)

    def test_literal_fixture_rejects_mislabelled_parameters(self):
        for modes, bits, repeats in (("G", 3, 1), ("BB", 4, 1), ("BB", 3, 2)):
            with self.assertRaisesRegex(ValueError, "literal GL64 fixture"):
                self.run_case(modes, bits, literal=True, repeats=repeats)
        self.assertEqual(self.run_case()["backing"], 172)


if __name__ == "__main__":
    unittest.main()
