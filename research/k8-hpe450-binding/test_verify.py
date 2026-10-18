#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
"""Dense algebra cross-check and source-export failure controls."""
from fractions import Fraction
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hpe450_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def dense_matrix(operations, registers):
    """Independent full matrix evaluation, including arbitrary private inputs."""
    n = len(registers)
    matrix = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    for op in operations:
        target = registers.index(tuple(op[1]))
        if op[0] == "clear":
            matrix[target] = [Fraction(0)] * n
        elif op[0] == "copy":
            matrix[target] = matrix[registers.index(tuple(op[2]))].copy()
        elif op[0] == "scale":
            matrix[target] = [x * Fraction(op[2], op[3]) for x in matrix[target]]
        else:
            source = registers.index(tuple(op[2]))
            matrix[target] = [a + Fraction(op[3], op[4]) * b
                              for a, b in zip(matrix[target], matrix[source])]
    return matrix


class BindingTests(unittest.TestCase):
    def test_sparse_row_and_column_against_dense_matrix(self):
        registers = [("L", 0), ("L", 1), ("L", 2), ("C", 0)]
        alphabet = [
            ["add", ["L", 0], ["L", 1], 1, 2],
            ["add", ["L", 1], ["L", 2], -3, 4],
            ["scale", ["L", 0], 2, -1],
            ["clear", ["C", 0]],
            ["copy", ["C", 0], ["L", 2]],
            ["add", ["L", 1], ["C", 0], 1, 1],
            ["add", ["C", 0], ["L", 0], 1, 4],
            ["scale", ["C", 0], -1, 2],
        ]
        for word in itertools.product(alphabet, repeat=3):
            matrix = dense_matrix(word, registers)
            operations = [v.scalar(op) for op in word]
            for helper in range(3):
                row, column = v.scalar_row_column(operations, helper=helper)
                self.assertEqual(row, {r: matrix[helper][j] for j, r in enumerate(registers)
                                       if matrix[helper][j]})
                self.assertEqual(column, {r: matrix[i][helper] for i, r in enumerate(registers)
                                          if matrix[i][helper]})

    def test_restored_row_does_not_imply_isolated_column(self):
        row, column = v.scalar_row_column([v.scalar(["add", ["L", 1], ["L", 0], 3, 2])], helper=0)
        self.assertEqual(row, {("L", 0): 1})
        self.assertEqual(column, {("L", 0): 1, ("L", 1): Fraction(3, 2)})

    def test_structural_failure_controls(self):
        for op in (["scale", ["L", 0], 1, 0], ["scale", ["L", 0], True, 1],
                   ["copy", ["L", 0], ["L", 0]], ["add", ["L", -1], ["L", 1], 1, 1]):
            with self.assertRaises(v.Reject):
                v.scalar(op)
        with self.assertRaisesRegex(v.Reject, "dependent_frame_basis"):
            v.span([1, 2, 3])
        with self.assertRaisesRegex(v.Reject, "lean_pair_literal"):
            v.literal_pair3("def pair3 : Pair := missing")
        with self.assertRaisesRegex(v.Reject, "duplicate_json_key"):
            json.loads('{"rank":7,"rank":8}', object_pairs_hook=v.unique_object)
        self.assertNotEqual(v.encoded({"rank": 1}), v.encoded({"rank": True}))

    def test_source_tamper_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for row in v.read(HERE / "SOURCES.json")["files"]:
                if row["usage"] == "input":
                    dest = root / row["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / row["path"], dest)
            self.assertEqual(v.source_check(root), v.source_check())
            with (root / v.SOURCE / "hpe_emit_local.py").open("a") as out:
                out.write("\n# changed source\n")
            with self.assertRaisesRegex(v.Reject, "source_hash"):
                v.source_check(root)

    def test_read_only_optimized_export_and_corrupt_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(HERE / name, package / name)
            for row in v.read(HERE / "SOURCES.json")["files"]:
                if row["usage"] == "input":
                    dest = root / row["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / row["path"], dest)
            files = list(root.rglob("*"))
            files = [p for p in files if p.is_file()]
            before = {p: p.read_bytes() for p in files}
            for p in files:
                p.chmod(0o444)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            env = dict(os.environ, PYTHONOPTIMIZE="2")
            try:
                result = subprocess.run(command, cwd=tmp, env=env, capture_output=True, text=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("PASS_K8_HPE450_FINITE_BINDING", result.stdout)
                self.assertEqual(before, {p: p.read_bytes() for p in files})
                self.assertEqual(set(files), {p for p in root.rglob("*") if p.is_file()})
                receipt = package / "RESULT.json"
                receipt.chmod(0o644)
                bad = json.loads(receipt.read_text())
                bad["orientations"]["forward"]["pre_wrapper_index"] += 1
                receipt.write_text(json.dumps(bad))
                result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, timeout=180)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("receipt_mismatch", result.stderr)
            finally:
                for p in files:
                    p.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
