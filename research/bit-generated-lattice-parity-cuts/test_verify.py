#!/usr/bin/env python3
# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Behavioral checks, independent oracles and actual relocated CLI mutants."""

import copy
import hashlib
import importlib.util
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
# A fixed local module, not user-selected code or a plugin.
spec = importlib.util.spec_from_file_location("parity_cuts", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def invoke(root, *args, optimized=False):
    command = [sys.executable, "-I", "-B"]
    if optimized:
        command.append("-O")
    return subprocess.run(command + [str(root / "verify.py"), *args], cwd=root,
                          text=True, capture_output=True, timeout=60, check=False)


def snapshot(root):
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.iterdir() if path.is_file()}


class ParityCutsTests(unittest.TestCase):
    def test_literal_eight_call_rejection(self):
        example = verify.read_json(HERE / "EXAMPLE.json")
        result = verify.screen(example)
        self.assertEqual(result["status"], "REJECT_GENERATED_LATTICE_PARITY_CUT")
        self.assertTrue(result["determinant_matches"])
        self.assertEqual(result["minimum_margin"], -2)
        self.assertEqual(result["characters_checked"], 64)
        self.assertEqual(result["witness"], {"basis_values": [1, 0, 0, 0, 0, 0],
                                           "paid_indices": [0], "target_indices": [0, 1, 2]})
        self.assertEqual(result["target_classes"], [[1, 1, 1, 0, 1, 0],
                                                   [1, 1, 0, 1, 1, 0],
                                                   [1, 0, 0, 0, 1, 1]])

    def test_unsaturated_lattice_and_fractional_values(self):
        value = verify.instance([(2, 0), (0, 2)], [(1, 0), (1, 2)])
        self.assertEqual(verify.screen(value)["outside_targets"], [0, 1])
        value = verify.instance([(2, 0), (0, 2)], [(2, 2)])
        result = verify.screen(value)
        self.assertEqual(result["target_classes"], [[1, 1]])
        self.assertTrue(result["status"].startswith("PASS_"))
        value = verify.instance([("1/2", 0), (0, "-1/3")], [("1/2", "-1/3")])
        self.assertTrue(verify.screen(value)["status"].startswith("PASS_"))
        for order in itertools.permutations((6, 10, 15)):
            result = verify.screen(verify.instance([(n, 0) for n in order], [(1, 0)]))
            self.assertEqual(result["basis"], ((1, 0, 0, 0),))
            self.assertEqual(result["target_classes"], [[1]])

    def test_independent_oracles_and_maximum_shape(self):
        self.assertEqual(verify.independent_oracle(), 3132)
        self.assertEqual(verify.relation_oracle(), 2544)
        units = [[[int(4 * i + j == k) for j in range(4)] for i in range(4)]
                 for k in range(12)]
        target = [[sum(matrix[i][j] for matrix in units) for j in range(4)] for i in range(4)]
        value = {"address_dimension": 4, "paid_frames": units,
                 "target_frames": [target] + [[[0] * 4 for _ in range(4)]] * 11}
        result = verify.screen(value)
        self.assertEqual(result["characters_checked"], 4096)
        self.assertTrue(result["status"].startswith("PASS_"))
        zeros = verify.screen(verify.instance([], [(0, 0)]))
        self.assertEqual(zeros["characters_checked"], 1)
        self.assertTrue(zeros["status"].startswith("PASS_"))
        self.assertEqual(verify.screen(verify.instance([], [(1, 0)]))["outside_targets"], [0])

    def test_determinant_and_invalid_boundaries(self):
        result = verify.screen(verify.instance([(1, 0)], [(3, 0)]))
        self.assertEqual(result["minimum_margin"], 0)
        self.assertEqual(result["status"], "REJECT_DETERMINANT")
        base = verify.instance([(1, 0)], [(1, 0)])
        invalid = []
        for bad in (True, 0, 5):
            value = copy.deepcopy(base)
            value["address_dimension"] = bad
            invalid.append(value)
        for bad in (True, 1.0, "1/0", "1/65536", 65536, "NaN"):
            value = copy.deepcopy(base)
            value["paid_frames"][0][0][0] = bad
            invalid.append(value)
        invalid.extend([verify.instance([(0, 0)], [(1, 0)]),
                        verify.instance([(1, 0)] * 13, [(1, 0)]),
                        verify.instance([(1, 0)], [(1, 0)] * 13),
                        {"address_dimension": 2, "paid_frames": [[[1, 0], [0, 1]]],
                         "target_frames": [[[1, 0], [0, 1]]]}, {}])
        for value in invalid:
            with self.subTest(value=value), self.assertRaises((ValueError, ZeroDivisionError)):
                verify.screen(value)
        with self.assertRaisesRegex(ValueError, "integer capacity"):
            verify.bounded([1 << 4096])
        primes = (65521, 65519, 65497, 65479, 65449, 65447,
                  65437, 65423, 65419, 65413, 65407, 65393)
        with self.assertRaisesRegex(ValueError, "common denominator capacity"):
            verify.screen(verify.instance([(f"1/{p}", 0) for p in primes], [(0, 0)]))

    def test_relocated_cli_and_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("verify.py", "EXAMPLE.json", "RESULT.json"):
                shutil.copyfile(HERE / name, root / name)
            before = snapshot(root)
            for optimized in (False, True):
                result = invoke(root, optimized=optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("PASS_GENERATED_LATTICE_PARITY_CUTS", result.stdout)
            rejection = invoke(root, "--input", str(root / "EXAMPLE.json"))
            self.assertEqual(rejection.returncode, 1, rejection.stderr)
            self.assertEqual(json.loads(rejection.stdout)["minimum_margin"], -2)
            self.assertEqual(snapshot(root), before)
            (root / "positive.json").write_text(json.dumps(verify.instance([(2, 0)], [(2, 0)])))
            self.assertEqual(invoke(root, "--input", str(root / "positive.json")).returncode, 0)
            for data in ('{"a":1,"a":2}', '[' * 2000 + '0' + ']' * 2000, ' ' * 65537):
                (root / "invalid.json").write_text(data)
                result = invoke(root, "--input", str(root / "invalid.json"))
                self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(invoke(root, "--input", str(root / "missing.json")).returncode, 2)
            self.assertEqual(invoke(root, "--input", str(root / "positive.json"), "--write").returncode, 2)

    def test_actual_implementation_and_receipt_mutants(self):
        source = (HERE / "verify.py").read_text()
        mutants = [
            ("return tuple(tuple(row) for row in work[:pivot])",
             "return tuple(tuple(x // math.gcd(*row) for x in row) for row in work[:pivot])"),
            ("result.update(character_cut(p, t, len(basis)))",
             "result.update(character_cut(integer_paid, integer_targets, dimension**2))"),
            ("if len(p) - len(t) < best[0]:", "if False:"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("EXAMPLE.json", "RESULT.json"):
                shutil.copyfile(HERE / name, root / name)
            for old, new in mutants:
                self.assertEqual(source.count(old), 1)
                (root / "verify.py").write_text(source.replace(old, new))
                result = invoke(root, optimized=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("receipt mismatch", result.stderr)
            (root / "verify.py").write_text(source)
            for key, value in (("minimum_margin", -1), ("unused", False), ("unused", 0.0)):
                receipt = json.loads((HERE / "RESULT.json").read_text())
                if key == "minimum_margin":
                    receipt["example"][key] = value
                else:
                    receipt["direct_nine_calls"]["minimum_margin"] = value
                (root / "RESULT.json").write_text(json.dumps(receipt))
                result = invoke(root)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("receipt mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
