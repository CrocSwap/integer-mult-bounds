#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal algebra expectations and real CLI failure controls."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify

ARCHIVE = verify.ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"


class ChartOrderTests(unittest.TestCase):
    def command(self, package=HERE, archive=ARCHIVE, optimized=False, extra=()):
        args = [sys.executable, "-I", "-B", "-Wall"]
        if optimized:
            args.append("-O")
        args += [str(package / "verify.py"), "--archive", str(archive), *extra]
        return subprocess.run(args, capture_output=True, text=True, timeout=30)

    def test_real_cli_standard_and_optimized(self):
        expected = ("PASS_SOURCE_CODE_CHART_ORDER orders=6,6,infinite trace=1456 "
                    "eigenvalue=170..171 columns=336 controls=4 no_new_kappa\n")
        before = (HERE / "RESULT.json").read_bytes()
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.command(optimized=optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")
        self.assertEqual((HERE / "RESULT.json").read_bytes(), before)

    def test_literal_pair_and_cubic(self):
        pair = verify.multiply(verify.small_action(True), verify.small_action())
        self.assertEqual(pair, [{0: 1, 2: 12}, {0: -156, 1: -11, 2: -2016},
                                {0: 14, 1: 1, 2: 181}])
        self.assertEqual(verify.polynomial3(pair), [-1, 27, -171, 1])
        self.assertEqual(verify.evaluate([-1, 27, -171, 1], 170), -24311)
        self.assertEqual(verify.evaluate([-1, 27, -171, 1], 171), 4616)
        self.assertEqual(verify.determinant3(pair), 1)

    def test_individual_order_and_same_chart_return(self):
        unit = [{0: 1}, {1: 1}, {2: 1}]
        for swapped in (False, True):
            action = verify.small_action(swapped)
            power = unit
            for exponent in range(1, 7):
                power = verify.multiply(action, power)
                self.assertEqual(power == unit, exponent == 6)
            pair = verify.multiply(action, action)
            self.assertEqual(verify.polynomial3(pair), [-1, 0, 0, 1])
            self.assertEqual(verify.multiply(verify.multiply(pair, pair), pair), unit)

    def test_query_source_and_section_dimensions(self):
        result = verify.run(ARCHIVE)
        self.assertEqual(result["query_sha256"],
                         "70055070e6f0465dcb9f99773769809f032043e7a1cba4f0c0fe5e5c365f0213")
        self.assertEqual(result["pair_trace"], 1456)
        self.assertEqual(result["pair_fixed_dimension"], 88)
        self.assertEqual(result["pair_active_dimension"], 24)
        self.assertEqual(result["semantic_failure_controls"], 4)

    def test_corrupt_archive_fails_before_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.tar.gz"
            raw = bytearray(ARCHIVE.read_bytes())
            raw[10] ^= 1
            bad.write_bytes(raw)
            result = self.command(archive=bad, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("archive pin mismatch", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_forged_receipt_is_rejected_without_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            path = package / "RESULT.json"
            data = json.loads(path.read_text())
            data["pair_trace"] = 112
            path.write_text(json.dumps(data))
            forged = path.read_bytes()
            result = self.command(package=package, optimized=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)
            self.assertEqual(path.read_bytes(), forged)
            self.assertEqual(result.stdout, "")

    def test_ambiguous_cut_and_register_bounds(self):
        word = {"v": 112, "R": 480, "h": 9, "centers": list(range(413, 421))}
        for program in ([], [["phase", "centers"], ["phase", "centers"]]):
            with self.assertRaisesRegex(ValueError, "ambiguous centre cut"):
                verify.extract_query(word, program)
        for port in (("L", 704), ("C", 8), ("L", -1), ("other", 0), ("L", True)):
            with self.assertRaises(ValueError):
                verify.register(port)
        self.assertEqual(verify.register(("L", 703)), 703)
        self.assertEqual(verify.register(("C", 7)), 711)

    def test_unknown_cli_option_is_rejected(self):
        result = self.command(extra=("--unknown-option",))
        self.assertEqual(result.returncode, 2)
        self.assertIn("unrecognized arguments", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
