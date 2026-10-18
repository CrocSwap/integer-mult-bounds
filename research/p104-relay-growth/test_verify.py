# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the actual pinned relay, including optimized exports."""

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("relay_growth", PACKAGE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


class RelayControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.witness, cls.fixture, cls.word = V.load_inputs()
        cls.correction, cls.initial, cls.final = V.geometry(cls.witness, cls.fixture)
        cls.gates, _, _ = V.check_word(cls.word, cls.initial, cls.final)

    def test_complete_endpoint_and_growth(self):
        result = V.audit(self.witness, self.fixture, self.word)
        self.assertEqual(result["forward"]["max_row_l1"], "70")
        self.assertEqual(result["logical_inverse_transpose"]["max_row_l1"], "56")
        for direction in ("forward", "logical_inverse_transpose"):
            self.assertEqual(result[direction]["max_denominator_exponent"], 3)
            self.assertEqual(result[direction]["endpoint_coefficients"], 1535121)
        self.assertEqual(result["rank_mass"], 9279)
        self.assertEqual(result["fixed_template"]["overfill"], "4935")

    def test_actual_endpoint_faults_in_both_directions(self):
        # Preserve all frame contacts. Reject these on the complete linear map.
        early = next(i for i, gate in enumerate(self.gates) if 104 <= gate[1] < 208)
        for name in ("missing_dirty_compensation", "wrong_scalar", "missing_cleanup"):
            gates = list(self.gates)
            if name == "missing_dirty_compensation":
                gates.pop(early)
            elif name == "wrong_scalar":
                p, dst, src, n, e = gates[early]
                gates[early] = (p, dst, src, -n, e)
            else:
                gates.pop()
            for dual in (False, True):
                with self.subTest(fault=name, dual=dual):
                    with self.assertRaisesRegex(ValueError, "endpoint coefficient"):
                        V.replay(gates, self.correction, dual=dual)

    def test_frame_chronology_and_capacity_faults(self):
        faults = ("nonnested", "wrong_source", "early_write", "missing_move", "index", "capacity")
        for name in faults:
            word = copy.deepcopy(self.word)
            ops = word["ops"]
            if name == "nonnested":
                next(op for op in ops if op[0] == "move")[2] = []
            elif name == "wrong_source":
                next(op for op in ops if op[0] == "read")[2] = 0
            elif name == "early_write":
                next(op for op in ops if op[0] == "write" and op[4] == 4058)[4] = 0
            elif name == "missing_move":
                i = max(i for i, op in enumerate(ops) if op[0] == "move")
                ops.pop(i)
            elif name == "index":
                next(op for op in ops if op[0] == "read")[1] = 1031
            else:
                ops.append(ops[-1])
            with self.subTest(fault=name):
                with self.assertRaises(ValueError):
                    V.check_word(word, self.initial, self.final)

    def test_equivalent_binary_bases(self):
        word = copy.deepcopy(self.word)
        for op in word["ops"]:
            if op[0] == "move" and 1 < len(op[2]) < 9:
                a, b, *rest = op[2]
                op[2] = [b, a ^ b, *reversed(rest)]
        gates, profile, counts = V.check_word(word, self.initial, self.final)
        self.assertEqual(gates, self.gates)
        self.assertEqual(sum(r * n for r, n in profile.items()), 9279)
        self.assertEqual(counts["move"], 4840)

    def test_transient_growth_with_unchanged_endpoint(self):
        # All added operands are restored FULL-frame helpers. These gate-level
        # controls exceed the fixed word's event cap and do not replace its input.
        gates = list(self.gates)
        first = 208
        for sign in (1, -1):
            for _ in range(20):
                gates.append((len(gates) + V.EVENTS, first, first + 1, 4 * sign, 0))
        for dst, src, sign in ((first, first + 1, 1), (first + 2, first, 1),
                               (first + 2, first, -1), (first, first + 1, -1)):
            gates.append((len(gates) + V.EVENTS, dst, src, sign, 2))
        result = V.replay(gates, self.correction)
        self.assertEqual(result["max_row_l1"], "81")
        self.assertEqual(result["max_denominator_exponent"], 4)

    def test_arithmetic_capacity_rejection(self):
        zero = V.Row([0] * V.SIZE, 0)
        numerator = [0] * V.SIZE
        numerator[0] = 1 << V.MAX_BITS
        with self.assertRaisesRegex(ValueError, "row capacity"):
            V.add_row(zero, V.Row(numerator, 0), 1, 0)
        numerator[0] = 1
        with self.assertRaisesRegex(ValueError, "row capacity"):
            V.add_row(zero, V.Row(numerator, V.MAX_EXPONENT), 1, 2)

    def test_optimized_git_free_export_and_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research/p104-relay-growth"
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            core = root / "research/p104-native-channel/inputs"
            core.mkdir(parents=True)
            for name in ("LOWRANK-WITNESS.json", "P104-FIXTURE.json"):
                shutil.copyfile(V.ROOT / "research/p104-native-channel/inputs" / name, core / name)
            before = snapshot(root)
            command = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]
            env = {**os.environ, "PATH": "/nonexistent"}
            result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["forward"]["max_row_l1"], "70")
            self.assertEqual(snapshot(root), before)
            expected_path = package / "EXPECTED.json"
            expected = expected_path.read_text()
            changed = json.loads(expected)
            changed["forward"]["max_row_l1"] = "69"
            expected_path.write_text(json.dumps(changed))
            result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt drift", result.stderr)
            expected_path.write_text(expected)
            with (core / "LOWRANK-WITNESS.json").open("a") as stream:
                stream.write(" ")
            result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source pin", result.stderr)

    def test_receipt_drift_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.json"
            command = [sys.executable, "-I", "-O", "-Werror", "-B",
                       str(PACKAGE / "verify.py"), "--out", str(receipt)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(receipt.read_text()), json.loads(result.stdout))
            receipt.write_text("do not overwrite")
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FileExistsError", result.stderr)
            self.assertEqual(receipt.read_text(), "do not overwrite")


def snapshot(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


if __name__ == "__main__":
    unittest.main()
