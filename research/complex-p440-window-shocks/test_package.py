#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Semantic and fail-closed controls for the scoped donor-window result."""
import copy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


V, ORACLE = module("verify"), module("independent")


class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = V.load_word(HERE / "inputs/BASE-WORD.json.gz")

    def test_unbounded_coefficients_and_singular_systems(self):
        columns = [{0: Q(2), 1: Q(3)}, {0: Q(-1), 2: Q(5)}]
        target = V.plus({k: v * Q(17, 31) for k, v in columns[0].items()}, columns[1], Q(-19, 23))
        self.assertTrue(V.in_span(columns, target))
        self.assertEqual(ORACLE.integer_rank(columns), ORACLE.integer_rank(columns + [target]))
        self.assertFalse(V.in_span(columns, {**target, 3: Q(1)}))
        self.assertGreater(ORACLE.integer_rank(columns + [{**target, 3: Q(1)}]), ORACLE.integer_rank(columns))
        self.assertTrue(V.in_span([columns[0], columns[0]], {k: Q(7, 9) * v for k, v in columns[0].items()}))
        self.assertFalse(V.in_span([columns[0], columns[0]], columns[1]))
        self.assertTrue(V.in_span([{}, {}], {}))
        self.assertFalse(V.in_span([{}, {}], {9: Q(1)}))

    def test_anchor_pruning_accepts_planted_repairs(self):
        for directions in [
            [((588, 1),)],
            [((0, 1), (588, 1)), ((0, 1),)],
            [((0, 1), (588, 1)), ((1, 1), (588, 1)), ((0, 1), (1, 1))],
            [((0, 1), (588, 1)), ((1, 1), (588, 1)), ((0, -1), (1, -1), (588, 1))],
        ]:
            # Add an unrelated padding direction for the first planted case.
            with self.assertRaisesRegex(ValueError, "repair exists"):
                V.exclude_three({588: Q(1)}, directions + [((9, 1),)])

    def test_windows_stop_at_writes_and_are_bounded(self):
        word = {
            "B": [["add", 1, 0, 1, 1, []], ["add", 2, 0, 1, 1, []],
                  ["scale", 0, 2, 1, []], ["add", 3, 0, 1, 1, []],
                  ["add", 4, 0, 1, 1, []], ["add", 5, 0, 1, 1, []]],
            "cleanup": [], "early_cleanup": [],
        }
        _, windows, _, _ = V.enumerate_windows(word, pivot=9, max_reads=2)
        actual = [(w["start"], w["end"]) for w, _ in windows if w["donor"] == 0]
        self.assertEqual(actual, [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6)])
        for window, response in windows:
            pulses = {window["start"]: [(window["donor"], Q(1))], window["end"]: [(window["donor"], Q(-1))]}
            self.assertEqual(response, ORACLE.run(word["B"], {}, pulses))

    def test_pivot_write_is_rejected(self):
        bad = copy.deepcopy(self.word)
        bad["B"].insert(100, ["scale", 440, 2, 1, []])
        with self.assertRaisesRegex(ValueError, "pivot is written"):
            V.enumerate_windows(bad)
        with self.assertRaisesRegex(ValueError, "pivot is not constant"):
            ORACLE.direct_windows(bad)

    def test_scalar_shocks_superpose_even_when_windows_overlap(self):
        # The added operations are all shears from the unchanged pivot, so
        # overlapping donor windows still add their endpoint error columns.
        gates = [["add", 1, 0, 2, 1], ["add", 2, 1, -3, 2], ["add", 3, 0, 1, 1]]
        first = {0: [(0, Q(5, 7))], 3: [(0, Q(-5, 7))]}
        second = {1: [(1, Q(-2, 3))], 2: [(1, Q(2, 3))]}
        union = {k: first.get(k, []) + second.get(k, []) for k in set(first) | set(second)}
        self.assertEqual(ORACLE.run(gates, {}, union), V.plus(ORACLE.run(gates, {}, first), ORACLE.run(gates, {}, second)))

    def test_actual_source_and_receipt_corruptions(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            source = bytearray((HERE / "inputs/BASE-WORD.json.gz").read_bytes())
            source[-5] ^= 1
            (p / "bad.gz").write_bytes(source)
            saved = json.loads((HERE / "CERTIFICATE.json").read_text())
            saved["nonzero_windows"] += 1
            (p / "bad.json").write_text(json.dumps(saved))
            sources = json.loads((HERE / "SOURCES.json").read_text())
            sources["vendored_inputs"][0]["source_commit"] = "0" * 40
            (p / "bad-sources.json").write_text(json.dumps(sources))
            for args, expected in [(["--word", str(p / "bad.gz")], "word SHA256 mismatch"),
                                   (["--certificate", str(p / "bad.json")], "saved certificate mismatch"),
                                   (["--sources", str(p / "bad-sources.json")], "vendored source identity mismatch")]:
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), *args],
                                        capture_output=True, text=True, cwd=p, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
                self.assertNotIn("PASS_P440", result.stdout)

    def test_four_window_map_and_adverse_changes(self):
        baseline = ORACLE.literal_map(self.word)
        honest = V.positive_windows()
        self.assertEqual(ORACLE.literal_map(self.word, honest), baseline)
        self.assertNotEqual(ORACLE.literal_map(self.word, honest, omit_close=True), baseline)
        for index in range(4):
            bad = copy.deepcopy(honest)
            bad[index]["coefficient"] = str(-Q(bad[index]["coefficient"]))
            self.assertNotEqual(ORACLE.literal_map(self.word, bad), baseline)
        # Wrongly keep one removed old read: compare against its separate
        # full linear response, which is nonzero on arbitrary input columns.
        modified = copy.deepcopy(self.word)
        modified["B"][928][3] = 2
        self.assertNotEqual(ORACLE.literal_map(modified), baseline)


if __name__ == "__main__":
    unittest.main(verbosity=2)
