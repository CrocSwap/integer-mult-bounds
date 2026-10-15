#!/usr/bin/env python3
"""Behavioral controls for the local-ring lowering. Apache-2.0.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
"""
from itertools import product
import json
from math import gcd
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify
from child import (compile_projector, direct_action, execute, eye, multiply,
                   inverse, require)


class ChildTests(unittest.TestCase):
    def test_all_gl2_mod9_projectors(self):
        """An exhaustive independent chart family over a nonfield ring."""
        projectors = set()
        charts = 0
        for a, b, c, d in product(range(9), repeat=4):
            determinant = (a * d - b * c) % 9
            if gcd(determinant, 3) != 1:
                continue
            charts += 1
            di = pow(determinant, -1, 9)
            # Direct formula g diag(1,0) g^-1, separate from the compiler.
            projectors.add((a * d * di % 9, -a * b * di % 9,
                            c * d * di % 9, -c * b * di % 9))
        self.assertEqual(charts, 3888)
        self.assertEqual(len(projectors), 108)
        accepted, rejected = 0, 0
        for a, b, c, d in sorted(projectors):
            p = [[a, b], [c, d]]
            if gcd(a, 3) != 1:
                with self.assertRaisesRegex(ValueError, "nongeneric northeast pivot"):
                    compile_projector(p, 1, 3, 2)
                rejected += 1
                continue
            form = compile_projector(p, 1, 3, 2)
            accepted += 1
            for f in (1, 2, 3):
                weights = tuple((1, 2, 4, 5, 7, 8)[:2 * f])
                for position in range(4 * f):
                    head = [int(i == position) for i in range(2 * f)]
                    tail = [int(i + 2 * f == position) for i in range(2 * f)]
                    want = direct_action(p, weights, f, head, tail, 9)
                    self.assertEqual(execute(form, weights, f, head, tail), want)
        # Over F3, a=1 permits bc=0 (5 choices) and a=2 permits bc=1
        # (2 choices). Each rank-one projector has 3^2 lifts modulo 9.
        self.assertEqual((accepted, rejected), (7 * 9, 5 * 9))

    def test_nonzero_nonunit_is_not_zero(self):
        p = [[3, 1], [3, 7]]
        self.assertEqual(multiply(p, p, 9), p)
        self.assertEqual(p[0][0] % 3, 0)
        self.assertNotEqual(p[0][0], 0)
        with self.assertRaisesRegex(ValueError, "nongeneric northeast pivot"):
            compile_projector(p, 1, 3, 2)

    def test_high_field_counterexample(self):
        low = [[1, 24], [0, 0]]
        high = [[11, 24], [10, 15]]
        self.assertEqual([[x % 5 for x in row] for row in low],
                         [[x % 5 for x in row] for row in high])
        f0, f1 = [compile_projector(p, 1, 5, 2) for p in (low, high)]
        self.assertEqual((f0.pivots, f1.pivots), ((1,), (11,)))
        self.assertNotEqual(execute(f0, (1, 1), 1, [0, 0], [0, 1]),
                            execute(f1, (1, 1), 1, [0, 0], [0, 1]))

    def test_selected_source_mutations(self):
        original_root = verify.ROOT
        temporary_parent = original_root.parent / "tmp"
        temporary_parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="weighted-child-pins-", dir=temporary_parent) as folder:
            root = Path(folder)
            pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
            inputs = [p["path"] for p in pins if p["usage"] == "input"]
            for name in inputs:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original_root / name, target)
            try:
                verify.ROOT = root
                verify.source_object()
                for name in inputs:
                    target = root / name
                    raw = target.read_bytes()
                    target.write_bytes(raw + b"\nmutated\n")
                    with self.subTest(source=name):
                        with self.assertRaisesRegex(ValueError, "source binding"):
                            verify.source_object()
                    target.write_bytes(raw)
            finally:
                verify.ROOT = original_root

    def test_missing_receipt_and_no_overwrite_cli(self):
        temporary_parent = Path(tempfile.gettempdir())
        with tempfile.TemporaryDirectory(prefix="weighted-child-cli-", dir=temporary_parent) as folder:
            root = Path(folder)
            for name in ("verify.py", "child.py"):
                shutil.copyfile(HERE / name, root / name)
            command = [sys.executable, "-I", "-O", "-B", str(root / "verify.py")]
            missing = subprocess.run(command, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("RESULT.json", missing.stderr)
            target = root / "existing.json"
            target.write_text("preserve me\n")
            present = subprocess.run(command + ["--write-result", str(target)],
                                     capture_output=True, text=True, timeout=15)
            self.assertNotEqual(present.returncode, 0)
            self.assertIn("already exists", present.stderr)
            self.assertEqual(target.read_text(), "preserve me\n")


if __name__ == "__main__":
    unittest.main()
