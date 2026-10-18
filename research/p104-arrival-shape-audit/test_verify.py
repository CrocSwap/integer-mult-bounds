#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the literal arrival counterexample."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import verify as subject


class ArrivalControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.witness, fixture = subject.load_inputs()
        cls.matrix = subject.correction(fixture)
        cls.word = subject.make_word(cls.witness, cls.matrix)

    def reject_endpoint(self, word):
        rows, _, _ = subject.execute(word)
        with self.assertRaisesRegex(ValueError, "arbitrary-input endpoint"):
            subject.check_endpoints(rows)

    def test_positive_complete_word_and_literal_pair(self):
        result = subject.audit()
        self.assertEqual(result["events"], 39002)
        self.assertEqual(result["registers"], 5272)
        self.assertEqual(result["added_profile"], {1: 9984, 7: 4992})
        rows, _, _ = subject.execute(self.word)
        self.assertEqual(rows["Y0"], {"Y0": 1, "X0": 1})
        self.assertEqual(rows["H0_2"], {"H0_2": 1})
        self.assertEqual(
            self.word["program"][:3],
            [
                ["add", "Y0", "H0_2", "-1", []],
                ["transport", "H0_2", [], [228], 1],
                ["add", "H0_2", "X2", "-1/2", [228]],
            ],
        )

    def test_missing_dirty_compensation_rejects(self):
        bad = copy.deepcopy(self.word)
        bad["program"][0][3] = "0"
        self.reject_endpoint(bad)

    def test_wrong_delivery_and_lost_helper_cleanup_reject(self):
        for offset in (0, 2):
            bad = copy.deepcopy(self.word)
            # Four initial events per carrier, followed by the frozen core.
            position = 4 * 4992 + 4058 + offset
            bad["program"][position][3] = "0"
            self.reject_endpoint(bad)

    def test_wrong_coefficient_rejects(self):
        bad = copy.deepcopy(self.word)
        bad["program"][2][3] = "1/2"
        self.reject_endpoint(bad)

    def test_wrong_frame_and_rank_reject(self):
        for field, value, message in (
            (4, 6, "transport rank"),
            (2, [1], "transport entry"),
            (3, [228], "monotone carrier"),
        ):
            bad = copy.deepcopy(self.word)
            bad["program"][3][field] = value
            with self.assertRaisesRegex(ValueError, message):
                subject.execute(bad)

    def test_early_cleanup_rejects(self):
        bad = copy.deepcopy(self.word)
        first_final = 4 * 4992 + 4058
        cleanup = bad["program"].pop(first_final + 2)
        bad["program"].insert(4, cleanup)
        with self.assertRaisesRegex(ValueError, "common addition frame"):
            subject.execute(bad)

    def test_equivalent_binary_bases_pass(self):
        equivalent = copy.deepcopy(self.word)
        for value in equivalent["initial_frames"].values():
            value.reverse()
        for value in equivalent["final_frames"].values():
            value.reverse()
        for event in equivalent["program"]:
            fields = (2, 3) if event[0] == "transport" else (-1,)
            for field in fields:
                event[field] = list(reversed(event[field]))
        rows, profile, _ = subject.execute(equivalent)
        subject.check_endpoints(rows)
        self.assertEqual(profile[7], 5000)

    def test_capacity_and_input_pins_reject(self):
        bad = copy.deepcopy(self.word)
        bad["program"].append(bad["program"][0])
        with self.assertRaisesRegex(ValueError, "event capacity"):
            subject.execute(bad)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            original = subject.PACKAGE
            sources = json.loads((original / "SOURCES.json").read_text())
            sources["files"][2]["sha256"] = "0" * 64
            (package / "SOURCES.json").write_text(json.dumps(sources))
            try:
                subject.PACKAGE = package
                with self.assertRaisesRegex(ValueError, "source pin"):
                    subject.load_inputs()
            finally:
                subject.PACKAGE = original

    def test_optimized_cli_receipt_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "receipt.json"
            argv = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(subject.PACKAGE / "verify.py"),
                "--out",
                str(output),
                "--relay-word",
                str(Path(directory) / "word.json"),
            ]
            env = dict(os.environ, PYTHONOPTIMIZE="2")
            done = subprocess.run(
                argv, capture_output=True, text=True, check=True, timeout=30, env=env
            )
            receipt = json.loads(output.read_text())
            self.assertEqual(receipt["added_rank_mass"], 44928)
            self.assertEqual(json.loads(done.stdout), receipt)
            word = json.loads((Path(directory) / "word.json").read_text())
            self.assertEqual(word["lifetimes"], 4992)
            self.assertEqual(len(word["ops"]), 34945)
            self.assertEqual(
                word["ops"][:4],
                [
                    ["move_zero_all", 4992],
                    ["write", 0, 0, "-1", 0],
                    ["move", 0, [228]],
                    ["read", 0, 2, "-1/2", 0],
                ],
            )
            failed = subprocess.run(
                argv, capture_output=True, text=True, check=False, timeout=30, env=env
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("FileExistsError", failed.stderr)
            self.assertEqual(json.loads(output.read_text()), receipt)


if __name__ == "__main__":
    unittest.main()
